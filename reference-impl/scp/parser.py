"""Parser for SCP collections."""

from __future__ import annotations

import logging
from pathlib import Path

import orjson

from scp import checksum, compression, schema
from scp.exceptions import ChecksumError, DecompressionError, SizeLimitError, ValidationError

logger = logging.getLogger(__name__)


class CollectionMetadata:
    """Collection metadata from first line of SCP file."""

    def __init__(self, data: dict):
        """Initialize collection metadata.

        Args:
            data: Collection metadata dictionary
        """
        self.raw = data
        coll = data["collection"]
        self.id = coll["id"]
        self.section = coll["section"]
        self.type = coll["type"]
        self.generated = coll["generated"]
        self.since = coll.get("since")
        self.checksum = coll.get("checksum")
        self.version = coll["version"]

    def __repr__(self) -> str:
        return f"<Collection {self.id} ({self.type}) section={self.section}>"


class Page:
    """SCP page object."""

    def __init__(self, data: dict):
        """Initialize page object.

        Args:
            data: Page dictionary
        """
        self.raw = data
        self.url = data["url"]
        self.title = data["title"]
        self.description = data["description"]
        self.author = data.get("author")
        self.published = data.get("published")
        self.modified = data["modified"]
        self.language = data["language"]
        self.canonical = data.get("canonical")
        self.robots = data.get("robots", [])
        self.schema_data = data.get("schema")
        self.content = data["content"]

    def __repr__(self) -> str:
        return f"<Page {self.url}>"


