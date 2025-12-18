# Site Content Protocol (SCP)

A collection-based protocol that reduces waste of bandwidth, processing power, and energy through pre-generated snapshots and deltas.

## The Problem

Web crawlers (search engines, AI bots, aggregators) consume massive bandwidth and server resources by parsing web-pages designed for human viewing.
With the explosion of AI crawlers, this traffic has become a significant cost for websites and strain on internet infrastructure.

Sources:

- https://radar.cloudflare.com/year-in-review/2025
- https://thelibre.news/foss-infrastructure-is-under-attack-by-ai-companies/
- https://scrapeops.io/web-scraping-playbook/web-scraping-market-report-2025/


## The Solution

SCP enables websites to serve pre-generated collections of their content in compressed JSON Lines format.

**Target Goals**:

- 50-60% bandwidth reduction for initial snapshots vs compressed HTML
- 90-95% bandwidth reduction with delta updates (after initial download)
- 90% faster parsing than HTML/CSS/JS processing
- 90% fewer requests - one download fetches entire site sections
- Zero impact on user experience (users continue accessing regular sites)

## How It Works

Websites pre-generate compressed collections and host them on CDN or Cloud Object Storage:

1. Website generates blog-snapshot-2025-01-15.scp.gz (5,247 pages → 52 MB)
2. Uploads to CDN or Cloud Object Storage
3. Declares availability of content collections in sitemap.xml
4. Crawler downloads entire collection in one request
5. Later: crawler downloads delta blog-delta-2025-01-16.scp.gz (47 pages → 480 KB)


## Technical Overview

SCP uses JSON Lines (newline-delimited JSON) format, compressed with gzip or zstd.

### File Structure

- File extension: `.scp.gz` (gzip) or `.scp.zst` (zstd)
- Content-Type: `application/x-ndjson+gzip` or `application/x-ndjson+zstd`
- Format: One JSON object per line

```jsonl
{"collection":{"id":"blog-snapshot-2025-01-15","section":"blog","type":"snapshot","generated":"2025-01-15T00:00:00Z","version":"0.1"}}
{"url":"https://example.com/blog/post-1","title":"First Post","description":"...","modified":"2025-01-15T09:00:00Z","language":"en","content":[...]}
{"url":"https://example.com/blog/post-2","title":"Second Post","description":"...","modified":"2025-01-14T10:00:00Z","language":"en","content":[...]}
```

- Line 1: Collection metadata (snapshot or delta)
- Lines 2+: Individual pages

### Page Structure

Each page is a JSON object with:

```json
{
  "url": "https://example.com/blog/post-title",
  "title": "Page Title",
  "description": "Meta description for SEO",
  "author": "John Doe",
  "published": "2024-01-15T10:30:00Z",
  "modified": "2024-01-20T14:22:00Z",
  "language": "en",
  "content": [
    {"type": "heading", "level": 1, "text": "Main Heading"},
    {"type": "text", "text": "Paragraph content goes here."},
    {"type": "link", "url": "https://example.com", "text": "Link text"},
    {"type": "image", "url": "https://example.com/image.jpg", "alt": "Alt text"},
    {"type": "list", "ordered": false, "items": ["Item 1", "Item 2"]},
    {"type": "code", "language": "python", "code": "print('Hello')"},
    {"type": "table", "rows": [["Cell 1", "Cell 2"], ["Cell 3", "Cell 4"]]}
  ]
}
```

### Content Block Types

- text: Paragraph text
- heading: H1-H6 headings (level 1-6)
- link: Hyperlinks with optional rel attributes
- image: Images with alt text
- list: Ordered or unordered lists
- code: Code blocks with language syntax
- table: Tables (row-major array format)
- quote: Blockquotes with optional citation
- video: Video embeds with sources, captions, transcripts
- audio: Audio content with metadata
- structured: Schema.org structured data (JSON-LD)

## Discovery via Sitemap

