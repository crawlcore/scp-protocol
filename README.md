# Site Content Protocol (SCP)

A collection-based format for serving clean, structured web content to AI training systems and search engines. Websites provide pre-generated JSON collections optimized for machine consumption, while end users continue accessing regular HTML pages.

## The Problem

AI training systems and search engines need massive web content datasets, but current HTML scraping approaches create three critical problems:

1. **Low-quality training data** - Content extracted from HTML is contaminated with navigation menus, advertisements, boilerplate text, and formatting markup, degrading model training quality.
2. **High infrastructure costs** - Processing complete HTML/CSS/JavaScript responses for millions of pages creates substantial bandwidth and computational overhead for both publishers and crawlers.
3. **Legal and ethical uncertainty** - Automated scraping exists in a gray area. Websites lack a clear, voluntary mechanism to contribute high-quality content to AI training while maintaining control over their intellectual property.

## The Solution

SCP provides a voluntary, structured alternative to HTML scraping. Websites generate clean JSON collections from their CMS/database and serve them from CDN or object storage, while crawlers download entire content sections efficiently.

**Expected Impact**:

- **Clean training data**: Structured content without navigation menus, ads, boilerplate, or formatting markup
- **Voluntary contribution**: Clear mechanism for sites to contribute high-quality content to AI training with explicit consent
- **Reduced infrastructure costs**: Lower bandwidth and processing overhead for both publishers and crawlers
- **Efficient updates**: Delta collections deliver only changed pages, minimizing redundant transfers
- **Zero user impact**: End users continue accessing regular HTML pages

## Resources

- **Documentation**: [scp-protocol.org](https://scp-protocol.org) - Getting started, guides, and examples
- **Specification**: [scp_specification.md](scp_specification.md) - Technical specification (v0.1)
- **License**: [CC0 1.0 Universal](LICENSE) - Public Domain

## Contact

Vasiliy Kiryanov

- https://github.com/vasiliyk
- https://x.com/vasiliykiryanov
- https://linkedin.com/in/vasiliykiryanov
