# Site Content Protocol (SCP)

## What is SCP?

The Site Content Protocol (SCP) is a format for serving clean, structured web content to AI training systems and search engines. Websites provide pre-generated JSON collections optimized for machine consumption, while end users continue accessing regular HTML pages.

## Problem

AI training systems and search engines need massive web content datasets, but current HTML scraping approaches create three critical problems:

1. **Low-quality training data** - Content extracted from HTML is contaminated with navigation menus, advertisements, boilerplate text, and formatting markup, degrading model training quality.
2. **High infrastructure costs** - Processing complete HTML/CSS/JavaScript responses for millions of pages creates substantial bandwidth and computational overhead for both publishers and crawlers.
3. **Legal and ethical uncertainty** - Automated scraping exists in a gray area. Websites lack a clear, voluntary mechanism to contribute high-quality content to AI training while maintaining control over their intellectual property.

## Solution

SCP provides a voluntary, structured alternative to HTML scraping:

**For Publishers:**

- Generate clean JSON collections from your CMS/database (not HTML parsing)
- Host compressed files on CDN or object storage
- Declare collection availability in sitemap.xml
- Maintain full control over what content is included

**For Crawlers:**

- Download entire content sections in one request
- Receive structured data optimized for training/indexing
- Use efficient delta updates (only changed pages)
- Respect publisher-provided content boundaries

**Example:**

1. Website generates `blog-snapshot-day15.scp.gz` (5,247 pages → 52 MB)
2. Uploads to CDN or Cloud Object Storage
3. Crawler downloads entire collection in one request
4. Later: crawler downloads delta `blog-delta-day16.scp.gz` (47 pages → 480 KB)

### Expected Impact

- **Clean training data**: Structured content without navigation menus, ads, boilerplate, or formatting markup
- **Voluntary contribution**: Clear mechanism for sites to contribute high-quality content to AI training with explicit consent
- **Reduced infrastructure costs**: Lower bandwidth and processing overhead for both publishers and crawlers
- **Efficient updates**: Delta collections deliver only changed pages, minimizing redundant transfers
- **Zero user impact**: End users continue accessing regular HTML pages

## Documentation

- [Implementation Guide](implementation.md) - Generate collections from your data
- [CLI Tools](cli-tools.md) - Validation and inspection tools
- [Reference Implementation (Python)](https://github.com/crawlcore/scp-protocol/tree/main/reference-impl) - Parser, generator, and CLI tools
- [Full Specification v0.1](https://github.com/crawlcore/scp-protocol/blob/main/scp_specification.md) - Complete technical specification

**Schemas:**

- [collection.json](schemas/collection.json) - JSON Schema for collection metadata
- [page.json](schemas/page.json) - JSON Schema for page objects

## Project Status

**Completed**:

- Specification draft complete (v0.1)
- Reference implementation (Python)

**Next Steps**:

1. Community feedback (1 month)
     - Post to Hacker News, Reddit, tech blogs
     - Iterate on spec based on feedback
2. Update of IETF Internet-Draft (2 weeks)

## License

The SCP specification and reference implementation are released under the **CC0 1.0 Universal** license (Public Domain).
