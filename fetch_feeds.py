#!/usr/bin/env python3
"""
fetch_feeds.py

Reads `feed_urls.json`, skips URLs listed in `invalid_urls.json`,
downloads each feed and saves it in the `feeds/` directory.
On failure, records the error in `invalid_urls.json` so the URL is
never fetched again.
"""

import json
import os
import re
import sys
import time
from urllib.parse import urlparse

import requests

FEEDS_DIR = "feeds"
FEED_URLS_FILE = "feed_urls.json"
INVALID_URLS_FILE = "invalid_urls.json"

HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; RSS-Downloader/1.0)"}


def url_to_filename(url: str) -> str:
    """Convert a URL into a safe filesystem filename."""
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    parsed = urlparse(url)
    parts = [parsed.netloc] + [p for p in parsed.path.split("/") if p]
    if not parts:
        parts = ["index"]
    base = "_".join(parts)
    base = re.sub(r"[^\w\-.]", "_", base)
    if not base.endswith((".xml", ".rss", ".html", ".opml")):
        base += ".xml"
    return base[:200]


def load_json(path):
    """Return parsed JSON data, or an empty dict/list if the file doesn't exist."""
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {} if path == INVALID_URLS_FILE else []


def save_json(path, data):
    """Write JSON data to a file."""
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")


def main():
    feed_urls = load_json(FEED_URLS_FILE)
    if not feed_urls:
        print(f"No URLs found in {FEED_URLS_FILE}. Exiting.", file=sys.stderr)
        sys.exit(1)

    invalid = load_json(INVALID_URLS_FILE)
    print(f"Loaded {len(invalid)} previously invalid URL(s).")

    
    to_fetch = [url for url in feed_urls if url not in invalid]
    print(f"Fetching {len(to_fetch)} of {len(feed_urls)} URLs ({len(invalid)} skipped).")

    os.makedirs(FEEDS_DIR, exist_ok=True)

    failed_this_run = {}
    success_count = 0

    for idx, url in enumerate(to_fetch, start=1):
        filename = url_to_filename(url)
        filepath = os.path.join(FEEDS_DIR, filename)

        print(f"[{idx:02d}/{len(to_fetch)}] {url}  →  {filepath}")

        try:
            if idx > 1:
                time.sleep(1)  
            resp = requests.get(url, headers=HEADERS, timeout=30)
            resp.raise_for_status()
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(resp.text)
            success_count += 1
        except Exception as exc:
            error_msg = str(exc)
            print(f"    ERROR: {error_msg}", file=sys.stderr)
            failed_this_run[url] = error_msg


    if failed_this_run:
        invalid.update(failed_this_run)
        save_json(INVALID_URLS_FILE, invalid)
        print(f"Recorded {len(failed_this_run)} new invalid URL(s) in {INVALID_URLS_FILE}")

    print(f"\nDone. Success: {success_count}, failures this run: {len(failed_this_run)}")


if __name__ == "__main__":
    main()
