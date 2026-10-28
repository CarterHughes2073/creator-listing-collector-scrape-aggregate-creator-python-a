from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol


@dataclass(frozen=True)
class SourceRequest:
    url: str
    creator: str


@dataclass(frozen=True)
class Listing:
    creator: str
    title: str
    source_url: str
    delivery: str


class SourceClient(Protocol):
    def scrape(self, url: str) -> dict[str, Any]:
        raise NotImplementedError

    def publish(self, queue: str, payload: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError


def _listing(request: SourceRequest, scraped: dict[str, Any]) -> Listing:
    text = str(scraped.get("content", scraped.get("markdown", ""))).strip()
    title = text.splitlines()[0].lstrip("# ").strip() or request.url
    return Listing(request.creator, title, request.url, "digital-download")


def collect_updates(
    requests: list[SourceRequest], known_urls: set[str], client: SourceClient, queue: str
) -> list[Listing]:
    """Scrape each source and queue only unseen listings for subscriber updates."""
    updates: list[Listing] = []
    for request in requests:
        listing = _listing(request, client.scrape(request.url))
        if listing.source_url in known_urls:
            continue
        client.publish(queue, {"event": "listing-added", "listing": listing.__dict__})
        updates.append(listing)
    return updates
