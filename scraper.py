import os
from pathlib import Path
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

def find_chrome_path():
    """Try to find Chrome executable on Windows."""
    possible_paths = [
        Path("C:/Program Files/Google/Chrome/Application/chrome.exe"),
        Path("C:/Program Files (x86)/Google/Chrome/Application/chrome.exe"),
        Path(os.environ.get("LOCALAPPDATA", "")) / "Google/Chrome/Application/chrome.exe",
    ]
    for path in possible_paths:
        if path.exists():
            return str(path)
    raise FileNotFoundError("Google Chrome executable not found. Please install Chrome or update path.")

def scrape_url(url: str):
    try:
        chrome_path = find_chrome_path()
        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=True,
                executable_path=chrome_path
            )
            page = browser.new_page()
            page.goto(url, timeout=60000)

            html = page.content()
            soup = BeautifulSoup(html, "lxml")

            title = soup.title.string.strip() if soup.title else ""

            browser.close()
            return {"title": title, "html": html}

    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    print(scrape_url("https://example.com"))
