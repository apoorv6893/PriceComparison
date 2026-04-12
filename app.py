import streamlit as st
import requests
from bs4 import BeautifulSoup

st.set_page_config(page_title="Price Comparison", layout="wide")

st.title("🛒 Product Price Comparison")
st.write("Compare prices across Amazon & Flipkart")

product = st.text_input("Enter product name (e.g. iPhone 15)")

# -------- MOCK DATA (for stable demo) --------
MOCK_DATA = {
    "iphone 17 pro": {
        "amazon": {
            "title": "Apple iPhone 17 Pro (256GB)",
            "price": "₹1,39,999",
            "rating": "4.6 ⭐"
        },
        "flipkart": {
            "title": "Apple iPhone 17 Pro (256GB)",
            "price": "₹1,37,999",
            "rating": "4.5 ⭐"
        }
    },
    "iphone 15": {
        "amazon": {
            "title": "Apple iPhone 15 (128GB)",
            "price": "₹79,999",
            "rating": "4.5 ⭐"
        },
        "flipkart": {
            "title": "Apple iPhone 15 (128GB)",
            "price": "₹78,499",
            "rating": "4.4 ⭐"
        }
    }
}

# -------- HEADERS --------
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

# -------- SAFE DISPLAY --------
def safe_display(value):
    return value if value not in ["Not found", "Error", None] else "Data unavailable"

# -------- AMAZON SCRAPER --------
def search_amazon(query):
    url = f"https://www.amazon.in/s?k={query}"
    try:
        r = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")

        title = soup.select_one("span.a-size-medium")
        price = soup.select_one("span.a-price-whole")
        rating = soup.select_one("span.a-icon-alt")

        return {
            "title": title.text if title else "Not found",
            "price": f"₹{price.text}" if price else "Not found",
            "rating": rating.text if rating else "Not found",
            "link": url
        }
    except:
        return {"title": "Error", "price": "Error", "rating": "Error", "link": url}

# -------- FLIPKART SCRAPER --------
def search_flipkart(query):
    url = f"https://www.flipkart.com/search?q={query}"
    try:
        r = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")

        title = soup.select_one("div._4rR01T, a.s1Q9rs")
        price = soup.select_one("div._30jeq3")
        rating = soup.select_one("div._3LWZlK")

        return {
            "title": title.text if title else "Not found",
            "price": price.text if price else "Not found",
            "rating": rating.text if rating else "Not found",
            "link": url
        }
    except:
        return {"title": "Error", "price": "Error", "rating": "Error", "link": url}

# -------- MAIN LOGIC --------
if product:
    query = product.lower().strip()

    st.divider()
    st.subheader(f"Results for: {product}")

    col1, col2 = st.columns(2)

    # Check mock first
    if query in MOCK_DATA:
        st.success("✅ Showing reliable demo data")

        amazon = MOCK_DATA[query]["amazon"]
        flipkart = MOCK_DATA[query]["flipkart"]

    else:
        st.warning("⚠️ Live data may fail due to scraping limitations")

        with st.spinner("Fetching live data..."):
            amazon = search_amazon(product)
            flipkart = search_flipkart(product)

    # -------- AMAZON COLUMN --------
    with col1:
        st.markdown("## 🟡 Amazon")
        st.write("**Product:**", safe_display(amazon["title"]))
        st.write("**Price:**", safe_display(amazon["price"]))
        st.write("**Rating:**", safe_display(amazon["rating"]))
        st.markdown(f"[🔗 View Product]({amazon.get('link', '#')})")

    # -------- FLIPKART COLUMN --------
    with col2:
        st.markdown("## 🔵 Flipkart")
        st.write("**Product:**", safe_display(flipkart["title"]))
        st.write("**Price:**", safe_display(flipkart["price"]))
        st.write("**Rating:**", safe_display(flipkart["rating"]))
        st.markdown(f"[🔗 View Product]({flipkart.get('link', '#')})")

    st.divider()
    st.info("⚠️ Demo note: Stable results shown for known products. Live scraping may fail.")
