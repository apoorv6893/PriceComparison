import streamlit as st
import yfinance as yf
import pandas as pd
import datetime
import plotly.express as px

st.set_page_config(page_title="Global Market Dashboard", layout="wide")

st.title("🌍 Global Market Dashboard")

# -------- SYMBOL MAP --------
symbols = {
    "NIFTY 50": "^NSEI",
    "SENSEX": "^BSESN",
    "BANK NIFTY": "^NSEBANK",
    "S&P 500": "^GSPC",
    "NASDAQ": "^IXIC",
    "DOW JONES": "^DJI",
    "NIKKEI 225": "^N225",
    "HANG SENG": "^HSI",
    "SHANGHAI": "000001.SS",
    "GOLD": "GC=F",
    "CRUDE OIL": "CL=F"
}

# -------- INTERVAL MAP --------
interval_map = {
    "4H": "1h",
    "1D": "1d",
    "1M": "1d",
    "1Y": "1d"
}

# -------- DATA FETCH --------
@st.cache_data
def get_data(ticker, start, end, interval):
    try:
        data = yf.download(ticker, start=start, end=end, interval=interval, progress=False)
        if data is None or data.empty:
            return None
        data["Returns"] = data["Close"].pct_change()
        return data
    except:
        return None

# =========================
# 📈 SECTION 1: MARKET
# =========================

st.header("📈 Market Trends")

# 🔹 Time controls (TOP SECTION)
colA, colB = st.columns(2)

with colA:
    start_date_1 = st.date_input("Start Date (Trends)", datetime.date.today() - datetime.timedelta(days=30))

with colB:
    end_date_1 = st.date_input("End Date (Trends)", datetime.date.today())

selected_assets = st.multiselect(
    "Select Indices / Commodities",
    list(symbols.keys()),
    default=["NIFTY 50", "S&P 500", "NASDAQ"]
)

# 🔹 GRID (2 per row)
for i in range(0, len(selected_assets), 2):
    cols = st.columns(2)

    for j in range(2):
        if i + j < len(selected_assets):
            asset = selected_assets[i + j]

            with cols[j]:
                st.subheader(asset)

                interval_label = st.radio(
                    f"Interval - {asset}",
                    ["4H", "1D", "1M", "1Y"],
                    horizontal=True,
                    key=f"interval_{asset}"
                )

                interval = interval_map[interval_label]

                data = get_data(symbols[asset], start_date_1, end_date_1, interval)

                if data is not None:
                    st.line_chart(data["Close"])
                else:
                    st.warning("Data unavailable")

# =========================
# 🔗 SECTION 2: CORRELATION
# =========================

st.header("🔗 Correlation Analyzer")

# 🔹 Time controls (CORRELATION SECTION)
colC, colD = st.columns(2)

with colC:
    start_date_2 = st.date_input("Start Date (Correlation)", datetime.date.today() - datetime.timedelta(days=30))

with colD:
    end_date_2 = st.date_input("End Date (Correlation)", datetime.date.today())

selected_corr_assets = st.multiselect(
    "Select Assets",
    list(symbols.keys()),
    default=["NIFTY 50", "S&P 500", "GOLD"]
)

if len(selected_corr_assets) >= 2:

    df = pd.DataFrame()

    for asset in selected_corr_assets:
        data = get_data(symbols[asset], start_date_2, end_date_2, "1d")
        if data is not None:
            df[asset] = data["Returns"]

    df = df.dropna()

    if not df.empty:
        corr = df.corr()

        st.subheader("📊 Correlation Table")
        st.dataframe(corr)

        st.subheader("🔥 Correlation Heatmap")

        fig = px.imshow(
            corr,
            text_auto=True,
            color_continuous_scale="RdBu",
            zmin=-1,
            zmax=1
        )

        st.plotly_chart(fig, use_container_width=True)

        st.subheader("📉 Returns Comparison")
        st.line_chart(df)

    else:
        st.warning("Not enough overlapping data")

else:
    st.info("Select at least 2 assets")

# -------- INFO --------
st.info("Global markets | Section-wise time control | Interactive heatmap")
