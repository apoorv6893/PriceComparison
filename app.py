import streamlit as st
import requests
from bs4 import BeautifulSoup

st.set_page_config(page_title="Price तुलना", layout="wide")

st.title("🛒 Product Price Comparison")
st.write("Compare prices across Amazon & Flipkart")

product = st.text_input("Enter product name (e.g. iPhone 15)")

headers = {
    "User-Agent": "Mozilla/5.0"
}

# -------- Amazon Scraper --------
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
            "price": f"₹{price.text}" if price else "-",
            "rating": rating.text if rating else "-",
            "link": url
        }
    except:
        return {"title": "Error", "price": "-", "rating": "-", "link": url}


# -------- Flipkart Scraper --------
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
            "price": price.text if price else "-",
            "rating": rating.text if rating else "-",
            "link": url
        }
    except:
        return {"title": "Error", "price": "-", "rating": "-", "link": url}


# -------- Main Logic --------
if product:
    st.divider()
    st.subheader(f"Results for: {product}")

    col1, col2 = st.columns(2)

    with st.spinner("Fetching data..."):
        amazon = search_amazon(product)
        flipkart = search_flipkart(product)

    # Amazon Column
    with col1:
        st.markdown("## Amazon")
        st.write("**Product:**", amazon["title"])
        st.write("**Price:**", amazon["price"])
        st.write("**Rating:**", amazon["rating"])
        st.markdown(f"[🔗 View Product]({amazon['link']})")

    # Flipkart Column
    with col2:
        st.markdown("## Flipkart")
        st.write("**Product:**", flipkart["title"])
        st.write("**Price:**", flipkart["price"])
        st.write("**Rating:**", flipkart["rating"])
        st.markdown(f"[🔗 View Product]({flipkart['link']})")

    st.divider()

    st.info("Demo only: Prices are scraped and may not always be accurate.")