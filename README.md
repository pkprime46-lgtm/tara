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
- Cloud-ready runtime (`PORT`/`HOST`) + health check endpoint (`/healthz`).

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
curl -i http://127.0.0.1:8000/healthz
```

If you get `HTTP/1.0 200 OK`, the app is running.

## Deploy as a cloud app (easy)

I can't directly press deploy buttons in your cloud account from this environment, but I made this repo cloud-ready and added provider config files (`render.yaml`, `railway.json`) so you can deploy in a few clicks.

This repo includes a `Dockerfile`, so you can deploy on Render/Railway/Fly.io/any container host.

### Option A: Render (using `render.yaml`)

1. Push this repo to GitHub.
2. In Render, click **New +** → **Blueprint**.
3. Select your repo (Render reads `render.yaml`).
4. Click **Apply** and wait for deploy.

Render will expose a public URL like `https://your-app.onrender.com`.

### Option B: Railway

1. Create a new Railway project from your GitHub repo.
2. Railway reads `railway.json` and the `Dockerfile`.
3. Deploy.
4. Open generated domain.

### Option C: Run container yourself

```bash
docker build -t product-catalogue-app .
docker run --rm -p 8000:8000 -e PORT=8000 product-catalogue-app
```

Then open `http://localhost:8000`.

## API

`POST /api/search`

```json
{
  "prompt": "Find best price for amul milk"
}
```

Returns parsed query + consolidated product list.
