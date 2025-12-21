## Overview

The SCP Python reference implementation includes three command-line tools for working with SCP collections.

| Tool              | Purpose                                                   |
|-------------------|-----------------------------------------------------------|
| **scp-validate**  | Validate SCP collections against JSON schemas             |
| **scp-inspect**   | Inspect and view SCP collections in human-readable format |
| **scp-benchmark** | Compare HTML vs SCP file sizes and parse performance      |

## scp-validate

Validate SCP collection files against the specification.

### Basic Usage

```bash
# Validate a collection
scp-validate collection.scp.gz

# Validate multiple collections
scp-validate snapshot.scp.gz delta.scp.gz
```

### Options

```bash
# Verbose output (show detailed validation info)
scp-validate -v collection.scp.gz
scp-validate --verbose collection.scp.gz

# Strict mode (fail on warnings, not just errors)
scp-validate --strict collection.scp.gz

# Quiet mode (only show errors)
scp-validate -q collection.scp.gz
scp-validate --quiet collection.scp.gz
```

### What Gets Validated

- **Collection metadata**: Required fields, version, type, timestamps
- **Page objects**: Required fields, URL format, date formats
- **Content blocks**: Block types, required fields per type
- **Checksums**: SHA-256 validation if present
- **Compression**: Decompression ratio (max 100:1)
- **Size limits**: 50 GB compressed max, 500 GB decompressed max
- **JSON format**: Valid JSON Lines format

## scp-inspect

Inspect SCP collections and display contents in human-readable format.

### Basic Usage

```bash
# Show collection metadata only
scp-inspect collection.scp.gz

# Show collection metadata and all pages
scp-inspect --pages collection.scp.gz

# Show everything (metadata, pages, content blocks)
scp-inspect --content collection.scp.gz
```

### Options

```bash
# Limit number of pages shown
scp-inspect --pages --limit 10 collection.scp.gz

# JSON output (machine-readable)
scp-inspect --json collection.scp.gz > output.json

# Show specific page by URL
scp-inspect --url "https://example.com/page" collection.scp.gz

# Show only pages modified after date
scp-inspect --since "2025-01-15T00:00:00Z" collection.scp.gz
```


### Use Cases

**Check collection contents**:
```bash
scp-inspect collection.scp.gz
```

**Find specific page**:
```bash
scp-inspect --url "https://example.com/blog/my-post" collection.scp.gz
```

**Export to JSON**:
```bash
scp-inspect --json collection.scp.gz > data.json
```

**View recent changes (delta)**:
```bash
scp-inspect --pages --since "2025-01-15T00:00:00Z" collection.scp.gz
```

**Debug content blocks**:
```bash
scp-inspect --content --limit 1 collection.scp.gz
```

## scp-benchmark

Compare HTML files against SCP collections to measure bandwidth savings and performance improvements.

### Basic Usage

```bash
# Compare SCP collection with original HTML files
scp-benchmark collection.scp.gz page1.html page2.html page3.html

# Works with any number of HTML files
scp-benchmark collection.scp.gz *.html
```

### Arguments

```
scp-benchmark <scp_file> <html_file1> [html_file2] ...

Arguments:
  scp_file       SCP collection file (.scp.gz or .scp.zst)
  html_files     One or more HTML files to compare against

Note:
  The HTML files should be the same pages that were converted to the SCP file
  to ensure a fair comparison.
```


### Metrics Explained

- **Number of files**: HTML requires separate requests per page; SCP bundles all pages in one file
- **Size (raw)**: Uncompressed size comparison
- **Size (compressed)**: Compressed size comparison (gzip level 6 for both)
- **Parse time**: Time to parse and extract content from HTML vs SCP
- **Compression ratio**: How much the SCP file compresses

### Use Cases

**Validate bandwidth savings claim**:
```bash
scp-benchmark blog-snapshot.scp.gz /path/to/html/*.html
```

**Compare different sections**:
```bash
scp-benchmark docs.scp.gz docs/*.html
scp-benchmark blog.scp.gz blog/*.html
```

**Benchmark your website**:
```bash
# Generate both SCP collection and HTML from your backend data
python generate_collection.py  # Creates collection.scp.gz
python generate_html.py         # Creates HTML files for users

# Compare the two formats
scp-benchmark collection.scp.gz output/page1.html output/page2.html
```

## Installation

All three tools are included when you install the SCP Python package:

```bash
# Clone the repository
git clone https://github.com/crawlcore/scp-protocol.git
cd scp-protocol/reference-impl

# Install the package
pip install -e .
```
