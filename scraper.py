import cloudscraper
from bs4 import BeautifulSoup

def scrape_url(url: str):
    try:
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
        resp.raise_for_status()  # will raise HTTPError on 403/404 etc.

        # Parse with BeautifulSoup
        soup = BeautifulSoup(resp.text, "lxml")
        title = soup.title.string.strip() if soup.title else "No title found"

        print(f"[{resp.status_code}] Success")
        print(f"Title: {title}")
        print(resp.text[:500])  # preview HTML

        return {"status": resp.status_code, "title": title, "html": resp.text}

    except Exception as e:
        print(f"Scraping failed: {e}")
        return {"error": str(e)}

if __name__ == "__main__":
    url = "https://www.orica.com/news-media/2025/successful-completion-of-long-term-us-private-placement"
    result = scrape_url(url)
