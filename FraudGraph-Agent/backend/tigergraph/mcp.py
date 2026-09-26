"""TigerGraph MCP client.

Runs the ``tigergraph-mcp`` server as a subprocess and speaks JSON-RPC over
stdio, so the rest of the backend can reach TigerGraph through the MCP tool
surface instead of re-implementing connection and authentication logic.

Two deliberate choices:

* **No new dependencies.** The MCP SDK is not required. The stdio transport is
  newline-delimited JSON-RPC, which the standard library handles fine, and the
  ``tigergraph-mcp`` CLI may live in a different interpreter than this venv.
* **Single-sourced configuration.** The backend reads ``TIGERGRAPH_*`` from
  ``Settings``; the MCP server reads ``TG_*`` in its own namespace. The mapping
  is done here when building the subprocess environment, so credentials live in
  exactly one place.

Nothing here fabricates graph data. If the server or the instance is
unreachable, the failure is surfaced to the caller.
"""

from __future__ import annotations

import json
import os
import subprocess
from dataclasses import dataclass
from typing import Any

from backend.app.config import Settings
from backend.app.logging import get_logger
from backend.tigergraph.client import (
    TigerGraphClient,
    TigerGraphConfigurationError,
)

logger = get_logger(__name__)

# MCP protocol version negotiated during initialize.
_PROTOCOL_VERSION = "2025-06-18"

# Tools this backend is allowed to invoke. The full tigergraph-mcp surface is
# 69 tools (~29k tokens); the graph investigation only needs read access.
_DEFAULT_TOOLS = (
    "read-only",
)


class TigerGraphMCPError(RuntimeError):
    """Raised when the MCP server cannot be reached or returns an error."""


@dataclass(frozen=True)
class MCPResult:
    """Structured result of an MCP tool call."""

    success: bool
    operation: str
    summary: str = ""
    data: Any = None
    error: str = ""
    suggestions: list[str] | None = None


def build_mcp_env(settings: Settings) -> dict[str, str]:
    """Map the backend's TIGERGRAPH_* settings onto the MCP TG_* namespace.

    Keeping this translation in one place means .env only has to carry the
    TIGERGRAPH_* names the Settings model actually reads.
    """
    env = dict(os.environ)

    host = settings.tigergraph_host.strip()
    if host:
        env["TG_HOST"] = host

    graph_name = settings.tigergraph_graph_name.strip()
    if graph_name:
        env["TG_GRAPHNAME"] = graph_name

    username = settings.tigergraph_username.strip()
    if username:
        env["TG_USERNAME"] = username

    password = settings.tigergraph_password
    if password:
        env["TG_PASSWORD"] = password

    token = settings.tigergraph_api_token.strip()
    if token:
        env["TG_API_TOKEN"] = token
        # A token supersedes user/password for the MCP server.
        env.pop("TG_USERNAME", None)
        env.pop("TG_PASSWORD", None)

    if getattr(settings, "tigergraph_secret", ""):
        env["TG_SECRET"] = settings.tigergraph_secret

    return env


