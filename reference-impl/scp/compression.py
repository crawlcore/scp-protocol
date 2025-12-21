"""Compression and decompression utilities for SCP collections.

Supports gzip and zstd compression formats with safety limits to prevent
compression bomb attacks.
"""

from __future__ import annotations

import gzip
import io

try:
    import zstandard as zstd

    ZSTD_AVAILABLE = True
except ImportError:
    ZSTD_AVAILABLE = False

from scp.exceptions import CompressionBombError, CompressionError, DecompressionError

# Security limits
MAX_COMPRESSED_SIZE = 50 * 1024 * 1024 * 1024  # 50 GB
MAX_DECOMPRESSED_SIZE = 500 * 1024 * 1024 * 1024  # 500 GB
MAX_COMPRESSION_RATIO = 100  # 100:1 ratio
MIN_SIZE_FOR_RATIO_CHECK = 1 * 1024 * 1024  # Only check ratio after 1 MB decompressed


def compress_gzip(data: bytes, level: int = 6) -> bytes:
    """Compress data using gzip.

    Args:
        data: Uncompressed data
        level: Compression level (1-9), default 6

    Returns:
        Compressed data

    Raises:
        CompressionError: If compression fails
    """
    if len(data) > MAX_DECOMPRESSED_SIZE:
        raise CompressionError(f"Data size {len(data)} exceeds maximum {MAX_DECOMPRESSED_SIZE}")

    try:
        return gzip.compress(data, compresslevel=level)
    except Exception as e:
        raise CompressionError(f"gzip compression failed: {e}") from e


def compress_zstd(data: bytes, level: int = 9) -> bytes:
    """Compress data using zstd.

    Args:
        data: Uncompressed data
        level: Compression level (1-22), default 9

    Returns:
        Compressed data

    Raises:
        CompressionError: If compression fails or zstd not available
    """
    if not ZSTD_AVAILABLE:
        raise CompressionError("zstandard library not installed")

    if len(data) > MAX_DECOMPRESSED_SIZE:
        raise CompressionError(f"Data size {len(data)} exceeds maximum {MAX_DECOMPRESSED_SIZE}")

    try:
        compressor = zstd.ZstdCompressor(level=level)
        return compressor.compress(data)
    except Exception as e:
        raise CompressionError(f"zstd compression failed: {e}") from e


def decompress_gzip(data: bytes, max_size: int | None = None) -> bytes:
    """Decompress gzip data with safety checks.

    Args:
        data: Compressed data
        max_size: Maximum decompressed size (default: MAX_DECOMPRESSED_SIZE)

    Returns:
        Decompressed data

    Raises:
        DecompressionError: If decompression fails
        CompressionBombError: If decompression ratio exceeds limits
    """
    if max_size is None:
        max_size = MAX_DECOMPRESSED_SIZE

    compressed_size = len(data)
    if compressed_size > MAX_COMPRESSED_SIZE:
        raise DecompressionError(
            f"Compressed size {compressed_size} exceeds maximum {MAX_COMPRESSED_SIZE}"
        )

    try:
        # Decompress with size checking
        decompressor = gzip.GzipFile(fileobj=io.BytesIO(data))
        output = io.BytesIO()
        chunk_size = 8192
        total_decompressed = 0

        while True:
            chunk = decompressor.read(chunk_size)
            if not chunk:
                break

            total_decompressed += len(chunk)

            # Check decompression ratio (only after minimum threshold to avoid false positives)
            if (
                total_decompressed >= MIN_SIZE_FOR_RATIO_CHECK
                and compressed_size > 0
                and total_decompressed / compressed_size > MAX_COMPRESSION_RATIO
            ):
                raise CompressionBombError(
                    f"Decompression ratio exceeds {MAX_COMPRESSION_RATIO}:1"
                )

            # Check absolute size
            if total_decompressed > max_size:
                raise CompressionBombError(f"Decompressed size exceeds maximum {max_size}")

            output.write(chunk)

        return output.getvalue()
    except CompressionBombError:
        raise
    except Exception as e:
        raise DecompressionError(f"gzip decompression failed: {e}") from e


def decompress_zstd(data: bytes, max_size: int | None = None) -> bytes:
    """Decompress zstd data with safety checks.

    Args:
        data: Compressed data
        max_size: Maximum decompressed size (default: MAX_DECOMPRESSED_SIZE)

    Returns:
        Decompressed data

    Raises:
        DecompressionError: If decompression fails or zstd not available
        CompressionBombError: If decompression ratio exceeds limits
    """
    if not ZSTD_AVAILABLE:
        raise DecompressionError("zstandard library not installed")

    if max_size is None:
        max_size = MAX_DECOMPRESSED_SIZE

    compressed_size = len(data)
    if compressed_size > MAX_COMPRESSED_SIZE:
        raise DecompressionError(
            f"Compressed size {compressed_size} exceeds maximum {MAX_COMPRESSED_SIZE}"
        )

    try:
        decompressor = zstd.ZstdDecompressor()
        output = io.BytesIO()
        chunk_size = 8192
        total_decompressed = 0

        with decompressor.stream_reader(io.BytesIO(data)) as reader:
            while True:
                chunk = reader.read(chunk_size)
                if not chunk:
                    break

                total_decompressed += len(chunk)

                # Check decompression ratio (only after minimum threshold to avoid false positives)
                if (
                    total_decompressed >= MIN_SIZE_FOR_RATIO_CHECK
                    and compressed_size > 0
                    and total_decompressed / compressed_size > MAX_COMPRESSION_RATIO
                ):
                    raise CompressionBombError(
                        f"Decompression ratio exceeds {MAX_COMPRESSION_RATIO}:1"
                    )

                # Check absolute size
                if total_decompressed > max_size:
                    raise CompressionBombError(f"Decompressed size exceeds maximum {max_size}")

                output.write(chunk)

        return output.getvalue()
    except CompressionBombError:
        raise
    except Exception as e:
        raise DecompressionError(f"zstd decompression failed: {e}") from e


def detect_compression(data: bytes) -> str:
    """Detect compression format from file header.

    Args:
        data: First few bytes of file

    Returns:
        "gzip", "zstd", or "none"
    """
    if len(data) < 4:
        return "none"

    # gzip magic number: 1f 8b
    if data[0:2] == b"\x1f\x8b":
        return "gzip"

    # zstd magic number: 28 b5 2f fd
    if data[0:4] == b"\x28\xb5\x2f\xfd":
        return "zstd"

    return "none"
