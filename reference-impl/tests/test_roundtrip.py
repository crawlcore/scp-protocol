"""Roundtrip tests (generate then parse)."""

from __future__ import annotations

from pathlib import Path

from scp import generator, parser


def test_roundtrip_basic(tmp_path: Path) -> None:
    """Test basic roundtrip: generate then parse."""
    # Generate
    gen = generator.SCPGenerator("test", "blog")
    gen.add_page(
        url="https://example.com/page",
        title="Test Page",
        description="A test page",
        modified="2025-01-15T10:00:00Z",
        language="en",
        content=[
            {"type": "heading", "level": 1, "text": "Title"},
            {"type": "text", "text": "Content goes here."},
        ],
    )

    file_path = tmp_path / "test.scp.gz"
    gen.save(file_path)

    # Parse
    scp_parser = parser.SCPParser()
    metadata, pages = scp_parser.parse_file(file_path)

    # Verify
    assert metadata.id == "test"
    assert metadata.section == "blog"
    assert len(pages) == 1
    assert pages[0].url == "https://example.com/page"
    assert pages[0].title == "Test Page"
    assert len(pages[0].content) == 2


def test_roundtrip_multiple_pages(tmp_path: Path) -> None:
    """Test roundtrip with multiple pages."""
    gen = generator.SCPGenerator("test", "blog")

    for i in range(10):
        gen.add_page(
            url=f"https://example.com/post-{i}",
            title=f"Post {i}",
            description=f"Post number {i}",
            modified="2025-01-15T10:00:00Z",
            language="en",
            content=[{"type": "text", "text": f"Content {i}"}],
        )

    file_path = tmp_path / "test.scp.gz"
    gen.save(file_path)

    scp_parser = parser.SCPParser()
    _, pages = scp_parser.parse_file(file_path)

    assert len(pages) == 10
    for i, page in enumerate(pages):
        assert page.url == f"https://example.com/post-{i}"
        assert page.title == f"Post {i}"


def test_roundtrip_all_content_types(tmp_path: Path) -> None:
    """Test roundtrip with all content block types."""
    gen = generator.SCPGenerator("test", "docs")

    gen.add_page(
        url="https://example.com/docs",
        title="Documentation",
        description="Full documentation",
        modified="2025-01-15T10:00:00Z",
        language="en",
        content=[
            {"type": "heading", "level": 1, "text": "Heading 1"},
            {"type": "heading", "level": 2, "text": "Heading 2"},
            {"type": "text", "text": "Paragraph text"},
            {"type": "link", "url": "https://example.com", "text": "Link", "rel": ["nofollow"]},
            {"type": "image", "url": "https://example.com/img.jpg", "alt": "Image"},
            {"type": "list", "ordered": False, "items": ["Item 1", "Item 2"]},
            {"type": "list", "ordered": True, "items": ["Step 1", "Step 2"]},
            {"type": "code", "language": "python", "code": "print('hello')"},
            {"type": "table", "rows": [["A", "B"], ["C", "D"]]},
            {"type": "quote", "text": "Quote", "citation": "Author"},
            {
                "type": "video",
                "sources": [{"url": "https://example.com/video.mp4"}],
                "title": "Video",
            },
            {
                "type": "audio",
                "sources": [{"url": "https://example.com/audio.mp3"}],
                "title": "Audio",
            },
            {"type": "structured", "format": "json-ld", "data": {"@type": "Thing"}},
        ],
    )

    file_path = tmp_path / "test.scp.gz"
    gen.save(file_path)

    scp_parser = parser.SCPParser()
    _, pages = scp_parser.parse_file(file_path)

    assert len(pages) == 1
    assert len(pages[0].content) == 13

    # Verify each content type
    content = pages[0].content
    assert content[0]["type"] == "heading"
    assert content[2]["type"] == "text"
    assert content[3]["type"] == "link"
    assert content[4]["type"] == "image"
    assert content[5]["type"] == "list"
    assert content[7]["type"] == "code"
    assert content[8]["type"] == "table"
    assert content[9]["type"] == "quote"
    assert content[10]["type"] == "video"
    assert content[11]["type"] == "audio"
    assert content[12]["type"] == "structured"


def test_roundtrip_with_checksum(tmp_path: Path) -> None:
    """Test roundtrip with checksum validation."""
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
    metadata, pages = scp_parser.parse_file(file_path)

    assert metadata.checksum is not None
    assert len(pages) == 1


def test_roundtrip_delta_collection(tmp_path: Path) -> None:
    """Test roundtrip with delta collection."""
    gen = generator.SCPGenerator("test-delta", "blog", "delta", since="2025-01-14T00:00:00Z")
    gen.add_page(
        url="https://example.com/updated",
        title="Updated",
        description="Updated page",
        modified="2025-01-15T10:00:00Z",
        language="en",
        content=[{"type": "text", "text": "New content"}],
    )

    file_path = tmp_path / "delta.scp.gz"
    gen.save(file_path)

    scp_parser = parser.SCPParser()
    metadata, pages = scp_parser.parse_file(file_path)

    assert metadata.type == "delta"
    assert metadata.since == "2025-01-14T00:00:00Z"
    assert len(pages) == 1


def test_roundtrip_utf8(tmp_path: Path) -> None:
    """Test roundtrip with UTF-8 content."""
    gen = generator.SCPGenerator("test", "blog")

    gen.add_page(
        url="https://example.com/utf8",
        title="UTF-8 你好 🌍",
        description="Testing UTF-8",
        modified="2025-01-15T10:00:00Z",
        language="zh",
        content=[
            {"type": "heading", "level": 1, "text": "标题 Title Заголовок"},
            {"type": "text", "text": "Hello 世界 Мир 🚀"},
            {"type": "list", "ordered": False, "items": ["項目 1", "項目 2", "Пункт 3"]},
        ],
    )

    file_path = tmp_path / "utf8.scp.gz"
    gen.save(file_path)

    scp_parser = parser.SCPParser()
    _, pages = scp_parser.parse_file(file_path)

    page = pages[0]
    assert "你好" in page.title
    assert "🌍" in page.title
    assert "标题" in page.content[0]["text"]
    assert "世界" in page.content[1]["text"]
    assert "項目" in page.content[2]["items"][0]


def test_roundtrip_uncompressed(tmp_path: Path) -> None:
    """Test roundtrip with uncompressed file."""
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


def test_roundtrip_zstd(tmp_path: Path) -> None:
    """Test roundtrip with zstd compression."""
    gen = generator.SCPGenerator("test", "blog")
    gen.add_page(
        url="https://example.com/",
        title="Home",
        description="Homepage",
        modified="2025-01-15T10:00:00Z",
        language="en",
        content=[{"type": "text", "text": "Welcome"}],
    )

    file_path = tmp_path / "test.scp.zst"
    gen.save(file_path, compress="zstd")

    scp_parser = parser.SCPParser()
    metadata, pages = scp_parser.parse_file(file_path)

    assert len(pages) == 1
