from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from time import perf_counter
from typing import Any

from backend.app.config import Settings
from backend.tigergraph.client import (
    TigerGraphClient,
    TigerGraphRequestError,
)


class QueryRegistryError(RuntimeError):
    """Raised when a GSQL query cannot be registered or resolved."""


class QueryParameterError(ValueError):
    """Raised when required query parameters are missing or invalid."""


@dataclass(frozen=True)
class QueryDefinition:
    name: str
    file_path: Path
    parameters: tuple[str, ...]
    description: str = ""


@dataclass(frozen=True)
class QueryExecution:
    query_name: str
    rows: list[dict[str, Any]]
    execution_time_ms: float
    parameter_names: tuple[str, ...]


class TigerGraphQueryRunner:
    _query_pattern = re.compile(
        r"""
        CREATE\s+QUERY\s+
        (?P<name>[A-Za-z_][A-Za-z0-9_]*)
        \s*\(
        (?P<parameters>.*?)
        \)
        """,
        re.IGNORECASE | re.DOTALL | re.VERBOSE,
    )

    _parameter_pattern = re.compile(
        r"""
        (?:
            SET|BAG|LIST|FILE|PRINT|SumAccum|SumAccum|AvgAccum|MaxAccum|
            MinAccum|CountAccum|HeapAccum|GroupByAccum|MapAccum
        )?
        \s*
        (?P<type>
            [A-Za-z_][A-Za-z0-9_]*(?:<[^>]+>)?
        )
        \s+
        (?P<name>[A-Za-z_][A-Za-z0-9_]*)
        """,
        re.IGNORECASE | re.VERBOSE,
    )

    def __init__(
        self,
        settings: Settings,
        client: TigerGraphClient | None = None,
    ) -> None:
        self.settings = settings
        self.client = client or TigerGraphClient(settings)
        self._queries: dict[str, QueryDefinition] = {}

    def discover(self) -> list[QueryDefinition]:
        query_dir = self.settings.tigergraph_queries_dir

        if not query_dir.exists():
            raise QueryRegistryError(
                f"TigerGraph query directory does not exist: {query_dir}"
            )

        discovered: dict[str, QueryDefinition] = {}

        for file_path in sorted(query_dir.rglob("*.gsql")):
            definitions = self._parse_file(file_path)

            for definition in definitions:
                if definition.name in discovered:
                    existing = discovered[definition.name]

                    raise QueryRegistryError(
                        "Duplicate TigerGraph query name "
                        f"'{definition.name}' found in "
                        f"{existing.file_path} and {definition.file_path}."
                    )

                discovered[definition.name] = definition

        self._queries = discovered

        return list(discovered.values())

    def register(
        self,
        definition: QueryDefinition,
    ) -> None:
        if not definition.name.strip():
            raise QueryRegistryError(
                "Query name cannot be empty."
            )

        if definition.name in self._queries:
            raise QueryRegistryError(
                f"Query '{definition.name}' is already registered."
            )

        self._queries[definition.name] = definition

    def get(
        self,
        query_name: str,
    ) -> QueryDefinition:
        if not self._queries:
            self.discover()

        definition = self._queries.get(query_name)

        if definition is None:
            raise QueryRegistryError(
                f"TigerGraph query '{query_name}' is not registered."
            )

        return definition

    def list_queries(self) -> list[QueryDefinition]:
        if not self._queries:
            self.discover()

        return sorted(
            self._queries.values(),
            key=lambda item: item.name,
        )

    def execute(
        self,
        query_name: str,
        parameters: dict[str, Any] | None = None,
    ) -> QueryExecution:
        definition = self.get(query_name)

        resolved_parameters = parameters or {}

        self._validate_parameters(
            definition,
            resolved_parameters,
        )

        started = perf_counter()

        try:
            rows = self.client.run_query(
                definition.name,
                parameters=resolved_parameters,
            )
        except TigerGraphRequestError:
            raise
        except Exception as exc:
            raise TigerGraphRequestError(
                f"Failed to execute TigerGraph query "
                f"'{query_name}': {exc}"
            ) from exc

        elapsed_ms = (perf_counter() - started) * 1000

        return QueryExecution(
            query_name=definition.name,
            rows=rows,
            execution_time_ms=elapsed_ms,
            parameter_names=definition.parameters,
        )

    def explain(
        self,
        query_name: str,
    ) -> dict[str, Any]:
        definition = self.get(query_name)

        return {
            "name": definition.name,
            "file": str(definition.file_path),
            "parameters": list(definition.parameters),
            "description": definition.description,
        }

    def _parse_file(
        self,
        file_path: Path,
    ) -> list[QueryDefinition]:
        try:
            content = file_path.read_text(
                encoding="utf-8",
            )
        except OSError as exc:
            raise QueryRegistryError(
                f"Unable to read GSQL file {file_path}: {exc}"
            ) from exc

        definitions: list[QueryDefinition] = []

        for match in self._query_pattern.finditer(content):
            name = match.group("name")
            parameter_block = match.group("parameters")

            parameters = self._parse_parameters(
                parameter_block,
            )

            description = self._extract_description(
                content,
                match.start(),
            )

            definitions.append(
                QueryDefinition(
                    name=name,
                    file_path=file_path,
                    parameters=tuple(parameters),
                    description=description,
                )
            )

        return definitions

    def _parse_parameters(
        self,
        parameter_block: str,
    ) -> list[str]:
        if not parameter_block.strip():
            return []

        parameters: list[str] = []

        for raw_parameter in parameter_block.split(","):
            candidate = raw_parameter.strip()

            if not candidate:
                continue

            match = self._parameter_pattern.search(
                candidate,
            )

            if match is None:
                raise QueryRegistryError(
                    "Unable to parse GSQL query parameter: "
                    f"'{candidate}'."
                )

            parameters.append(
                match.group("name"),
            )

        return parameters

    @staticmethod
    def _extract_description(
        content: str,
        query_position: int,
    ) -> str:
        prefix = content[:query_position]
        lines = prefix.splitlines()

        comments: list[str] = []

        for line in reversed(lines):
            stripped = line.strip()

            if stripped.startswith("//"):
                comments.append(
                    stripped[2:].strip(),
                )
                continue

            if not stripped:
                if comments:
                    break
                continue

            break

        comments.reverse()

        return " ".join(comments).strip()

    @staticmethod
    def _validate_parameters(
        definition: QueryDefinition,
        parameters: dict[str, Any],
    ) -> None:
        expected = set(definition.parameters)
        provided = set(parameters)

        missing = expected - provided

        if missing:
            missing_names = ", ".join(
                sorted(missing),
            )

            raise QueryParameterError(
                f"Query '{definition.name}' is missing "
                f"required parameter(s): {missing_names}."
            )

        unknown = provided - expected

        if unknown:
            unknown_names = ", ".join(
                sorted(unknown),
            )

            raise QueryParameterError(
                f"Query '{definition.name}' received "
                f"unknown parameter(s): {unknown_names}."
            )