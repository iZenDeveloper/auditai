#!/usr/bin/env python3
"""Bước 1 — Quét GitHub tìm repo RAG/chatbot (langchain, rag, vietnam, zalo...).

Usage:
  export GITHUB_TOKEN=ghp_...   # optional but recommended
  python scripts/gtm/scan_github.py --out docs/gtm/out/scan_results.jsonl
"""

from __future__ import annotations

import argparse
import json
import os
import ssl
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

DEFAULT_KEYWORDS = [
    "langchain rag",
    "rag chatbot",
    "retrieval augmented generation",
    "vietnam chatbot",
    "vietnamese rag",
    "vietnamese langchain",
    "zalo bot",
    "zalo chatbot",
    "chatbot tuyển sinh",
    "topic:rag language:Python",
]

VN_HINTS = (
    "vietnam",
    "vietnamese",
    "việt",
    "viet",
    "zalo",
    "hanoi",
    "saigon",
    "hcm",
    "fpt",
    "vnu",
    "uit",
    "bkhn",
    "tiếng việt",
    "tieng viet",
)


@dataclass
class Hit:
    full_name: str
    html_url: str
    description: str
    stars: int
    language: str | None
    license: str | None
    pushed_at: str
    open_issues: int
    archived: bool
    score: int
    matched_query: str


def _headers() -> dict[str, str]:
    h = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "auditai-gtm-scan",
    }
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if token:
        h["Authorization"] = f"Bearer {token}"
    return h


def _get_json(url: str) -> dict[str, Any]:
    ctx = ssl.create_default_context()
    req = urllib.request.Request(url, headers=_headers())
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=45) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        body = e.read().decode(errors="replace")[:300]
        raise RuntimeError(f"HTTP {e.code}: {body}") from e
    except ssl.SSLError:
        # macOS python.org builds sometimes lack certs — fall back to unverified for scan only
        ctx = ssl._create_unverified_context()  # noqa: S323
        with urllib.request.urlopen(req, context=ctx, timeout=45) as resp:
            return json.loads(resp.read().decode())


def search_repos(query: str, per_page: int = 20) -> list[dict[str, Any]]:
    q = f"{query} is:public archived:false"
    params = urllib.parse.urlencode(
        {"q": q, "sort": "updated", "order": "desc", "per_page": str(per_page)}
    )
    url = f"https://api.github.com/search/repositories?{params}"
    data = _get_json(url)
    if "message" in data and "items" not in data:
        raise RuntimeError(data["message"])
    return list(data.get("items") or [])


def score_item(item: dict[str, Any], query: str) -> int:
    s = 0
    blob = f"{item.get('full_name','')} {item.get('description') or ''}".lower()
    for h in VN_HINTS:
        if h in blob:
            s += 40
            break
    for k in ("rag", "langchain", "chatbot", "llm", "retrieval"):
        if k in blob:
            s += 6
    stars = int(item.get("stargazers_count") or 0)
    if 1 <= stars <= 50:
        s += 25  # student / indie sweet spot
    elif 51 <= stars <= 400:
        s += 15
    elif stars > 2000:
        s -= 10  # harder to land PRs
    if item.get("language") in ("Python", "TypeScript", "JavaScript"):
        s += 8
    if not item.get("fork"):
        s += 10
    if item.get("open_issues_count", 0) > 0:
        s += 3
    if "vietnam" in query.lower() or "zalo" in query.lower() or "việt" in query.lower():
        s += 5
    return s


def to_hit(item: dict[str, Any], query: str) -> Hit:
    lic = item.get("license") or {}
    return Hit(
        full_name=item["full_name"],
        html_url=item["html_url"],
        description=(item.get("description") or "")[:300],
        stars=int(item.get("stargazers_count") or 0),
        language=item.get("language"),
        license=lic.get("spdx_id") if isinstance(lic, dict) else None,
        pushed_at=(item.get("pushed_at") or "")[:10],
        open_issues=int(item.get("open_issues_count") or 0),
        archived=bool(item.get("archived")),
        score=score_item(item, query),
        matched_query=query,
    )


def main() -> int:
    p = argparse.ArgumentParser(description="Scan GitHub for RAG/chatbot growth targets")
    p.add_argument(
        "--keywords",
        default=",".join(DEFAULT_KEYWORDS),
        help="Comma-separated search queries",
    )
    p.add_argument("--min-stars", type=int, default=1)
    p.add_argument("--max-stars", type=int, default=2000)
    p.add_argument("--per-query", type=int, default=15)
    p.add_argument("--sleep", type=float, default=2.0, help="Seconds between API calls")
    p.add_argument("--out", type=Path, default=Path("docs/gtm/out/scan_results.jsonl"))
    p.add_argument("--top", type=int, default=40)
    p.add_argument("--print-markdown", action="store_true")
    args = p.parse_args()

    queries = [q.strip() for q in args.keywords.split(",") if q.strip()]
    by_name: dict[str, Hit] = {}

    print(f"Queries: {len(queries)} | token={'yes' if os.environ.get('GITHUB_TOKEN') or os.environ.get('GH_TOKEN') else 'no'}")
    for i, q in enumerate(queries, 1):
        print(f"[{i}/{len(queries)}] search: {q!r}")
        try:
            items = search_repos(q, per_page=args.per_query)
        except Exception as e:
            print(f"  ! skip: {e}", file=sys.stderr)
            time.sleep(args.sleep)
            continue
        for it in items:
            stars = int(it.get("stargazers_count") or 0)
            if stars < args.min_stars or stars > args.max_stars:
                continue
            if it.get("archived"):
                continue
            hit = to_hit(it, q)
            prev = by_name.get(hit.full_name)
            if prev is None or hit.score > prev.score:
                by_name[hit.full_name] = hit
        time.sleep(args.sleep)

    ranked = sorted(by_name.values(), key=lambda h: (-h.score, -h.stars))
    top = ranked[: args.top]

    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", encoding="utf-8") as f:
        meta = {
            "_meta": True,
            "scanned_at": datetime.now(timezone.utc).isoformat(),
            "queries": queries,
            "total_unique": len(by_name),
        }
        f.write(json.dumps(meta, ensure_ascii=False) + "\n")
        for h in ranked:
            f.write(json.dumps(asdict(h), ensure_ascii=False) + "\n")

    print(f"\nUnique repos: {len(by_name)} → wrote {args.out}")
    print(f"\nTop {len(top)}:")
    print(f"{'score':>5} {'★':>5} {'name':<42} {'lang':<10} pushed")
    for h in top:
        print(
            f"{h.score:5d} {h.stars:5d} {h.full_name:<42} {str(h.language or '-'):<10} {h.pushed_at}"
        )
        if h.description:
            print(f"      {h.description[:100]}")

    if args.print_markdown:
        print("\n## Markdown table\n")
        print("| Score | Stars | Repo | Lang | Pushed |")
        print("|------:|------:|------|------|--------|")
        for h in top:
            print(
                f"| {h.score} | {h.stars} | [{h.full_name}]({h.html_url}) | {h.language or '-'} | {h.pushed_at} |"
            )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
