# Site Content Protocol (SCP) Specification v0.1

## Abstract

This document defines the Site Content Protocol (SCP), a format for serving structured web content to automated crawlers.
SCP enables websites to provide pre-generated, compressed collections of content via standard HTTP, which may reduce bandwidth consumption compared to traditional HTML crawling.
The protocol uses JSON Lines format with gzip or zstd compression, discovered via sitemap.xml extensions, and supports both full snapshots and incremental delta updates.
This specification defines the file format, collection protocol, HTTP transport requirements, and security considerations for SCP implementations.

## Introduction

### Problem Statement

AI training systems require massive web content datasets for language model development and knowledge extraction. Current approaches rely on scraping HTML designed for human browsing, which creates three fundamental problems:

1. **Low-quality training data**: Content extraction from HTML produces noisy datasets contaminated with navigation menus, advertisements, boilerplate text, and formatting markup. This degrades model training quality and requires extensive post-processing.

2. **High infrastructure costs**: Processing complete HTML/CSS/JavaScript for millions of pages generates substantial bandwidth and computational overhead. Large-scale content indexing systems must process and discard significant portions of retrieved HTML that consist of presentation markup, navigation, and other non-content elements.

3. **Legal and ethical uncertainty**: Automated scraping exists in a gray area between technical possibility and copyright/terms-of-service compliance. Sites that wish to contribute high-quality content to AI training have no standard mechanism to do so voluntarily.

The Site Content Protocol addresses these problems by providing a standard format for websites to voluntarily publish clean, structured content optimized for automated consumption, reducing infrastructure costs while improving data quality and establishing clear consent.

### Solution Overview

The Site Content Protocol (SCP) enables websites to serve crawler-optimized content separately from regular human-facing access:

1. Website owners pre-generate compressed collections of their content (blog posts, documentation, products) in structured JSON format
2. Collections are hosted on CDN or Cloud Object Storage and advertised in sitemap.xml
3. Crawlers download entire sections at once instead of requesting individual pages
4. End users continue browsing unchanged websites with zero impact

A single download replaces thousands of individual page requests, reducing infrastructure overhead while maintaining complete content fidelity for automated crawlers.
Bandwidth efficiency depends on content type, update frequency, and compression effectiveness.

### Goals and Non-Goals

**Goals:**

- Reduce bandwidth consumption and server load for web crawling
- Provide complete, structured content for search indexing and content discovery
- Minimize implementation complexity for both publishers and crawlers
- Leverage existing HTTP standards and infrastructure (sitemap.xml, standard HTTP caching)
- Enable efficient incremental updates via delta collections

**Non-Goals:**

- Replace HTML for human-facing web browsing
- Provide real-time API access to content
- Support interactive or dynamic content
- Define authentication mechanisms for automated crawlers
- Define payment mechanisms for content access

### Expected Performance Characteristics

The following characteristics are expected based on the protocol design, though actual results will vary by implementation and content:

**Bandwidth efficiency:**
- Initial snapshots provide size reduction compared to downloading all pages as compressed HTML
- Delta updates provide substantial bandwidth savings compared to re-downloading full snapshots
- For sites already using HTTP conditional requests (ETag/If-Modified-Since) effectively, bandwidth savings will be lower, but SCP still provides:
  - Request count reduction (1 collection request vs. thousands of conditional requests, even if most return 304 Not Modified)
  - Better batch compression efficiency (compressing multiple pages together vs. individual page compression)
  - Simpler content extraction (structured JSON vs. HTML/CSS/JS parsing)

**Processing efficiency:**
- JSON parsing may be significantly faster than HTML/CSS/JS processing
- Structured content blocks eliminate need for DOM traversal and content extraction heuristics

Performance claims should be validated through implementation-specific benchmarking.

## Terminology and Conventions

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED", "NOT RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be interpreted as described in BCP 14 [RFC2119] [RFC8174] when, and only when, they appear in all capitals, as shown here.

