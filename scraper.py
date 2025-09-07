import cloudscraper
from bs4 import BeautifulSoup
from urllib.parse import urljoin

def scrape_url(url: str):
    """
    Scrape a webpage using CloudScraper and BeautifulSoup.
    
    Returns:
        dict: {
            url,
            title,
            description,
            meta_tags,
            headings,
            links,
            images,
            content_html,
            content_text,
        }
    """
    try:
        # Create a CloudScraper session with a realistic browser
        scraper = cloudscraper.create_scraper(
            browser={"browser": "chrome", "platform": "windows", "mobile": False}
        )
        
        # Optional headers to reduce 403 errors
        headers = {
            "Referer": "https://www.google.com/",
            "Accept-Language": "en-US,en;q=0.9",
        }

        # Fetch the page
        resp = scraper.get(url, headers=headers, timeout=30)
        resp.raise_for_status()  # Raises HTTPError on 4xx/5xx

        soup = BeautifulSoup(resp.text, "lxml")

        # Title
        title = soup.title.string.strip() if soup.title else ""

        # Meta description
        desc_tag = soup.find("meta", attrs={"name": "description"})
        description = desc_tag.get("content", "").strip() if desc_tag else ""

        # All meta tags
        meta_tags = {m.get("name", m.get("property", "")): m.get("content", "")
                     for m in soup.find_all("meta") if m.get("content")}

        # Main content
        main_content = soup.find("main") or soup.find("article") or soup.body
        content_html = str(main_content) if main_content else ""
        content_text = main_content.get_text(separator="\n", strip=True) if main_content else ""

        # Headings
        headings = [h.get_text(strip=True) for h in soup.find_all(["h1", "h2", "h3"])]

        # Links (full URLs)
        links = [urljoin(url, a["href"]) for a in soup.find_all("a", href=True)]

        # Images (full URLs)
        images = [urljoin(url, img["src"]) for img in soup.find_all("img", src=True)]

        return {
            "url": url,
            "title": title,
            "description": description,
            "meta_tags": meta_tags,
            "headings": headings,
            "links": links,
            "images": images,
            "content_html": content_html,
            "content_text": content_text,
        }

    except Exception as e:
        return {"error": f"Scraping failed: {type(e).__name__}: {str(e)}"}
