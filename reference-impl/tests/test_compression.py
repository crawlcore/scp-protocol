"""Tests for compression module."""

from __future__ import annotations

import pytest

from scp import compression
from scp.exceptions import CompressionBombError, DecompressionError


def test_compress_decompress_gzip() -> None:
    """Test gzip compression roundtrip."""
    data = b"Hello, World!" * 1000
    compressed = compression.compress_gzip(data)
    assert len(compressed) < len(data)
    decompressed = compression.decompress_gzip(compressed)
    assert decompressed == data


def test_compress_decompress_zstd() -> None:
    """Test zstd compression roundtrip."""
    data = b"Hello, World!" * 1000
    compressed = compression.compress_zstd(data)
    assert len(compressed) < len(data)
    decompressed = compression.decompress_zstd(compressed)
    assert decompressed == data


def test_detect_compression_gzip() -> None:
    """Test gzip detection."""
    data = b"test data"
    compressed = compression.compress_gzip(data)
    assert compression.detect_compression(compressed) == "gzip"


def test_detect_compression_zstd() -> None:
    """Test zstd detection."""
    data = b"test data"
    compressed = compression.compress_zstd(data)
    assert compression.detect_compression(compressed) == "zstd"


def test_detect_compression_none() -> None:
    """Test uncompressed data detection."""
    data = b"test data"
    assert compression.detect_compression(data) == "none"


def test_compression_bomb_protection_gzip() -> None:
    """Test compression bomb protection for gzip."""
    # Create highly compressible data that would exceed ratio limit
    data = b"A" * (200 * 1024 * 1024)  # 200 MB of 'A's
    compressed = compression.compress_gzip(data)

    # Should raise compression bomb error
    with pytest.raises(CompressionBombError):
        compression.decompress_gzip(compressed)


def test_compression_bomb_protection_zstd() -> None:
    """Test compression bomb protection for zstd."""
    # Create highly compressible data that would exceed ratio limit
    data = b"A" * (200 * 1024 * 1024)  # 200 MB of 'A's
    compressed = compression.compress_zstd(data)

    # Should raise compression bomb error
    with pytest.raises(CompressionBombError):
        compression.decompress_zstd(compressed)


def test_max_decompressed_size() -> None:
    """Test maximum decompressed size enforcement."""
    small_limit = 1024  # 1 KB
    data = b"A" * 2048  # 2 KB
    compressed = compression.compress_gzip(data)

    with pytest.raises(CompressionBombError):
        compression.decompress_gzip(compressed, max_size=small_limit)


def test_invalid_gzip_data() -> None:
    """Test handling of invalid gzip data."""
    with pytest.raises(DecompressionError):
        compression.decompress_gzip(b"not gzip data")


def test_invalid_zstd_data() -> None:
    """Test handling of invalid zstd data."""
    with pytest.raises(DecompressionError):
        compression.decompress_zstd(b"not zstd data")


def test_compress_empty_data() -> None:
    """Test compressing empty data."""
    data = b""
    compressed = compression.compress_gzip(data)
    decompressed = compression.decompress_gzip(compressed)
    assert decompressed == data