This specification uses the following terms:

- **Automated Crawler**: An automated agent that retrieves and indexes web content. This includes search engines, AI training systems, content aggregators, and other automated indexing services.
- **Collection**: A pre-generated file containing metadata and page objects in JSON Lines format
- **Snapshot**: A complete collection representing the full state of a content section
- **Delta**: An incremental collection containing only pages modified since a previous snapshot or delta
- **Section**: A logical grouping of related pages (e.g., "blog", "docs", "products")
- **Page**: A single web page represented as a JSON object with metadata and content blocks
- **Content Block**: A structured representation of page content (text, heading, image, etc.)

## File Format

SCP collections use JSON Lines (newline-delimited JSON) format, compressed with gzip or zstd.

### Structure

- File extension: `.scp.gz` (gzip), `.scp.zst` (zstd), or `.scp` (uncompressed)
- Content-Type: `application/scp`
- Content-Encoding: `gzip` or `zstd` (for compressed files)
- Format: One JSON object per line, each line represents one page
- First line MUST contain collection metadata
- Subsequent lines: Individual pages (one page per line)
- Compression: Entire file is compressed after JSON Lines construction (no partial compression)

### Collection Metadata

**Snapshot Collection:**
```json
{
  "collection": {
    "id": "blog-snapshot-q1",
    "section": "blog",
    "type": "snapshot",
    "generated": "2000-03-31T23:59:59Z",
    "checksum": "sha256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    "version": "0.1"
  }
}
```

