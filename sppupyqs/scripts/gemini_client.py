from __future__ import annotations

import json
import time
from typing import Any

from google import genai


class GeminiExtractionError(Exception):
    pass


class GeminiMetadataClient:
    def __init__(
        self,
        api_keys: list[str],
        model_name: str,
        system_prompt: str,
        response_schema: dict[str, Any],
        retries_per_key: int,
        retry_delay_seconds: float,
    ) -> None:
        if not api_keys:
            raise ValueError("At least one Gemini API key is required.")

        self.api_keys = api_keys
        self.model_name = model_name
        self.system_prompt = system_prompt
        self.response_schema = response_schema
        self.retries_per_key = retries_per_key
        self.retry_delay_seconds = retry_delay_seconds

    def extract_metadata(
        self,
        *,
        branch: str,
        semester: str,
        subject_name: str,
        subject_slug: str,
        pdf_url: str,
        extracted_text: str,
    ) -> dict[str, Any]:
        user_prompt = (
            "Parse this university exam paper into structured metadata and questions.\n\n"
            f"Branch slug: {branch}\n"
            f"Semester slug: {semester}\n"
            f"Subject slug: {subject_slug}\n"
            f"Subject name: {subject_name}\n"
            f"PDF URL: {pdf_url}\n\n"
            "Raw PDF text follows:\n"
            f"{extracted_text}"
        )

        failures: list[str] = []

        for key_index, api_key in enumerate(self.api_keys, start=1):
            client = genai.Client(api_key=api_key)

            for attempt in range(1, self.retries_per_key + 1):
                try:
                    response = client.models.generate_content(
                        model=self.model_name,
                        contents=user_prompt,
                        config={
                            "system_instruction": self.system_prompt,
                            "response_mime_type": "application/json",
                            "response_schema": self.response_schema,
                        },
                    )
                    return self._parse_response(response.text)
                except Exception as error:  # pragma: no cover
                    failures.append(
                        f"key={key_index} attempt={attempt} error={type(error).__name__}: {error}"
                    )
                    if attempt < self.retries_per_key:
                        time.sleep(self.retry_delay_seconds * attempt)

        raise GeminiExtractionError("; ".join(failures))

    @staticmethod
    def _parse_response(response_text: str) -> dict[str, Any]:
        if not response_text or not response_text.strip():
            raise GeminiExtractionError("Gemini returned an empty response.")

        try:
            return json.loads(response_text)
        except json.JSONDecodeError as error:
            raise GeminiExtractionError("Gemini returned invalid JSON.") from error
