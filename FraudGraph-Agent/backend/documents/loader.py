from __future__ import annotations

from pathlib import Path
from typing import Any

from backend.app.config import Settings
from backend.app.logging import get_logger
from backend.documents.dataset import HHGOADatasetInspector

logger = get_logger("documents.loader")


class DatasetLoader:
    """Prepares and loads inspected dataset files for TigerGraph graph ingestion."""

    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.inspector = HHGOADatasetInspector(settings)

    def load_dataset(self) -> dict[str, Any]:
        inspection = self.inspector.inspect_schema()
        if not inspection["dataset_present"]:
            logger.info("dataset_not_present_skipping_load")
            return {
                "success": False,
                "loaded_files": [],
                "record_count": 0,
                "message": inspection["message"],
            }

        # If files exist, report discovered schemas
        return {
            "success": True,
            "loaded_files": inspection["files_found"],
            "schemas": inspection["schemas"],
            "message": f"Dataset ready for ingestion: {len(inspection['files_found'])} file(s).",
        }
