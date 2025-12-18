# Site Content Protocol (SCP) Specification v0.1

## Overview

### Problem
Web crawlers (search engines, AI bots, aggregators) consume massive bandwidth and server resources by parsing web-pages
designed for human viewing. With the explosion of AI crawlers, this traffic has become a significant cost for
websites and strain on internet infrastructure.

### Solution
SCP (Site Content Protocol) enables websites to serve crawler-optimized content separately from regular human-facing access.

How it works:
- Website owners use automation to pre-generate compressed collections of their content (blog posts, documentation, products) in structured JSON format
- Collections are hosted on CDN (like Cloudflare R2) or Cloud Object storage (like Cloudflare R2) and advertised in sitemap.xml
- Crawlers download entire sections at once instead of requesting individual pages
- End users continue browsing unchanged web-sites with zero impact

### Result
A single download replaces thousands of individual page requests, reducing bandwidth by 50-95% while maintaining complete content fidelity for search engines and AI systems.

Will be added in the future:
- Bot verification to ensure only approved crawlers access site content using [Web Bot Auth](https://developers.cloudflare.com/bots/reference/bot-verification/web-bot-auth/)
- Pay for content to support fair crawler-content creator dynamic using model similar to [Pay Per Crawl](https://blog.cloudflare.com/introducing-pay-per-crawl/)

## Design Goals

### Core Principles

1. Efficiency: Minimize bandwidth and processing via collections (batch hundreds/thousands of pages into single requests)
2. Completeness: Capture all information needed for search indexing and content discovery
3. Simplicity: Pre-generated collections on CDN / Cloud Object storage with delta updates

### Target Metrics

- 50-60% bandwidth savings for initial snapshots vs compressed HTML
- 90-95% bandwidth savings with delta updates (after initial download)
- 90% faster parsing than HTML/CSS/JS processing
- 90% fewer requests (one download fetches entire site sections instead of page-by-page crawling)

## File Format

SCP collections use JSON Lines (newline-delimited JSON) format, compressed with gzip or zstd.

### Structure

- File extension: `.scp.gz` (gzip) or `.scp.zst` (zstd)
- Content-Type: `application/x-ndjson+gzip` or `application/x-ndjson+zstd`
- Format: One JSON object per line, each line represents one page
- First line: Collection metadata (optional)
- Subsequent lines: Individual pages

### Collection Metadata

**Snapshot Collection:**
```json
{
  "collection": {
    "id": "blog-snapshot-2024-Q1",
    "section": "blog",
    "type": "snapshot",
    "generated": "2024-03-31T23:59:59Z",
    "checksum": "sha256:abc123def456789...",
    "version": "0.1"
  }
}
```

**Delta Collection:**
```json
{
  "collection": {
    "id": "blog-delta-2025-01-15",
    "section": "blog",
    "type": "delta",
    "generated": "2025-01-15T23:00:00Z",
    "since": "2025-01-14T00:00:00Z",
    "checksum": "sha256:def789abc123456...",
    "version": "0.1"
  }
}
```

**Fields**:
- `collection` (object): Metadata about this collection
  - `id` (string, required): Unique identifier for this specific collection
  - `section` (string, required): Section name (e.g., "blog", "docs", "all")
  - `type` (string, required): Collection type - "snapshot" (full state) or "delta" (incremental changes)
  - `generated` (string, required): ISO 8601 timestamp when collection was created
  - `since` (string, required for delta): ISO 8601 timestamp indicating changes since this time (delta collections only)
  - `checksum` (string, optional): SHA-256 checksum for integrity verification (format: "sha256:hexdigest")
  - `version` (string, required): SCP format version

### Page Schema

Each subsequent line is a JSON object representing one page:

```json
{
  "url": "https://example.com/blog/post-title",
  "title": "Page Title",
  "description": "Meta description for SEO",
  "author": "John Doe",
  "published": "2024-01-15T10:30:00Z",
  "modified": "2024-01-20T14:22:00Z",
  "language": "en",
  "canonical": "https://example.com/blog/post-title",
  "robots": ["noarchive"],
  "schema": {
    "@context": "https://schema.org",
    "@type": "BlogPosting",
    "keywords": ["scp", "protocol", "web"],
    "articleSection": "Technology"
  },
  "content": [
    {"type": "heading", "level": 1, "text": "Main Heading"},
    {"type": "text", "text": "Paragraph content goes here."},
    {"type": "link", "url": "https://example.com", "text": "Link text", "rel": ["nofollow"]},
    {"type": "image", "url": "https://example.com/image.jpg", "alt": "Alt text"},
    {"type": "list", "ordered": false, "items": ["Item 1", "Item 2", "Item 3"]},
    {"type": "code", "language": "python", "code": "print('Hello')"},
    {"type": "table", "rows": [["Cell 1", "Cell 2"], ["Cell 3", "Cell 4"]]},
    {"type": "quote", "text": "Quote text", "citation": "Source"},
    {"type": "video", "sources": [{"url": "https://example.com/video.mp4"}], "title": "Video Title"},
    {"type": "audio", "sources": [{"url": "https://example.com/audio.mp3"}], "title": "Audio Title"},
    {"type": "structured", "format": "json-ld", "data": {...}}
  ]
}
```

### Page Fields

**Metadata Fields** (top level):
- `url` (string, required): Full URL of the page
- `title` (string, required): Page title
- `description` (string, required): Meta description
- `author` (string, optional): Content author
- `published` (string, optional): ISO 8601 publication date
- `modified` (string, required): ISO 8601 last modified date
- `language` (string, required): Language code (e.g., "en", "es")
- `canonical` (string, optional): Canonical URL
- `robots` (array of strings, optional): Robot directives: `["noindex", "nofollow", "noarchive", "nosnippet", "notranslate", "noimageindex"]`
- `schema` (object, optional): Schema.org structured data (e.g., Product, Recipe, BlogPosting, Event)
- `content` (array, required): Ordered array of content blocks

### Schema.org Integration (Optional)

The optional `schema` field allows sites to include Schema.org structured data for enhanced search results and semantic understanding.

**When to use:**
- **Products**: Add pricing, ratings, availability, brand information
- **Recipes**: Include ingredients, cooking time, nutrition information
- **Events**: Provide dates, locations, ticket information
- **How-to guides**: Specify steps, required tools, estimated time
- **Articles/Blog posts**: Add keywords, article section, word count (optional)

**When to skip:**
- Simple blog posts without additional metadata
- Documentation pages
- Static content pages

**Example - Product with Schema.org:**
```json
{
  "url": "https://store.com/products/amazing-widget",
  "title": "Amazing Widget - Premium Quality",
  "description": "The best widget on the market",
  "modified": "2025-01-15T10:00:00Z",
  "language": "en",
  "schema": {
    "@context": "https://schema.org",
    "@type": "Product",
    "name": "Amazing Widget",
    "brand": {"@type": "Brand", "name": "WidgetCo"},
    "offers": {
      "@type": "Offer",
      "price": "29.99",
      "priceCurrency": "USD",
      "availability": "https://schema.org/InStock"
    },
    "aggregateRating": {
      "@type": "AggregateRating",
      "ratingValue": "4.5",
      "reviewCount": "89"
    }
  },
  "content": [...]
}
```

**Example - Recipe with Schema.org:**
```json
{
  "url": "https://recipes.com/chocolate-cake",
  "title": "Best Chocolate Cake Recipe",
  "description": "Moist and delicious chocolate cake",
  "modified": "2025-01-15T10:00:00Z",
  "language": "en",
  "schema": {
    "@context": "https://schema.org",
    "@type": "Recipe",
    "name": "Chocolate Cake",
    "recipeYield": "8 servings",
    "prepTime": "PT30M",
    "cookTime": "PT45M",
    "recipeIngredient": ["2 cups flour", "1 cup sugar", "3/4 cup cocoa powder"],
    "nutrition": {
      "@type": "NutritionInformation",
      "calories": "320 calories"
    }
  },
  "content": [...]
}
```

### Content Block Types

#### Text
```json
{"type": "text", "text": "Paragraph content"}
```

#### Heading
```json
{"type": "heading", "level": 1, "text": "Heading text"}
```
- `level`: 1-6 for H1-H6

#### Link
```json
{"type": "link", "url": "https://example.com", "text": "Link text", "rel": ["nofollow", "sponsored"]}
```
- `rel` (optional): Array of link relationships

#### Image
```json
{"type": "image", "url": "https://example.com/image.jpg", "alt": "Alt text"}
```

#### List
```json
{"type": "list", "ordered": false, "items": ["Item 1", "Item 2"]}
```
- `ordered`: `true` for ol, `false` for ul

#### Code
```json
{"type": "code", "language": "python", "code": "print('Hello')"}
```
- `language` (optional): Programming language identifier

#### Table
```json
{"type": "table", "rows": [["Header 1", "Header 2"], ["Cell 1", "Cell 2"]]}
```
- `rows`: Array of arrays (row-major order)

#### Quote
```json
{"type": "quote", "text": "Quote text", "citation": "Source"}
```
- `citation` (optional): Attribution

#### Video
```json
{
  "type": "video",
  "sources": [
    {"url": "https://example.com/video.mp4", "format": "mp4", "quality": "1080p", "size": 52428800},
    {"url": "https://example.com/video.webm", "format": "webm", "quality": "720p", "size": 31457280}
  ],
  "poster": "https://example.com/thumbnail.jpg",
  "title": "Video Title",
  "description": "Video description",
  "duration": 300,
  "width": 1920,
  "height": 1080,
  "captions": [
    {"language": "en", "url": "https://example.com/captions-en.vtt", "label": "English"},
    {"language": "es", "url": "https://example.com/captions-es.vtt", "label": "Español"}
  ],
  "chapters": [
    {"time": 0, "title": "Introduction"},
    {"time": 60, "title": "Main Content"}
  ],
  "embed": "https://youtube.com/watch?v=xyz123",
  "transcript": "Full text transcript of video content..."
}
```
- `sources` (required): Array of video sources with different formats/qualities
- `poster` (optional): Thumbnail image URL
- `title` (required): Video title
- `description` (optional): Video description
- `duration` (optional): Duration in seconds
- `width`, `height` (optional): Video dimensions in pixels
- `captions` (optional): Array of caption/subtitle files
- `chapters` (optional): Array of chapter markers
- `embed` (optional): External platform embed URL (YouTube, Vimeo, etc.)
- `transcript` (optional): Full text transcript for search indexing

**Simplified format** (single source):
```json
{"type": "video", "sources": [{"url": "https://example.com/video.mp4"}], "title": "Title"}
```

#### Audio
```json
{
  "type": "audio",
  "sources": [
    {"url": "https://example.com/podcast.mp3", "format": "mp3", "bitrate": 320, "size": 7340032},
    {"url": "https://example.com/podcast.ogg", "format": "ogg", "bitrate": 256, "size": 5898240}
  ],
  "title": "Episode 42: Web Standards",
  "description": "Discussion about web protocols",
  "artist": "Tech Podcast",
  "album": "Season 3",
  "duration": 3600,
  "coverArt": "https://example.com/cover.jpg",
  "transcript": "Full text transcript...",
  "chapters": [
    {"time": 0, "title": "Introduction"},
    {"time": 300, "title": "Main Discussion"}
  ]
}
```
- `sources` (required): Array of audio sources with different formats
- `title` (required): Audio title
- `description` (optional): Audio description
- `artist` (optional): Artist/creator name
- `album` (optional): Album/series name
- `duration` (optional): Duration in seconds
- `coverArt` (optional): Cover image URL
- `transcript` (optional): Full text transcript for search indexing
- `chapters` (optional): Array of chapter markers

**Simplified format** (single source):
```json
{"type": "audio", "sources": [{"url": "https://example.com/audio.mp3"}], "title": "Title"}
```

#### Structured Data
```json
{"type": "structured", "format": "json-ld", "data": {"@context": "https://schema.org", ...}}
```
- `format`: "json-ld", "microdata", or "schema-org"
- `data`: Structured data object

## JSON Schema

### Page Object Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["url", "title", "description", "modified", "language", "content"],
  "properties": {
    "url": {
      "type": "string",
      "format": "uri",
      "pattern": "^https?://"
    },
    "title": {
      "type": "string"
    },
    "description": {
      "type": "string"
    },
    "author": {
      "type": "string"
    },
    "published": {
      "type": "string",
      "format": "date-time"
    },
    "modified": {
      "type": "string",
      "format": "date-time"
    },
    "language": {
      "type": "string",
      "pattern": "^[a-z]{2}(-[A-Z]{2})?$"
    },
    "canonical": {
      "type": "string",
      "format": "uri"
    },
    "robots": {
      "type": "array",
      "items": {
        "type": "string",
        "enum": ["noindex", "nofollow", "noarchive", "nosnippet", "notranslate", "noimageindex"]
      },
      "uniqueItems": true
    },
    "schema": {
      "type": "object",
      "description": "Optional Schema.org structured data (JSON-LD format)"
    },
    "content": {
      "type": "array",
      "minItems": 1,
      "items": {
        "$ref": "#/definitions/contentBlock"
      }
    }
  },
  "definitions": {
    "contentBlock": {
      "oneOf": [
        {
          "type": "object",
          "required": ["type", "text"],
          "properties": {
            "type": {"const": "text"},
            "text": {"type": "string"}
          }
        },
        {
          "type": "object",
          "required": ["type", "level", "text"],
          "properties": {
            "type": {"const": "heading"},
            "level": {"type": "integer", "minimum": 1, "maximum": 6},
            "text": {"type": "string"}
          }
        },
        {
          "type": "object",
          "required": ["type", "url", "text"],
          "properties": {
            "type": {"const": "link"},
            "url": {"type": "string", "format": "uri"},
            "text": {"type": "string"},
            "rel": {
              "type": "array",
              "items": {"type": "string"}
            }
          }
        },
        {
          "type": "object",
          "required": ["type", "url", "alt"],
          "properties": {
            "type": {"const": "image"},
            "url": {"type": "string", "format": "uri"},
            "alt": {"type": "string"}
          }
        },
        {
          "type": "object",
          "required": ["type", "ordered", "items"],
          "properties": {
            "type": {"const": "list"},
            "ordered": {"type": "boolean"},
            "items": {
              "type": "array",
              "items": {"type": "string"}
            }
          }
        },
        {
          "type": "object",
          "required": ["type", "code"],
          "properties": {
            "type": {"const": "code"},
            "language": {"type": "string"},
            "code": {"type": "string"}
          }
        },
        {
          "type": "object",
          "required": ["type", "rows"],
          "properties": {
            "type": {"const": "table"},
            "rows": {
              "type": "array",
              "items": {
                "type": "array",
                "items": {"type": "string"}
              }
            }
          }
        },
        {
          "type": "object",
          "required": ["type", "text"],
          "properties": {
            "type": {"const": "quote"},
            "text": {"type": "string"},
            "citation": {"type": "string"}
          }
        },
        {
          "type": "object",
          "required": ["type", "sources", "title"],
          "properties": {
            "type": {"const": "video"},
            "sources": {
              "type": "array",
              "minItems": 1,
              "items": {
                "type": "object",
                "required": ["url"],
                "properties": {
                  "url": {"type": "string", "format": "uri"},
                  "format": {"type": "string"},
                  "quality": {"type": "string"},
                  "size": {"type": "integer"}
                }
              }
            },
            "poster": {"type": "string", "format": "uri"},
            "title": {"type": "string"},
            "description": {"type": "string"},
            "duration": {"type": "integer", "minimum": 0},
            "width": {"type": "integer", "minimum": 0},
            "height": {"type": "integer", "minimum": 0},
            "captions": {
              "type": "array",
              "items": {
                "type": "object",
                "required": ["language", "url", "label"],
                "properties": {
                  "language": {"type": "string"},
                  "url": {"type": "string", "format": "uri"},
                  "label": {"type": "string"}
                }
              }
            },
            "chapters": {
              "type": "array",
              "items": {
                "type": "object",
                "required": ["time", "title"],
                "properties": {
                  "time": {"type": "integer", "minimum": 0},
                  "title": {"type": "string"}
                }
              }
            },
            "embed": {"type": "string", "format": "uri"},
            "transcript": {"type": "string"}
          }
        },
        {
          "type": "object",
          "required": ["type", "sources", "title"],
          "properties": {
            "type": {"const": "audio"},
            "sources": {
              "type": "array",
              "minItems": 1,
              "items": {
                "type": "object",
                "required": ["url"],
                "properties": {
                  "url": {"type": "string", "format": "uri"},
                  "format": {"type": "string"},
                  "bitrate": {"type": "integer"},
                  "size": {"type": "integer"}
                }
              }
            },
            "title": {"type": "string"},
            "description": {"type": "string"},
            "artist": {"type": "string"},
            "album": {"type": "string"},
            "duration": {"type": "integer", "minimum": 0},
            "coverArt": {"type": "string", "format": "uri"},
            "transcript": {"type": "string"},
            "chapters": {
              "type": "array",
              "items": {
                "type": "object",
                "required": ["time", "title"],
                "properties": {
                  "time": {"type": "integer", "minimum": 0},
                  "title": {"type": "string"}
                }
              }
            }
          }
        },
        {
          "type": "object",
          "required": ["type", "format", "data"],
          "properties": {
            "type": {"const": "structured"},
            "format": {
              "type": "string",
              "enum": ["json-ld", "microdata", "schema-org"]
            },
            "data": {"type": "object"}
          }
        }
      ]
    }
  }
}
```

### Collection Metadata Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["collection"],
  "properties": {
    "collection": {
      "type": "object",
      "required": ["id", "section", "type", "generated", "version"],
      "properties": {
        "id": {
          "type": "string",
          "pattern": "^[a-zA-Z0-9-_]+$"
        },
        "section": {
          "type": "string",
          "pattern": "^[a-zA-Z0-9-_]+$"
        },
        "type": {
          "type": "string",
          "enum": ["snapshot", "delta"]
        },
        "generated": {
          "type": "string",
          "format": "date-time"
        },
        "since": {
          "type": "string",
          "format": "date-time",
          "description": "Required for delta collections, indicates changes since this timestamp"
        },
        "checksum": {
          "type": "string",
          "pattern": "^sha256:[a-fA-F0-9]{64}$",
          "description": "Optional SHA-256 checksum for integrity verification"
        },
        "version": {
          "type": "string",
          "pattern": "^\\d+\\.\\d+$"
        }
      },
      "if": {
        "properties": {
          "type": {"const": "delta"}
        }
      },
      "then": {
        "required": ["id", "section", "type", "generated", "since", "version"]
      }
    }
  }
}
```


## Compression

**Recommended**:
- **gzip level 6**: Broad compatibility, good compression
- **zstd level 9**: Better compression ratio, modern standard

**File extensions**:
- `.scp.gz` for gzip
- `.scp.zst` for zstd

Entire file is compressed after JSON Lines construction. No partial compression.

## Validation

Parsers SHOULD validate:

1. **File decompression**: Verify compressed file can be decompressed
2. **JSON validity**: Each line must be valid JSON
3. **Required fields**: `url`, `title`, `description`, `modified`, `language`, `content`
4. **URL format**: Valid HTTP/HTTPS URLs
5. **Content types**: All content blocks have valid `type` field

## Error Handling

### Fatal Errors (reject entire file):
- Decompression failure
- Invalid JSON on any line
- Missing required fields in page object
- Decompression ratio exceeds 100:1 (compression bomb protection)

### Non-Fatal Errors (skip line, continue parsing):
- Unknown content block `type` (log warning, skip block)
- Invalid URL format (log warning, skip page)
- Heading level outside 1-6 (clamp to nearest valid value)

### Fallback Strategy:
When SCP parsing fails, crawlers MUST fall back to fetching and parsing HTML version of pages.

## Collection Protocol

SCP uses a **collections-only** approach where entire site sections are bundled into single compressed JSON Lines files, rather than serving pages individually.
This maximizes compression efficiency and simplifies implementation.

### Discovery via Sitemap

Sites advertise SCP collections in `sitemap.xml` using an extended namespace:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"
        xmlns:scp="https://scp-protocol.org/schemas/sitemap/1.0">

  <!-- SCP Metadata -->
  <scp:version>0.1</scp:version>
  <scp:compression>zstd,gzip</scp:compression>

  <!-- Available Sections -->
  <scp:section name="all" updateFreq="daily" pages="~12000"/>
  <scp:section name="blog" updateFreq="daily" pages="~5000"/>
  <scp:section name="docs" updateFreq="weekly" pages="~200"/>
  <scp:section name="products" updateFreq="hourly" pages="~1000"/>

  <!-- Snapshot Collections (full state) -->
  <scp:collection section="blog" type="snapshot"
                  url="https://r2.example.com/collections/blog-snapshot-2025-01-15.scp.gz"
                  generated="2025-01-15T00:00:00Z" expires="2025-01-16T00:00:00Z"
                  pages="5247" size="52000000"/>

  <scp:collection section="all" type="snapshot"
                  url="https://r2.example.com/collections/all-snapshot-latest.scp.gz"
                  generated="2025-01-15T00:00:00Z" expires="2025-01-16T00:00:00Z"
                  pages="12450" size="125000000"/>

  <!-- Delta Collections (incremental changes) -->
  <scp:delta section="blog" period="2025-01-15"
             url="https://r2.example.com/collections/blog-delta-2025-01-15.scp.gz"
             generated="2025-01-15T23:00:00Z" expires="2025-01-17T00:00:00Z"
             pages="47" size="480000"
             since="2025-01-14T00:00:00Z"/>

  <scp:delta section="all" period="2025-01-15"
             url="https://r2.example.com/collections/all-delta-2025-01-15.scp.gz"
             generated="2025-01-15T23:00:00Z" expires="2025-01-17T00:00:00Z"
             pages="124" size="1250000"
             since="2025-01-14T00:00:00Z"/>
</urlset>
```

### Sitemap XML Schema Definition

The SCP sitemap extension namespace is formally defined by the following XML Schema (XSD):

```xml
<?xml version="1.0" encoding="UTF-8"?>
<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema"
           targetNamespace="https://scp-protocol.org/schemas/sitemap/1.0"
           xmlns:scp="https://scp-protocol.org/schemas/sitemap/1.0"
           elementFormDefault="qualified">

  <!-- Root-level elements that appear directly under <urlset> -->

  <xs:element name="version">
    <xs:annotation>
      <xs:documentation>
        SCP protocol version (e.g., "1.0")
      </xs:documentation>
    </xs:annotation>
    <xs:simpleType>
      <xs:restriction base="xs:string">
        <xs:pattern value="\d+\.\d+"/>
      </xs:restriction>
    </xs:simpleType>
  </xs:element>

  <xs:element name="compression">
    <xs:annotation>
      <xs:documentation>
        Comma-separated list of supported compression formats (e.g., "zstd,gzip")
      </xs:documentation>
    </xs:annotation>
    <xs:simpleType>
      <xs:restriction base="xs:string">
        <xs:pattern value="[a-z]+(,[a-z]+)*"/>
      </xs:restriction>
    </xs:simpleType>
  </xs:element>

  <xs:element name="section">
    <xs:annotation>
      <xs:documentation>
        Defines an available content section
      </xs:documentation>
    </xs:annotation>
    <xs:complexType>
      <xs:attribute name="name" type="xs:string" use="required">
        <xs:annotation>
          <xs:documentation>Section identifier (e.g., "blog", "docs", "all")</xs:documentation>
        </xs:annotation>
      </xs:attribute>
      <xs:attribute name="updateFreq" use="required">
        <xs:annotation>
          <xs:documentation>Update frequency for this section</xs:documentation>
        </xs:annotation>
        <xs:simpleType>
          <xs:restriction base="xs:string">
            <xs:enumeration value="hourly"/>
            <xs:enumeration value="daily"/>
            <xs:enumeration value="weekly"/>
            <xs:enumeration value="monthly"/>
          </xs:restriction>
        </xs:simpleType>
      </xs:attribute>
      <xs:attribute name="pages" type="xs:string" use="required">
        <xs:annotation>
          <xs:documentation>
            Approximate page count (can use "~" prefix for estimates, e.g., "~5000")
          </xs:documentation>
        </xs:annotation>
      </xs:attribute>
    </xs:complexType>
  </xs:element>

  <xs:element name="collection">
    <xs:annotation>
      <xs:documentation>
        Pre-generated snapshot collection file (full section state)
      </xs:documentation>
    </xs:annotation>
    <xs:complexType>
      <xs:attribute name="section" type="xs:string" use="required">
        <xs:annotation>
          <xs:documentation>Section identifier this collection belongs to</xs:documentation>
        </xs:annotation>
      </xs:attribute>
      <xs:attribute name="type" use="required">
        <xs:annotation>
          <xs:documentation>Collection type (snapshot for full state)</xs:documentation>
        </xs:annotation>
        <xs:simpleType>
          <xs:restriction base="xs:string">
            <xs:enumeration value="snapshot"/>
          </xs:restriction>
        </xs:simpleType>
      </xs:attribute>
      <xs:attribute name="url" type="xs:anyURI" use="required">
        <xs:annotation>
          <xs:documentation>Direct download URL for the collection file</xs:documentation>
        </xs:annotation>
      </xs:attribute>
      <xs:attribute name="generated" type="xs:dateTime" use="required">
        <xs:annotation>
          <xs:documentation>Timestamp when this collection was generated</xs:documentation>
        </xs:annotation>
      </xs:attribute>
      <xs:attribute name="expires" type="xs:dateTime" use="required">
        <xs:annotation>
          <xs:documentation>Timestamp when this collection URL expires</xs:documentation>
        </xs:annotation>
      </xs:attribute>
      <xs:attribute name="pages" type="xs:integer" use="required">
        <xs:annotation>
          <xs:documentation>Number of pages in this collection</xs:documentation>
        </xs:annotation>
      </xs:attribute>
      <xs:attribute name="size" type="xs:integer" use="required">
        <xs:annotation>
          <xs:documentation>File size in bytes (compressed)</xs:documentation>
        </xs:annotation>
      </xs:attribute>
    </xs:complexType>
  </xs:element>

  <xs:element name="delta">
    <xs:annotation>
      <xs:documentation>
        Pre-generated delta collection (incremental updates)
      </xs:documentation>
    </xs:annotation>
    <xs:complexType>
      <xs:attribute name="section" type="xs:string" use="required">
        <xs:annotation>
          <xs:documentation>Section identifier this delta belongs to</xs:documentation>
        </xs:annotation>
      </xs:attribute>
      <xs:attribute name="period" type="xs:string" use="required">
        <xs:annotation>
          <xs:documentation>Time period identifier (e.g., "2025-01-15" for daily deltas)</xs:documentation>
        </xs:annotation>
      </xs:attribute>
      <xs:attribute name="url" type="xs:anyURI" use="required">
        <xs:annotation>
          <xs:documentation>Direct download URL for the delta file</xs:documentation>
        </xs:annotation>
      </xs:attribute>
      <xs:attribute name="generated" type="xs:dateTime" use="required">
        <xs:annotation>
          <xs:documentation>Timestamp when this delta was generated</xs:documentation>
        </xs:annotation>
      </xs:attribute>
      <xs:attribute name="expires" type="xs:dateTime" use="required">
        <xs:annotation>
          <xs:documentation>Timestamp when this delta URL expires</xs:documentation>
        </xs:annotation>
      </xs:attribute>
      <xs:attribute name="pages" type="xs:integer" use="required">
        <xs:annotation>
          <xs:documentation>Number of pages in this delta</xs:documentation>
        </xs:annotation>
      </xs:attribute>
      <xs:attribute name="size" type="xs:integer" use="required">
        <xs:annotation>
          <xs:documentation>File size in bytes (compressed)</xs:documentation>
        </xs:annotation>
      </xs:attribute>
      <xs:attribute name="since" type="xs:dateTime" use="required">
        <xs:annotation>
          <xs:documentation>Timestamp from which this delta covers changes</xs:documentation>
        </xs:annotation>
      </xs:attribute>
    </xs:complexType>
  </xs:element>

</xs:schema>
```

**Schema Location**: `https://scp-protocol.org/schemas/sitemap/1.0/sitemap-extension.xsd`

**Usage in Sitemap**:
```xml
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"
        xmlns:scp="https://scp-protocol.org/schemas/sitemap/1.0"
        xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
        xsi:schemaLocation="https://scp-protocol.org/schemas/sitemap/1.0
                            https://scp-protocol.org/schemas/sitemap/1.0/sitemap-extension.xsd">
  <!-- SCP elements here -->
</urlset>
```

### Snapshots and Deltas

**Design Principle**: SCP provides pre-generated snapshot collections (full state) and delta collections (incremental changes). For real-time API access to the data layer, sites should provide separate APIs.

#### Snapshot Collections

**Full section state**, generated periodically based on `updateFreq`:

```xml
<scp:collection section="blog" type="snapshot"
                url="https://r2.example.com/blog-snapshot-2025-01-15.scp.gz"
                generated="2025-01-15T00:00:00Z"
                expires="2025-01-16T00:00:00Z"
                pages="5247" size="52000000"/>
```

- Contains ALL pages in the section
- Updated hourly/daily/weekly based on section updateFreq
- Highly cacheable (24h+ TTL for daily updates)
- First crawl downloads full snapshot

####  Delta Collections

**Incremental changes**, contains only modified/new pages:

```xml
<scp:delta section="blog" period="2025-01-15"
           url="https://r2.example.com/blog-delta-2025-01-15.scp.gz"
           generated="2025-01-15T23:00:00Z"
           expires="2025-01-17T00:00:00Z"
           pages="47" size="480000"
           since="2025-01-14T00:00:00Z"/>
```

- Contains ONLY pages modified/created during the period
- Generated hourly/daily based on section updateFreq
- Much smaller than snapshots (typically <1% of snapshot size)
- Subsequent crawls download deltas and merge locally

### Crawler Workflow

**Initial Crawl**:
1. Parse sitemap.xml
2. Download snapshot collection for each section
3. Index all pages

**Incremental Updates**:
1. Check sitemap for new delta collections
2. Download delta-2025-01-15.scp.gz (47 pages)
3. Download delta-2025-01-16.scp.gz (89 pages)
4. Merge deltas into local index (update/add pages)
5. Optionally: Re-download full snapshot periodically (weekly/monthly) to ensure consistency

**Example Timeline**:
- Day 1: Download blog-snapshot (5,247 pages, 52 MB)
- Day 2: Download blog-delta-2025-01-16 (47 pages, 480 KB)
- Day 3: Download blog-delta-2025-01-17 (89 pages, 920 KB)
- Day 4: Download blog-delta-2025-01-18 (124 pages, 1.2 MB)

**Bandwidth savings**: 54.6 MB vs. 208 MB traditional (4 daily full crawls) = **74% bandwidth reduction**

### Direct Download from Sitemap

Crawlers download collections directly from URLs advertised in `sitemap.xml`:

1. Parse sitemap.xml to find snapshot and delta URLs
2. Download files directly from CDN (e.g., Cloudflare R2)
3. No query endpoint needed - all collections are pre-generated
4. Collections can be accessible with standard HTTP GET

**Example**:
```bash
# Download snapshot
curl https://r2.example.com/collections/blog-snapshot-2025-01-15.scp.gz

# Download delta
curl https://r2.example.com/collections/blog-delta-2025-01-15.scp.gz
```

### Caching and Hosting

Snapshot and delta collections SHOULD be hosted on CDN/object storage:

**Recommended: Cloudflare R2**
- High bandwidth allowance
- Global CDN distribution
- No egress fees

**R2 URL Structure**:
```
https://r2.example.com/collections/blog-snapshot-2025-01-15.scp.gz
https://r2.example.com/collections/blog-delta-2025-01-15.scp.gz
```

**TTL Strategy**:
- Snapshots: 24-48 hours (based on updateFreq)
- Deltas: 24-72 hours (keep recent deltas available)
- Old deltas can be removed after crawlers have had time to fetch them

**Public Access**: Collections are publicly accessible via standard HTTPS. No authentication required for reading.

**Rate Limiting** (optional):
- CDNs typically handle rate limiting automatically
- For self-hosted: Apply standard rate limits per IP/bot
- Return `429 Too Many Requests` with `Retry-After` header when exceeded

## Implementation Checklist

### For Website Owners

- [ ] Define content sections (e.g., blog, docs, products)
- [ ] Implement snapshot generator (generates full section collections)
- [ ] Implement delta generator (generates incremental change collections)
- [ ] Configure Cloudflare R2 or similar CDN/object storage
- [ ] Set up automated generation schedule (hourly/daily based on updateFreq)
- [ ] Upload snapshot and delta files to CDN/object storage
- [ ] Add SCP metadata to sitemap.xml with snapshot and delta URLs
- [ ] Clean up old delta files periodically (keep last 7-30 days)

### For Crawler Developers

- [ ] Parse sitemap.xml for snapshot and delta collection URLs
- [ ] Download snapshot collections on initial crawl
- [ ] Download delta collections for incremental updates
- [ ] Implement JSON Lines parser (decompress + parse line-by-line)
- [ ] Handle compressed files (.scp.gz with gzip, .scp.zst with zstd)
- [ ] Validate JSON schema for each page object
- [ ] Merge delta updates into local index (update/insert pages)
- [ ] Track which deltas have been processed to avoid duplicates
- [ ] Periodically re-download full snapshots for consistency

## Security Considerations

1. **JSON Validation**: Validate each line is valid JSON before processing
2. **Size limits**: Enforce maximums to prevent DoS:
   - **Total file (compressed)**: 50 GB maximum
   - **Total file (decompressed)**: 500 GB maximum
   - **Single page object**: 100 MB maximum (reject oversized pages)
   - Reject collections exceeding these limits
3. **Compression bombs**: Limit decompression ratio to 100:1 maximum
   - Example: 10 MB compressed must not exceed 1 GB decompressed
   - Abort decompression if ratio is exceeded
4. **Schema validation**: Verify required fields exist and have correct types
5. **URL sanitization**: Validate and sanitize all URLs (page URLs and content URLs)
6. **Content sanitization**: Sanitize text content as you would with HTML (XSS prevention)
7. **Rate limiting**: Apply normal rate limits to SCP query endpoints

## Versioning

Version is indicated in the collection metadata's `version` field and sitemap's `<scp:version>` element.

**Sitemap version declaration**:
```xml
<scp:version>0.1</scp:version>
```

**Collection metadata version**:
```json
{"collection": {"version": "0.1", ...}}
```

Future versions may introduce new content block types or optional fields. Parsers SHOULD ignore unknown fields gracefully.

## Examples

### Example 1: Minimal Snapshot Collection (Two Pages)

**Uncompressed .scp file** (before gzip/zstd compression):

```jsonl
{"collection":{"id":"example-minimal","section":"all","type":"snapshot","generated":"2025-01-15T10:00:00Z","checksum":"sha256:a1b2c3d4e5f6..","version":"0.1"}}
{"url":"https://example.com/","title":"Home Page","description":"Welcome to our site","modified":"2025-01-15T09:00:00Z","language":"en","content":[{"type":"heading","level":1,"text":"Welcome"},{"type":"text","text":"Hello World!"}]}
{"url":"https://example.com/about","title":"About Us","description":"Learn about our company","author":"John Doe","published":"2024-12-01T10:00:00Z","modified":"2025-01-10T15:30:00Z","language":"en","content":[{"type":"heading","level":1,"text":"About Us"},{"type":"text","text":"We are a company."}]}
```

**Format**: 3 lines total
- Line 1: Collection metadata
- Line 2: Home page
- Line 3: About page

### Example 2: Blog Post with Rich Content

```json
{
  "url": "https://example.com/blog/getting-started",
  "title": "Getting Started with SCP",
  "description": "Learn how to implement Site Content Protocol",
  "author": "Jane Smith",
  "published": "2025-01-10T08:00:00Z",
  "modified": "2025-01-12T14:22:00Z",
  "language": "en",
  "canonical": "https://example.com/blog/getting-started",
  "robots": ["noarchive"],
  "content": [
    {"type": "heading", "level": 1, "text": "Getting Started with SCP"},
    {"type": "text", "text": "SCP provides a structured format for web content."},
    {"type": "heading", "level": 2, "text": "Installation"},
    {"type": "code", "language": "bash", "code": "npm install scp-generator"},
    {"type": "text", "text": "That's it! You're ready to go."},
    {"type": "link", "url": "https://docs.example.com", "text": "Read the docs", "rel": ["noopener"]},
    {"type": "image", "url": "https://example.com/images/diagram.png", "alt": "Architecture diagram"}
  ]
}
```

### Example 3: Page with Table and List

```json
{
  "url": "https://example.com/features",
  "title": "Feature Comparison",
  "description": "Compare SCP features",
  "modified": "2025-01-15T10:00:00Z",
  "language": "en",
  "content": [
    {"type": "heading", "level": 1, "text": "Features"},
    {"type": "text", "text": "SCP offers these benefits:"},
    {"type": "list", "ordered": false, "items": ["Fast parsing", "Bandwidth savings", "Easy implementation"]},
    {"type": "heading", "level": 2, "text": "Comparison Table"},
    {"type": "table", "rows": [
      ["Feature", "SCP", "HTML"],
      ["Size", "Small", "Large"],
      ["Parsing", "Fast", "Slow"],
      ["Readable", "No", "Yes"]
    ]}
  ]
}
```

### Example 4: Page with Structured Data

```json
{
  "url": "https://example.com/products/widget",
  "title": "Amazing Widget",
  "description": "The best widget ever made",
  "modified": "2025-01-15T10:00:00Z",
  "language": "en",
  "content": [
    {"type": "heading", "level": 1, "text": "Amazing Widget"},
    {"type": "text", "text": "This widget will change your life."},
    {"type": "structured", "format": "json-ld", "data": {
      "@context": "https://schema.org",
      "@type": "Product",
      "name": "Amazing Widget",
      "description": "The best widget ever made",
      "offers": {
        "@type": "Offer",
        "price": "29.99",
        "priceCurrency": "USD"
      }
    }}
  ]
}
```

### Example 5: Complete Snapshot Collection File Structure

**Filename**: `blog-2025-q1.scp.gz`

**Uncompressed content**:
```jsonl
{"collection":{"id":"blog-2025-q1","section":"blog","type":"snapshot","generated":"2025-01-15T00:00:00Z","checksum":"sha256:f7d8e9a1b2c3d4e5...","version":"0.1"}}
{"url":"https://example.com/blog/post-1","title":"First Post","description":"The first post"...}
{"url":"https://example.com/blog/post-2","title":"Second Post","description":"The second post"...}
{"url":"https://example.com/blog/post-3","title":"Third Post","description":"The third post"...}
```

**After gzip compression**: Binary file, ~60% smaller than uncompressed

**Usage**:
1. Crawler downloads `blog-2025-q1.scp.gz`
2. Decompress with gzip
3. Parse line-by-line (streaming)
4. Process each page object

