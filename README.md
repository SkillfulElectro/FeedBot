# 🤖 FeedBot

FeedBot is a lightweight Python tool that periodically downloads RSS/Atom feeds from a configurable list of URLs and stores them as individual files inside a `feeds/` directory. A GitHub Actions workflow runs the script on a schedule and commits any updated feed files back to the repository, making it an easy-to-use, self-updating feed archive.

---

## 📂 Directory structure

```
.
├── feeds/                 # Output directory – one file per feed
├── feed_urls.json         # List of feed URLs to fetch
├── invalid_urls.json      # Auto-generated list of broken/blocked URLs
├── fetch_feeds.py         # Main Python script
└── .github/workflows/feeds.yml   # CI/CD workflow definition
```

---

## 🚀 Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/SkillfulElectro/FeedBot.git
   cd feedbot
   ```

2. **Install Python dependencies**
   ```bash
   pip install requests
   ```
   (Only `requests` is needed. The script uses standard library modules otherwise.)

3. **Edit the feed list (optional)**  
   Modify `feed_urls.json` to include the feeds you care about.  
   The file is a simple JSON array of URL strings.

---

## 🏃 Usage

### Manual run

```bash
python fetch_feeds.py
```

The script will:
- Read `feed_urls.json` and `invalid_urls.json` (if it exists).
- Skip any URLs that have previously failed.
- Download each feed and save it as `feeds/<safe_filename>.xml`.
- If a URL fails, record the error in `invalid_urls.json` so it is never fetched again.

### Automated execution (GitHub Actions)

The included workflow (`.github/workflows/feeds.yml`) runs every 6 hours.  
You can also trigger it manually from the **Actions** tab → **“Download RSS Feeds”** → **Run workflow**.

On each successful run, new or updated feed files are automatically committed to the repository.

---

## ⚙️ Configuration

### `feed_urls.json`
A JSON array of feed URLs.  
*Example:*
```json
[
  "https://feeds.bbci.co.uk/news/rss.xml",
  "https://rss.nytimes.com/services/xml/rss/nyt/World.xml"
]
```

### `invalid_urls.json`
Automatically created and maintained by the script. It maps failing URLs to the error that occurred.  
*Example:*
```json
{
  "https://example.com/broken-feed": "404 Client Error: Not Found"
}
```
URLs in this file are **permanently skipped** until you manually remove them.

---

## 🧠 How it works

1. The script loads the two JSON files.
2. It determines which URLs are new or previously successful (i.e., not in `invalid_urls.json`).
3. For each such URL, it performs an HTTP GET with a polite delay and writes the raw feed content into `feeds/`.
4. Any HTTP or connection error is caught, and the URL + error message is added to `invalid_urls.json`.
5. The GitHub Actions workflow commits all changes (`feeds/` and `invalid_urls.json`) back to the repository.

The approach ensures that:
- You always have a recent copy of each working feed.
- Broken feeds do not pollute the output directory and are not retried indefinitely.
- Everything is version-controlled and visible in the repository history.

---

## 🤝 Contributing

Pull requests are welcome! If you want to add a new feed or improve the script, feel free to open an issue or a PR.

---

## 📄 License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.
