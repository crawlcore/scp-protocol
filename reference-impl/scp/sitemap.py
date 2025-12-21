"""Sitemap generation with SCP extensions."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from lxml import etree


@dataclass
class SCPSection:
    """SCP section metadata."""

    name: str
    update_freq: str  # hourly, daily, weekly, monthly
    pages: str  # e.g., "~5000"


@dataclass
class SCPCollection:
    """SCP snapshot collection."""

    section: str
    url: str
    generated: str  # ISO 8601
    expires: str  # ISO 8601
    pages: int
    size: int  # bytes


@dataclass
class SCPDelta:
    """SCP delta collection."""

    section: str
    period: str  # e.g., "2025-01-15"
    url: str
    generated: str  # ISO 8601
    expires: str  # ISO 8601
    pages: int
    size: int  # bytes
    since: str  # ISO 8601


class SitemapGenerator:
    """Generator for sitemap.xml with SCP extensions."""

    SITEMAP_NS = "http://www.sitemaps.org/schemas/sitemap/0.9"
    SCP_NS = "https://scp-protocol.org/schemas/sitemap/1.0"

    def __init__(self, version: str = "0.1", compression: list[str] | None = None):
        """Initialize sitemap generator.

        Args:
            version: SCP protocol version
            compression: List of supported compression formats
        """
        self.version = version
        self.compression = compression or ["zstd", "gzip"]
        self.sections: list[SCPSection] = []
        self.collections: list[SCPCollection] = []
        self.deltas: list[SCPDelta] = []

    def add_section(self, name: str, update_freq: str, pages: str) -> None:
        """Add a section definition.

        Args:
            name: Section identifier
            update_freq: Update frequency (hourly, daily, weekly, monthly)
            pages: Approximate page count (e.g., "~5000")
        """
        self.sections.append(SCPSection(name=name, update_freq=update_freq, pages=pages))

    def add_collection(
        self,
        section: str,
        url: str,
        generated: str,
        expires: str,
        pages: int,
        size: int,
    ) -> None:
        """Add a snapshot collection.

        Args:
            section: Section identifier
            url: Direct download URL
            generated: ISO 8601 generation timestamp
            expires: ISO 8601 expiration timestamp
            pages: Number of pages in collection
            size: File size in bytes (compressed)
        """
        self.collections.append(
            SCPCollection(
                section=section,
                url=url,
                generated=generated,
                expires=expires,
                pages=pages,
                size=size,
            )
        )

    def add_delta(
        self,
        section: str,
        period: str,
        url: str,
        generated: str,
        expires: str,
        pages: int,
        size: int,
        since: str,
    ) -> None:
        """Add a delta collection.

        Args:
            section: Section identifier
            period: Time period identifier
            url: Direct download URL
            generated: ISO 8601 generation timestamp
            expires: ISO 8601 expiration timestamp
            pages: Number of pages in delta
            size: File size in bytes (compressed)
            since: ISO 8601 timestamp for changes since
        """
        self.deltas.append(
            SCPDelta(
                section=section,
                period=period,
                url=url,
                generated=generated,
                expires=expires,
                pages=pages,
                size=size,
                since=since,
            )
        )

    def generate(self) -> str:
        """Generate sitemap XML with SCP extensions.

        Returns:
            Formatted XML string
        """
        # Define namespaces
        nsmap: dict[str | None, str] = {None: self.SITEMAP_NS, "scp": self.SCP_NS}

        # Create root element
        urlset = etree.Element("urlset", nsmap=nsmap)  # type: ignore[arg-type]

        # Add SCP metadata
        version_elem = etree.SubElement(urlset, f"{{{self.SCP_NS}}}version")
        version_elem.text = self.version

        compression_elem = etree.SubElement(urlset, f"{{{self.SCP_NS}}}compression")
        compression_elem.text = ",".join(self.compression)

        # Add sections
        for section in self.sections:
            etree.SubElement(
                urlset,
                f"{{{self.SCP_NS}}}section",
                attrib={
                    "name": section.name,
                    "updateFreq": section.update_freq,
                    "pages": section.pages,
                },
            )

        # Add collections
        for collection in self.collections:
            etree.SubElement(
                urlset,
                f"{{{self.SCP_NS}}}collection",
                attrib={
                    "section": collection.section,
                    "type": "snapshot",
                    "url": collection.url,
                    "generated": collection.generated,
                    "expires": collection.expires,
                    "pages": str(collection.pages),
                    "size": str(collection.size),
                },
            )

        # Add deltas
        for delta in self.deltas:
            etree.SubElement(
                urlset,
                f"{{{self.SCP_NS}}}delta",
                attrib={
                    "section": delta.section,
                    "period": delta.period,
                    "url": delta.url,
                    "generated": delta.generated,
                    "expires": delta.expires,
                    "pages": str(delta.pages),
                    "size": str(delta.size),
                    "since": delta.since,
                },
            )

        # Convert to pretty-printed string
        xml_bytes = etree.tostring(
            urlset,
            pretty_print=True,
            xml_declaration=True,
            encoding="UTF-8",
        )

        return xml_bytes.decode("utf-8")

    def save(self, file_path: str | Path) -> None:
        """Generate and save sitemap.xml file.

        Args:
            file_path: Output file path
        """
        xml_content = self.generate()

        file_path = Path(file_path)
        file_path.parent.mkdir(parents=True, exist_ok=True)

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(xml_content)
