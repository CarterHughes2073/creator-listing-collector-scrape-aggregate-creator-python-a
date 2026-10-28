from __future__ import annotations

import json

from creator_listings import SourceRequest, collect_updates
from infrai_client import InfraiClient


def main() -> None:
    sources = [
        SourceRequest("https://example.com/creator-a", "creator-a"),
        SourceRequest("https://example.org/creator-b", "creator-b"),
    ]
    client = InfraiClient()
    updates = collect_updates(sources, set(), client, "creator-listing-updates")
    print(json.dumps([item.__dict__ for item in updates], indent=2))


if __name__ == "__main__":
    main()
