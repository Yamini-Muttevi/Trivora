from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup


def scrape_url(url: str):
    try:
        with sync_playwright() as p:
            # Launch Chromium in headless mode
            browser = p.chromium.launch(headless=True)
            context = browser.new_context()

            page = context.new_page()
            page.goto(url, timeout=60000)

            # Wait until page is fully loaded
            page.wait_for_load_state("networkidle")

            # Extract raw HTML
            html_content = page.content()
            browser.close()

            # Parse with BeautifulSoup
            soup = BeautifulSoup(html_content, "lxml")

            # --- Extract metadata ---
            title = soup.title.string.strip() if soup.title else None

            # Publish date (often in <time> or a span with date class)
            publish_date = None
            time_tag = soup.find("time")
            if time_tag:
                publish_date = time_tag.get_text(strip=True)

            # Tags (if present in meta or page body)
            tags = []
            tag_elements = soup.select(".tags a, .article-tags a, .meta-tags a")
            if tag_elements:
                tags = [t.get_text(strip=True) for t in tag_elements]

            # Article body (main content area)
            article_text = None
            article = soup.find("main") or soup.find("article")
            if article:
                article_text = article.get_text(separator="\n", strip=True)

            return {
                "url": url,
                "title": title,
                "publish_date": publish_date,
                "tags": tags,
                "text": article_text,
                "html": html_content
            }

    except Exception as e:
        return {"error": str(e)}


if __name__ == "__main__":
    url = "https://www.orica.com/news-media/2025/successful-completion-of-long-term-us-private-placement"
    result = scrape_url(url)

    if "error" in result:
        print("❌ Error:", result["error"])
    else:
        print("✅ Title:", result["title"])
        print("📅 Date:", result["publish_date"])
        print("🏷 Tags:", result["tags"])
        print("\n--- Article Preview ---\n")
        print(result["text"][:1000])  # print first 1000 chars of text