**Delta Collection:**
```json
{
  "collection": {
    "id": "blog-delta-day15",
    "section": "blog",
    "type": "delta",
    "generated": "2000-01-15T23:00:00Z",
    "since": "2000-01-14T00:00:00Z",
    "checksum": "sha256:5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8",
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
  - `version` (string, required): SCP format version (e.g., "0.1"). Parsers SHOULD ignore unknown fields for forward compatibility.

### Page Schema

Each subsequent line is a JSON object representing one page:

```json
{
  "url": "https://example.com/blog/post-title",
  "title": "Page Title",
  "description": "Meta description for SEO",
  "author": "John Doe",
  "published": "2000-01-15T10:30:00Z",
  "modified": "2000-01-20T14:22:00Z",
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
    {"type": "video", "name": "Video Title", "url": [{"href": "https://example.com/video.mp4", "mediaType": "video/mp4"}]},
    {"type": "audio", "name": "Audio Title", "url": [{"href": "https://example.com/audio.mp3", "mediaType": "audio/mpeg"}]}
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

The `schema` field SHOULD be used when Schema.org defines a standardized type for the content. Common examples include:
- **Products**: Add pricing, ratings, availability, brand information
- **Recipes**: Include ingredients, cooking time, nutrition information
- **Events**: Provide dates, locations, ticket information
- **How-to guides**: Specify steps, required tools, estimated time
- **Articles/Blog posts**: Add keywords, article section, word count (optional)

**When to skip:**
- Simple blog posts without additional metadata
- Documentation pages
- Static content pages

#### Relationship to Page-Level Fields

Page-level metadata fields (`title`, `description`, `author`, `published`, `modified`) are REQUIRED basic metadata.
When the optional `schema` field is provided with Schema.org structured data, the following correspondences exist:

**Field mappings:**
- `title` ↔ Schema.org `name` (for Product, Organization, etc.) or `headline` (for Article, BlogPosting, etc.)
- `description` ↔ Schema.org `description`
- `author` ↔ Schema.org `author` (as Person or Organization type)
- `published` ↔ Schema.org `datePublished`
- `modified` ↔ Schema.org `dateModified`

**Processing model:**

When extracting structured data, crawlers SHOULD:
1. Use Schema.org properties when present and processing structured data
2. Fall back to page-level fields when Schema.org properties are absent
3. Use page-level fields for basic page indexing regardless of schema presence

**Consistency recommendations:**

Implementations SHOULD maintain consistency between corresponding page-level and Schema.org fields when both represent the same information.
However, the following differences are acceptable:
- Page `title` MAY include SEO optimization, branding suffixes, or formatting that differs from Schema.org `name` or `headline`
- Page `description` MAY include calls-to-action or promotional text that differs from Schema.org `description`
- Schema.org fields SHOULD represent the canonical, semantic identity of the content entity

**Example - Product with Schema.org:**
```json
{
  "url": "https://store.com/products/amazing-widget",
  "title": "Amazing Widget - Premium Quality",
  "description": "The best widget on the market",
  "modified": "2000-01-15T10:00:00Z",
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

Video content blocks use ActivityStreams 2.0 [ACTIVITYSTREAMS] Video object properties with SCP extensions for crawler needs.

```json
{
  "type": "video",
  "name": "Video Title",
  "url": [
    {"href": "https://example.com/video.mp4", "mediaType": "video/mp4"},
    {"href": "https://example.com/video.webm", "mediaType": "video/webm"},
    {"href": "https://youtube.com/watch?v=xyz123", "mediaType": "text/html", "rel": "alternate"}
  ],
  "duration": "PT5M20S",
  "width": 1920,
  "height": 1080,
  "icon": {
    "type": "Image",
    "url": "https://example.com/thumbnail.jpg"
  },
  "summary": "Video description",
  "captions": [
    {"language": "en", "url": "https://example.com/captions-en.vtt", "label": "English"},
    {"language": "es", "url": "https://example.com/captions-es.vtt", "label": "Español"}
  ],
  "chapters": [
    {"time": 0, "title": "Introduction"},
    {"time": 60, "title": "Main Content"}
  ],
  "transcript": "Full text transcript of video content..."
}
```

**ActivityStreams 2.0 properties:**
- `name` (required): Video title
- `url` (required): Video URL(s). Can be a single URL string or array of objects with `href` and `mediaType`
- `duration` (optional): Duration in ISO 8601 format (e.g., "PT5M20S" for 5 minutes 20 seconds)
- `width`, `height` (optional): Video dimensions in pixels
- `icon` (optional): Thumbnail/poster image as Image object
- `summary` (optional): Video description

**SCP extensions for crawler/accessibility needs:**
- `captions` (optional): Array of caption/subtitle files (WebVTT format)
- `chapters` (optional): Array of chapter markers with time (seconds) and title
- `transcript` (optional): Full text transcript for search indexing

#### Audio

Audio content blocks use ActivityStreams 2.0 [ACTIVITYSTREAMS] Audio object properties with SCP extensions for crawler needs.

```json
{
  "type": "audio",
  "name": "Episode 42: Web Standards",
  "url": [
    {"href": "https://example.com/podcast.mp3", "mediaType": "audio/mpeg"},
    {"href": "https://example.com/podcast.ogg", "mediaType": "audio/ogg"}
  ],
  "duration": "PT1H",
  "icon": {
    "type": "Image",
    "url": "https://example.com/cover.jpg"
  },
  "summary": "Discussion about web protocols",
  "attributedTo": "Tech Podcast",
  "partOf": "Season 3",
  "chapters": [
    {"time": 0, "title": "Introduction"},
    {"time": 300, "title": "Main Discussion"}
  ],
  "transcript": "Full text transcript of audio content..."
}
```

**ActivityStreams 2.0 properties:**
- `name` (required): Audio title
- `url` (required): Audio URL(s). Can be a single URL string or array of objects with `href` and `mediaType`
- `duration` (optional): Duration in ISO 8601 format (e.g., "PT1H" for 1 hour, "PT5M30S" for 5 minutes 30 seconds)
- `icon` (optional): Cover art/thumbnail image as Image object
- `summary` (optional): Audio description
- `attributedTo` (optional): Artist/creator name or Person object
- `partOf` (optional): Album/series name or Collection object

**SCP extensions for crawler/accessibility needs:**
- `chapters` (optional): Array of chapter markers with time (seconds) and title
- `transcript` (optional): Full text transcript for search indexing

## JSON Schema

### Page Object Schema

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
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
          "required": ["type", "name", "url"],
          "properties": {
            "type": {"const": "video"},
            "name": {"type": "string"},
            "url": {
              "oneOf": [
                {"type": "string", "format": "uri"},
                {
                  "type": "array",
                  "minItems": 1,
                  "items": {
                    "type": "object",
                    "required": ["href", "mediaType"],
                    "properties": {
                      "href": {"type": "string", "format": "uri"},
                      "mediaType": {"type": "string"},
                      "rel": {"type": "string"}
                    }
                  }
                }
              ]
            },
            "duration": {
              "type": "string",
              "pattern": "^PT(?=.*[HMS])(\\d+H)?(\\d+M)?(\\d+(\\.\\d+)?S)?$",
              "description": "ISO 8601 duration format (e.g., PT5M20S). Requires at least one component (H, M, or S)."
            },
            "width": {"type": "integer", "minimum": 0},
            "height": {"type": "integer", "minimum": 0},
            "icon": {
              "type": "object",
              "properties": {
                "type": {"const": "Image"},
                "url": {"type": "string", "format": "uri"}
              }
            },
            "summary": {"type": "string"},
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
            "transcript": {"type": "string"}
          }
        },
        {
          "type": "object",
          "required": ["type", "name", "url"],
          "properties": {
            "type": {"const": "audio"},
            "name": {"type": "string"},
            "url": {
              "oneOf": [
                {"type": "string", "format": "uri"},
                {
                  "type": "array",
                  "minItems": 1,
                  "items": {
                    "type": "object",
                    "required": ["href", "mediaType"],
                    "properties": {
                      "href": {"type": "string", "format": "uri"},
                      "mediaType": {"type": "string"}
                    }
                  }
                }
              ]
            },
            "duration": {
              "type": "string",
              "pattern": "^PT(?=.*[HMS])(\\d+H)?(\\d+M)?(\\d+(\\.\\d+)?S)?$",
              "description": "ISO 8601 duration format (e.g., PT1H for 1 hour). Requires at least one component (H, M, or S)."
            },
            "icon": {
              "type": "object",
              "properties": {
                "type": {"const": "Image"},
                "url": {"type": "string", "format": "uri"}
              }
            },
            "summary": {"type": "string"},
            "attributedTo": {"type": "string"},
            "partOf": {"type": "string"},
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
            "transcript": {"type": "string"}
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
  "$schema": "https://json-schema.org/draft/2020-12/schema",
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

## Validation

Parsers MUST validate:

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
- **Unknown content block type**: Parsers encountering unknown content block types MUST log a warning, MAY skip the block, and MUST continue processing the remaining content blocks and pages
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
                  url="https://r2.example.com/collections/blog-snapshot-day15.scp.gz"
                  generated="2000-01-15T00:00:00Z" expires="2000-01-16T00:00:00Z"
                  pages="5247" size="52000000"/>

  <scp:collection section="all" type="snapshot"
                  url="https://r2.example.com/collections/all-snapshot-latest.scp.gz"
                  generated="2000-01-15T00:00:00Z" expires="2000-01-16T00:00:00Z"
                  pages="12450" size="125000000"/>

  <!-- Delta Collections (incremental changes) -->
  <scp:delta section="blog" period="day15"
             url="https://r2.example.com/collections/blog-delta-day15.scp.gz"
             generated="2000-01-15T23:00:00Z" expires="2000-01-17T00:00:00Z"
             pages="47" size="480000"
             since="2000-01-14T00:00:00Z"/>

  <scp:delta section="all" period="day15"
             url="https://r2.example.com/collections/all-delta-day15.scp.gz"
             generated="2000-01-15T23:00:00Z" expires="2000-01-17T00:00:00Z"
             pages="124" size="1250000"
             since="2000-01-14T00:00:00Z"/>
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

#### Delta Collections

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

### Direct Download from Sitemap

Crawlers download collections directly from URLs advertised in `sitemap.xml`:

1. Parse sitemap.xml to find snapshot and delta URLs
2. Download files directly from CDN or object storage
3. No query endpoint needed - all collections are pre-generated
4. Collections are accessible with standard HTTP GET

Collections are downloaded directly via HTTP GET requests to the URLs advertised in sitemap.xml. Standard HTTP features (caching, conditional requests, compression) apply.

## Use with HTTP

This section defines how SCP collections are served and accessed over HTTP, following standards defined in [RFC7230] (HTTP/1.1 Message Syntax and Routing), [RFC7231] (HTTP/1.1 Semantics and Content), [RFC7232] (HTTP/1.1 Conditional Requests), and [RFC7234] (HTTP/1.1 Caching).

### Content-Type and Encoding

Servers MUST set appropriate Content-Type and Content-Encoding headers when serving SCP collections:

**For gzip-compressed collections** (`.scp.gz`):
```http
Content-Type: application/scp
Content-Encoding: gzip
```

**For zstd-compressed collections** (`.scp.zst`):
```http
Content-Type: application/scp
Content-Encoding: zstd
```

**For uncompressed collections** (`.scp`):
```http
Content-Type: application/scp
```

Servers SHOULD include the Content-Length header to indicate the file size (compressed or uncompressed).

### Conditional Requests

To avoid unnecessary downloads, servers SHOULD support HTTP conditional requests as defined in [RFC7232], and crawlers SHOULD use them.

#### Server-Side Requirements

Servers SHOULD provide `ETag` and `Last-Modified` headers with collection responses:

```http
HTTP/1.1 200 OK
Content-Type: application/scp
Content-Encoding: gzip
Content-Length: 52000000
ETag: "sha256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
Last-Modified: Wed, 15 Jan 2025 23:00:00 GMT
Cache-Control: public, max-age=86400

[collection data]
```

**ETag format**: Servers SHOULD use the SHA-256 checksum from the collection metadata as the ETag value:
```
ETag: "sha256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
```

**Last-Modified format**: Servers SHOULD use the collection's `generated` timestamp converted to HTTP-date format as defined in [RFC7231] Section 7.1.1.1.

Servers MUST respond with `304 Not Modified` when the `If-None-Match` or `If-Modified-Since` conditions indicate the client's cached version is current.

#### Crawler-Side Requirements

On subsequent requests to previously downloaded collections, crawlers SHOULD send conditional request headers:

```http
GET /collections/blog-snapshot-2025-01-15.scp.gz HTTP/1.1
Host: r2.example.com
If-None-Match: "sha256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
If-Modified-Since: Wed, 15 Jan 2025 23:00:00 GMT
```

**Handling responses**:
- **304 Not Modified**: Skip download; cached collection is current
- **200 OK**: Download new version; collection has been updated

**Crawler requirements**:
1. Crawlers MUST store the `ETag` and `Last-Modified` values from successful (200 OK) responses
2. Crawlers SHOULD send both `If-None-Match` and `If-Modified-Since` when available
3. Crawlers MUST handle `304 Not Modified` responses by using their cached version

This optimization is especially valuable for:
- Snapshots that don't change frequently (daily/weekly)
- Checking for deltas that might not exist for all time periods
- Reducing CDN egress costs

### Caching Directives

Servers SHOULD include Cache-Control headers as defined in [RFC7234] to indicate caching behavior. Cache duration SHOULD be chosen based on the collection's update frequency declared in sitemap.xml.

**Recommended for snapshots** (updated daily/weekly):
```http
Cache-Control: public, max-age=86400, stale-while-revalidate=3600
```
- `public`: Content is cacheable by any cache
- `max-age`: RECOMMENDED to match or exceed the update interval (e.g., 86400 for daily updates, 604800 for weekly)
- `stale-while-revalidate`: OPTIONAL directive to serve stale content while fetching fresh version

**Recommended for deltas** (updated frequently):
```http
Cache-Control: public, max-age=3600, must-revalidate
```
- `max-age`: RECOMMENDED to be shorter than snapshots (e.g., 3600 for hourly updates)
- `must-revalidate`: RECOMMENDED to ensure crawlers check for newer deltas

Servers MAY use different cache durations based on their specific update patterns and infrastructure requirements.

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
7. **Rate limiting**: Apply normal rate limits to collection HTTP requests to prevent abuse

## IANA Considerations

This section requests IANA to register a media type and namespace identifier for the Site Content Protocol.

### Media Type Registration

This document requests the registration of the media type `application/scp` in accordance with [RFC6838].

#### Media Type: application/scp

- **Type name:** application
- **Subtype name:** scp
- **Required parameters:** N/A
- **Optional parameters:** N/A
- **Encoding considerations:** Binary. SCP collections are newline-delimited JSON (JSON Lines) that MAY be compressed using gzip or zstd compression. When compressed, the `Content-Encoding` header indicates the compression method used (gzip or zstd).
- **Security considerations:** See Section "Security Considerations" of this document. SCP collections should be validated for: JSON syntax correctness, schema compliance, size limits (compressed and decompressed), decompression bomb protection (100:1 ratio limit), and URL sanitization.
- **Interoperability considerations:**
  - Uncompressed files use newline-delimited JSON format (JSON Lines) as defined in [JSONLINES]
  - Compressed files require gzip (RFC1952) or zstd decompression support
  - Compression method is indicated via the `Content-Encoding` HTTP header, not the media type
  - Parsers MUST support JSON Lines format and SHOULD support both gzip and zstd decompression
- **Published specification:** This document (Site Content Protocol Specification)
- **Applications that use this media type:** Web crawlers, search engines, content indexing systems, site content aggregators, AI training systems
- **Fragment identifier considerations:** N/A
- **Additional information:**
  - **Magic number(s):** None (JSON Lines format). When compressed: 1F 8B (gzip), 28 B5 2F FD (zstd)
  - **File extension(s):** .scp (uncompressed), .scp.gz (gzip-compressed), .scp.zst (zstd-compressed)
  - **Macintosh file type code(s):** N/A
- **Person & email address to contact for further information:** vasiliy.kiryanov@gmail.com
- **Intended usage:** COMMON
- **Restrictions on usage:** None
- **Author:** Vasiliy Kiryanov
- **Change controller:** IETF

### XML Namespace Registration

This document requests registration of the following XML namespace in the IETF XML Registry as defined in [RFC3688].

- **URI:** https://scp-protocol.org/schemas/sitemap/1.0
- **Registrant Contact:** vasiliy.kiryanov@gmail.com
- **XML:** The XML Schema Definition (XSD) is provided in Section "Sitemap XML Schema Definition"

## References

### Normative References

**[RFC2119]**
Bradner, S., "Key words for use in RFCs to Indicate Requirement Levels", BCP 14, RFC 2119, DOI 10.17487/RFC2119, March 1997, <https://www.rfc-editor.org/info/rfc2119>.

**[RFC3688]**
Mealling, M., "The IETF XML Registry", BCP 81, RFC 3688, DOI 10.17487/RFC3688, January 2004, <https://www.rfc-editor.org/info/rfc3688>.

**[RFC8174]**
Lepper, B., "Ambiguity of Uppercase vs Lowercase in RFC 2119 Key Words", BCP 14, RFC 8174, DOI 10.17487/RFC8174, May 2017, <https://www.rfc-editor.org/info/rfc8174>.

**[RFC6838]**
Freed, N., Klensin, J., and T. Hansen, "Media Type Specifications and Registration Procedures", BCP 13, RFC 6838, DOI 10.17487/RFC6838, January 2013, <https://www.rfc-editor.org/info/rfc6838>.

**[RFC7230]**
Fielding, R., Ed. and J. Reschke, Ed., "Hypertext Transfer Protocol (HTTP/1.1): Message Syntax and Routing", RFC 7230, DOI 10.17487/RFC7230, June 2014, <https://www.rfc-editor.org/info/rfc7230>.

**[RFC7231]**
Fielding, R., Ed. and J. Reschke, Ed., "Hypertext Transfer Protocol (HTTP/1.1): Semantics and Content", RFC 7231, DOI 10.17487/RFC7231, June 2014, <https://www.rfc-editor.org/info/rfc7231>.

**[RFC7232]**
Fielding, R., Ed. and J. Reschke, Ed., "Hypertext Transfer Protocol (HTTP/1.1): Conditional Requests", RFC 7232, DOI 10.17487/RFC7232, June 2014, <https://www.rfc-editor.org/info/rfc7232>.

**[RFC7234]**
Fielding, R., Ed., Nottingham, M., Ed., and J. Reschke, Ed., "Hypertext Transfer Protocol (HTTP/1.1): Caching", RFC 7234, DOI 10.17487/RFC7234, June 2014, <https://www.rfc-editor.org/info/rfc7234>.

**[RFC8259]**
Bray, T., Ed., "The JavaScript Object Notation (JSON) Data Interchange Format", STD 90, RFC 8259, DOI 10.17487/RFC8259, December 2017, <https://www.rfc-editor.org/info/rfc8259>.

### Informative References

**[ACTIVITYSTREAMS]**
Snell, J., Ed. and E. Prodromou, Ed., "Activity Streams 2.0", W3C Recommendation, May 2017, <https://www.w3.org/TR/activitystreams-core/>.

**[JSONLINES]**
JSON Lines, "JSON Lines text format, also called newline-delimited JSON", <https://jsonlines.org/>.

**[SCHEMA.ORG]**
Schema.org Community Group, "Schema.org - Schema.org", <https://schema.org/>.

**[SITEMAP]**
Sitemaps.org, "Sitemaps XML format", <https://www.sitemaps.org/protocol.html>.

## Examples

### Example 1: Minimal Snapshot Collection (Two Pages)

**Uncompressed .scp file** (before gzip/zstd compression):

```jsonl
{"collection":{"id":"example-minimal","section":"all","type":"snapshot","generated":"2025-01-15T10:00:00Z","checksum":"sha256:2c26b46b68ffc68ff99b453c1d30413413422d706483bfa0f98a5e886266e7ae","version":"0.1"}}
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

### Example 4: Product Page with Schema.org Data

```json
{
  "url": "https://example.com/products/widget",
  "title": "Amazing Widget",
  "description": "The best widget ever made",
  "modified": "2025-01-15T10:00:00Z",
  "language": "en",
  "schema": {
    "@context": "https://schema.org",
    "@type": "Product",
    "name": "Amazing Widget",
    "description": "The best widget ever made",
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
  "content": [
    {"type": "heading", "level": 1, "text": "Amazing Widget"},
    {"type": "text", "text": "This widget will change your life. Now with 50% more amazingness!"},
    {"type": "list", "ordered": false, "items": ["High quality materials", "2-year warranty", "Free shipping"]},
    {"type": "image", "url": "https://example.com/images/widget.jpg", "alt": "Amazing Widget product photo"}
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

**After gzip compression**: Binary file

**Usage**:
1. Crawler downloads `blog-2025-q1.scp.gz`
2. Decompress with gzip
3. Parse line-by-line (streaming)
4. Process each page object

