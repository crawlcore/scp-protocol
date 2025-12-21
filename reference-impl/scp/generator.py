"""Generator for SCP collections."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

import orjson

from scp import checksum, compression
from scp.exceptions import ValidationError


class SCPGenerator:
    """Generator for creating SCP collection files."""

    def __init__(
        self,
        collection_id: str,
        section: str,
        collection_type: str = "snapshot",
        since: str | None = None,
        version: str = "0.1",
    ):
        """Initialize generator.

        Args:
            collection_id: Unique collection identifier
            section: Section name (e.g., blog, docs)
            collection_type: "snapshot" or "delta"
            since: ISO 8601 timestamp for delta collections
            version: SCP format version

        Raises:
            ValidationError: If parameters are invalid
        """
        if collection_type not in ("snapshot", "delta"):
            raise ValidationError(f"Invalid collection type: {collection_type}")

        if collection_type == "delta" and not since:
            raise ValidationError("Delta collections require 'since' parameter")

        self.collection_id = collection_id
        self.section = section
        self.collection_type = collection_type
        self.since = since
        self.version = version
        self.pages: list[dict] = []

    def add_page(
        self,
        url: str,
        title: str,
        description: str,
        modified: str,
        language: str,
        content: list[dict],
        author: str | None = None,
        published: str | None = None,
        canonical: str | None = None,
        robots: list[str] | None = None,
        schema_data: dict | None = None,
    ) -> None:
        """Add a page to the collection.

        Args:
            url: Full page URL
            title: Page title
            description: Meta description
            modified: ISO 8601 last modified date
            language: Language code (e.g., "en")
            content: List of content blocks
            author: Optional author name
            published: Optional ISO 8601 publication date
            canonical: Optional canonical URL
            robots: Optional list of robot directives
            schema_data: Optional Schema.org structured data
        """
        page = {
            "url": url,
            "title": title,
            "description": description,
            "modified": modified,
            "language": language,
            "content": content,
        }

        if author:
            page["author"] = author
        if published:
            page["published"] = published
        if canonical:
            page["canonical"] = canonical
        if robots:
            page["robots"] = robots
        if schema_data:
            page["schema"] = schema_data  # type: ignore[assignment]

        self.pages.append(page)

    def add_page_dict(self, page: dict) -> None:
        """Add a page from dictionary.

        Args:
            page: Page dictionary with all required fields
        """
        self.pages.append(page)

    def generate(
        self, include_checksum: bool = True, compress: str | None = "gzip", compress_level: int = 6
    ) -> bytes:
        """Generate SCP collection file content.

        Args:
            include_checksum: Whether to include SHA-256 checksum
            compress: Compression type ("gzip", "zstd", or None)
            compress_level: Compression level (1-9 for gzip, 1-22 for zstd)

        Returns:
            Compressed (or uncompressed) file content

        Raises:
            ValidationError: If no pages added
        """
        if not self.pages:
            raise ValidationError("No pages added to collection")

        # Collection metadata
        metadata = {
            "collection": {
                "id": self.collection_id,
                "section": self.section,
                "type": self.collection_type,
                "generated": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
                "version": self.version,
            }
        }

        if self.since:
            metadata["collection"]["since"] = self.since

        # Convert to JSON Lines format
        output_lines = [orjson.dumps(metadata).decode("utf-8")]

        for page in self.pages:
            output_lines.append(orjson.dumps(page).decode("utf-8"))

        # Join with newlines
        content = "\n".join(output_lines)
        data = content.encode("utf-8")

        # Add checksum if requested
        if include_checksum:
            file_checksum = checksum.calculate_checksum(data)
            metadata["collection"]["checksum"] = file_checksum

            # Rebuild with checksum
            output_lines[0] = orjson.dumps(metadata).decode("utf-8")
            content = "\n".join(output_lines)
            data = content.encode("utf-8")

        # Compress if requested
        if compress == "gzip":
            return compression.compress_gzip(data, level=compress_level)
        elif compress == "zstd":
            return compression.compress_zstd(data, level=compress_level)
        elif compress is None:
            return data
        else:
            raise ValidationError(f"Unknown compression type: {compress}")

    def save(
        self,
        file_path: str | Path,
        include_checksum: bool = True,
        compress: str | None = "gzip",
        compress_level: int = 6,
    ) -> None:
        """Generate and save SCP collection file.

        Args:
            file_path: Output file path
            include_checksum: Whether to include SHA-256 checksum
            compress: Compression type ("gzip", "zstd", or None)
            compress_level: Compression level

        Raises:
            ValidationError: If generation fails
        """
        data = self.generate(
            include_checksum=include_checksum, compress=compress, compress_level=compress_level
        )

        file_path = Path(file_path)
        file_path.parent.mkdir(parents=True, exist_ok=True)

        with open(file_path, "wb") as f:
            f.write(data)


def generate_collection(
    collection_id: str,
    section: str,
    pages: list[dict],
    collection_type: str = "snapshot",
    since: str | None = None,
    output_path: str | Path | None = None,
    compress: str | None = "gzip",
) -> bytes | None:
    """Generate SCP collection (convenience function).

    Args:
        collection_id: Unique collection identifier
        section: Section name
        pages: List of page dictionaries
        collection_type: "snapshot" or "delta"
        since: ISO 8601 timestamp for delta collections
        output_path: Optional output file path (if None, returns bytes)
        compress: Compression type ("gzip", "zstd", or None)

    Returns:
        Compressed data if output_path is None, otherwise None
    """
    generator = SCPGenerator(
        collection_id=collection_id,
        section=section,
        collection_type=collection_type,
        since=since,
    )

    for page in pages:
        generator.add_page_dict(page)

    if output_path:
        generator.save(output_path, compress=compress)
        return None
    else:
        return generator.generate(compress=compress)
