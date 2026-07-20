#!/usr/bin/env python3
"""Dump the MCP tool contracts to a static, one-fetch JSON artifact.

Spawns the published npm MCP servers over stdio, performs the MCP
`initialize` handshake, calls `tools/list` (following pagination), and
writes every tool definition — name, description, inputSchema,
annotations — to docs/reference/mcp-tools.json.

The running server's `tools/list` remains the source of truth (see
AGENTS.md, "Source-of-truth boundaries"); this artifact is a stamped
point-in-time snapshot so agents can read the full contract without
installing Node or spawning a server. Regenerate whenever an upstream
package publishes a new version:

    python3 scripts/dump_mcp_tools.py

Requires: Node >= 18 with `npx` on PATH, network access to npmjs.org.
Zero Python dependencies by choice, like the sibling scripts.
"""
from __future__ import annotations

import json
import os
import select
import subprocess
import sys
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
OUT_PATH = REPO / "docs" / "reference" / "mcp-tools.json"

PROTOCOL_VERSION = "2024-11-05"

# Dummy env that lets @tronlink/mcp-server-tronlink register its full tool
# surface without a real wallet, browser, or credentials:
#   - TRONLINK_EXTENSION_PATH only needs to exist on disk;
#   - TL_TRONGRID_URL / TL_GASFREE_BASE_URL / TL_MULTISIG_* switch the
#     on-chain / gasfree / multisig capabilities on (their handlers check
#     wallet availability at call time, not at registration time);
#   - PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD avoids a ~100MB browser fetch.
# Placeholder values are never dialled: tools/list makes no network calls.
def tronlink_env(dummy_dir: str) -> dict[str, str]:
    return {
        "PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD": "1",
        "TRONLINK_EXTENSION_PATH": dummy_dir,
        "TL_TRONGRID_URL": "https://nile.trongrid.io",
        "TL_GASFREE_BASE_URL": "https://example.invalid",
        "TL_MULTISIG_BASE_URL": "https://example.invalid",
        "TL_MULTISIG_SECRET_ID": "placeholder",
        "TL_MULTISIG_SECRET_KEY": "placeholder",
        "TL_MULTISIG_CHANNEL": "placeholder",
    }


SERVERS = [
    {
        "id": "mcp-server-tronlink",
        "npm": "@tronlink/mcp-server-tronlink",
        "docs": "https://docs.tronlink.org/ai-support/mcp-server-tronlink/",
        "env": tronlink_env,
    },
    {
        "id": "mcp-tronlink-signer",
        "npm": "mcp-tronlink-signer",
        "docs": "https://docs.tronlink.org/ai-support/mcp-tronlink-signer/",
        "env": lambda dummy_dir: {"PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD": "1"},
    },
]


def npm_latest_version(package: str) -> str:
    result = subprocess.run(
        ["npm", "view", package, "version"],
        check=True,
        capture_output=True,
        text=True,
        timeout=60,
    )
    return result.stdout.strip()


def git_short_sha() -> str:
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


class McpStdioClient:
    """Minimal newline-delimited JSON-RPC client for MCP stdio servers."""

    def __init__(self, argv: list[str], env: dict[str, str]):
        self.proc = subprocess.Popen(
            argv,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            env={**os.environ, **env},
            text=True,
            bufsize=1,
        )
        self._next_id = 0

    def _send(self, message: dict) -> None:
        assert self.proc.stdin is not None
        self.proc.stdin.write(json.dumps(message) + "\n")
        self.proc.stdin.flush()

    def _read_until(self, want_id: int, timeout: float) -> dict:
        """Read lines until the response with `want_id` arrives.

        Skips notifications and any non-JSON noise a server may emit on
        stdout. select() keeps us from blocking past the deadline.
        """
        assert self.proc.stdout is not None
        deadline = time.monotonic() + timeout
        while True:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise TimeoutError(f"no response with id={want_id} within {timeout}s")
            if self.proc.poll() is not None:
                raise RuntimeError(f"server exited early (code {self.proc.returncode})")
            ready, _, _ = select.select([self.proc.stdout], [], [], min(remaining, 1.0))
            if not ready:
                continue
            line = self.proc.stdout.readline()
            if not line:
                raise RuntimeError("server closed stdout")
            try:
                message = json.loads(line)
            except json.JSONDecodeError:
                continue
            if message.get("id") == want_id:
                if "error" in message:
                    raise RuntimeError(f"JSON-RPC error: {message['error']}")
                return message["result"]

    def request(self, method: str, params: dict | None = None, timeout: float = 60.0) -> dict:
        self._next_id += 1
        message: dict = {"jsonrpc": "2.0", "id": self._next_id, "method": method}
        if params is not None:
            message["params"] = params
        self._send(message)
        return self._read_until(self._next_id, timeout)

    def notify(self, method: str) -> None:
        self._send({"jsonrpc": "2.0", "method": method})

    def close(self) -> None:
        self.proc.terminate()
        try:
            self.proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            self.proc.kill()


def list_all_tools(client: McpStdioClient) -> tuple[list[dict], str]:
    """Run the MCP handshake and drain paginated tools/list."""
    init = client.request(
        "initialize",
        {
            "protocolVersion": PROTOCOL_VERSION,
            "capabilities": {},
            "clientInfo": {"name": "dump_mcp_tools", "version": "1.0"},
        },
        # First response may wait on npx package download; be generous.
        timeout=300.0,
    )
    client.notify("notifications/initialized")

    tools: list[dict] = []
    cursor: str | None = None
    while True:
        params: dict = {"cursor": cursor} if cursor else {}
        result = client.request("tools/list", params)
        tools.extend(result.get("tools", []))
        cursor = result.get("nextCursor")
        if not cursor:
            break
    return tools, init.get("protocolVersion", PROTOCOL_VERSION)


def dump_server(spec: dict, dummy_dir: str) -> dict:
    version = npm_latest_version(spec["npm"])
    print(f"[{spec['id']}] npm latest: {version}; spawning via npx ...")
    client = McpStdioClient(
        ["npx", "-y", f"{spec['npm']}@{version}"],
        env=spec["env"](dummy_dir),
    )
    try:
        tools, protocol = list_all_tools(client)
    finally:
        client.close()
    if not tools:
        raise SystemExit(f"[{spec['id']}] tools/list returned no tools — refusing to write an empty contract")
    tools.sort(key=lambda t: t.get("name", ""))
    print(f"[{spec['id']}] captured {len(tools)} tools")
    return {
        "name": spec["id"],
        "npmPackage": spec["npm"],
        "version": version,
        "protocolVersion": protocol,
        "docs": spec["docs"],
        "toolCount": len(tools),
        "tools": tools,
    }


def main() -> None:
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    with tempfile.TemporaryDirectory() as dummy_dir:
        servers = [dump_server(spec, dummy_dir) for spec in SERVERS]

    artifact = {
        "title": "TronLink MCP tool contracts — static snapshot",
        "description": (
            "Full tool definitions (name, description, inputSchema, annotations) "
            "captured from the published npm MCP servers via the MCP tools/list "
            "endpoint. The running server's tools/list remains the source of "
            "truth; this file is a stamped snapshot for one-fetch consumption."
        ),
        "generated": generated_at,
        "commit": git_short_sha(),
        "generator": "scripts/dump_mcp_tools.py",
        "errorCodes": "https://docs.tronlink.org/reference/error-code-map/",
        "servers": servers,
    }
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(artifact, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    total = sum(s["toolCount"] for s in servers)
    print(f"Wrote {OUT_PATH.relative_to(REPO)} ({total} tools across {len(servers)} servers)")


if __name__ == "__main__":
    main()
