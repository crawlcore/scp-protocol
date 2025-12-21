# SCP Protocol - Python Reference Implementation

Python reference implementation for the **Site Content Protocol (SCP)** v0.1.

## Quick Start

```bash
# Install
pip install scp-protocol

# Parse a collection
from scp import parse_collection
metadata, pages = parse_collection("collection.scp.gz")

# Generate a collection
from scp.generator import SCPGenerator
gen = SCPGenerator("my-snapshot", "blog")
gen.add_page(...)
gen.save("output.scp.gz")
```

## Documentation

**Full documentation:** https://scp-protocol.org/reference-impl/

- [Installation](https://scp-protocol.org/reference-impl/getting-started/installation/)
- [Quick Start Guide](https://scp-protocol.org/reference-impl/getting-started/quickstart/)
- [API Reference](https://scp-protocol.org/reference-impl/api/parser/)
- [CLI Tools](https://scp-protocol.org/reference-impl/guide/cli-tools/)

## Features

- Full SCP 0.1 specification support
- Compression: gzip and zstd with safety limits
- Validation: JSON schema validation
- Security: Compression bomb protection, size limits, checksum verification
- Performance: orjson for fast JSON, lxml for XML
- CLI Tools: Validator, inspector, benchmark tool

## CLI Tools

The reference implementation includes three command-line tools:

- **scp-validate** - Validate SCP files against JSON schemas
- **scp-inspect** - Inspect and view SCP collections in human-readable format
- **scp-benchmark** - Compare HTML vs SCP file sizes and parse performance

### Usage Examples

```bash
# Validate a collection
scp-validate collection.scp.gz

# Inspect collection contents
scp-inspect collection.scp.gz --limit 5

# Benchmark HTML vs SCP (requires original HTML files)
scp-benchmark collection.scp.gz original1.html original2.html
```

## Implementation Guide

Websites should generate SCP collections directly from their data sources using the generator API:

```python
from scp.generator import SCPGenerator

# Create generator
gen = SCPGenerator("blog-snapshot-2025-01-15", "blog", "snapshot")

# Add pages from your data source
for post in database.query("SELECT * FROM posts"):
    gen.add_page(
        url=post.url,
        title=post.title,
        description=post.excerpt,
        author=post.author,
        modified=post.updated_at,
        language="en",
        content=convert_to_content_blocks(post.content)
    )

# Save collection
gen.save("blog-snapshot.scp.gz", compress="gzip")
```


## Development

```bash
# Install with dev dependencies
pip install -e ".[dev]"

# Run tests
pytest
```