class SCPParser:
    """Parser for SCP collection files.

    Supports compressed (.scp.gz, .scp.zst) and uncompressed (.scp) files.
    Parses line-by-line for memory efficiency.
    """

    def __init__(self, strict: bool = False):
        """Initialize parser.

        Args:
            strict: Whether to raise on non-fatal errors like unknown content blocks

        Note:
            Validation is mandatory per SCP v0.1 specification.
            Parsers MUST validate collection metadata and page objects.
        """
        self.strict = strict
        self.metadata: CollectionMetadata | None = None
        self.pages: list[Page] = []
        self._errors: list[str] = []

    @property
    def errors(self) -> list[str]:
        """Get list of non-fatal errors encountered during parsing."""
        return self._errors

    def parse_file(self, file_path: str | Path) -> tuple[CollectionMetadata, list[Page]]:
        """Parse SCP collection file.

        Args:
            file_path: Path to .scp, .scp.gz, or .scp.zst file

        Returns:
            Tuple of (metadata, pages)

        Raises:
            DecompressionError: If decompression fails
            ValidationError: If validation fails
            ChecksumError: If checksum verification fails
        """
        file_path = Path(file_path)

        # Read file
        with open(file_path, "rb") as f:
            compressed_data = f.read()

        # Detect compression and decompress
        compression_type = compression.detect_compression(compressed_data)

        if compression_type == "gzip":
            data = compression.decompress_gzip(compressed_data)
        elif compression_type == "zstd":
            data = compression.decompress_zstd(compressed_data)
        elif compression_type == "none":
            data = compressed_data
        else:
            raise DecompressionError(f"Unknown compression type: {compression_type}")

        # Verify checksum if present
        lines = data.decode("utf-8").strip().split("\n")
        if not lines or not lines[0]:
            raise ValidationError("Empty file")

        # Parse first line (collection metadata)
        try:
            metadata_dict = orjson.loads(lines[0])
        except orjson.JSONDecodeError as e:
            raise ValidationError(f"Invalid JSON in line 1: {e}") from e

        if "collection" not in metadata_dict:
            raise ValidationError("First line must contain collection metadata")

        # Validate metadata (mandatory per SCP v0.1 spec)
        schema.validate_collection_metadata(metadata_dict)

        self.metadata = CollectionMetadata(metadata_dict)

        # Verify checksum if present
        if self.metadata.checksum:
            try:
                checksum.validate_checksum(data, self.metadata.checksum)
            except ChecksumError as e:
                if self.strict:
                    raise
                self._errors.append(f"Checksum validation failed: {e}")

        # Parse pages
        self.pages = []
        for line_num, line in enumerate(lines[1:], start=2):
            if not line.strip():
                continue

            try:
                page_dict = orjson.loads(line)
            except orjson.JSONDecodeError as e:
                error_msg = f"Invalid JSON in line {line_num}: {e}"
                if self.strict:
                    raise ValidationError(error_msg) from e
                self._errors.append(error_msg)
                continue

            # Check page size
            page_size = len(line.encode("utf-8"))
            if page_size > schema.MAX_PAGE_SIZE:
                raise SizeLimitError(
                    f"Page at line {line_num} exceeds maximum size "
                    f"({page_size} > {schema.MAX_PAGE_SIZE})"
                )

            # Validate page (mandatory per SCP v0.1 spec)
            try:
                schema.validate_page(page_dict)
            except ValidationError as e:
                error_msg = f"Page validation failed at line {line_num}: {e}"
                if self.strict:
                    raise ValidationError(error_msg) from e
                self._errors.append(error_msg)
                continue

            # Check for unknown content block types (SCP v0.1 spec: MUST log warning, MUST continue)
            if "content" in page_dict:
                for block_idx, block in enumerate(page_dict["content"]):
                    if isinstance(block, dict) and "type" in block:
                        try:
                            is_known = schema.validate_content_block(block)
                            if not is_known:
                                # MUST log warning for unknown types
                                warning_msg = (
                                    f"Unknown content block type '{block['type']}' "
                                    f"at line {line_num}, block {block_idx}. "
                                    f"Skipping block and continuing (per SCP v0.1 spec)."
                                )
                                logger.warning(warning_msg)
                                self._errors.append(warning_msg)
                        except ValidationError:
                            # Known type but validation failed - already handled by page validation
                            pass

            try:
                page = Page(page_dict)
                self.pages.append(page)
            except Exception as e:
                error_msg = f"Failed to parse page at line {line_num}: {e}"
                if self.strict:
                    raise ValidationError(error_msg) from e
                self._errors.append(error_msg)

        return self.metadata, self.pages

    def parse_bytes(self, data: bytes) -> tuple[CollectionMetadata, list[Page]]:
        """Parse SCP collection from bytes.

        Args:
            data: Compressed or uncompressed SCP data

        Returns:
            Tuple of (metadata, pages)
        """
        # Detect compression
        compression_type = compression.detect_compression(data)

        if compression_type == "gzip":
            decompressed = compression.decompress_gzip(data)
        elif compression_type == "zstd":
            decompressed = compression.decompress_zstd(data)
        else:
            decompressed = data

        # Parse lines
        lines = decompressed.decode("utf-8").strip().split("\n")
        if not lines:
            raise ValidationError("Empty data")

        # Parse metadata (mandatory per SCP v0.1 spec)
        metadata_dict = orjson.loads(lines[0])
        schema.validate_collection_metadata(metadata_dict)
        self.metadata = CollectionMetadata(metadata_dict)

        # Verify checksum
        if self.metadata.checksum:
            checksum.validate_checksum(decompressed, self.metadata.checksum)

        # Parse pages
        self.pages = []
        for line_num, line in enumerate(lines[1:], start=2):
            if not line.strip():
                continue

            page_dict = orjson.loads(line)
            # Validate page (mandatory per SCP v0.1 spec)
            schema.validate_page(page_dict)

            # Check for unknown content block types (SCP v0.1 spec: MUST log warning, MUST continue)
            if "content" in page_dict:
                for block_idx, block in enumerate(page_dict["content"]):
                    if isinstance(block, dict) and "type" in block:
                        try:
                            is_known = schema.validate_content_block(block)
                            if not is_known:
                                # MUST log warning for unknown types
                                warning_msg = (
                                    f"Unknown content block type '{block['type']}' "
                                    f"at line {line_num}, block {block_idx}. "
                                    f"Skipping block and continuing (per SCP v0.1 spec)."
                                )
                                logger.warning(warning_msg)
                        except ValidationError:
                            # Known type but validation failed - already handled by page validation
                            pass

            self.pages.append(Page(page_dict))

        return self.metadata, self.pages


def parse_collection(
    file_path: str | Path, strict: bool = False
) -> tuple[CollectionMetadata, list[Page]]:
    """Parse SCP collection file (convenience function).

    Args:
        file_path: Path to .scp, .scp.gz, or .scp.zst file
        strict: Whether to raise on non-fatal errors

    Returns:
        Tuple of (metadata, pages)

    Note:
        Validation is mandatory per SCP v0.1 specification.
    """
    parser = SCPParser(strict=strict)
    return parser.parse_file(file_path)
