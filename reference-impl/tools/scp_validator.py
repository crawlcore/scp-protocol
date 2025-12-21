"""SCP collection validator tool.

Validates SCP collection files against the specification.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from scp.parser import SCPParser


def main() -> int:
    """Main entry point for scp-validate command."""
    parser = argparse.ArgumentParser(
        description="Validate SCP collection files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  scp-validate collection.scp.gz
  scp-validate --strict snapshot.scp.gz
  scp-validate --no-validate delta.scp.gz
        """,
    )

    parser.add_argument("file", type=Path, help="SCP collection file to validate")

    parser.add_argument(
        "--strict",
        action="store_true",
        help="Strict mode: fail on non-fatal errors like unknown content blocks",
    )

    parser.add_argument(
        "--no-validate",
        action="store_true",
        help="Skip JSON schema validation (only check format)",
    )

    parser.add_argument(
        "-q", "--quiet", action="store_true", help="Suppress output, only return exit code"
    )

    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Verbose output with detailed information"
    )

    args = parser.parse_args()

    # Check file exists
    if not args.file.exists():
        print(f"Error: File not found: {args.file}", file=sys.stderr)
        return 1

    # Parse file
    scp_parser = SCPParser(validate=not args.no_validate, strict=args.strict)

    try:
        metadata, pages = scp_parser.parse_file(args.file)

        if not args.quiet:
            print(f"✓ Valid SCP collection: {args.file}")
            print(f"  Collection ID: {metadata.id}")
            print(f"  Type: {metadata.type}")
            print(f"  Section: {metadata.section}")
            print(f"  Version: {metadata.version}")
            print(f"  Generated: {metadata.generated}")
            if metadata.since:
                print(f"  Since: {metadata.since}")
            if metadata.checksum:
                print("  Checksum: ✓ Verified")
            print(f"  Pages: {len(pages)}")

            if args.verbose:
                print("\nPages:")
                for i, page in enumerate(pages[:10], 1):  # Show first 10
                    print(f"  {i}. {page.url}")
                    print(f"     Title: {page.title}")
                    print(f"     Content blocks: {len(page.content)}")
                if len(pages) > 10:
                    print(f"  ... and {len(pages) - 10} more pages")

        # Show non-fatal errors
        if scp_parser.errors:
            print(f"\n⚠ {len(scp_parser.errors)} warning(s):", file=sys.stderr)
            for error in scp_parser.errors:
                print(f"  - {error}", file=sys.stderr)

        return 0

    except Exception as e:
        if not args.quiet:
            print(f"✗ Validation failed: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
