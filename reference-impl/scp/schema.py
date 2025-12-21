"""JSON Schema validation for SCP collections."""

from __future__ import annotations

from pathlib import Path

import jsonschema
import orjson

from scp.exceptions import ValidationError

# Maximum sizes
MAX_PAGE_SIZE = 100 * 1024 * 1024  # 100 MB per page
MAX_CONTENT_BLOCKS = 1000  # Maximum content blocks per page

# Load schemas from JSON files (root-level schemas directory)
SCHEMA_DIR = Path(__file__).parent.parent.parent / "schemas"


def load_schema(name: str) -> dict:
    """Load JSON schema from file.

    Args:
        name: Schema name (without .json extension)

    Returns:
        Schema dictionary

    Raises:
        ValidationError: If schema file cannot be loaded
    """
    schema_path = SCHEMA_DIR / f"{name}.json"
    try:
        with open(schema_path, "rb") as f:
            return orjson.loads(f.read())  # type: ignore[no-any-return]
    except FileNotFoundError as e:
        raise ValidationError(f"Schema file not found: {schema_path}") from e
    except orjson.JSONDecodeError as e:
        raise ValidationError(f"Invalid JSON in schema file {schema_path}: {e}") from e


# Load schemas at module import
COLLECTION_SCHEMA = load_schema("collection")
PAGE_SCHEMA = load_schema("page")


def validate_collection_metadata(data: dict) -> None:
    """Validate collection metadata against schema.

    Args:
        data: Collection metadata dictionary

    Raises:
        ValidationError: If validation fails
    """
    try:
        jsonschema.validate(instance=data, schema=COLLECTION_SCHEMA)
    except jsonschema.ValidationError as e:
        raise ValidationError(f"Collection metadata validation failed: {e.message}") from e
    except jsonschema.SchemaError as e:
        raise ValidationError(f"Invalid schema: {e.message}") from e


def validate_page(data: dict) -> None:
    """Validate page object against schema.

    Args:
        data: Page object dictionary

    Raises:
        ValidationError: If validation fails
    """
    try:
        # Check content array size
        if "content" in data and len(data["content"]) > MAX_CONTENT_BLOCKS:
            raise ValidationError(
                f"Content array has {len(data['content'])} blocks, "
                f"maximum is {MAX_CONTENT_BLOCKS}"
            )

        jsonschema.validate(instance=data, schema=PAGE_SCHEMA)
    except jsonschema.ValidationError as e:
        raise ValidationError(f"Page validation failed: {e.message}") from e
    except jsonschema.SchemaError as e:
        raise ValidationError(f"Invalid schema: {e.message}") from e


def validate_content_block(block: dict) -> bool:
    """Validate a single content block.

    Args:
        block: Content block dictionary

    Returns:
        True if valid, False if unknown type (which is acceptable)

    Raises:
        ValidationError: If validation fails for known types
    """
    if not isinstance(block, dict):
        raise ValidationError("Content block must be a dictionary")

    if "type" not in block:
        raise ValidationError("Content block missing 'type' field")

    # Known content block types
    known_types = {
        "text",
        "heading",
        "link",
        "image",
        "list",
        "code",
        "table",
        "quote",
        "video",
        "audio",
        "structured",
    }

    # If unknown type, return False without validation (graceful skip)
    if block["type"] not in known_types:
        return False

    # Extract content block schema from page schema
    content_block_schema = {
        "$schema": PAGE_SCHEMA["$schema"],
        "definitions": PAGE_SCHEMA["definitions"],
        "$ref": "#/definitions/contentBlock",
    }

    try:
        jsonschema.validate(instance=block, schema=content_block_schema)
        return True
    except jsonschema.ValidationError as e:
        raise ValidationError(f"Content block validation failed: {e.message}") from e
