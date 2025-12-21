"""Benchmark HTML vs SCP file sizes and performance.

This tool compares the size and parse time of HTML files versus SCP collections
to validate the bandwidth savings and performance claims of the SCP protocol.
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

from lxml import html

sys.path.insert(0, str(Path(__file__).parent.parent))

from scp import compression, parser


def get_file_size(path: Path) -> int:
    """Get file size in bytes."""
    return path.stat().st_size


def compress_html(html_path: Path) -> int:
    """Compress HTML file with gzip and return compressed size.

    Args:
        html_path: Path to HTML file

    Returns:
        Compressed size in bytes
    """
    with open(html_path, "rb") as f:
        html_data = f.read()

    compressed = compression.compress_gzip(html_data, level=6)
    return len(compressed)


def parse_html_timed(html_path: Path) -> float:
    """Parse HTML file and measure time.

    Args:
        html_path: Path to HTML file

    Returns:
        Parse time in seconds
    """
    start = time.perf_counter()

    with open(html_path, "rb") as f:
        tree = html.parse(f)
        root = tree.getroot()

        # Simulate actual parsing work
        _ = root.find(".//title")
        _ = list(root.iter("p"))
        _ = list(root.iter("h1"))
        _ = list(root.iter("h2"))

    return time.perf_counter() - start


def parse_scp_timed(scp_path: Path) -> tuple[float, int]:
    """Parse SCP file and measure time.

    Args:
        scp_path: Path to SCP file

    Returns:
        Tuple of (parse_time, page_count)
    """
    start = time.perf_counter()

    scp_parser = parser.SCPParser()
    metadata, pages = scp_parser.parse_file(scp_path)

    parse_time = time.perf_counter() - start
    return parse_time, len(pages)


def benchmark_files(html_files: list[Path], scp_file: Path) -> dict:
    """Benchmark HTML files versus SCP collection.

    Args:
        html_files: List of HTML file paths
        scp_file: Path to SCP collection file

    Returns:
        Dictionary with benchmark results
    """
    results = {
        "html": {
            "files": len(html_files),
            "raw_size": 0,
            "compressed_size": 0,
            "parse_time": 0.0,
        },
        "scp": {
            "files": 1,
            "raw_size": 0,
            "compressed_size": 0,
            "parse_time": 0.0,
            "pages": 0,
        },
    }

    # Benchmark HTML files
    print("Benchmarking HTML files...")
    for html_file in html_files:
        if not html_file.exists():
            print(f"Warning: {html_file} not found, skipping")
            continue

        print(f"  {html_file.name}...")

        # Size measurements
        raw_size = get_file_size(html_file)
        compressed_size = compress_html(html_file)

        results["html"]["raw_size"] += raw_size
        results["html"]["compressed_size"] += compressed_size

        # Parse time
        parse_time = parse_html_timed(html_file)
        results["html"]["parse_time"] += parse_time

    # Benchmark SCP file
    print("\nBenchmarking SCP file...")
    print(f"  {scp_file.name}...")

    if not scp_file.exists():
        print(f"Error: SCP file not found: {scp_file}")
        sys.exit(1)

    # Size measurements
    compressed_size = get_file_size(scp_file)
    results["scp"]["compressed_size"] = compressed_size

    # Decompress to get raw size
    with open(scp_file, "rb") as f:
        if scp_file.suffix == ".gz":
            decompressed = compression.decompress_gzip(f.read())
        elif scp_file.suffix == ".zst":
            decompressed = compression.decompress_zstd(f.read())
        else:
            decompressed = f.read()

    results["scp"]["raw_size"] = len(decompressed)

    # Parse time and page count
    parse_time, page_count = parse_scp_timed(scp_file)
    results["scp"]["parse_time"] = parse_time
    results["scp"]["pages"] = page_count

    return results


def print_benchmark_results(results: dict) -> None:
    """Print formatted benchmark results.

    Args:
        results: Benchmark results dictionary
    """
    html = results["html"]
    scp = results["scp"]

    # Calculate savings
    raw_savings = ((html["raw_size"] - scp["raw_size"]) / html["raw_size"] * 100
                   if html["raw_size"] > 0 else 0)
    compressed_savings = ((html["compressed_size"] - scp["compressed_size"]) /
                          html["compressed_size"] * 100
                          if html["compressed_size"] > 0 else 0)
    parse_speedup = (html["parse_time"] / scp["parse_time"]
                     if scp["parse_time"] > 0 else 0)
    file_reduction = ((html["files"] - scp["files"]) / html["files"] * 100
                      if html["files"] > 0 else 0)

    print("\n" + "=" * 80)
    print("BENCHMARK RESULTS")
    print("=" * 80)
    print()

    # File counts
    print(f"{'Metric':<30} {'HTML':<20} {'SCP':<20} {'Savings':<10}")
    print("-" * 80)
    print(f"{'Number of files':<30} {html['files']:<20} {scp['files']:<20} {file_reduction:>8.1f}%")
    print()

    # Size comparison
    print(
        f"{'Size (raw)':<30} {html['raw_size']:>15,} B  "
        f"{scp['raw_size']:>15,} B  {raw_savings:>8.1f}%"
    )
    print(
        f"{'Size (raw KB)':<30} {html['raw_size']/1024:>15.1f} KB "
        f"{scp['raw_size']/1024:>15.1f} KB"
    )
    print()
    print(
        f"{'Size (compressed)':<30} {html['compressed_size']:>15,} B  "
        f"{scp['compressed_size']:>15,} B  {compressed_savings:>8.1f}%"
    )
    print(
        f"{'Size (compressed KB)':<30} {html['compressed_size']/1024:>15.1f} KB "
        f"{scp['compressed_size']/1024:>15.1f} KB"
    )
    print()

    # Parse time comparison
    print(
        f"{'Parse time':<30} {html['parse_time']:>15.4f} s  "
        f"{scp['parse_time']:>15.4f} s  {parse_speedup:>7.1f}x faster"
    )
    print()

    # Additional metrics
    print(f"{'Pages in SCP':<30} {scp['pages']}")
    print(f"{'Compression ratio (SCP)':<30} {scp['raw_size']/scp['compressed_size']:>15.2f}:1")
    print()

    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"✓ Bandwidth savings (compressed):  {compressed_savings:>6.1f}%")
    print(f"✓ File reduction:                   {file_reduction:>6.1f}%")
    print(f"✓ Parse speed improvement:          {parse_speedup:>6.1f}x")
    print("=" * 80)


def main() -> None:
    """CLI entry point."""
    if len(sys.argv) < 3:
        print("SCP Benchmark Tool")
        print("=" * 80)
        print("Compares HTML files versus SCP collections to measure bandwidth savings")
        print("and performance improvements.")
        print("\nUsage:")
        print("  python scp_benchmark.py <scp_file> <html_file1> [html_file2] ...")
        print("\nArguments:")
        print("  scp_file       SCP collection file (.scp.gz or .scp.zst)")
        print("  html_files     One or more HTML files to compare against")
        print("\nExample:")
        print("  python scp_benchmark.py wikipedia.scp.gz /tmp/web_crawler.html /tmp/cdn.html")
        print("\nNote:")
        print("  The HTML files should be the same pages that were converted to the SCP file.")
        print("  This ensures a fair comparison.")
        print("=" * 80)
        sys.exit(1)

    scp_file = Path(sys.argv[1])
    html_files = [Path(f) for f in sys.argv[2:]]

    # Validate inputs
    if not scp_file.exists():
        print(f"Error: SCP file not found: {scp_file}")
        sys.exit(1)

    for html_file in html_files:
        if not html_file.exists():
            print(f"Error: HTML file not found: {html_file}")
            sys.exit(1)

    # Run benchmark
    print("Starting benchmark...")
    print(f"SCP file:    {scp_file}")
    print(f"HTML files:  {len(html_files)}")
    print()

    results = benchmark_files(html_files, scp_file)
    print_benchmark_results(results)


if __name__ == "__main__":
    main()
