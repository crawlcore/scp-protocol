"""Tests for schema validation module."""

from __future__ import annotations

import pytest

from scp import schema
from scp.exceptions import ValidationError


def test_validate_collection_metadata_snapshot() -> None:
    """Test valid snapshot collection metadata."""
    data = {
        "collection": {
            "id": "test-snapshot",
            "section": "blog",
            "type": "snapshot",
            "generated": "2025-01-15T10:00:00Z",
            "version": "0.1",
        }
    }

    schema.validate_collection_metadata(data)  # Should not raise


def test_validate_collection_metadata_delta() -> None:
    """Test valid delta collection metadata."""
    data = {
        "collection": {
            "id": "test-delta",
            "section": "blog",
            "type": "delta",
            "generated": "2025-01-15T10:00:00Z",
            "since": "2025-01-14T00:00:00Z",
            "version": "0.1",
        }
    }

    schema.validate_collection_metadata(data)  # Should not raise


def test_validate_collection_metadata_missing_field() -> None:
    """Test collection metadata with missing required field."""
    data = {
        "collection": {
            "id": "test",
            "section": "blog",
            # Missing 'type'
            "generated": "2025-01-15T10:00:00Z",
            "version": "0.1",
        }
    }

    with pytest.raises(ValidationError):
        schema.validate_collection_metadata(data)


def test_validate_collection_metadata_delta_missing_since() -> None:
    """Test delta collection without 'since' field."""
    data = {
        "collection": {
            "id": "test-delta",
            "section": "blog",
            "type": "delta",
            "generated": "2025-01-15T10:00:00Z",
            # Missing 'since'
            "version": "0.1",
        }
    }

    with pytest.raises(ValidationError):
        schema.validate_collection_metadata(data)


def test_validate_page_minimal() -> None:
    """Test minimal valid page object."""
    data = {
        "url": "https://example.com/page",
        "title": "Test Page",
        "description": "A test page",
        "modified": "2025-01-15T10:00:00Z",
        "language": "en",
        "content": [{"type": "text", "text": "Hello"}],
    }

    schema.validate_page(data)  # Should not raise


def test_validate_page_missing_required() -> None:
    """Test page object missing required field."""
    data = {
        "url": "https://example.com/page",
        "title": "Test Page",
        # Missing 'description'
        "modified": "2025-01-15T10:00:00Z",
        "language": "en",
        "content": [{"type": "text", "text": "Hello"}],
    }

    with pytest.raises(ValidationError):
        schema.validate_page(data)


def test_validate_page_invalid_url() -> None:
    """Test page with invalid URL."""
    data = {
        "url": "not-a-url",
        "title": "Test",
        "description": "Test",
        "modified": "2025-01-15T10:00:00Z",
        "language": "en",
        "content": [{"type": "text", "text": "Hello"}],
    }

    with pytest.raises(ValidationError):
        schema.validate_page(data)


def test_validate_page_too_many_content_blocks() -> None:
    """Test page exceeding maximum content blocks."""
    data = {
        "url": "https://example.com/page",
        "title": "Test",
        "description": "Test",
        "modified": "2025-01-15T10:00:00Z",
        "language": "en",
        "content": [{"type": "text", "text": f"Block {i}"} for i in range(1001)],
    }

    with pytest.raises(ValidationError, match="maximum is 1000"):
        schema.validate_page(data)


def test_validate_content_block_text() -> None:
    """Test valid text content block."""
    block = {"type": "text", "text": "Hello, World!"}

    assert schema.validate_content_block(block) is True


def test_validate_content_block_heading() -> None:
    """Test valid heading content block."""
    block = {"type": "heading", "level": 2, "text": "Section Title"}

    assert schema.validate_content_block(block) is True


def test_validate_content_block_link() -> None:
    """Test valid link content block."""
    block = {"type": "link", "url": "https://example.com", "text": "Click here"}

    assert schema.validate_content_block(block) is True


def test_validate_content_block_unknown_type() -> None:
    """Test unknown content block type (should be allowed)."""
    block = {"type": "unknown", "data": "something"}

    # Unknown types return False but don't raise
    result = schema.validate_content_block(block)
    assert result is False


def test_validate_content_block_missing_type() -> None:
    """Test content block without type field."""
    block = {"text": "Hello"}

    with pytest.raises(ValidationError, match="missing 'type' field"):
        schema.validate_content_block(block)


def test_validate_content_block_invalid_heading_level() -> None:
    """Test heading with invalid level."""
    block = {"type": "heading", "level": 7, "text": "Invalid"}

    with pytest.raises(ValidationError):
        schema.validate_content_block(block)
