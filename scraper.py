from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import requests
import cloudscraper


def parse_content(html, url):
    """Parse HTML and extract structured content."""
    soup = BeautifulSoup(html, "lxml")

    # Title
    title = soup.title.string.strip() if soup.title else ""

    # Meta description
    desc_tag = soup.find("meta", attrs={"name": "description"})
    description = desc_tag.get("content", "").strip() if desc_tag else ""

    # Main content (prefer <main> or <article>)
    main_content = soup.find("main") or soup.find("article") or soup.body
    content_html = str(main_content) if main_content else ""
    content_text = (
        main_content.get_text(separator="\n", strip=True) if main_content else ""
    )

    # Headings
    headings = [h.get_text(strip=True) for h in soup.find_all(["h1", "h2", "h3"])]

    # Links
    links = [a["href"] for a in soup.find_all("a", href=True)]

    # Images
    images = [img["src"] for img in soup.find_all("img", src=True)]

    return {
        "url": url,
        "title": title,
        "description": description,
        "headings": headings,
        "links": links,
        "images": images,
        "content_html": content_html,
        "content_text": content_text,
    }


def scrape_url(url: str):
    """Scrape a URL with stronger Requests → Playwright → Cloudscraper fallback."""
    e1 = e2 = e3 = None

    # 1. Try Requests with stronger headers
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Referer": "https://www.google.com/",
            "DNT": "1",
            "Upgrade-Insecure-Requests": "1",
        }
        resp = requests.get(url, timeout=30, headers=headers)
        resp.raise_for_status()
        return {"method": "requests", **parse_content(resp.text, url)}
    except Exception as ex2:
        e2 = ex2
        print(f"[WARN] Requests failed: {e2}")

    # 2. Try Playwright (if Chromium is available)
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(url, timeout=60000)
            html = page.content()
            browser.close()
            return {"method": "playwright", **parse_content(html, url)}
    except Exception as ex1:
        e1 = ex1
        print(f"[WARN] Playwright failed: {e1}")

    # 3. Try Cloudscraper
    try:
        scraper = cloudscraper.create_scraper(
            browser={"browser": "chrome", "platform": "windows", "mobile": False}
        )
        resp = scraper.get(url, timeout=30)
        resp.raise_for_status()
        return {"method": "cloudscraper", **parse_content(resp.text, url)}
    except Exception as ex3:
        e3 = ex3
        print(f"[WARN] Cloudscraper failed: {e3}")

    # If all failed → return structured error with details
    return {
        "method": "failed",
        "error": "All scraping methods failed",
        "details": {
            "requests": str(e2),
            "playwright": str(e1),
            "cloudscraper": str(e3),
        },
    }
