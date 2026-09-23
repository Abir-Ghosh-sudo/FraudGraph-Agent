from __future__ import annotations

import csv
from pathlib import Path
from typing import Any

from backend.app.config import Settings
from backend.app.logging import get_logger

logger = get_logger("documents.dataset")


class HHGOADatasetInspector:
    """
    Inspects dataset files in raw_data_dir dynamically at runtime.
    Does NOT assume schema or column names, and fails gracefully if empty.
    """

    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.raw_dir = settings.raw_data_dir

    def discover_files(self) -> list[Path]:
        if not self.raw_dir.exists():
            return []
        files = [
            f for f in self.raw_dir.iterdir()
            if f.is_file() and not f.name.startswith(".") and f.name != ".gitkeep"
        ]
        return sorted(files)

    def inspect_schema(self) -> dict[str, Any]:
        files = self.discover_files()
        if not files:
            return {
                "dataset_present": False,
                "raw_dir": str(self.raw_dir),
                "files_found": [],
                "schemas": {},
                "message": (
                    f"No dataset files found in {self.raw_dir}. "
                    "Place dataset CSV or parquet files into the raw directory to enable graph loading."
                ),
            }

        schemas: dict[str, Any] = {}
        for f in files:
            suffix = f.suffix.lower()
            if suffix == ".csv":
                try:
                    with open(f, mode="r", encoding="utf-8", errors="replace") as csvfile:
                        reader = csv.reader(csvfile)
                        headers = next(reader, [])
                        sample_row = next(reader, [])
                        schemas[f.name] = {
                            "file_type": "csv",
                            "columns": headers,
                            "column_count": len(headers),
                            "sample_preview": dict(zip(headers, sample_row)) if sample_row else {},
                        }
                except Exception as exc:
                    schemas[f.name] = {"error": str(exc)}
            else:
                schemas[f.name] = {
                    "file_type": suffix.lstrip("."),
                    "size_bytes": f.stat().st_size,
                }

        return {
            "dataset_present": True,
            "raw_dir": str(self.raw_dir),
            "files_found": [f.name for f in files],
            "schemas": schemas,
            "message": f"Discovered {len(files)} files in raw data directory.",
        }
