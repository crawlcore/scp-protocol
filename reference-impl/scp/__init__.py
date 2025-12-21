"""Site Content Protocol (SCP) Python reference implementation."""

__version__ = "0.1.0"

from scp.exceptions import (
    ChecksumError,
    CompressionError,
    DecompressionError,
    SCPError,
    SizeLimitError,
    ValidationError,
)
from scp.generator import SCPGenerator, generate_collection
from scp.parser import SCPParser, parse_collection

__all__ = [
    "SCPParser",
    "parse_collection",
    "SCPGenerator",
    "generate_collection",
    "SCPError",
    "CompressionError",
    "DecompressionError",
    "ValidationError",
    "ChecksumError",
    "SizeLimitError",
]
