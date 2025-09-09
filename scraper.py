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
    content_text = (
        main_content.get_text(separator="\n", strip=True) if main_content else ""
    )
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
    e1 = e2 = e3 = None

    # 1. Requests with headers
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
            "Accept-Language": "en-US,en;q=0.9",
            "Referer": "https://www.google.com/",
        }
        resp = requests.get(url, headers=headers, timeout=30)
        resp.raise_for_status()
        return {"method": "requests", **parse_content(resp.text, url)}
    except Exception as ex1:
        e1 = ex1
        print(f"[WARN] Requests failed: {e1}")

    # 2. ScrapingBee (free tier)
    try:
        SCRAPINGBEE_KEY = "U18KCPMEWGI2FQ6SES5E82OCXW4ET3GZLD7SXIUAB571Y1L6183RCBSPQYKGA49NYXFMG9JXZI5RFATM"  # get from scrapingbee.com
        api_url = f"https://app.scrapingbee.com/api/v1?api_key={SCRAPINGBEE_KEY}&url={url}"
        resp = requests.get(api_url, timeout=60)
        resp.raise_for_status()
        return {"method": "scrapingbee", **parse_content(resp.text, url)}
    except Exception as ex2:
        e2 = ex2
        print(f"[WARN] ScrapingBee failed: {e2}")

    # 3. Cloudscraper fallback
    try:
        scraper = cloudscraper.create_scraper()
        resp = scraper.get(url, timeout=30)
        resp.raise_for_status()
        return {"method": "cloudscraper", **parse_content(resp.text, url)}
    except Exception as ex3:
        e3 = ex3
        print(f"[WARN] Cloudscraper failed: {e3}")

    return {
        "method": "failed",
        "error": "All scraping methods failed",
        "details": {
            "requests": str(e1),
            "scrapingbee": str(e2),
            "cloudscraper": str(e3),
        },
    }
