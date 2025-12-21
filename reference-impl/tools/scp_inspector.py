"""SCP collection inspector tool.

Displays human-readable information about SCP collection files.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import orjson

from scp.parser import SCPParser


def format_size(size_bytes: int) -> str:
    """Format byte size as human-readable string."""
    size = float(size_bytes)
    for unit in ["B", "KB", "MB", "GB"]:
        if size < 1024:
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} TB"


def main() -> int:
    """Main entry point for scp-inspect command."""
    parser = argparse.ArgumentParser(
        description="Inspect SCP collection files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  scp-inspect collection.scp.gz
  scp-inspect --pages snapshot.scp.gz
  scp-inspect --content delta.scp.gz
  scp-inspect --json collection.scp.gz > output.json
        """,
    )

    parser.add_argument("file", type=Path, help="SCP collection file to inspect")

    parser.add_argument("--pages", action="store_true", help="Show detailed page information")

    parser.add_argument(
        "--content", action="store_true", help="Show content blocks (implies --pages)"
    )

    parser.add_argument("--json", action="store_true", help="Output as JSON")

    parser.add_argument(
        "--limit", type=int, default=None, help="Limit number of pages shown (default: all)"
    )

    args = parser.parse_args()

    # Check file exists
    if not args.file.exists():
        print(f"Error: File not found: {args.file}", file=sys.stderr)
        return 1

    # Parse file
    scp_parser = SCPParser(validate=False)  # Don't validate for inspection

    try:
        metadata, pages = scp_parser.parse_file(args.file)

        if args.json:
            # JSON output
            output = {
                "file": str(args.file),
                "size": args.file.stat().st_size,
                "metadata": metadata.raw,
                "page_count": len(pages),
            }

            if args.pages or args.content:
                output["pages"] = [page.raw for page in pages[: args.limit]]

            # orjson returns bytes, need to decode
            json_bytes = orjson.dumps(
                output, option=orjson.OPT_INDENT_2 | orjson.OPT_NON_STR_KEYS
            )
            print(json_bytes.decode("utf-8"))

        else:
            # Human-readable output
            file_size = args.file.stat().st_size

            print(f"SCP Collection: {args.file}")
            print(f"File size: {format_size(file_size)}")
            print()

            print("Collection Metadata:")
            print(f"  ID: {metadata.id}")
            print(f"  Type: {metadata.type}")
            print(f"  Section: {metadata.section}")
            print(f"  Version: {metadata.version}")
            print(f"  Generated: {metadata.generated}")
            if metadata.since:
                print(f"  Since: {metadata.since}")
            if metadata.checksum:
                print(f"  Checksum: {metadata.checksum}")
            print()

            print(f"Pages: {len(pages)}")

            if args.pages or args.content:
                print()
                limit = args.limit if args.limit else len(pages)
                for i, page in enumerate(pages[:limit], 1):
                    print(f"\nPage {i}:")
                    print(f"  URL: {page.url}")
                    print(f"  Title: {page.title}")
                    print(f"  Description: {page.description}")
                    if page.author:
                        print(f"  Author: {page.author}")
                    if page.published:
                        print(f"  Published: {page.published}")
                    print(f"  Modified: {page.modified}")
                    print(f"  Language: {page.language}")
                    print(f"  Content blocks: {len(page.content)}")

                    if args.content:
                        print("  Content:")
                        for j, block in enumerate(page.content, 1):
                            block_type = block.get("type", "unknown")
                            print(f"    {j}. {block_type}", end="")

                            if block_type == "heading":
                                print(f" (level {block['level']}): {block['text'][:50]}")
                            elif block_type == "text":
                                text = block["text"][:80]
                                print(f": {text}{'...' if len(block['text']) > 80 else ''}")
                            elif block_type == "link":
                                print(f": {block['text']} → {block['url']}")
                            elif block_type == "image":
                                print(f": {block['alt']} ({block['url']})")
                            elif block_type == "code":
                                lang = block.get("language", "")
                                print(f" ({lang}): {len(block['code'])} chars")
                            elif block_type == "list":
                                list_type = "ordered" if block["ordered"] else "unordered"
                                print(f" ({list_type}): {len(block['items'])} items")
                            elif block_type == "table":
                                rows = len(block["rows"])
                                cols = len(block["rows"][0]) if rows > 0 else 0
                                print(f": {rows}×{cols}")
                            elif block_type == "video":
                                print(f": {block['title']}")
                            elif block_type == "audio":
                                print(f": {block['title']}")
                            else:
                                print()

                if limit < len(pages):
                    print(f"\n... and {len(pages) - limit} more pages")

        return 0

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
