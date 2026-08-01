#!/usr/bin/env python3
"""Minimal Blockbench MCP (Streamable HTTP) client for EndReborn asset generation.

The Blockbench MCP plugin (v1.6.1) serves a Streamable-HTTP MCP endpoint at
http://localhost:3000/bb-mcp. Each run performs the initialize handshake, then
issues one or more tool calls against the *current* Blockbench project (which
persists in the app across runs, so the artist can watch it build up live).

Usage:
    python bb_mcp.py list                      # list tool names
    python bb_mcp.py schema <tool> [<tool>...]  # print input schemas
    python bb_mcp.py call <tool> '<json-args>'  # single tool call
    python bb_mcp.py batch <file.json>          # [{"name":..,"arguments":..}, ...]
"""
import json
import sys
import urllib.request

URL = "http://localhost:3000/bb-mcp"


class BB:
    def __init__(self, url=URL):
        self.url = url
        self.sid = None
        self._id = 0
        self._initialize()

    def _post(self, payload, extra_headers=None):
        data = json.dumps(payload).encode()
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream",
        }
        if self.sid:
            headers["Mcp-Session-Id"] = self.sid
        if extra_headers:
            headers.update(extra_headers)
        req = urllib.request.Request(self.url, data=data, headers=headers, method="POST")
        with urllib.request.urlopen(req, timeout=60) as resp:
            sid = resp.headers.get("mcp-session-id")
            if sid:
                self.sid = sid
            body = resp.read().decode()
        return self._parse(body)

    @staticmethod
    def _parse(body):
        body = body.strip()
        if not body:
            return None
        # SSE framing: pull the JSON out of the last `data:` line.
        if body.startswith("event:") or "\ndata:" in body or body.startswith("data:"):
            chunks = []
            for line in body.splitlines():
                if line.startswith("data:"):
                    chunks.append(line[5:].strip())
            body = chunks[-1] if chunks else body
        return json.loads(body)

    def _initialize(self):
        self._id += 1
        self._post({
            "jsonrpc": "2.0", "id": self._id, "method": "initialize",
            "params": {
                "protocolVersion": "2025-06-18", "capabilities": {},
                "clientInfo": {"name": "voidweaver-bb", "version": "1.0"},
            },
        })
        # initialized notification (no id, no response body expected)
        try:
            self._post({"jsonrpc": "2.0", "method": "notifications/initialized"})
        except Exception:
            pass

    def rpc(self, method, params=None):
        self._id += 1
        return self._post({"jsonrpc": "2.0", "id": self._id, "method": method,
                           "params": params or {}})

    def list_tools(self):
        return self.rpc("tools/list").get("result", {}).get("tools", [])

    def call(self, name, arguments=None):
        r = self.rpc("tools/call", {"name": name, "arguments": arguments or {}})
        if "error" in r:
            raise RuntimeError(f"{name} error: {r['error']}")
        result = r.get("result", {})
        if result.get("isError"):
            raise RuntimeError(f"{name} tool error: {result}")
        return result

    @staticmethod
    def text(result):
        out = []
        for b in (result or {}).get("content", []):
            if b.get("type") == "text":
                out.append(b["text"])
        return "\n".join(out)


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return
    cmd = sys.argv[1]
    bb = BB()
    if cmd == "list":
        for t in bb.list_tools():
            print(t["name"])
    elif cmd == "schema":
        wanted = set(sys.argv[2:])
        for t in bb.list_tools():
            if not wanted or t["name"] in wanted:
                print("### " + t["name"])
                print(json.dumps(t.get("inputSchema", {}), indent=2))
                print()
    elif cmd == "call":
        args = json.loads(sys.argv[3]) if len(sys.argv) > 3 else {}
        print(bb.text(bb.call(sys.argv[2], args)) or json.dumps(
            bb.call(sys.argv[2], args), indent=2))
    elif cmd == "batch":
        calls = json.load(open(sys.argv[2]))
        for c in calls:
            res = bb.call(c["name"], c.get("arguments", {}))
            print(f"[ok] {c['name']}: {bb.text(res)[:200]}")
    else:
        print("unknown command", cmd)


if __name__ == "__main__":
    main()
