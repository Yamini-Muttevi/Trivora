from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import requests
import cloudscraper

def scrape_with_playwright(url: str):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)  # ✅ bundled Chromium
        page = browser.new_page()
        page.goto(url, timeout=60000)

        html = page.content()
        soup = BeautifulSoup(html, "lxml")
        title = soup.title.string.strip() if soup.title else ""

        browser.close()
        return {"method": "playwright", "title": title, "html": html}

def scrape_with_requests(url: str):
    resp = requests.get(url, timeout=30, headers={"User-Agent": "Mozilla/5.0"})
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "lxml")
    title = soup.title.string.strip() if soup.title else ""
    return {"method": "requests", "title": title, "html": resp.text}

def scrape_with_cloudscraper(url: str):
    scraper = cloudscraper.create_scraper(browser={"browser": "chrome", "platform": "windows", "mobile": False})
    resp = scraper.get(url, timeout=30)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "lxml")
    title = soup.title.string.strip() if soup.title else ""
    return {"method": "cloudscraper", "title": title, "html": resp.text}

def scrape_url(url: str):
    try:
        return scrape_with_playwright(url)
    except Exception as e1:
        print(f"[WARN] Playwright failed: {e1}")
        try:
            return scrape_with_requests(url)
        except Exception as e2:
            print(f"[WARN] Requests failed: {e2}")
            try:
                return scrape_with_cloudscraper(url)
            except Exception as e3:
                return {"error": f"All scraping methods failed", "details": [str(e1), str(e2), str(e3)]}

if __name__ == "__main__":
    result = scrape_url("https://example.com")
    print(result)
