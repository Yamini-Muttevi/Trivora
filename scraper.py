import os
from bs4 import BeautifulSoup
import requests
import cloudscraper

# Optional: Enable Playwright only if supported
USE_PLAYWRIGHT = os.getenv("USE_PLAYWRIGHT", "false").lower() == "true"

# Try importing Playwright if enabled
if USE_PLAYWRIGHT:
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        USE_PLAYWRIGHT = False
        print("[WARN] Playwright not available in this environment.")

def parse_content(html, url):
    """Parse HTML and extract structured content."""
    soup = BeautifulSoup(html, "lxml")

    title = soup.title.string.strip() if soup.title else ""
    desc_tag = soup.find("meta", attrs={"name": "description"})
    description = desc_tag.get("content", "").strip() if desc_tag else ""

    main_content = soup.find("main") or soup.find("article") or soup.body
    content_html = str(main_content) if main_content else ""
    content_text = main_content.get_text(separator="\n", strip=True) if main_content else ""

    headings = [h.get_text(strip=True) for h in soup.find_all(["h1", "h2", "h3"])]
    links = [a["href"] for a in soup.find_all("a", href=True)]
    images = [img["src"] for img in soup.find_all("img", src=True)]

    return {
        "url": url,
        "title": title,
        "description": description,
        "headings_count": len(headings),
        "links_count": len(links),
        "images_count": len(images),
        "headings": headings,
        "links": links,
        "images": images,
        "content_html": content_html,
        "content_text": content_text,
    }

def scrape_url(url: str):
    """Scrape a URL using Playwright → Requests → Cloudscraper fallback."""
    e1 = e2 = e3 = None

    # 1. Try Playwright (if enabled)
    if USE_PLAYWRIGHT:
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                page.goto(url, timeout=60000, wait_until="networkidle")
                page.wait_for_timeout(3000)  # wait for JS to settle
                html = page.content()
                browser.close()
                parsed = parse_content(html, url)
                # Detect bot protection page
                if parsed["title"].lower().startswith("just a moment"):
                    raise Exception("Bot protection page detected")
                return {"method": "playwright", **parsed}
        except Exception as ex1:
            e1 = ex1
            print(f"[WARN] Playwright failed: {e1}")

    # 2. Try Requests
    try:
        resp = requests.get(url, timeout=30, headers={"User-Agent": "Mozilla/5.0"})
        resp.raise_for_status()
        return {"method": "requests", **parse_content(resp.text, url)}
    except Exception as ex2:
        e2 = ex2
        print(f"[WARN] Requests failed: {e2}")

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

    return {
        "method": "failed",
        "error": "All scraping methods failed",
        "details": [str(e1), str(e2), str(e3)],
    }
