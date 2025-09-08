from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup


def scrape_url(url: str) -> dict:
    """Scrape a URL using Playwright (headless Chromium) and return page info."""
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                user_agent=(
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/139.0.0.0 Safari/537.36"
                )
            )
            page = context.new_page()

            # Go to page and wait until network is idle
            page.goto(url, wait_until="networkidle")

            # Extract HTML
            html = page.content()

            # Parse with BeautifulSoup
            soup = BeautifulSoup(html, "lxml")

            title = soup.title.string.strip() if soup.title else ""
            meta_desc = ""
            desc_tag = soup.find("meta", attrs={"name": "description"})
            if desc_tag and desc_tag.get("content"):
                meta_desc = desc_tag["content"]

            browser.close()

            return {
                "url": url,
                "title": title,
                "description": meta_desc,
                "html": html[:1000]  # first 1000 chars only
            }

    except Exception as e:
        return {"error": f"Scraping failed: {e}"}


if __name__ == "__main__":
    test_url = "https://www.orica.com/news-media/2025/successful-completion-of-long-term-us-private-placement"
    result = scrape_url(test_url)
    print(result)
