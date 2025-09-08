from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

def scrape_url(url: str):
    try:
        with sync_playwright() as p:
            # Launch with system Chrome
            browser = p.chromium.launch(
                headless=True,
                executable_path="/usr/bin/google-chrome"  # 👈 update path if needed
            )
            page = browser.new_page()
            page.goto(url, timeout=60000)

            # Get page content
            html = page.content()
            soup = BeautifulSoup(html, "lxml")

            # Title
            title = soup.title.string.strip() if soup.title else ""

            browser.close()
            return {"title": title, "html": html}

    except Exception as e:
        return {"error": str(e)}

# Example
if __name__ == "__main__":
    result = scrape_url("https://example.com")
    print(result)
