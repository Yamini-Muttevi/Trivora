import cloudscraper

url = "https://www.orica.com/news-media/2025/successful-completion-of-long-term-us-private-placement"

scraper = cloudscraper.create_scraper(
    browser={"browser": "chrome", "platform": "windows", "mobile": False}
)

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/139.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.orica.com/news-media",
    "Connection": "keep-alive"
}

resp = scraper.get(url, headers=headers, timeout=30)
print(resp.status_code)
print(resp.text[:500])  # show first 500 chars