class TigerGraphMCPClient:
    """Thin JSON-RPC-over-stdio client for the tigergraph-mcp server."""

    def __init__(
        self,
        settings: Settings,
        *,
        command: str | None = None,
        timeout_seconds: float | None = None,
    ) -> None:
        self.settings = settings
        self.command = command or os.environ.get(
            "TIGERGRAPH_MCP_COMMAND", "tigergraph-mcp"
        )
        self.timeout_seconds = (
            timeout_seconds or settings.tigergraph_mcp_timeout_seconds
        )
        self._proc: subprocess.Popen[str] | None = None
        self._next_id = 0

    # ------------------------------------------------------------------
    # Configuration
    # ------------------------------------------------------------------
    def is_enabled(self) -> bool:
        if not self.settings.tigergraph_mcp_enabled:
            return False
        try:
            TigerGraphClient(self.settings).graph_name
        except TigerGraphConfigurationError:
            return False
        return True

    # ------------------------------------------------------------------
    # Process lifecycle
    # ------------------------------------------------------------------
    def _start(self) -> subprocess.Popen[str]:
        if self._proc is not None and self._proc.poll() is None:
            return self._proc

        env = build_mcp_env(self.settings)

        try:
            self._proc = subprocess.Popen(
                [self.command],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=env,
                text=True,
                encoding="utf-8",
                bufsize=1,
            )
        except FileNotFoundError as exc:
            raise TigerGraphMCPError(
                f"The '{self.command}' executable was not found. Install "
                "tigergraph-mcp and ensure it is on PATH, or set "
                "TIGERGRAPH_MCP_COMMAND to its full path."
            ) from exc

        return self._proc

    def close(self) -> None:
        proc = self._proc
        self._proc = None
        if proc is None or proc.poll() is not None:
            return
        try:
            if proc.stdin:
                proc.stdin.close()
            proc.terminate()
            proc.wait(timeout=5)
        except Exception:  # noqa: BLE001
            proc.kill()

    def __enter__(self) -> TigerGraphMCPClient:
        return self

    def __exit__(self, *exc_info: object) -> None:
        self.close()

    # ------------------------------------------------------------------
    # JSON-RPC plumbing
    # ------------------------------------------------------------------
    def _send(self, payload: dict[str, Any]) -> dict[str, Any]:
        proc = self._start()

        if proc.stdin is None or proc.stdout is None:
            raise TigerGraphMCPError("MCP subprocess has no stdio pipes.")

        self._next_id += 1
        payload["id"] = self._next_id
        payload.setdefault("jsonrpc", "2.0")

        proc.stdin.write(json.dumps(payload) + "\n")
        proc.stdin.flush()

        while True:
            line = proc.stdout.readline()
            if not line:
                stderr = ""
                if proc.stderr is not None:
                    try:
                        proc.stderr.flush()
                    except Exception:  # noqa: BLE001
                        pass
                raise TigerGraphMCPError(
                    "MCP server closed the connection"
                    + (f". stderr: {stderr}" if stderr else ".")
                )

            line = line.strip()
            if not line:
                continue

            try:
                message = json.loads(line)
            except json.JSONDecodeError:
                # Non-JRPC chatter; ignore it rather than failing the call.
                continue

            if message.get("id") == payload["id"]:
                return message

    def initialize(self) -> dict[str, Any]:
        """Perform the MCP initialize handshake."""
        response = self._send(
            {
                "method": "initialize",
                "params": {
                    "protocolVersion": _PROTOCOL_VERSION,
                    "capabilities": {},
                    "clientInfo": {"name": "fraudgraph-backend", "version": "1"},
                },
            }
        )

        if "error" in response:
            raise TigerGraphMCPError(
                f"MCP initialize failed: {response['error']}"
            )

        return response.get("result", {})

    def call_tool(
        self,
        tool_name: str,
        arguments: dict[str, Any] | None = None,
    ) -> MCPResult:
        """Invoke a single MCP tool and normalise its structured response."""
        self.initialize()

        response = self._send(
            {
                "method": "tools/call",
                "params": {
                    "name": tool_name,
                    "arguments": arguments or {},
                },
            }
        )

        if "error" in response:
            error = response["error"]
            message = (
                error.get("message")
                if isinstance(error, dict)
                else str(error)
            )
            return MCPResult(
                success=False,
                operation=tool_name,
                error=message or "MCP call failed",
            )

        result = response.get("result", {})

        # The server reports tool-level failures inside the result payload.
        if result.get("isError"):
            return MCPResult(
                success=False,
                operation=tool_name,
                error=_first_text(result) or "MCP tool reported an error",
            )

        payload = _first_json_object(result)

        if payload is not None:
            return MCPResult(
                success=bool(payload.get("success", True)),
                operation=str(payload.get("operation", tool_name)),
                summary=str(payload.get("summary", "")),
                data=payload.get("data"),
                error=str(payload.get("error", "")),
                suggestions=payload.get("suggestions"),
            )

        return MCPResult(
            success=True,
            operation=tool_name,
            summary=_first_text(result),
        )

    # ------------------------------------------------------------------
    # Convenience wrappers
    # ------------------------------------------------------------------
    def health(self) -> MCPResult:
        """Report whether the MCP server can reach TigerGraph."""
        return self.call_tool("tigergraph__list_connections", {})

    def vertex_count(self) -> MCPResult:
        return self.call_tool("tigergraph__get_vertex_count", {})

    def edge_count(self) -> MCPResult:
        return self.call_tool("tigergraph__get_edge_count", {})

    def graph_schema(self) -> MCPResult:
        return self.call_tool("tigergraph__get_graph_schema", {})

    def list_graphs(self) -> MCPResult:
        return self.call_tool("tigergraph__list_graphs", {})

    def get_node_edges(self, node_id: str) -> MCPResult:
        return self.call_tool("tigergraph__get_node_edges", {"node_id": node_id})


# ----------------------------------------------------------------------
# Response helpers
# ----------------------------------------------------------------------


def _content_items(result: dict[str, Any]) -> list[Any]:
    content = result.get("content")
    return content if isinstance(content, list) else []


def _first_text(result: dict[str, Any]) -> str:
    for item in _content_items(result):
        if isinstance(item, dict) and isinstance(item.get("text"), str):
            return item["text"]
    return ""


def _first_json_object(result: dict[str, Any]) -> dict[str, Any] | None:
    """Extract the tool's structured JSON payload, if it returned one.

    The MCP server often wraps the payload in a ```json fence, so fences are
    stripped before parsing. Without this, a tool-level ``"success": false``
    would be missed and the call would be reported as successful.
    """
    for item in _content_items(result):
        if not isinstance(item, dict):
            continue
        text = item.get("text")
        if not isinstance(text, str):
            continue
        for candidate in _json_candidates(text):
            try:
                parsed = json.loads(candidate)
            except json.JSONDecodeError:
                continue
            if isinstance(parsed, dict):
                return parsed
    return None


def _json_candidates(text: str) -> list[str]:
    """Return the raw text plus any fenced blocks it contains."""
    candidates = [text.strip()]

    for marker in ("```json", "```"):
        start = text.find(marker)
        if start == -1:
            continue
        start += len(marker)
        end = text.find("```", start)
        if end == -1:
            continue
        candidates.append(text[start:end].strip())

    return [c for c in candidates if c]


__all__ = [
    "MCPResult",
    "TigerGraphMCPClient",
    "TigerGraphMCPError",
    "build_mcp_env",
]
