# Site Content Protocol (SCP)

A collection-based protocol that reduces waste of bandwidth, processing power, and energy through pre-generated snapshots and deltas.

## The Problem

Web crawlers (search engines, AI bots, aggregators) consume massive bandwidth and server resources by parsing web-pages designed for human viewing.
With the explosion of AI crawlers, this traffic has become a significant cost for websites and strain on internet infrastructure.

## The Solution

SCP enables websites to serve pre-generated collections of their content in compressed format from CDN or Cloud Object Storage.

**Target Goals**:

- 50-60% bandwidth reduction for initial snapshots vs compressed HTML
- 90-95% bandwidth reduction with delta updates (after initial download)
- 90% faster parsing than HTML/CSS/JS processing
- 90% fewer requests - one download fetches entire site sections
- Zero impact on user experience (users continue accessing regular sites)

## Resources

- **Documentation**: [scp-protocol.org](https://scp-protocol.org) - Getting started, guides, and examples
- **Specification**: [scp_specification.md](scp_specification.md) - Technical specification (v0.1)
- **License**: [CC0 1.0 Universal](LICENSE) - Public Domain

## Contact

Vasiliy Kiryanov

- https://github.com/vasiliyk
- https://x.com/vasiliykiryanov
- https://linkedin.com/in/vasiliykiryanov
