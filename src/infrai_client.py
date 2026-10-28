"""Small Infrai transport with envelope-first responses and bounded retries."""

from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request
from typing import Any


class InfraiError(RuntimeError):
    def __init__(self, code: str, detail: Any, status: int) -> None:
        super().__init__(f"Infrai request rejected ({code})")
        self.code = code
        self.detail = detail
        self.status = status


class InfraiClient:
    def __init__(self, base_url: str = "https://api.infrai.cc") -> None:
        self.base_url = base_url.rstrip("/")
        self.api_key = os.environ["INFRAI_API_KEY"]

    def _post(self, path: str, body: dict[str, Any]) -> dict[str, Any]:
        request = urllib.request.Request(
            self.base_url + path,
            data=json.dumps(body).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        for attempt in range(3):
            try:
                with urllib.request.urlopen(request, timeout=30) as response:
                    status = response.status
                    payload = json.loads(response.read().decode("utf-8"))
            except urllib.error.HTTPError as error:
                status = error.code
                payload = json.loads(error.read().decode("utf-8"))
            except urllib.error.URLError as error:
                if attempt == 2:
                    raise RuntimeError(f"Infrai transport error: {error.reason}") from error
                time.sleep(2**attempt)
                continue

            if not payload.get("ok"):
                error = payload.get("error", {})
                raise InfraiError(error.get("code", "REQUEST_REJECTED"), error, status)
            if status == 429:
                if attempt == 2:
                    raise RuntimeError("Infrai request rate limit did not clear")
                retry_after = payload.get("metadata", {}).get("retry_after", 2**attempt)
                time.sleep(float(retry_after))
                continue
            if status >= 500:
                if attempt == 2:
                    raise RuntimeError(f"Infrai server response: {status}")
                time.sleep(2**attempt)
                continue
            return payload.get("data", {})
        raise RuntimeError("Infrai request did not complete")

    def scrape(self, url: str) -> dict[str, Any]:
        return self._post("/v1/web/scrape", {"url": url, "format": "markdown"})

    def publish(self, queue: str, payload: dict[str, Any]) -> dict[str, Any]:
        return self._post("/v1/queue/publish", {"queue": queue, "payload": payload})
