import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="Market Dashboard", layout="wide")

st.title("📊 Market Dashboard: Weekly Trends & Correlation")

# -------- SYMBOL MAP --------
symbols = {
    "NIFTY 50": "^NSEI",
    "SENSEX": "^BSESN",
    "BANK NIFTY": "^NSEBANK",
    "GOLD": "GC=F",
    "CRUDE OIL": "CL=F"
}

# -------- FETCH DATA --------
@st.cache_data
def get_data(ticker):
    data = yf.download(ticker, period="1mo", interval="1d")
    data["Returns"] = data["Close"].pct_change()
    return data

# -------- SECTION 1: WEEKLY TREND --------
st.header("📈 Week-on-Week Performance")

cols = st.columns(3)

for i, (name, ticker) in enumerate(symbols.items()):
    data = get_data(ticker)

    with cols[i % 3]:
        st.subheader(name)
        st.line_chart(data["Close"])

# -------- SECTION 2: SELECT FOR CORRELATION --------
st.header("🔗 Correlation Analyzer")

col1, col2 = st.columns(2)

with col1:
    option1 = st.selectbox("Select First Asset", list(symbols.keys()))

with col2:
    option2 = st.selectbox("Select Second Asset", list(symbols.keys()), index=1)

# -------- CORRELATION CALC --------
data1 = get_data(symbols[option1])
data2 = get_data(symbols[option2])

df = pd.DataFrame({
    option1: data1["Returns"],
    option2: data2["Returns"]
}).dropna()

correlation = df.corr().iloc[0, 1]

# -------- DISPLAY --------
st.subheader("📊 Correlation Result")

st.metric("Correlation", round(correlation, 3))

st.line_chart(df)

# -------- INTERPRETATION --------
if correlation > 0.5:
    st.success("Strong Positive Correlation 📈")
elif correlation < -0.5:
    st.error("Strong Negative Correlation 📉")
else:
    st.info("Weak / No Correlation")

# -------- INFO --------
st.info("Data source: Yahoo Finance (no API key required)")
