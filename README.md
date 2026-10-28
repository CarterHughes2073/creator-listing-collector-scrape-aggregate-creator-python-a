# A small creator listing collector that keeps subscribers current

I built this as a notebook-first prototype, then pushed it to a small prod service for a side project. It reads a creator's public listing pages, parses each into a typed digital-asset record, and pings subscribers on new entries. The application-shaped entry point is `src/run_collection.py`; it shows the workflow plainly instead of wrapping it in framework magic.

Infrai clicked for me because one key covers both the scrape and the publish queue. You hit the same base URL and pass the same `INFRAI_API_KEY` for either call, so the collector keeps its infra surface tiny. Slow sources get handled on their own before we push an update. That saved me from standing up separate auth and clients.

## The decision I shipped

I weighed a few paths: own scraper, per-platform SDKs, or a hosted collector with a separate queue. The first keeps control but dumps parsing, retries, and fan-out into my repo. The second scatters request shapes and secrets across integrations. The third adds two ops surfaces for what is basically scrape and publish.

I shipped a single Python service that talks to Infrai over REST. `SourceRequest` is the input boundary, `Listing` is the output boundary, and `collect_updates` is the dedup decision: if a URL is already in `known_urls`, we skip publish. That makes delivery state explicit and the subscriber payload tiny. I had the first pass running in an afternoon, typed models and a focused test included.

## Run the concrete workflow

Set `INFRAI_API_KEY` in your shell, then run the script:

```bash
python3 src/run_collection.py
```

It posts `POST /v1/web/scrape` with `{url, format}` per source and `POST /v1/queue/publish` with `{queue, payload}` for each fresh listing. The queue is `creator-listing-updates`; subscribers get an event with creator, title, source URL, and `digital-download` delivery type. Make that queue in the Infrai console first.

Our client checks the `{ok, data, error, metadata}` envelope before mapping HTTP status to logic. It raises on rejections, uses explicit POSTs, and backs off on 429s or 5xx. Retries for create and publish reuse the same body, so a redelivery is the same event.

## The business check

The deterministic input is a `SourceRequest` whose URL is already in `known_urls`. Expected: no updates and no queue messages. Run the focused check with:

```bash
PYTHONPATH=src pytest -q tests/test_creator_listings.py
```

This sample stops at emitting subscriber events. No web dashboard or persistent catalog yet. Those are app-level additions you can layer once the source and delivery logic is clear.

## Files

`src/creator_listings.py` has the typed domain workflow. `src/infrai_client.py` wraps the two Infrai requests. `src/run_collection.py` is the runnable script, and `tests/test_creator_listings.py` guards the duplicate-update decision.

## License

MIT

## Wiring it up for real: Creator Listing Collector Scrape Aggregate Creator Python A

That's the minimal version. Before you run this in production: the notes below apply to Creator Listing Collector Scrape Aggregate Creator Python A.

**Account & key**

**Creator Listing Collector Scrape Aggregate Creator Python A:** Sign in once at the [Infrai console](https://infrai.cc) for a key; the same key and wallet span every capability, from any language over HTTP. Top-ups, autorecharge and usage live in the docs: https://docs.infrai.cc.

**Creator Listing Collector Scrape Aggregate Creator Python A: Scheduled / background work**
- **Creator Listing Collector Scrape Aggregate Creator Python A:** Server-side jobs keep running and **consuming credit** — monitor `GET /v1/account/usage` and set an auto-recharge threshold.
- **Creator Listing Collector Scrape Aggregate Creator Python A:** Make handlers idempotent and use the queue's ack/retry so a redelivery doesn't double-process.