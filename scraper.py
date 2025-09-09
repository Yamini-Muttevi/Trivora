from bs4 import BeautifulSoup
import requests
import cloudscraper


# ===========================
# HTML Parser
# ===========================
def parse_content(html, url):
    """Parse HTML and extract structured content."""
    soup = BeautifulSoup(html, "lxml")

    # Title
    title = soup.title.string.strip() if soup.title else ""

    # Meta description
    desc_tag = soup.find("meta", attrs={"name": "description"})
    description = desc_tag.get("content", "").strip() if desc_tag else ""

    # Main content
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


# ===========================
# Scraper
# ===========================
def scrape_url(url: str):
    """Scrape a URL with Requests → Browserless → Cloudscraper fallback."""
    e1 = e2 = e3 = None

    # 1. Try Requests with strong headers
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
    except Exception as ex1:
        e1 = ex1
        print(f"[WARN] Requests failed: {e1}")

    # 2. Try Browserless API (requires API key)
    try:
        BROWSERLESS_API_KEY = "2T1LWqT1oodNPi237859cb277598c1cd76d50bf1020d710fc"  # 🔑 replace with your real key
        response = requests.post(
            f"https://chrome.browserless.io/content?token={BROWSERLESS_API_KEY}",
            json={"url": url},
            timeout=60,
        )
        response.raise_for_status()
        html = response.text
        return {"method": "browserless", **parse_content(html, url)}
    except Exception as ex2:
        e2 = ex2
        print(f"[WARN] Browserless failed: {e2}")

    # 3. Try Cloudscraper as last fallback
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
            "requests": str(e1),
            "browserless": str(e2),
            "cloudscraper": str(e3),
        },
    }
