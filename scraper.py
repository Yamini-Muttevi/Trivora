import cloudscraper
from bs4 import BeautifulSoup

def scrape_url(url: str):
    try:
        scraper = cloudscraper.create_scraper(
            browser={
                "browser": "chrome",
                "platform": "windows",
                "mobile": False
            }
        )
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) " 
                          "AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/139.0.0.0 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9",
        }

        resp = scraper.get(url, headers=headers, timeout=30)
        resp.raise_for_status()

        soup = BeautifulSoup(resp.text, "lxml")
        return soup.title.string if soup.title else "No title found"

    except Exception as e:
        return f"Scraping failed: {e}"

print(scrape_url("https://www.orica.com/news-media/2025/successful-completion-of-long-term-us-private-placement"))
