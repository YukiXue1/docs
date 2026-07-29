# Security Policy

## Reporting a vulnerability

Please do **not** open a public GitHub issue for security vulnerabilities.

Report privately by email to **tronlink@tronlink.org** — TronLink's officially published contact address (listed on [tronlink.org](https://www.tronlink.org/)) — with a subject line starting with `[SECURITY]`.

Where possible, include:

- The affected surface and version: the TronLink extension or mobile app, `mcp-server-tronlink`, `tronlink-mcp-core`, `mcp-tronlink-signer`, `tronlink-signer`, `@tronlink/tronlink-cli`, `tronlink-skills`, or this documentation site.
- Reproduction steps or a proof of concept.
- An impact assessment — in particular whether funds can be moved, or a signing approval bypassed, without user interaction.

The machine-readable disclosure pointer is published at [https://docs.tronlink.org/.well-known/security.txt](https://docs.tronlink.org/.well-known/security.txt) (RFC 9116; also served at `/security.txt`).

## Scope

This repository holds the developer documentation site ([docs.tronlink.org](https://docs.tronlink.org/)). Vulnerabilities in TronLink products themselves live in their own repositories (listed in [AGENTS.md](AGENTS.md)); until each of those ships its own security policy, use the reporting channel above for them as well.

Issues in scope for this repository specifically:

- Content injection / XSS on docs.tronlink.org.
- Documentation that instructs an unsafe default — e.g. an example that bypasses human-in-the-loop approval, weakens the SSRF allowlist, or would leak a private key or API secret.
- Supply-chain issues in the site build pipeline (`.github/workflows/`, `scripts/`).

## What not to report here

Lost funds, phishing reports, and account-support requests are user-support matters — use the support channels on [tronlink.org](https://www.tronlink.org/), not this policy.
