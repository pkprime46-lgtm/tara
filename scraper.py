from __future__ import annotations

import re
from dataclasses import asdict, dataclass
from typing import Iterable
from urllib.parse import quote
from urllib.request import Request, urlopen

SITE_BASE_URLS = {
    "swiggy": "https://www.swiggy.com",
    "blinkit": "https://blinkit.com",
    "zepto": "https://www.zepto.com",
}

FALLBACK_CATALOG = {
    "swiggy": [
        {"name": "Amul Taaza Toned Milk 1L", "price": 68, "image": "", "unit": "1 L"},
        {"name": "Aashirvaad Atta", "price": 320, "image": "", "unit": "5 kg"},
        {"name": "Lay's Classic Salted Chips", "price": 20, "image": "", "unit": "52 g"},
    ],
    "blinkit": [
        {"name": "Amul Gold Full Cream Milk", "price": 72, "image": "", "unit": "1 L"},
        {"name": "Aashirvaad Whole Wheat Atta", "price": 329, "image": "", "unit": "5 kg"},
        {"name": "Lay's India's Magic Masala", "price": 20, "image": "", "unit": "52 g"},
    ],
    "zepto": [
        {"name": "Amul Slim n Trim Milk", "price": 70, "image": "", "unit": "1 L"},
        {"name": "Fortune Chakki Fresh Atta", "price": 300, "image": "", "unit": "5 kg"},
        {"name": "Lay's American Style Cream & Onion", "price": 20, "image": "", "unit": "52 g"},
    ],
}


@dataclass(slots=True)
class Product:
    name: str
    price: float | None
    unit: str
    image: str
    source: str
    score: float
    link: str


class PromptInterpreter:
    stopwords = {
        "show",
        "me",
        "find",
        "buy",
        "best",
        "price",
        "prices",
        "for",
        "with",
        "under",
        "around",
        "and",
        "on",
        "in",
        "please",
        "need",
        "want",
        "search",
        "products",
        "product",
        "catalog",
        "catalogue",
    }

    def parse(self, prompt: str) -> str:
        cleaned = re.sub(r"[^a-zA-Z0-9\s]", " ", prompt.lower())
        tokens = [tok for tok in cleaned.split() if tok and tok not in self.stopwords]
        if not tokens:
            return prompt.strip().lower()
        if "milk" in tokens:
            rest = [t for t in tokens if t != "milk"]
            return " ".join(["milk", *rest])
        return " ".join(tokens)


class WebStoreScraper:
    def fetch(self, site: str, query: str) -> list[dict]:
        base = SITE_BASE_URLS[site]
        url = f"{base}/search?query={quote(query)}"

        try:
            req = Request(
                url,
                headers={"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/124.0 Safari/537.36"},
            )
            with urlopen(req, timeout=3.5) as resp:  # nosec B310
                html = resp.read().decode("utf-8", errors="ignore")
            parsed = self._extract_minimal_products(html)
            if parsed:
                return parsed
        except Exception:
            pass

        return FALLBACK_CATALOG[site]

    @staticmethod
    def _extract_minimal_products(html: str) -> list[dict]:
        products: list[dict] = []

        json_matches = re.findall(r'"name"\s*:\s*"([^"]+)"', html)
        for name in json_matches[:10]:
            if len(name) < 4:
                continue
            products.append({"name": name, "price": None, "unit": "", "image": ""})

        return products


class SearchService:
    def __init__(self):
        self.interpreter = PromptInterpreter()
        self.scraper = WebStoreScraper()

    def search(self, prompt: str) -> dict:
        query = self.interpreter.parse(prompt)

        all_products: list[Product] = []
        for source in ("swiggy", "blinkit", "zepto"):
            items = self.scraper.fetch(source, query)
            for item in items:
                score = self._score_similarity(query, item.get("name", ""))
                if score < 0.18:
                    continue
                all_products.append(
                    Product(
                        name=item.get("name", "Unknown product"),
                        price=item.get("price"),
                        unit=item.get("unit", ""),
                        image=item.get("image", ""),
                        source=source,
                        score=round(score, 3),
                        link=f"{SITE_BASE_URLS[source]}/search?query={quote(query)}",
                    )
                )

        all_products.sort(key=lambda p: ((p.price if p.price is not None else 99999), -p.score))
        catalog = [asdict(product) for product in all_products]

        return {
            "prompt": prompt,
            "query": query,
            "total": len(catalog),
            "summary": self._build_summary(catalog),
            "results": catalog,
        }

    def _score_similarity(self, query: str, candidate: str) -> float:
        q_tokens = set(query.lower().split())
        c_tokens = set(re.sub(r"[^a-zA-Z0-9\s]", " ", candidate.lower()).split())
        if not q_tokens or not c_tokens:
            return 0.0
        overlap = len(q_tokens & c_tokens)
        return overlap / len(q_tokens)

    @staticmethod
    def _build_summary(catalog: Iterable[dict]) -> str:
        grouped: dict[str, list[float]] = {"swiggy": [], "blinkit": [], "zepto": []}

        for item in catalog:
            if item["price"] is not None:
                grouped[item["source"]].append(float(item["price"]))

        parts = []
        for source, prices in grouped.items():
            if prices:
                avg_price = sum(prices) / len(prices)
                parts.append(f"{source.title()}: avg ₹{avg_price:.1f}")
            else:
                parts.append(f"{source.title()}: no price data")

        return " | ".join(parts)
