# mapper.py
import re
import json
from html import unescape
from collections import Counter

STOPWORDS = {
    "about","above","after","again","against","all","am","an","and","any","are","as","at","be","because","been",
    "before","being","below","between","both","but","by","could","did","do","does","doing","down","during","each",
    "few","for","from","further","had","has","have","having","he","her","here","hers","herself","him","himself",
    "his","how","i","if","in","into","is","it","its","itself","just","me","more","most","my","myself","no","nor",
    "not","of","off","on","once","only","or","other","ought","our","ours","ourselves","out","over","own","same",
    "she","should","so","some","such","than","that","the","their","theirs","them","themselves","then","there",
    "these","they","this","those","through","to","too","under","until","up","very","was","we","were","what","when",
    "where","which","while","who","whom","why","with","would","you","your","yours","yourself","yourselves"
}

def clean_text(text: str) -> str:
    if not text:
        return ""
    text = unescape(text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()

def extract_publish_date(text: str) -> str:
    m = re.search(r"\b(\d{1,2}\s+[A-Z][a-z]+\s+20\d{2})\b", text)
    if m:
        return m.group(1)
    return ""

def extract_contacts(text: str) -> dict:
    contacts = {}
    # Extract Analysts Contact
    m = re.search(r"Analysts Contact\s+(.+?)\s+Mobile\s+([+0-9\s]+)", text, re.S)
    if m:
        contacts["Analysts Contact"] = {"Name": m.group(1).strip(), "Mobile": m.group(2).strip()}
    # Extract Media Contact
    m = re.search(r"Media Contact\s+(.+?)\s+Mobile\s+([+0-9\s]+)", text, re.S)
    if m:
        contacts["Media Contact"] = {"Name": m.group(1).strip(), "Mobile": m.group(2).strip()}
    return contacts

def extract_tags(text: str, top_n: int = 5) -> list:
    tokens = re.findall(r"\b[a-z]{4,}\b", text.lower())
    tokens = [t for t in tokens if t not in STOPWORDS]
    freq = Counter(tokens)
    return [w for w, _ in freq.most_common(top_n)]

def map_scraped_to_news(scraped: dict) -> dict:
    raw_text = scraped.get("body") or scraped.get("content_text") or ""
    raw_text = clean_text(raw_text)

    # Extract Title: usually first line after 'News & Media'
    title_match = re.search(r"News & Media.*?\n(.+?)\n\d{1,2}\s+[A-Z][a-z]+\s+20\d{2}", raw_text, re.S)
    title = title_match.group(1).strip() if title_match else scraped.get("title", "")

    # Extract Publish Date
    publish_date = extract_publish_date(raw_text)

    # Extract Body: everything after the date until "Analysts Contact" or "Media Contact"
    body_match = re.search(rf"{publish_date}(.*?)(Analysts Contact|Media Contact|$)", raw_text, re.S)
    body = body_match.group(1).strip() if body_match else ""

    contacts = extract_contacts(raw_text)

    fields = {
        "Title": title,
        "PublishDate": publish_date,
        "Body": body,
        "Author": scraped.get("author", "Orica"),
        "Image": (scraped.get("images") or [""])[0],
        "Tags": extract_tags(raw_text)
    }

    extras = {
        "Description": scraped.get("description", ""),
        "Contacts": contacts,
        "AllImages": scraped.get("images") or [],
        "RawText": raw_text
    }

    return {"Template": "News", "Fields": fields, "Extras": extras}

def map_content_to_template(scraped: dict, template_name: str = "News") -> dict:
    if template_name.lower() == "news":
        return map_scraped_to_news(scraped)
    else:
        raise ValueError(f"Template '{template_name}' not supported yet.")

# Quick test
if __name__ == "__main__":
    test_scraped = {
        "body": """NEWS & MEDIA
You are here:
Home
News & Media
2025
Print page as PDF
Email to a friend
Successful completion of long-term US private placement
16 Jul 2025
Oversubscribed bond issue extends debt maturity profile and further strengthens balance sheet.
Orica (ASX: ORI) is pleased to announce that it has successfully completed the issuance of USD390 million (equivalent) of fixed rate unsecured notes (‘Notes’) in the US Private Placement (‘USPP’) market.
Strong investor demand resulted in a final order book of USD4 billion, which provided favourable pricing opportunities on the transaction.
Orica’s Managing Director & CEO Sanjeev Gandhi said:
“We are extremely pleased by the overwhelming support from our debt investors, which demonstrates a strong endorsement of Orica’s strategic growth initiatives and our focus on value creation by improving operational performance.”
Orica’s Chief Financial Officer, James Crough added: “Access to term debt at competitive pricing is a fundamental element of Orica’s capital management strategy, and we are extremely pleased to have received this level of support from USPP investors, a key capital market for Orica.
“The proceeds raised will be used to repay USD150 million of notes maturing this calendar year, with the balance applied toward the repayment of existing drawn committed bank facilities. This issuance extends our drawn debt profile to 5.8 years.”
The Notes were issued by wholly owned subsidiary Orica Finance Limited and comprised of USD160 million, CAD100 million, JPY1,000 million tranches maturing in 10 years, and a USD150 million tranche maturing in 12 years.
Analysts Contact
Delphine Cassidy
Chief Communications Officer
Mobile +61 419 163 467
Media Contact
Andrew Valler
Head of Communications
Mobile +61 437 829 211""",
        "images": ["https://www.facebook.com/tr?id=1026614941373478&ev=PageView&noscript=1"],
        "author": "Orica",
        "description": "Oversubscribed bond issue extends debt maturity profile and further strengthens balance sheet."
    }
    mapped = map_content_to_template(test_scraped)
    print(json.dumps(mapped, indent=2, ensure_ascii=False))