Crawlers discover SCP collections through `sitemap.xml`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"
        xmlns:scp="https://scp-protocol.org/schemas/sitemap/1.0">

  <!-- SCP Metadata -->
  <scp:version>0.1</scp:version>
  <scp:compression>zstd,gzip</scp:compression>

  <!-- Available Sections -->
  <scp:section name="blog" updateFreq="daily" pages="~5000"/>
  <scp:section name="docs" updateFreq="weekly" pages="~200"/>

  <!-- Snapshot Collections (full state) -->
  <scp:collection section="blog" type="snapshot"
                  url="https://r2.example.com/blog-snapshot-2025-01-15.scp.gz"
                  generated="2025-01-15T00:00:00Z"
                  expires="2025-01-16T00:00:00Z"
                  pages="5247" size="52000000"/>

  <!-- Delta Collections (incremental changes) -->
  <scp:delta section="blog" period="2025-01-15"
             url="https://r2.example.com/blog-delta-2025-01-15.scp.gz"
             generated="2025-01-15T23:00:00Z"
             expires="2025-01-17T00:00:00Z"
             pages="47" size="480000"
             since="2025-01-14T00:00:00Z"/>
</urlset>
```

## Snapshots and Deltas

### Snapshot Collections

Full section state, regenerated periodically:

- Contains all pages in the section
- Updated daily/weekly based on section updateFreq
- First crawl downloads full snapshot
- Example: `blog-snapshot-2025-01-15.scp.gz` (5,247 pages, 52 MB)

### Delta Collections

Incremental changes only:

- Contains only modified/new pages during the period
- Much smaller than snapshots (typically <1% of snapshot size)
- Subsequent crawls download deltas and merge locally
- Example: `blog-delta-2025-01-15.scp.gz` (47 pages, 480 KB)

### Crawler Workflow

**Initial Crawl**:
1. Parse `sitemap.xml`
2. Download snapshot collection: `blog-snapshot-2025-01-15.scp.gz`
3. Decompress and parse JSON Lines
4. Index all 5,247 pages

**Incremental Updates** (next day):
1. Check `sitemap.xml` for new deltas
2. Download `blog-delta-2025-01-16.scp.gz` (89 pages, 920 KB)
3. Merge delta into local index (update/add pages)

**Timeline Example**:
- Day 1: Download snapshot (5,247 pages, 52 MB)
- Day 2: Download delta (47 pages, 480 KB)
- Day 3: Download delta (89 pages, 920 KB)
- Day 4: Download delta (124 pages, 1.2 MB)

**Total bandwidth**: 54.6 MB vs 208 MB traditional (4 daily full crawls) = **74% savings**

## Project Status

**Current Phase**: Specification draft complete (v0.1)

**Next Steps**:

- Ask community for review of specification draft
- Reference implementation (Python)
- Crawler support implementation for [qCrawl](https://github.com/crawlcore/qcrawl) crawler
- Collection generator tools (CMS and Frameworks plugins)

**After that**:

- Bot verification to ensure only approved crawlers access site content using [Web Bot Auth](https://developers.cloudflare.com/bots/reference/bot-verification/web-bot-auth/)
- Pay for content to support fair crawler-content creator dynamic using model similar to [Pay Per Crawl](https://blog.cloudflare.com/introducing-pay-per-crawl/)

## Getting Involved

- Implementers: Build collection generators and parsers (Python, Go, Rust, JavaScript)
- CMS Plugin Developers: WordPress, Drupal, Django integrations
- Crawler Developers: Crawler implementations
- Benchmarkers: Validate bandwidth savings on real websites


## Resources

- Specification: [scp_specification.md](scp_specification.md) - Technical specification (v0.1)
- License: [CC0 1.0 Universal](LICENSE) - Public Domain

## Contact

For questions, feedback:

Vasiliy Kiryanov

- https://github.com/vasiliyk
- https://x.com/vasiliykiryanov
- https://linkedin.com/in/vasiliykiryanov
