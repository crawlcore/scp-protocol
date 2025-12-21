"""Checksum calculation and validation for SCP collections."""

from __future__ import annotations

import hashlib
import re

from scp.exceptions import ChecksumError

CHECKSUM_PATTERN = re.compile(r"^sha256:[a-fA-F0-9]{64}$")


def calculate_checksum(data: bytes) -> str:
    """Calculate SHA-256 checksum of data.

    Args:
        data: Data to checksum

    Returns:
        Checksum string in format "sha256:hexdigest"
    """
    hash_obj = hashlib.sha256(data)
    return f"sha256:{hash_obj.hexdigest()}"


def validate_checksum(data: bytes, checksum: str) -> bool:
    """Validate data against SHA-256 checksum.

    Args:
        data: Data to validate
        checksum: Expected checksum in format "sha256:hexdigest"

    Returns:
        True if checksum matches

    Raises:
        ChecksumError: If checksum format is invalid or doesn't match
    """
    if not CHECKSUM_PATTERN.match(checksum):
        raise ChecksumError(f"Invalid checksum format: {checksum}")

    calculated = calculate_checksum(data)
    if calculated != checksum.lower():
        raise ChecksumError(
            f"Checksum mismatch: expected {checksum.lower()}, got {calculated}"
        )

    return True


def parse_checksum(checksum: str) -> str:
    """Parse and validate checksum format.

    Args:
        checksum: Checksum string

    Returns:
        Normalized checksum (lowercase)

    Raises:
        ChecksumError: If format is invalid
    """
    if not CHECKSUM_PATTERN.match(checksum):
        raise ChecksumError(f"Invalid checksum format: {checksum}")

    return checksum.lower()
