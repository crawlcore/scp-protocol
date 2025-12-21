"""Tests for checksum module."""

from __future__ import annotations

import pytest

from scp import checksum
from scp.exceptions import ChecksumError


def test_calculate_checksum() -> None:
    """Test checksum calculation."""
    data = b"Hello, World!"
    result = checksum.calculate_checksum(data)

    assert result.startswith("sha256:")
    assert len(result) == 71  # "sha256:" (7) + 64 hex chars


def test_calculate_checksum_deterministic() -> None:
    """Test checksum is deterministic."""
    data = b"test data"
    checksum1 = checksum.calculate_checksum(data)
    checksum2 = checksum.calculate_checksum(data)

    assert checksum1 == checksum2


def test_validate_checksum_success() -> None:
    """Test successful checksum validation."""
    data = b"Hello, World!"
    expected = checksum.calculate_checksum(data)

    assert checksum.validate_checksum(data, expected) is True


def test_validate_checksum_mismatch() -> None:
    """Test checksum mismatch detection."""
    data = b"Hello, World!"
    wrong_checksum = "sha256:" + "0" * 64

    with pytest.raises(ChecksumError, match="Checksum mismatch"):
        checksum.validate_checksum(data, wrong_checksum)


def test_validate_checksum_invalid_format() -> None:
    """Test invalid checksum format detection."""
    data = b"test"

    with pytest.raises(ChecksumError, match="Invalid checksum format"):
        checksum.validate_checksum(data, "invalid")

    with pytest.raises(ChecksumError, match="Invalid checksum format"):
        checksum.validate_checksum(data, "sha256:short")


def test_parse_checksum_valid() -> None:
    """Test parsing valid checksum."""
    valid = "sha256:" + "a" * 64
    result = checksum.parse_checksum(valid)

    assert result == valid.lower()


def test_parse_checksum_uppercase() -> None:
    """Test parsing uppercase checksum."""
    uppercase = "sha256:" + "A" * 64
    result = checksum.parse_checksum(uppercase)

    assert result == uppercase.lower()


def test_parse_checksum_invalid() -> None:
    """Test parsing invalid checksum."""
    with pytest.raises(ChecksumError):
        checksum.parse_checksum("invalid")
