#!/usr/bin/env python3
"""
fetch_feeds.py – Download RSS/Atom feeds and save each one as a file
inside a 'feeds' directory.
"""

import os
import re
import sys
import time
import requests
from urllib.parse import urlparse

# ---------------------------------------------------------------------------
# List of feed URLs (the same as in the question)
# ---------------------------------------------------------------------------
FEED_URLS = [
    "https://ir.thomsonreuters.com/rss/news-releases.xml",
    "https://www.reutersagency.com/feed/?best-topics=topNews",
    "https://apnews.com/hub/ap-top-news/rss",
    "https://feeds.bbci.co.uk/news/world/rss.xml",
    "http://feeds.bbci.co.uk/news/rss.xml",
    "http://news.bbc.co.uk/rss/feeds.opml",
    "https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml",
    "https://rss.nytimes.com/services/xml/rss/nyt/World.xml",
    "www.nytimes.com/rss",
    "https://feeds.npr.org/1001/rss.xml",
    "https://feeds.npr.org/1128/rss.xml",
    "https://feeds.npr.org/1017/rss.xml",
    "https://feeds.a.dj.com/rss/RSSWorldNews.xml",
    "www.wsj.com",
    "www.washingtonpost.com",
    "http://rss.cnn.com/rss/edition_world.rss",
    "http://rss.cnn.com/rss/cnn_us.rss",
    "edition.cnn.com/services/rss/",
    "https://www.pbs.org/newshour/feeds/rss/headlines",
    "https://www.pbs.org/newshour/feeds/rss/politics",
    "www.foxnews.com",
    "http://feeds.nbcnews.com/feeds/topstories",
    "https://www.cbsnews.com/latest/rss/main",
    "www.msnbc.com",
    "https://search.cnbc.com/rs/search/combinedcms/view.xml?partnerId=wrss01&id=100003114",
    "www.aljazeera.com",
    "https://www.coindesk.com/arc/outboundfeeds/rss/",
    "https://feeds.feedburner.com/CoinDesk",
    "https://cointelegraph.com/rss-feeds",
    "https://cointelegraph.com/rss",
    "https://decrypt.co/feed",
    "https://news.bitcoin.com/feed/",
    "https://www.reuters.com/finance/cryptocurrencies",
    "https://www.forbes.com/rss/",
]

# ---------------------------------------------------------------------------
# Helper: build a safe filename from a URL
# ---------------------------------------------------------------------------
def url_to_filename(url: str) -> str:
    """
    Convert a URL into a filesystem-safe filename.
    - Strip the scheme (http://, https://)
    - Remove any fragment or query string
    - Replace characters that are illegal on most filesystems
    - Ensure the name ends with .xml (or .html if no extension detected)
    """
    # Ensure the URL has a scheme; if not, default to https
    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    parsed = urlparse(url)

    # Build a base name from the host + path (skip empty parts)
    parts = [parsed.netloc] + [p for p in parsed.path.split("/") if p]
    if parts:
        base = "_".join(parts)
    else:
        base = "index"

    # Remove characters that are not alphanumeric, underscore, hyphen, or dot
    base = re.sub(r"[^\w\-.]", "_", base)

    # If the filename doesn't have a recognised extension, supply one
    if not base.endswith((".xml", ".rss", ".html", ".opml")):
        base += ".xml"

    # Prevent extremely long filenames (filesystem limits)
    if len(base) > 200:
        base = base[:200]

    return base


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    # Create the feeds directory (does nothing if it already exists)
    feeds_dir = "feeds"
    os.makedirs(feeds_dir, exist_ok=True)

    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; RSS-Feed-Downloader/1.0)"
    }

    for i, url in enumerate(FEED_URLS, start=1):
        filename = url_to_filename(url)
        filepath = os.path.join(feeds_dir, filename)

        print(f"[{i:02d}/{len(FEED_URLS)}] {url}  ->  {filepath}")

        try:
            # Some servers require a short delay between requests
            if i > 1:
                time.sleep(1)

            resp = requests.get(url, headers=headers, timeout=30)
            resp.raise_for_status()

            # Write the raw content as-is (the feed itself)
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(resp.text)

        except requests.exceptions.RequestException as exc:
            print(f"    ERROR: {exc}", file=sys.stderr)
            # Write a minimal error file so the workflow still sees output
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(f"<!-- Error fetching {url}: {exc} -->\n")
        except OSError as exc:
            print(f"    FILE ERROR: {exc}", file=sys.stderr)


if __name__ == "__main__":
    main()
