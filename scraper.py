import cloudscraper
from bs4 import BeautifulSoup

def scrape_url(url: str):
    try:
        scraper = cloudscraper.create_scraper(
            browser={"browser": "chrome", "platform": "windows", "mobile": False}
        )
        resp = scraper.get(url, timeout=30)
        resp.raise_for_status()

        soup = BeautifulSoup(resp.text, "lxml")

        # Title
        title = soup.title.string.strip() if soup.title else ""

        # Meta description
        desc_tag = soup.find("meta", attrs={"name": "description"})
        description = desc_tag.get("content", "").strip() if desc_tag else ""

        # Collect body HTML and text
        main_content = soup.find("main") or soup.find("article") or soup.body
        content_html = str(main_content) if main_content else ""
        content_text = main_content.get_text(separator="\n", strip=True) if main_content else ""

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

    except Exception as e:
        return {"error": f"Scraping failed: {type(e).__name__}: {str(e)}"}
