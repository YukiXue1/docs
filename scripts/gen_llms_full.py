#!/usr/bin/env python3
"""Generate per-language full-text bundles for LLM ingestion.

llms-full.{en,zh}.txt is the single-fetch, full-text variant of llms.txt
(https://llmstxt.org/). It bundles every page so an LLM can ingest the
whole documentation set in one request.

We also write `llms-full.txt` as a verbatim copy of the English bundle so
existing links (e.g. /llms-full.txt) keep working.

Usage:

    python3 scripts/gen_llms_full.py
        Generate the three bundles in docs/.

    python3 scripts/gen_llms_full.py --verify https://docs.tronlink.org
        Skip generation; sample-check that the curated indexes' links
        return 200 on the live deployment. Used as a post-deploy CI gate.
        If you hit SSL CERTIFICATE_VERIFY_FAILED locally on macOS, run
        `/Applications/Python\ 3.X/Install\ Certificates.command` once
        to install the CA bundle (CI on Ubuntu has it by default).

Pages are emitted in navigation order (mirroring the `en` and `zh` navs
in mkdocs.yml). Re-run this whenever docs change; wire it into CI to keep
it in sync.
"""
from __future__ import annotations

import argparse
import random
import re
import subprocess
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urljoin

DOCS = Path(__file__).resolve().parent.parent / "docs"
REPO = DOCS.parent

# In-bundle url markers use relative paths (just `<slug>/`), so they
# work under any deployment path without hardcoding a base prefix.

# English source pages, in nav order (see mkdocs.yml `en` nav).
PAGES_EN = [
    "introduction.en.md",
    "hd-wallets.en.md",
    "dapp/getting-started.en.md",
    "ai-support/ai-llms.en.md",
    "ai-support/security-model.en.md",
    "mobile/asset-management.en.md",
    "mobile/deeplink.en.md",
    "mobile/dapp-support.en.md",
    "plugin-wallet/active-requests.en.md",
    "plugin-wallet/passive-messages.en.md",
    "plugin-wallet/ledger-signing-update.en.md",
    "ai-support/mcp-server-tronlink.en.md",
    "ai-support/tronlink-mcp-core.en.md",
    "ai-support/tronlink-skills.en.md",
    "ai-support/mcp-tronlink-signer.en.md",
    "ai-support/tronlink-signer.en.md",
    "ai-support/tronlink-cli.en.md",
    "dapp/transfer.en.md",
    "dapp/multi-sign-transfer.en.md",
    "dapp/message-signing.en.md",
    "dapp/stake2.en.md",
    "reference/networks.en.md",
    "reference/glossary.en.md",
    "reference/error-code-map.en.md",
    "reference/faq.en.md",
]

# Chinese source pages, in nav order (see mkdocs.yml `zh` nav).
PAGES_ZH = [
    "introduction.zh.md",
    "hd-wallets.zh.md",
    "dapp/getting-started.zh.md",
    "ai-support/ai-llms.zh.md",
    "ai-support/security-model.zh.md",
    "mobile/asset-management.zh.md",
    "mobile/deeplink.zh.md",
    "mobile/dapp-support.zh.md",
    "plugin-wallet/active-requests.zh.md",
    "plugin-wallet/passive-messages.zh.md",
    "plugin-wallet/ledger-signing-update.zh.md",
    "ai-support/mcp-server-tronlink.zh.md",
    "ai-support/tronlink-mcp-core.zh.md",
    "ai-support/tronlink-skills.zh.md",
    "ai-support/mcp-tronlink-signer.zh.md",
    "ai-support/tronlink-signer.zh.md",
    "ai-support/tronlink-cli.zh.md",
    "dapp/transfer.zh.md",
    "dapp/multi-sign-transfer.zh.md",
    "dapp/message-signing.zh.md",
    "dapp/stake2.zh.md",
    "reference/networks.zh.md",
    "reference/glossary.zh.md",
    "reference/error-code-map.zh.md",
    "reference/faq.zh.md",
]


