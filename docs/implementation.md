## Core Principle: Use Backend Data Sources

Generate SCP collections directly from your backend data sources (databases, APIs, files), not by parsing HTML.

### Why Backend Data?

- **More accurate**: Canonical data source with no parsing ambiguity
- **Faster**: No HTML parsing overhead
- **Complete metadata**: Direct access to authors, tags, timestamps, custom fields
- **Better structure**: Database schema vs HTML parsing heuristics

## Quick Start

### Parse a Collection

```python
from scp import parse_collection

metadata, pages = parse_collection("blog-snapshot.scp.gz")

print(f"Collection: {metadata.id}")
print(f"Type: {metadata.type}")
print(f"Pages: {len(pages)}")

for page in pages[:5]:
    print(f"  {page.url}: {page.title}")
```

### Generate a Collection

```python
from scp.generator import SCPGenerator

gen = SCPGenerator("blog-snapshot-2025-01", "blog", "snapshot")

gen.add_page(
    url="https://example.com/post1",
    title="First Post",
    description="My first blog post",
    modified="2025-01-15T10:00:00Z",
    language="en",
    content=[
        {"type": "heading", "level": 1, "text": "First Post"},
        {"type": "text", "text": "This is my first post."},
    ]
)

gen.save("blog-snapshot.scp.gz")
```

## Basic Usage

### Generate a Snapshot Collection

```python
from scp.generator import SCPGenerator

# Create generator for snapshot
gen = SCPGenerator(
    collection_id="blog-snapshot-2025-01-15",
    section="blog",
    collection_type="snapshot"
)

# Add pages from your data source
for page in your_data_source.get_all_pages():
    gen.add_page(
        url=page.url,
        title=page.title,
        description=page.description,
        modified=page.modified.isoformat(),
        language=page.language,
        content=convert_to_content_blocks(page.content)
    )

# Save with compression
gen.save("blog-snapshot.scp.gz", compress="gzip")
```

### Generate a Delta Collection

```python
from scp.generator import SCPGenerator
from datetime import datetime, timedelta

# Create generator for delta
yesterday = datetime.now() - timedelta(days=1)

gen = SCPGenerator(
    collection_id=f"blog-delta-{datetime.now().strftime('%Y-%m-%d')}",
    section="blog",
    collection_type="delta",
    since=yesterday.isoformat()  # Required for deltas
)

# Add only modified/new pages
for page in your_data_source.get_pages_modified_since(yesterday):
    gen.add_page(
        url=page.url,
        title=page.title,
        description=page.description,
        modified=page.modified.isoformat(),
        language=page.language,
        content=convert_to_content_blocks(page.content)
    )

gen.save(f"blog-delta-{datetime.now().strftime('%Y-%m-%d')}.scp.gz", compress="gzip")
```

## Hosting Collections

### Cloudflare R2 (example)

```bash
# Upload to Cloudflare R2 using rclone
rclone copy blog-snapshot.scp.gz r2:your-bucket/collections/
```

Configure rclone for R2:
```bash
rclone config create r2 s3 \
  provider Cloudflare \
  access_key_id your-r2-access-key \
  secret_access_key your-r2-secret-key \
  endpoint https://your-account-id.r2.cloudflarestorage.com
```

### Update Sitemap.xml

After uploading, update your sitemap.xml:

```python
from scp.sitemap import SitemapGenerator

sitemap = SitemapGenerator("0.1", ["gzip", "zstd"])

# Add section metadata
sitemap.add_section("blog", update_freq="daily", pages=5247)

# Add snapshot
sitemap.add_collection(
    section="blog",
    collection_type="snapshot",
    url="https://cdn.example.com/collections/blog-snapshot-2025-01-15.scp.gz",
    generated="2025-01-15T00:00:00Z",
    pages=5247,
    size=52000000
)

# Add delta
sitemap.add_delta(
    section="blog",
    period="2025-01-15",
    url="https://cdn.example.com/collections/blog-delta-2025-01-15.scp.gz",
    generated="2025-01-15T23:00:00Z",
    pages=47,
    size=480000,
    since="2025-01-14T00:00:00Z"
)

# Save sitemap
sitemap.save("sitemap.xml")
```

## Automation

### Scheduled Generation (Cron)

```bash
#!/bin/bash
# generate-scp-collections.sh

# Generate snapshot
python generate_snapshot.py

# Upload to R2
rclone copy blog-snapshot.scp.gz r2:your-bucket/collections/

# Update sitemap
python update_sitemap.py

# Upload sitemap
rclone copy sitemap.xml r2:your-bucket/
```

Schedule with cron:
```
0 0 * * * /path/to/generate-scp-collections.sh
```

### On-Demand Generation (Webhook)

```python
from flask import Flask, request
from scp.generator import SCPGenerator
from datetime import datetime

app = Flask(__name__)

@app.route('/webhook/content-updated', methods=['POST'])
def content_updated():
    # Generate delta collection
    gen = SCPGenerator(
        collection_id=f"blog-delta-{datetime.now().strftime('%Y-%m-%d-%H%M')}",
        section="blog",
        collection_type="delta",
        since=get_last_generation_time()
    )

    # Add updated pages
    page_ids = request.json.get('updated_pages', [])
    for page_id in page_ids:
        page = get_page(page_id)
        gen.add_page(
            url=page.url,
            title=page.title,
            description=page.description,
            modified=page.modified.isoformat(),
            language=page.language,
            content=convert_to_content_blocks(page.content)
        )

    # Save and upload
    gen.save("blog-delta.scp.gz")
    upload_to_cdn("blog-delta.scp.gz")
    update_sitemap()

    return {"status": "success"}
```

## Best Practices

1. **Generate from source data**: Always use backend databases, APIs, or files
2. **Compress with gzip or zstd**: Use level 6 for gzip, level 9 for zstd
3. **Include checksums**: Always generate SHA-256 checksums
4. **Use CDN**: Host collections on CDN or Cloud Object Storage for bandwidth efficiency
5. **Schedule snapshots**: Generate full snapshots periodically (daily/weekly)
6. **Generate deltas**: Create incremental deltas between snapshots
7. **Update sitemap**: Keep sitemap.xml current with collection URLs
8. **Monitor size**: Track collection sizes to ensure efficiency
9. **Validate output**: Use scp-validate to check generated collections
