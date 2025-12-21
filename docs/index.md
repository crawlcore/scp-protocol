# Site Content Protocol (SCP)

## What is SCP?

The Site Content Protocol (SCP) is a collection-based format for efficiently serving web content to crawlers while users continue accessing regular HTML pages.

## Problem

Web crawlers (search engines, AI bots, aggregators) consume massive bandwidth and server resources by parsing web-pages designed for human viewing.
With the explosion of AI crawlers, this traffic has become a significant cost for websites and strain on internet infrastructure.

Sources:

- [Cloudflare Year in Review 2025](https://radar.cloudflare.com/year-in-review/2025)
- [FOSS Infrastructure Under Attack by AI Companies](https://thelibre.news/foss-infrastructure-is-under-attack-by-ai-companies/)
- [Web Scraping Market Report 2025](https://scrapeops.io/web-scraping-playbook/web-scraping-market-report-2025/)

## Solution

Websites pre-generate compressed collections and host them on CDN or Cloud Object Storage:

1. Website generates `blog-snapshot-2025-01-15.scp.gz` (5,247 pages → 52 MB)
2. Uploads to CDN or Cloud Object Storage
3. Declares availability of content collections in sitemap.xml
4. Crawler downloads entire collection in one request
5. Later: crawler downloads delta `blog-delta-2025-01-16.scp.gz` (47 pages → 480 KB)

### Expected Impact

- 50-60% bandwidth reduction for initial snapshots
- 90-95% bandwidth reduction with delta updates
- Faster parsing than HTML/CSS/JS
- 90% fewer requests (one download fetches entire sections)
- Zero impact on user experience

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

1. Community feedback (3 months)
   - Post to Hacker News, Reddit, tech blogs
   - Iterate on spec based on feedback
2. Creation of IETF Internet-Draft (2 months)

**Future**:

- Bot verification using [Web Bot Auth](https://developers.cloudflare.com/bots/reference/bot-verification/web-bot-auth/)
- Pay-per-crawl model similar to [Cloudflare's Pay Per Crawl](https://blog.cloudflare.com/introducing-pay-per-crawl/)


## License

The SCP specification and reference implementation are released under the **CC0 1.0 Universal** license (Public Domain).
