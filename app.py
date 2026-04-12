import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="Global Market Dashboard", layout="wide")

st.title("🌍 Global Market Dashboard")

# -------- SYMBOL MAP --------
symbols = {
    # India
    "NIFTY 50": "^NSEI",
    "SENSEX": "^BSESN",
    "BANK NIFTY": "^NSEBANK",

    # US
    "S&P 500": "^GSPC",
    "NASDAQ": "^IXIC",
    "DOW JONES": "^DJI",

    # Europe
    "FTSE 100": "^FTSE",
    "DAX": "^GDAXI",

    # Asia
    "NIKKEI 225": "^N225",
    "HANG SENG": "^HSI",
    "SHANGHAI": "000001.SS",

    # Commodities
    "GOLD": "GC=F",
    "CRUDE OIL": "CL=F"
}

# -------- TIMEFRAME --------
timeframe_options = {
    "1 Week": "5d",
    "1 Month": "1mo",
    "3 Months": "3mo",
    "6 Months": "6mo",
    "1 Year": "1y"
}

timeframe_label = st.selectbox("Select Timeframe", list(timeframe_options.keys()))
timeframe = timeframe_options[timeframe_label]

# -------- DATA FETCH --------
@st.cache_data
def get_data(ticker, period):
    try:
        data = yf.download(ticker, period=period, interval="1d", progress=False)
        if data is None or data.empty:
            return None
        data["Returns"] = data["Close"].pct_change()
        return data
    except:
        return None

# -------- SECTION 1: CHARTS --------
st.header("📈 Market Trends")

selected_assets = st.multiselect(
    "Select Indices / Commodities",
    list(symbols.keys()),
    default=["NIFTY 50", "S&P 500", "NASDAQ"]
)

if selected_assets:
    for asset in selected_assets:
        data = get_data(symbols[asset], timeframe)

        st.subheader(asset)

        if data is not None and "Close" in data:
            st.line_chart(data["Close"])
        else:
            st.warning(f"{asset}: Data unavailable")

# -------- SECTION 2: CORRELATION --------
st.header("🔗 Correlation Analyzer")

selected_corr_assets = st.multiselect(
    "Select Assets for Correlation",
    list(symbols.keys()),
    default=["NIFTY 50", "S&P 500"]
)

if len(selected_corr_assets) >= 2:

    df = pd.DataFrame()

    for asset in selected_corr_assets:
        data = get_data(symbols[asset], timeframe)

        if data is not None:
            df[asset] = data["Returns"]

    df = df.dropna()

    if not df.empty:
        st.subheader("📊 Correlation Matrix")
        st.dataframe(df.corr())

        st.subheader("📉 Returns Comparison")
        st.line_chart(df)
    else:
        st.warning("Not enough overlapping data for correlation")

else:
    st.info("Select at least 2 assets to view correlation")

# -------- INFO --------
st.info("Data source: Yahoo Finance | Timeframe adjustable | Global indices included")
