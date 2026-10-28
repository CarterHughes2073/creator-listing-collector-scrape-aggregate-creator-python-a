from creator_listings import SourceRequest, collect_updates


class FakeClient:
    def __init__(self):
        self.published = []

    def scrape(self, url):
        return {"content": f"# New pack from {url}"}

    def publish(self, queue, payload):
        self.published.append((queue, payload))
        return {"message_id": "local-test"}


def test_known_source_is_not_sent_again():
    client = FakeClient()
    requests = [SourceRequest("https://creator.test/pack", "mira")]

    updates = collect_updates(requests, {"https://creator.test/pack"}, client, "updates")

    assert updates == []
    assert client.published == []
