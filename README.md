# AI Product Catalogue Aggregator

A lightweight Python web app that accepts a natural-language prompt (e.g., "Find best price for Amul milk 1 litre") and aggregates product listings from:

- Swiggy (`www.swiggy.com`)
- Blinkit (`www.blinkit.com`)
- Zepto (`www.zepto.com`)

The UI presents products in a catalogue-style card grid and includes a quick cross-store summary.

## Features

- Prompt-based product search with lightweight AI interpretation.
- Aggregation across exactly three stores: Swiggy, Blinkit, Zepto.
- Catalogue card view sorted by price and relevance score.
- Graceful fallback catalog entries if websites are inaccessible.

## Run locally

Use `python3` (this environment may not have a `python` alias).

```bash
cd /workspace/tara
python3 app.py
```

Then open: `http://localhost:8000`

### Quick health check

In a second terminal, run:

```bash
curl -i http://127.0.0.1:8000/
```

If you get `HTTP/1.0 200 OK`, the app is running.

## API

`POST /api/search`

```json
{
  "prompt": "Find best price for amul milk"
}
```

Returns parsed query + consolidated product list.
