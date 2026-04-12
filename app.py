import streamlit as st
import yfinance as yf
import pandas as pd
import datetime
import plotly.graph_objects as go
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
        data = yf.download(
            ticker,
            start=start,
            end=end,
            interval=interval,
            progress=False,
            auto_adjust=True
        )
        if data is None or data.empty:
            return None
        data["Returns"] = data["Close"].pct_change()
        return data
    except:
        return None

# -------- DATE HELPER --------
def get_quick_range(option):
    end = datetime.date.today()
    if option == "1M":
        start = end - datetime.timedelta(days=30)
    elif option == "2M":
        start = end - datetime.timedelta(days=60)
    elif option == "6M":
        start = end - datetime.timedelta(days=180)
    elif option == "1Y":
        start = end - datetime.timedelta(days=365)
    elif option == "3Y":
        start = end - datetime.timedelta(days=365*3)
    elif option == "5Y":
        start = end - datetime.timedelta(days=365*5)
    return start, end

# -------- IMPROVED MOBILE CHART --------
def plot_chart(data, title):
    if data is None or data.empty:
        return None

    data = data.copy()

    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(0)

    if "Close" not in data.columns:
        return None

    data = data.dropna(subset=["Close"])

    if data.empty:
        return None

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=data.index,
            y=data["Close"],
            mode="lines",
            name=title,
            hovertemplate="Price: %{y:.2f}<br>Date: %{x}<extra></extra>"
        )
    )

    fig.update_layout(
        height=300,
        margin=dict(l=10, r=10, t=30, b=10),
        hovermode="closest",   # better for mobile
        dragmode=False,        # disable drag/pan
        xaxis=dict(
            showgrid=False,
            fixedrange=True,
            rangeslider=dict(visible=True)  # keep slider
        ),
        yaxis=dict(
            showgrid=False,
            fixedrange=True
        )
    )

    return fig

# =========================
# 📈 MARKET
# =========================

st.header("📈 Market Trends")

quick_option = st.radio(
    "Quick Select Duration",
    ["1M", "2M", "6M", "1Y", "3Y", "5Y"],
    horizontal=True
)

start_date, end_date = get_quick_range(quick_option)

col1, col2 = st.columns(2)

with col1:
    start_date = st.date_input("Start Date", start_date)

with col2:
    end_date = st.date_input("End Date", end_date)

select_all = st.checkbox("Select All Indices")

if select_all:
    selected_assets = list(symbols.keys())
else:
    selected_assets = st.multiselect(
        "Select Indices / Commodities",
        list(symbols.keys()),
        default=["NIFTY 50", "S&P 500", "NASDAQ"]
    )

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

                fig = plot_chart(data, asset)

                if fig:
                    st.plotly_chart(
                        fig,
                        use_container_width=True,
                        config={
                            "scrollZoom": False,
                            "displayModeBar": False,
                            "doubleClick": False
                        }
                    )
                else:
                    st.warning("Data unavailable")

# =========================
# 🔗 CORRELATION
# =========================

st.header("🔗 Correlation Analyzer")

quick_option_corr = st.radio(
    "Quick Select Duration (Correlation)",
    ["1M", "2M", "6M", "1Y", "3Y", "5Y"],
    horizontal=True,
    key="corr_quick"
)

start_date_corr, end_date_corr = get_quick_range(quick_option_corr)

col3, col4 = st.columns(2)

with col3:
    start_date_corr = st.date_input("Start Date (Correlation)", start_date_corr)

with col4:
    end_date_corr = st.date_input("End Date (Correlation)", end_date_corr)

select_all_corr = st.checkbox("Select All (Correlation)")

if select_all_corr:
    selected_corr_assets = list(symbols.keys())
else:
    selected_corr_assets = st.multiselect(
        "Select Assets",
        list(symbols.keys()),
        default=["NIFTY 50", "S&P 500", "GOLD"]
    )

if len(selected_corr_assets) > 8:
    st.warning("Too many assets selected. Showing first 8.")
    selected_corr_assets = selected_corr_assets[:8]

if len(selected_corr_assets) >= 2:

    df = pd.DataFrame()

    for asset in selected_corr_assets:
        data = get_data(symbols[asset], start_date_corr, end_date_corr, "1d")
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

st.info("Mobile optimized | Tap to inspect values | Slider for navigation")
