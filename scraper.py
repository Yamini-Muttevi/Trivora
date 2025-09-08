from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import requests
import cloudscraper

def parse_content(html, url):
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
        "headings": headings,
        "links": links,
        "images": images,
        "content_html": content_html,
        "content_text": content_text,
    }

def scrape_url(url: str):
    # 1. Try Playwright (best for JS/Cloudflare)
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(url, timeout=60000)
            html = page.content()
            browser.close()
            return {"method": "playwright", **parse_content(html, url)}
    except Exception as e1:
        print(f"[WARN] Playwright failed: {e1}")

    # 2. Try requests
    try:
        resp = requests.get(url, timeout=30, headers={"User-Agent": "Mozilla/5.0"})
        resp.raise_for_status()
        return {"method": "requests", **parse_content(resp.text, url)}
    except Exception as e2:
        print(f"[WARN] Requests failed: {e2}")

    # 3. Try cloudscraper
    try:
        scraper = cloudscraper.create_scraper(
            browser={"browser": "chrome", "platform": "windows", "mobile": False}
        )
        resp = scraper.get(url, timeout=30)
        resp.raise_for_status()
        return {"method": "cloudscraper", **parse_content(resp.text, url)}
    except Exception as e3:
        return {"error": f"All scraping methods failed: {e1} | {e2} | {e3}"}
