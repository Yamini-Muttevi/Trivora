from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import requests

def scrape_with_playwright(url: str):
    """Try scraping with Playwright (bundled Chromium)."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)  # ✅ no executable_path
        page = browser.new_page()
        page.goto(url, timeout=60000)

        html = page.content()
        soup = BeautifulSoup(html, "lxml")

        title = soup.title.string.strip() if soup.title else ""

        browser.close()
        return {"title": title, "html": html}

def scrape_with_requests(url: str):
    """Fallback: scrape with requests + BeautifulSoup (no JS)."""
    resp = requests.get(url, timeout=30, headers={"User-Agent": "Mozilla/5.0"})
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "lxml")
    title = soup.title.string.strip() if soup.title else ""

    return {"title": title, "html": resp.text}

def scrape_url(url: str):
    try:
        return scrape_with_playwright(url)
    except Exception as e1:
        print(f"[WARN] Playwright failed: {e1}")
        try:
            return scrape_with_requests(url)
        except Exception as e2:
            return {"error": f"Both Playwright and requests failed: {e1} | {e2}"}

if __name__ == "__main__":
    result = scrape_url("https://example.com")
    print(result)
