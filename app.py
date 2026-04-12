import streamlit as st
import yfinance as yf
import pandas as pd
import datetime

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

# -------- GLOBAL DATE FILTER --------
st.sidebar.header("📅 Time Range")

start_date = st.sidebar.date_input("Start Date", datetime.date.today() - datetime.timedelta(days=30))
end_date = st.sidebar.date_input("End Date", datetime.date.today())

# -------- INTERVAL OPTIONS --------
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

# -------- SELECT ASSETS --------
st.header("📈 Market Trends")

selected_assets = st.multiselect(
    "Select Indices / Commodities",
    list(symbols.keys()),
    default=["NIFTY 50", "S&P 500", "NASDAQ"]
)

# -------- GRID LAYOUT (2 per row) --------
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

                data = get_data(symbols[asset], start_date, end_date, interval)

                if data is not None:
                    st.line_chart(data["Close"])
                else:
                    st.warning("Data unavailable")

# -------- CORRELATION --------
st.header("🔗 Correlation Analyzer")

selected_corr_assets = st.multiselect(
    "Select Assets",
    list(symbols.keys()),
    default=["NIFTY 50", "S&P 500", "GOLD"]
)

if len(selected_corr_assets) >= 2:

    df = pd.DataFrame()

    for asset in selected_corr_assets:
        data = get_data(symbols[asset], start_date, end_date, "1d")
        if data is not None:
            df[asset] = data["Returns"]

    df = df.dropna()

    if not df.empty:
        corr = df.corr()

        st.subheader("📊 Correlation Table")
        st.dataframe(corr)

        st.subheader("🔥 Correlation Heatmap")
        st.write(corr.style.background_gradient(cmap="coolwarm"))

        st.subheader("📉 Returns Comparison")
        st.line_chart(df)

    else:
        st.warning("Not enough overlapping data")

else:
    st.info("Select at least 2 assets")

# -------- INFO --------
st.info("Global markets | Custom time range | Multi-interval charts | Correlation heatmap")