def git_short_sha() -> str:
    """Return short SHA of the worktree HEAD, or 'unknown' if git fails."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--short=12", "HEAD"],
            cwd=REPO,
            check=True,
            capture_output=True,
            text=True,
        )
        return result.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return "unknown"


def estimate_tokens(char_count: int) -> int:
    """Rough token estimate (~4 chars per token, OpenAI heuristic).

    Coarse on purpose: we want an order-of-magnitude hint for agents
    deciding whether to ingest the whole file. Zero-dep by choice.
    """
    return char_count // 4


def page_url(rel: str, lang: str) -> str:
    """`introduction.en.md` -> `introduction/` (relative to the bundle).

    The English bundle lives at `/llms-full.txt` and its sibling pages
    are at `/<slug>/`; the Chinese bundle lives at `/zh/llms-full.txt`
    and its sibling pages are at `/zh/<slug>/`. In both cases the URL
    marker is the same relative form, so an LLM that fetched the bundle
    from either locale can resolve it without knowing the deploy prefix.
    """
    suffix = f".{lang}.md"
    slug = rel[: -len(suffix)]
    return f"{slug}/"


def render_bundle(pages: list[str], lang: str, sha: str, generated_at: str) -> tuple[str, int, list[str]]:
    """Return (full_text, page_count, missing) for one language."""
    body_parts: list[str] = []
    missing: list[str] = []
    for rel in pages:
        path = DOCS / rel
        if not path.exists():
            missing.append(rel)
            continue
        body_parts.append("---")
        body_parts.append("")
        body_parts.append(f"<!-- source: docs/{rel} | url: {page_url(rel, lang)} -->")
        body_parts.append("")
        body_parts.append(path.read_text(encoding="utf-8").rstrip())
        body_parts.append("")

    body = "\n".join(body_parts)
    token_estimate = estimate_tokens(len(body))
    page_count = len(pages) - len(missing)

    if lang == "en":
        title = "# TronLink Developer Documentation — Full Text"
        blurb = (
            "Concatenation of all English documentation pages for single-fetch "
            "LLM ingestion. Generated by scripts/gen_llms_full.py. "
            "See ./llms.txt for the curated index."
        )
    else:
        title = "# TronLink 开发者文档 —— 全文"
        blurb = (
            "中文文档全文拼接，适合 LLM 一次性 ingest。由 scripts/gen_llms_full.py 生成。"
            "索引见 ../llms.txt 的 Localized 段。"
        )

    header = [
        title,
        "",
        f"> {blurb}",
        "",
        f"- Generated: {generated_at}",
        f"- Commit: {sha}",
        f"- Language: {lang}",
        f"- Pages: {page_count}",
        f"- Token estimate: ~{token_estimate:,} (chars / 4)",
        "",
    ]
    return "\n".join(header) + body + "\n", page_count, missing


LINK_RE = re.compile(r"\[[^\]]*\]\(([^)\s]+)\)")

# `> Updated: <iso> · Commit: <sha>` is upserted into llms.txt /
# llms.zh.txt so an agent can self-check staleness without parsing the
# bundle bodies.
UPDATED_PREFIX = "> Updated: "


def stamp_index_header(path: Path, updated_at: str, sha: str) -> None:
    """Upsert a `> Updated: <iso> · Commit: <sha>` line into a curated index.

    If a matching line already exists, replace it in place. Otherwise
    insert it as a fresh blockquote immediately after the primary blurb
    blockquote. No-op if the file lacks a primary blockquote (we'd
    rather raise loudly than guess where to put metadata).
    """
    new_line = f"{UPDATED_PREFIX}{updated_at} · Commit: {sha}"
    lines = path.read_text(encoding="utf-8").splitlines()

    for i, line in enumerate(lines):
        if line.startswith(UPDATED_PREFIX):
            lines[i] = new_line
            path.write_text("\n".join(lines) + "\n", encoding="utf-8")
            return

    quote_end: int | None = None
    in_quote = False
    for i, line in enumerate(lines):
        if line.startswith("> "):
            in_quote = True
        elif in_quote:
            quote_end = i
            break

    if quote_end is None:
        raise SystemExit(f"No primary blockquote in {path}; cannot stamp header")

    new_lines = lines[: quote_end + 1] + [new_line, ""] + lines[quote_end + 1 :]
    path.write_text("\n".join(new_lines) + "\n", encoding="utf-8")


def parse_index_links(path: Path) -> list[str]:
    """Extract in-site `[label](target)` link targets from a curated index.

    Skips external URLs, mailto, and pure anchors. The returned strings
    are the raw href values (relative to the index file's own location),
    suitable for `urljoin` against the index's deployed URL.
    """
    targets: list[str] = []
    for match in LINK_RE.finditer(path.read_text(encoding="utf-8")):
        href = match.group(1).strip()
        if href.startswith(("http://", "https://", "mailto:", "#")):
            continue
        targets.append(href)
    return targets


def http_status(url: str, timeout: float = 10.0) -> int:
    """GET `url`; return status code, or 0 on network failure.

    Uses GET (not HEAD) because some CDNs/proxies misroute HEAD requests
    or strip caching headers; the body is discarded.
    """
    req = urllib.request.Request(
        url,
        method="GET",
        headers={"User-Agent": "gen_llms_full/verify"},
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            resp.read(1)  # touch body to surface mid-stream errors; discard
            return resp.status
    except urllib.error.HTTPError as exc:
        return exc.code
    except (urllib.error.URLError, TimeoutError, OSError):
        return 0


def check_security_txt_expiry(min_days: int = 30) -> int:
    """Fail when docs/security.txt lacks an Expires field or the field is
    within `min_days` of lapsing — RFC 9116 consumers treat an expired
    security.txt as invalid, so this forces a refresh before it rots.
    Returns 0 when healthy, 1 otherwise.
    """
    path = DOCS / "security.txt"
    if not path.exists():
        print(f"Missing {path}", file=sys.stderr)
        return 1
    m = re.search(r"^Expires:\s*(\S+)", path.read_text(encoding="utf-8"), re.MULTILINE)
    if not m:
        print("security.txt has no Expires field", file=sys.stderr)
        return 1
    try:
        expires = datetime.fromisoformat(m.group(1).replace("Z", "+00:00"))
    except ValueError:
        print(f"security.txt Expires is not ISO 8601: {m.group(1)}", file=sys.stderr)
        return 1
    days_left = (expires - datetime.now(timezone.utc)).days
    if days_left < min_days:
        print(
            f"security.txt Expires {m.group(1)} is {days_left} days away "
            f"(< {min_days}) — bump the date in docs/security.txt",
            file=sys.stderr,
        )
        return 1
    print(f"security.txt Expires OK ({days_left} days left)")
    return 0


def verify_live(base_url: str, sample_size: int = 5) -> int:
    """Sample-check curated index links against `base_url`.

    Always probes the fixed endpoints (the four llms bundles, the
    agent-entry files, and the security.txt pointer); then picks
    `sample_size` additional random link targets from each curated index
    and probes those too. Returns 0 if every probe returns 200, 1 otherwise.
    """
    if check_security_txt_expiry():
        return 1
    base = base_url.rstrip("/") + "/"
    probes: list[tuple[str, str]] = [
        ("endpoint", urljoin(base, "llms.txt")),
        ("endpoint", urljoin(base, "zh/llms.txt")),
        ("endpoint", urljoin(base, "llms-full.txt")),
        ("endpoint", urljoin(base, "zh/llms-full.txt")),
        ("endpoint", urljoin(base, "AGENTS.txt")),
        ("endpoint", urljoin(base, "AGENTS.md")),
        ("endpoint", urljoin(base, "CLAUDE.md")),
        ("endpoint", urljoin(base, ".well-known/security.txt")),
        ("endpoint", urljoin(base, "security.txt")),
    ]
    for label, index_path, deploy_url in [
        ("en-sample", DOCS / "llms.txt", urljoin(base, "llms.txt")),
        ("zh-sample", DOCS / "llms.zh.txt", urljoin(base, "zh/llms.txt")),
    ]:
        if not index_path.exists():
            print(f"Missing index file: {index_path}", file=sys.stderr)
            return 1
        links = parse_index_links(index_path)
        if not links:
            print(f"No in-site links found in {index_path}", file=sys.stderr)
            return 1
        sample = random.sample(links, min(sample_size, len(links)))
        for href in sample:
            probes.append((label, urljoin(deploy_url, href)))

    print(f"Verifying {len(probes)} URLs against {base}")
    failures: list[tuple[str, int]] = []
    for label, url in probes:
        code = http_status(url)
        flag = "  OK" if code == 200 else f"FAIL {code:>3}"
        print(f"  [{label:9s}] {flag}  {url}")
        if code != 200:
            failures.append((url, code))

    if failures:
        print(f"\n{len(failures)} of {len(probes)} probes failed:", file=sys.stderr)
        for url, code in failures:
            print(f"  {code}  {url}", file=sys.stderr)
        return 1
    print(f"\nAll {len(probes)} URLs returned 200")
    return 0


def generate_bundles() -> None:
    sha = git_short_sha()
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    all_missing: dict[str, list[str]] = {}

    for lang, pages, out_name in [
        ("en", PAGES_EN, "llms-full.en.txt"),
        ("zh", PAGES_ZH, "llms-full.zh.txt"),
    ]:
        text, count, missing = render_bundle(pages, lang, sha, generated_at)
        out_path = DOCS / out_name
        out_path.write_text(text, encoding="utf-8")
        print(
            f"Wrote {out_path.relative_to(REPO)} "
            f"({count} pages, commit {sha}, ~{estimate_tokens(len(text)):,} tokens)"
        )
        if lang == "en":
            # Back-compat: keep llms-full.txt as a copy of the English bundle
            # so existing links (e.g. /llms-full.txt) keep resolving.
            (DOCS / "llms-full.txt").write_text(text, encoding="utf-8")
            print(f"Wrote {(DOCS / 'llms-full.txt').relative_to(REPO)} (alias of {out_name})")
        if missing:
            all_missing[lang] = missing

    for index_name in ("llms.txt", "llms.zh.txt"):
        index_path = DOCS / index_name
        if index_path.exists():
            stamp_index_header(index_path, generated_at, sha)
            print(f"Stamped {index_path.relative_to(REPO)} (commit {sha})")

    if all_missing:
        msg = "; ".join(f"{lang}: {', '.join(m)}" for lang, m in all_missing.items())
        raise SystemExit("Missing pages — " + msg)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--verify",
        metavar="BASE_URL",
        help="Skip generation; sample-check curated index links against this base URL "
             "(e.g. https://docs.tronlink.org).",
    )
    parser.add_argument(
        "--sample-size",
        type=int,
        default=5,
        help="Random links per locale to probe in --verify mode (default: 5).",
    )
    parser.add_argument(
        "--check-security-expiry",
        action="store_true",
        help="Only check that docs/security.txt Expires is not about to lapse.",
    )
    args = parser.parse_args()

    if args.check_security_expiry:
        sys.exit(check_security_txt_expiry())
    if args.verify:
        sys.exit(verify_live(args.verify, sample_size=args.sample_size))
    generate_bundles()


if __name__ == "__main__":
    main()
