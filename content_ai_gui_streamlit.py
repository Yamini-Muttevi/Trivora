import asyncio
import json
import streamlit as st
from scraper import scrape_url
from mapper import map_content_to_template

# -----------------------------
# Bootstrap: Ensure Playwright Chromium
# -----------------------------
def ensure_playwright_browsers():
    """Install Chromium if missing (first-time cloud run)."""
    try:
        from playwright._impl.cli.install import install
        asyncio.run(install(["chromium"]))
    except Exception as e:
        print(f"[WARN] Playwright auto-install failed: {e}")

ensure_playwright_browsers()


# -----------------------------
# Page Config
# -----------------------------
st.set_page_config(page_title="Trivora", layout="wide", page_icon="trivora logo.png")

# -----------------------------
# Custom CSS
# -----------------------------
st.markdown("""
    <style>
    .main-title {
        text-align: center;
        font-size: 3rem;
        background: linear-gradient(90deg, #ff6a00, #ee0979);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 900;
        margin-bottom: 1.5rem;
    }
    .subtitle {
        text-align: center;
        font-size: 1.2rem;
        color: #6b7280;
        margin-bottom: 2rem;
    }
    .step-card {
        padding: 1.8rem;
        border-radius: 1.2rem;
        background: #ffffff;
        border: 1px solid #e5e7eb;
        margin-bottom: 1.5rem;
        box-shadow: 0px 4px 12px rgba(0,0,0,0.08);
        transition: transform 0.2s ease-in-out;
    }
    .step-card:hover {
        transform: translateY(-4px);
        box-shadow: 0px 8px 18px rgba(0,0,0,0.12);
    }
    .stButton button, .stDownloadButton button {
        background: linear-gradient(90deg, #0072ff, #00c6ff);
        color: white !important;
        border-radius: 0.6rem;
        font-weight: bold;
        font-size: 1rem;
        padding: 0.6rem 1.2rem;
        transition: all 0.3s ease;
    }
    .stButton button:hover, .stDownloadButton button:hover {
        background: linear-gradient(90deg, #00c6ff, #0072ff);
        transform: scale(1.03);
    }
    </style>
""", unsafe_allow_html=True)

# -----------------------------
# Sidebar
# -----------------------------
st.sidebar.image("trivora logo.png", width=200)
st.sidebar.title("✨ Trivora")
st.sidebar.markdown("**Scrape → Map → Download** your content into ready-to-use JSON.")
st.sidebar.markdown("---")
st.sidebar.info("💡 Tip: Scrape an article → Map to 'News' → Download JSON")

# -----------------------------
# Header
# -----------------------------
st.markdown('<h1 class="main-title">Trivora</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Scrape. Map. Download.</p>', unsafe_allow_html=True)

# -----------------------------
# Step 1: Scraping
# -----------------------------
st.markdown('<div class="step-card">', unsafe_allow_html=True)
st.subheader("🔍 Step 1: Scrape Content")
url = st.text_input("Enter a live URL to scrape", placeholder="https://example.com/article")

if st.button("🚀 Scrape URL", use_container_width=True, type="primary"):
    if not url:
        st.error("Please enter a URL first.")
    else:
        with st.spinner("Scraping content..."):
            try:
                scraped = scrape_url(url)
                st.session_state["scraped"] = scraped
                st.success(f"✅ Scraping completed using **{scraped.get('method', 'unknown')}**")
            except Exception as e:
                st.error(f"❌ Scrape failed: {e}")

if "scraped" in st.session_state:
    with st.expander("📑 View Scraped Metadata", expanded=False):
        meta_preview = {
            "method": st.session_state["scraped"].get("method"),
            "title": st.session_state["scraped"].get("title")
        }
        st.code(json.dumps(meta_preview, indent=2), language="json")

    with st.expander("📝 View Full HTML (optional)", expanded=False):
        st.text_area("HTML Content", st.session_state["scraped"].get("html", ""), height=300)
st.markdown('</div>', unsafe_allow_html=True)

# -----------------------------
# Step 2: Mapping
# -----------------------------
st.markdown('<div class="step-card">', unsafe_allow_html=True)
st.subheader("🧠 Step 2: Map Content to Template")
template = st.selectbox("Choose Template", ["News", "Blog", "MediaRelease"])

if st.button("⚡ Map to Template", use_container_width=True):
    if "scraped" not in st.session_state:
        st.error("Please scrape a URL first.")
    else:
        try:
            mapped = map_content_to_template(st.session_state["scraped"], template)
            st.session_state["mapped"] = mapped
            st.success(f"✅ Successfully mapped to **{template}** template!")
        except Exception as e:
            st.error(f"❌ Mapping failed: {e}")

if "mapped" in st.session_state:
    with st.expander("🗂️ View Mapped JSON", expanded=True):
        st.code(json.dumps(st.session_state["mapped"], indent=2), language="json")
st.markdown('</div>', unsafe_allow_html=True)

# -----------------------------
# Step 3: Export
# -----------------------------
st.markdown('<div class="step-card">', unsafe_allow_html=True)
st.subheader("📂 Step 3: Download JSON")

if "mapped" in st.session_state:
    mapped_json = json.dumps(st.session_state["mapped"], indent=2)
    st.download_button(
        label="💾 Download Mapped JSON",
        data=mapped_json,
        file_name="mapped_content.json",
        mime="application/json",
        use_container_width=True
    )
else:
    st.info("⚠️ You need to map content before downloading.")
st.markdown('</div>', unsafe_allow_html=True)
