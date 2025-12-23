"""Tests for parser module."""

from __future__ import annotations

from pathlib import Path

import pytest

from scp import generator, parser
from scp.exceptions import ValidationError


@pytest.fixture
def example_snapshot(tmp_path: Path) -> Path:
    """Create example snapshot file."""
    gen = generator.SCPGenerator("test-snapshot", "blog", "snapshot")

    gen.add_page(
        url="https://example.com/post1",
        title="First Post",
        description="The first blog post",
        modified="2025-01-15T10:00:00Z",
        language="en",
        content=[
            {"type": "heading", "level": 1, "text": "First Post"},
            {"type": "text", "text": "This is the first post."},
        ],
    )

    gen.add_page(
        url="https://example.com/post2",
        title="Second Post",
        description="The second blog post",
        modified="2025-01-15T11:00:00Z",
        language="en",
        content=[
            {"type": "heading", "level": 1, "text": "Second Post"},
            {"type": "text", "text": "This is the second post."},
        ],
    )

    file_path = tmp_path / "test.scp.gz"
    gen.save(file_path)
    return file_path


def test_parse_snapshot(example_snapshot: Path) -> None:
    """Test parsing a snapshot collection."""
    scp_parser = parser.SCPParser()
    metadata, pages = scp_parser.parse_file(example_snapshot)

    assert metadata.type == "snapshot"
    assert metadata.section == "blog"
    assert metadata.version == "0.1"
    assert len(pages) == 2


def test_parse_page_attributes(example_snapshot: Path) -> None:
    """Test parsed page attributes."""
    scp_parser = parser.SCPParser()
    _, pages = scp_parser.parse_file(example_snapshot)

    page = pages[0]
    assert page.url == "https://example.com/post1"
    assert page.title == "First Post"
    assert page.description == "The first blog post"
    assert page.language == "en"
    assert len(page.content) == 2


def test_parse_content_blocks(example_snapshot: Path) -> None:
    """Test parsing content blocks."""
    scp_parser = parser.SCPParser()
    _, pages = scp_parser.parse_file(example_snapshot)

    content = pages[0].content
    assert content[0]["type"] == "heading"
    assert content[0]["level"] == 1
    assert content[0]["text"] == "First Post"
    assert content[1]["type"] == "text"
    assert content[1]["text"] == "This is the first post."


def test_parse_uncompressed(tmp_path: Path) -> None:
    """Test parsing uncompressed file."""
    gen = generator.SCPGenerator("test", "blog")
    gen.add_page(
        url="https://example.com/",
        title="Home",
        description="Homepage",
        modified="2025-01-15T10:00:00Z",
        language="en",
        content=[{"type": "text", "text": "Welcome"}],
    )

    file_path = tmp_path / "test.scp"
    gen.save(file_path, compress=None)

    scp_parser = parser.SCPParser()
    metadata, pages = scp_parser.parse_file(file_path)

    assert len(pages) == 1


def test_parse_with_checksum(tmp_path: Path) -> None:
    """Test parsing file with checksum validation."""
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
    gen.save(file_path, include_checksum=True)

    scp_parser = parser.SCPParser()
    metadata, _ = scp_parser.parse_file(file_path)

    assert metadata.checksum is not None
    assert metadata.checksum.startswith("sha256:")


def test_parse_delta_collection(tmp_path: Path) -> None:
    """Test parsing delta collection."""
    gen = generator.SCPGenerator("test-delta", "blog", "delta", since="2025-01-14T00:00:00Z")
    gen.add_page(
        url="https://example.com/updated",
        title="Updated Post",
        description="This post was updated",
        modified="2025-01-15T10:00:00Z",
        language="en",
        content=[{"type": "text", "text": "Updated content"}],
    )

    file_path = tmp_path / "delta.scp.gz"
    gen.save(file_path)

    scp_parser = parser.SCPParser()
    metadata, pages = scp_parser.parse_file(file_path)

    assert metadata.type == "delta"
    assert metadata.since == "2025-01-14T00:00:00Z"
    assert len(pages) == 1


def test_parse_empty_file(tmp_path: Path) -> None:
    """Test parsing empty file raises error."""
    file_path = tmp_path / "empty.scp"
    file_path.write_bytes(b"")

    scp_parser = parser.SCPParser()
    with pytest.raises(ValidationError, match="Empty"):
        scp_parser.parse_file(file_path)


def test_parse_invalid_json(tmp_path: Path) -> None:
    """Test parsing file with invalid JSON."""
    file_path = tmp_path / "invalid.scp"
    file_path.write_text("not json\n")

    scp_parser = parser.SCPParser()
    with pytest.raises(ValidationError, match="Invalid JSON"):
        scp_parser.parse_file(file_path)


def test_parse_strict_mode(tmp_path: Path) -> None:
    """Test strict mode fails on malformed pages."""
    # Create file with one valid and one invalid page
    content = (
        '{"collection":{"id":"test","section":"blog","type":"snapshot",'
        '"generated":"2025-01-15T10:00:00Z","version":"0.1"}}\n'
        '{"url":"https://example.com/valid","title":"Valid","description":"Valid page",'
        '"modified":"2025-01-15T10:00:00Z","language":"en",'
        '"content":[{"type":"text","text":"Valid"}]}\n'
        '{"url":"invalid-url","title":"Invalid","description":"Invalid page",'
        '"modified":"2025-01-15T10:00:00Z","language":"en",'
        '"content":[{"type":"text","text":"Invalid"}]}\n'
    )

    file_path = tmp_path / "mixed.scp"
    file_path.write_text(content)

    # Non-strict should skip invalid page
    scp_parser = parser.SCPParser(strict=False)
    _, pages = scp_parser.parse_file(file_path)
    assert len(pages) == 1
    assert len(scp_parser.errors) > 0

    # Strict should raise
    scp_parser_strict = parser.SCPParser(strict=True)
    with pytest.raises(ValidationError):
        scp_parser_strict.parse_file(file_path)


def test_parse_utf8_content(tmp_path: Path) -> None:
    """Test parsing UTF-8 content with emoji and multibyte chars."""
    gen = generator.SCPGenerator("test", "blog")
    gen.add_page(
        url="https://example.com/utf8",
        title="UTF-8 Test 你好 🌍",
        description="Testing UTF-8 content",
        modified="2025-01-15T10:00:00Z",
        language="zh",
        content=[
            {"type": "text", "text": "Hello 世界 🚀"},
            {"type": "heading", "level": 1, "text": "标题 Заголовок"},
        ],
    )

    file_path = tmp_path / "utf8.scp.gz"
    gen.save(file_path)

    scp_parser = parser.SCPParser()
    _, pages = scp_parser.parse_file(file_path)

    assert "你好" in pages[0].title
    assert "世界" in pages[0].content[0]["text"]
