from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import httpx

from backend.app.config import Settings


class TigerGraphError(RuntimeError):
    """Base exception for TigerGraph integration failures."""


class TigerGraphConfigurationError(TigerGraphError):
    """Raised when TigerGraph configuration is incomplete."""


class TigerGraphRequestError(TigerGraphError):
    """Raised when TigerGraph rejects or fails a request."""


@dataclass(frozen=True)
class TigerGraphResponse:
    status_code: int
    data: Any
    elapsed_ms: float


class TigerGraphClient:
    def __init__(
        self,
        settings: Settings,
        http_client: httpx.Client | None = None,
    ) -> None:
        self.settings = settings
        self._external_client = http_client

        if http_client is None:
            self._client = httpx.Client(
                timeout=settings.tigergraph_timeout_seconds,
            )
        else:
            self._client = http_client

    @property
    def base_url(self) -> str:
        host = self.settings.tigergraph_host.rstrip("/")

        if not host:
            raise TigerGraphConfigurationError(
                "TigerGraph host is not configured."
            )

        if host.endswith("/restpp"):
            return host

        return f"{host}/restpp"

    @property
    def graph_name(self) -> str:
        graph_name = self.settings.tigergraph_graph_name.strip()

        if not graph_name:
            raise TigerGraphConfigurationError(
                "TigerGraph graph name is not configured."
            )

        return graph_name

    def close(self) -> None:
        if self._external_client is None:
            self._client.close()

    def _headers(self) -> dict[str, str]:
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

        token = self.settings.tigergraph_api_token.strip()

        if token:
            headers["Authorization"] = f"Bearer {token}"

        return headers

    def _request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json: Any | None = None,
    ) -> TigerGraphResponse:
        url = f"{self.base_url}/{path.lstrip('/')}"

        try:
            response = self._client.request(
                method=method,
                url=url,
                headers=self._headers(),
                params=params,
                json=json,
            )
        except httpx.HTTPError as exc:
            raise TigerGraphRequestError(
                f"TigerGraph request failed: {exc}"
            ) from exc

        elapsed_ms = response.elapsed.total_seconds() * 1000

        try:
            data = response.json()
        except ValueError:
            data = response.text

        if response.is_error:
            detail = self._extract_error(data)

            raise TigerGraphRequestError(
                f"TigerGraph returned HTTP {response.status_code}: {detail}"
            )

        return TigerGraphResponse(
            status_code=response.status_code,
            data=data,
            elapsed_ms=elapsed_ms,
        )

    @staticmethod
    def _extract_error(data: Any) -> str:
        if isinstance(data, dict):
            for key in ("message", "error", "code"):
                value = data.get(key)

                if value:
                    return str(value)

            return str(data)

        if isinstance(data, list):
            return "; ".join(str(item) for item in data)

        return str(data)

    def health_check(self) -> dict[str, Any]:
        response = self._request(
            "GET",
            "/echo",
        )

        return {
            "healthy": response.status_code < 400,
            "status_code": response.status_code,
            "response": response.data,
            "elapsed_ms": response.elapsed_ms,
        }

    def get_vertex(
        self,
        vertex_type: str,
        vertex_id: str,
        *,
        select: str | None = None,
    ) -> dict[str, Any]:
        if not vertex_type.strip():
            raise ValueError("vertex_type cannot be empty.")

        if not vertex_id.strip():
            raise ValueError("vertex_id cannot be empty.")

        params: dict[str, Any] = {
            "graph": self.graph_name,
        }

        if select:
            params["select"] = select

        response = self._request(
            "GET",
            f"/graph/{self.graph_name}/vertices/{vertex_type}/{vertex_id}",
            params=params,
        )

        return self._unwrap_vertex_response(response.data)

    def get_vertices(
        self,
        vertex_type: str,
        *,
        limit: int = 100,
        where: str | None = None,
        select: str | None = None,
    ) -> list[dict[str, Any]]:
        if not vertex_type.strip():
            raise ValueError("vertex_type cannot be empty.")

        if not 1 <= limit <= 10000:
            raise ValueError("limit must be between 1 and 10000.")

        params: dict[str, Any] = {
            "graph": self.graph_name,
            "limit": limit,
        }

        if where:
            params["filter"] = where

        if select:
            params["select"] = select

        response = self._request(
            "GET",
            f"/graph/{self.graph_name}/vertices/{vertex_type}",
            params=params,
        )

        return self._unwrap_vertex_list(response.data)

    def get_edges(
        self,
        source_type: str,
        source_id: str,
        edge_type: str = "",
        *,
        target_type: str = "",
        target_id: str = "",
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        if not source_type.strip():
            raise ValueError("source_type cannot be empty.")

        if not source_id.strip():
            raise ValueError("source_id cannot be empty.")

        if not 1 <= limit <= 10000:
            raise ValueError("limit must be between 1 and 10000.")

        edge_path = edge_type.strip() or "*"

        if target_type:
            edge_path = f"{edge_path}/{target_type}"

        if target_id:
            edge_path = f"{edge_path}/{target_id}"

        response = self._request(
            "GET",
            (
                f"/graph/{self.graph_name}/edges/"
                f"{source_type}/{source_id}/{edge_path}"
            ),
            params={
                "graph": self.graph_name,
                "limit": limit,
            },
        )

        return self._unwrap_edge_list(response.data)

    def run_query(
        self,
        query_name: str,
        *,
        parameters: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        if not query_name.strip():
            raise ValueError("query_name cannot be empty.")

        params: dict[str, Any] = {
            "graph": self.graph_name,
        }

        if parameters:
            params.update(parameters)

        response = self._request(
            "GET",
            f"/query/{self.graph_name}/{query_name}",
            params=params,
        )

        return self._unwrap_query_response(response.data)

    def run_query_raw(
        self,
        query_name: str,
        *,
        parameters: dict[str, Any] | None = None,
    ) -> TigerGraphResponse:
        if not query_name.strip():
            raise ValueError("query_name cannot be empty.")

        params: dict[str, Any] = {
            "graph": self.graph_name,
        }

        if parameters:
            params.update(parameters)

        return self._request(
            "GET",
            f"/query/{self.graph_name}/{query_name}",
            params=params,
        )

    @staticmethod
    def _unwrap_vertex_response(data: Any) -> dict[str, Any]:
        if isinstance(data, dict):
            if "results" in data:
                results = data["results"]

                if isinstance(results, list) and results:
                    first = results[0]

                    if isinstance(first, dict):
                        return first

            if "vertex" in data and isinstance(data["vertex"], dict):
                return data["vertex"]

            return data

        raise TigerGraphRequestError(
            "Unexpected vertex response format from TigerGraph."
        )

    @staticmethod
    def _unwrap_vertex_list(data: Any) -> list[dict[str, Any]]:
        if isinstance(data, list):
            return [
                item for item in data
                if isinstance(item, dict)
            ]

        if isinstance(data, dict):
            results = data.get("results", data.get("vertices", []))

            if isinstance(results, list):
                return [
                    item for item in results
                    if isinstance(item, dict)
                ]

        raise TigerGraphRequestError(
            "Unexpected vertex-list response format from TigerGraph."
        )

    @staticmethod
    def _unwrap_edge_list(data: Any) -> list[dict[str, Any]]:
        if isinstance(data, list):
            return [
                item for item in data
                if isinstance(item, dict)
            ]

        if isinstance(data, dict):
            results = data.get("results", data.get("edges", []))

            if isinstance(results, list):
                return [
                    item for item in results
                    if isinstance(item, dict)
                ]

        raise TigerGraphRequestError(
            "Unexpected edge-list response format from TigerGraph."
        )

    @staticmethod
    def _unwrap_query_response(data: Any) -> list[dict[str, Any]]:
        if isinstance(data, list):
            return [
                item for item in data
                if isinstance(item, dict)
            ]

        if isinstance(data, dict):
            results = data.get("results", [])

            if isinstance(results, list):
                return [
                    item for item in results
                    if isinstance(item, dict)
                ]

            return [data]

        raise TigerGraphRequestError(
            "Unexpected query response format from TigerGraph."
        )