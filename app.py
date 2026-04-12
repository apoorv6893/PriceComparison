import streamlit as st
import requests
from bs4 import BeautifulSoup

st.set_page_config(page_title="Price Comparison", layout="wide")

st.title("🛒 Product Price Comparison")
st.write("Compare prices across multiple sellers")

product = st.text_input("Enter product name (e.g. iPhone 15)")

headers = {
    "User-Agent": "Mozilla/5.0"
}

# -------- GOOGLE SHOPPING SCRAPER (STABLE) --------
def search_google_shopping(query):
    url = f"https://www.google.com/search?q={query}&tbm=shop"
    results = []

    try:
        r = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")

        items = soup.select(".sh-dgr__grid-result")

        for item in items[:4]:  # top 4 results
            title = item.select_one(".tAxDx")
            price = item.select_one(".a8Pemb")
            seller = item.select_one(".aULzUe")

            results.append({
                "title": title.text if title else "No title",
                "price": price.text if price else "No price",
                "seller": seller.text if seller else "Unknown"
            })

        return results

    except:
        return []

# -------- MAIN LOGIC --------
if product:
    st.divider()
    st.subheader(f"Results for: {product}")

    with st.spinner("Fetching prices..."):
        results = search_google_shopping(product)

    if results:
        cols = st.columns(len(results))

        for i, item in enumerate(results):
            with cols[i]:
                st.markdown(f"### 🏬 {item['seller']}")
                st.write("**Product:**", item["title"])
                st.write("**Price:**", item["price"])

    else:
        st.error("Could not fetch results. Try a different product.")

    st.divider()
    st.info("Showing top sellers from Google Shopping (stable demo)")
