from __future__ import annotations

import json
from typing import Any

import httpx
from tenacity import (
    RetryError,
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from backend.app.config import Settings
from backend.app.errors import LLMError, LLMNotConfiguredError, LLMTimeoutError


class OllamaClient:
    """
    HTTP client for local Ollama.

    Sends structured prompts and receives text or JSON responses.
    Raises typed errors instead of fabricating results when unavailable.
    """

    def __init__(
        self,
        settings: Settings,
        http_client: httpx.Client | None = None,
    ) -> None:
        self.settings = settings
        self._external_client = http_client

        if http_client is None:
            self._client = httpx.Client(
                timeout=settings.llm_timeout_seconds,
            )
        else:
            self._client = http_client

    def close(self) -> None:
        if self._external_client is None:
            self._client.close()

    def is_available(self) -> bool:
        try:
            response = self._client.get(
                f"{self.settings.llm_base_url}/api/tags",
                timeout=5.0,
            )
            return response.is_success
        except (httpx.HTTPError, OSError):
            return False

    def generate(
        self,
        prompt: str,
        *,
        system: str | None = None,
        temperature: float | None = None,
        stream: bool = False,
    ) -> str:
        """
        Send a generation request to Ollama and return the response text.

        Never returns fabricated content — raises LLMError if unavailable.
        """
        if not self.settings.llm_configured:
            raise LLMNotConfiguredError(
                "LLM is not configured. Set llm_model and llm_base_url."
            )

        payload: dict[str, Any] = {
            "model": self.settings.llm_model,
            "prompt": prompt,
            "stream": stream,
            "options": {
                "temperature": (
                    temperature
                    if temperature is not None
                    else self.settings.llm_temperature
                ),
            },
        }

        if system:
            payload["system"] = system

        try:
            return self._generate_with_retry(payload)
        except RetryError as exc:
            raise LLMError(
                f"LLM request failed after retries: {exc}"
            ) from exc

    @retry(
        retry=retry_if_exception_type(
            (httpx.ConnectError, httpx.TimeoutException)
        ),
        stop=stop_after_attempt(2),
        wait=wait_exponential(multiplier=1, min=1, max=5),
        reraise=False,
    )
    def _generate_with_retry(self, payload: dict[str, Any]) -> str:
        url = f"{self.settings.llm_base_url}/api/generate"

        try:
            response = self._client.post(
                url,
                json=payload,
                timeout=self.settings.llm_timeout_seconds,
            )
        except httpx.TimeoutException as exc:
            raise LLMTimeoutError(
                f"LLM request timed out after {self.settings.llm_timeout_seconds}s."
            ) from exc
        except httpx.ConnectError as exc:
            raise LLMError(
                f"Cannot connect to Ollama at {self.settings.llm_base_url}."
            ) from exc
        except httpx.HTTPError as exc:
            raise LLMError(f"LLM HTTP error: {exc}") from exc

        if response.is_error:
            raise LLMError(
                f"Ollama returned HTTP {response.status_code}: "
                f"{response.text[:200]}"
            )

        try:
            data = response.json()
        except ValueError as exc:
            raise LLMError(
                f"Invalid JSON from Ollama: {response.text[:200]}"
            ) from exc

        text = data.get("response", "")

        if not isinstance(text, str) or not text.strip():
            raise LLMError("Ollama returned an empty response.")

        return text.strip()

    def generate_json(
        self,
        prompt: str,
        *,
        system: str | None = None,
        temperature: float | None = None,
    ) -> dict[str, Any]:
        """
        Generate and parse a JSON response from Ollama.

        Raises LLMOutputValidationError if the response is not valid JSON.
        """
        from backend.app.errors import LLMOutputValidationError

        raw = self.generate(
            prompt=prompt,
            system=system,
            temperature=temperature,
        )

        # Strip markdown code fences if present
        cleaned = raw.strip()
        if cleaned.startswith("```"):
            lines = cleaned.splitlines()
            inner = []
            in_block = False
            for line in lines:
                if line.startswith("```"):
                    in_block = not in_block
                    continue
                if in_block:
                    inner.append(line)
            cleaned = "\n".join(inner).strip()

        try:
            result = json.loads(cleaned)
        except json.JSONDecodeError as exc:
            raise LLMOutputValidationError(
                f"LLM response is not valid JSON: {exc}",
                detail={"raw_response": raw[:500]},
            ) from exc

        if not isinstance(result, dict):
            raise LLMOutputValidationError(
                "LLM JSON response is not a JSON object.",
                detail={"raw_response": raw[:500]},
            )

        return result
