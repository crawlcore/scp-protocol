"""Exception classes for SCP protocol."""


class SCPError(Exception):
    """Base exception for all SCP-related errors."""

    pass


class CompressionError(SCPError):
    """Raised when compression fails."""

    pass


class DecompressionError(SCPError):
    """Raised when decompression fails."""

    pass


class ValidationError(SCPError):
    """Raised when validation fails."""

    pass


class ChecksumError(SCPError):
    """Raised when checksum verification fails."""

    pass


class SizeLimitError(SCPError):
    """Raised when size limits are exceeded."""

    pass


class CompressionBombError(SizeLimitError):
    """Raised when decompression ratio exceeds safe limits (100:1)."""

    pass
