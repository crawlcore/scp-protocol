"""Tests for generator module."""

from __future__ import annotations

from pathlib import Path

import pytest

from scp import generator
from scp.exceptions import ValidationError


def test_generate_snapshot() -> None:
    """Test generating snapshot collection."""
    gen = generator.SCPGenerator("test-snapshot", "blog", "snapshot")

    gen.add_page(
        url="https://example.com/post",
        title="Test Post",
        description="A test post",
        modified="2025-01-15T10:00:00Z",
        language="en",
        content=[{"type": "text", "text": "Hello"}],
    )

    data = gen.generate(compress=None)
    assert len(data) > 0


def test_generate_delta() -> None:
    """Test generating delta collection."""
    gen = generator.SCPGenerator("test-delta", "blog", "delta", since="2025-01-14T00:00:00Z")

    gen.add_page(
        url="https://example.com/updated",
        title="Updated",
        description="Updated page",
        modified="2025-01-15T10:00:00Z",
        language="en",
        content=[{"type": "text", "text": "Updated"}],
    )

    data = gen.generate(compress=None)
    assert b"delta" in data
    assert b"2025-01-14" in data


def test_generate_compressed_gzip() -> None:
    """Test generating gzip compressed collection."""
    gen = generator.SCPGenerator("test", "blog")
    gen.add_page(
        url="https://example.com/",
        title="Home",
        description="Homepage",
        modified="2025-01-15T10:00:00Z",
        language="en",
        content=[{"type": "text", "text": "Welcome"}],
    )

    data = gen.generate(compress="gzip")
    assert data.startswith(b"\x1f\x8b")  # gzip magic number


def test_generate_compressed_zstd() -> None:
    """Test generating zstd compressed collection."""
    gen = generator.SCPGenerator("test", "blog")
    gen.add_page(
        url="https://example.com/",
        title="Home",
        description="Homepage",
        modified="2025-01-15T10:00:00Z",
        language="en",
        content=[{"type": "text", "text": "Welcome"}],
    )

    data = gen.generate(compress="zstd")
    assert data.startswith(b"\x28\xb5\x2f\xfd")  # zstd magic number


def test_generate_with_checksum() -> None:
    """Test generating collection with checksum."""
    gen = generator.SCPGenerator("test", "blog")
    gen.add_page(
        url="https://example.com/",
        title="Home",
        description="Homepage",
        modified="2025-01-15T10:00:00Z",
        language="en",
        content=[{"type": "text", "text": "Welcome"}],
    )

    data = gen.generate(compress=None, include_checksum=True)
    assert b"sha256:" in data


def test_generate_save_file(tmp_path: Path) -> None:
    """Test saving generated collection to file."""
    gen = generator.SCPGenerator("test", "blog")
    gen.add_page(
        url="https://example.com/",
        title="Home",
        description="Homepage",
        modified="2025-01-15T10:00:00Z",
        language="en",
        content=[{"type": "text", "text": "Welcome"}],
    )

    file_path = tmp_path / "test.scp.gz"
    gen.save(file_path)

    assert file_path.exists()
    assert file_path.stat().st_size > 0


def test_generate_no_pages_error() -> None:
    """Test generating without adding pages raises error."""
    gen = generator.SCPGenerator("test", "blog")

    with pytest.raises(ValidationError, match="No pages"):
        gen.generate()


def test_generate_delta_without_since_error() -> None:
    """Test creating delta without since parameter raises error."""
    with pytest.raises(ValidationError, match="since"):
        generator.SCPGenerator("test", "blog", "delta")


def test_generate_invalid_collection_type() -> None:
    """Test invalid collection type raises error."""
    with pytest.raises(ValidationError, match="Invalid collection type"):
        generator.SCPGenerator("test", "blog", "invalid")


def test_add_page_dict() -> None:
    """Test adding page from dictionary."""
    gen = generator.SCPGenerator("test", "blog")

    page_dict = {
        "url": "https://example.com/",
        "title": "Home",
        "description": "Homepage",
        "modified": "2025-01-15T10:00:00Z",
        "language": "en",
        "content": [{"type": "text", "text": "Welcome"}],
    }

    gen.add_page_dict(page_dict)
    assert len(gen.pages) == 1


def test_add_page_with_optional_fields() -> None:
    """Test adding page with all optional fields."""
    gen = generator.SCPGenerator("test", "blog")

    gen.add_page(
        url="https://example.com/post",
        title="Post",
        description="A post",
        modified="2025-01-15T10:00:00Z",
        language="en",
        content=[{"type": "text", "text": "Content"}],
        author="John Doe",
        published="2025-01-10T10:00:00Z",
        canonical="https://example.com/post",
        robots=["noarchive"],
        schema_data={"@type": "BlogPosting"},
    )

    assert len(gen.pages) == 1
    page = gen.pages[0]
    assert page["author"] == "John Doe"
    assert page["published"] == "2025-01-10T10:00:00Z"
    assert page["canonical"] == "https://example.com/post"
    assert page["robots"] == ["noarchive"]
    assert page["schema"] == {"@type": "BlogPosting"}


def test_generate_utf8_content() -> None:
    """Test generating UTF-8 content."""
    gen = generator.SCPGenerator("test", "blog")

    gen.add_page(
        url="https://example.com/utf8",
        title="UTF-8 Test 你好 🌍",
        description="Testing UTF-8",
        modified="2025-01-15T10:00:00Z",
        language="zh",
        content=[
            {"type": "text", "text": "Hello 世界 🚀"},
        ],
    )

    data = gen.generate(compress=None)
    text = data.decode("utf-8")
    assert "你好" in text
    assert "世界" in text
    assert "🚀" in text
