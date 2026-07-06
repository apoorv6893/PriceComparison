import streamlit as st
import yfinance as yf
import pandas as pd
import datetime
import plotly.graph_objects as go

st.set_page_config(
    page_title="Indian Indices Dashboard",
    layout="wide"
)

st.title("📈 Indian Indices Dashboard")

# ==========================================================
# SYMBOLS
# ==========================================================

symbols = {
    "NIFTY 50": "^NSEI",
    "SENSEX": "^BSESN",
    "BANK NIFTY": "^NSEBANK",
    "NIFTY IT": "^CNXIT",
    "NIFTY AUTO": "^CNXAUTO",
    "NIFTY FMCG": "^CNXFMCG",
    "NIFTY PHARMA": "^CNXPHARMA",
    "NIFTY METAL": "^CNXMETAL",
    "NIFTY REALTY": "^CNXREALTY",
    "NIFTY ENERGY": "^CNXENERGY",
    "NIFTY MEDIA": "^CNXMEDIA",
    "NIFTY PSU BANK": "^CNXPSUBANK"
}

constituents = {
    "NIFTY IT": [
        "TCS",
        "Infosys",
        "HCL Tech",
        "Wipro",
        "Tech Mahindra"
    ],
    "NIFTY AUTO": [
        "Maruti",
        "M&M",
        "Tata Motors",
        "Bajaj Auto",
        "Eicher Motors"
    ],
    "NIFTY FMCG": [
        "HUL",
        "ITC",
        "Nestle",
        "Britannia",
        "Godrej Consumer"
    ],
    "NIFTY PHARMA": [
        "Sun Pharma",
        "Dr Reddy",
        "Cipla",
        "Divis",
        "Lupin"
    ],
    "NIFTY METAL": [
        "Tata Steel",
        "JSW Steel",
        "Hindalco",
        "Vedanta",
        "NMDC"
    ],
    "NIFTY REALTY": [
        "DLF",
        "Godrej Properties",
        "Prestige",
        "Oberoi Realty",
        "Phoenix"
    ],
    "NIFTY ENERGY": [
        "Reliance",
        "ONGC",
        "BPCL",
        "IOC",
        "Power Grid"
    ],
    "NIFTY MEDIA": [
        "Sun TV",
        "Zee",
        "PVR Inox",
        "Network18",
        "TV18"
    ],
    "NIFTY PSU BANK": [
        "SBI",
        "PNB",
        "Canara Bank",
        "Union Bank",
        "Bank of Baroda"
    ]
}

interval_map = {
    "4H": "1h",
    "1D": "1d",
    "1M": "1d",
    "1Y": "1d"
}

# ==========================================================
# HELPERS
# ==========================================================

def quick_dates(option):

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
        start = end - datetime.timedelta(days=365 * 3)

    else:
        start = end - datetime.timedelta(days=365 * 5)

    return start, end


@st.cache_data
def get_history(symbol, start, end, interval):

    try:

        df = yf.download(
            symbol,
            start=start,
            end=end,
            interval=interval,
            auto_adjust=True,
            progress=False
        )

        if df.empty:
            return None

        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        return df

    except:
        return None


@st.cache_data
def get_5y(symbol):

    try:

        df = yf.download(
            symbol,
            period="5y",
            interval="1d",
            auto_adjust=True,
            progress=False
        )

        if df.empty:
            return None

        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        return df

    except:
        return None


def build_chart(df, title):

    fig = go.Figure()

    fig.add_trace(

        go.Scatter(
            x=df.index,
            y=df["Close"],
            mode="lines",
            name=title,
            hovertemplate="Value %{y:.2f}<extra></extra>"
        )

    )

    fig.update_layout(

        height=300,

        margin=dict(
            l=10,
            r=10,
            t=30,
            b=10
        ),

        hovermode="closest",

        dragmode=False,

        xaxis=dict(
            fixedrange=True,
            rangeslider=dict(
                visible=True
            )
        ),

        yaxis=dict(
            fixedrange=True
        )

    )

    return fig


def calculate_metrics(symbol):

    df = get_5y(symbol)

    if df is None:
        return None

    current = float(df["Close"].iloc[-1])

    today_change = (
        (df["Close"].iloc[-1] - df["Close"].iloc[-2])
        / df["Close"].iloc[-2]
    ) * 100

    high52 = float(df["High"].tail(252).max())

    low52 = float(df["Low"].tail(252).min())

    ath = float(df["High"].max())

    atl = float(df["Low"].min())

    pct_from_ath = ((current - ath) / ath) * 100

    pct_from_atl = ((current - atl) / atl) * 100

    position52 = (
        (current - low52)
        /
        (high52 - low52)
    ) * 100

    return {

        "history": df,

        "current": current,

        "today": today_change,

        "52high": high52,

        "52low": low52,

        "ath": ath,

        "atl": atl,

        "from_ath": pct_from_ath,

        "from_atl": pct_from_atl,

        "position": position52

    }


# ==========================================================
# TOP CHARTS
# ==========================================================

st.header("Market Overview")

quick = st.radio(
    "Duration",
    [
        "1M",
        "2M",
        "6M",
        "1Y",
        "3Y",
        "5Y"
    ],
    horizontal=True
)

start, end = quick_dates(quick)

left, right = st.columns(2)

for col, index_name in zip(
    [left, right],
    ["NIFTY 50", "SENSEX"]
):

    with col:

        st.subheader(index_name)

        interval = st.radio(

            f"{index_name}_interval",

            ["4H", "1D", "1M", "1Y"],

            horizontal=True,

            key=index_name

        )

        history = get_history(
            symbols[index_name],
            start,
            end,
            interval_map[interval]
        )

        if history is not None:

            fig = build_chart(
                history,
                index_name
            )

            st.plotly_chart(
                fig,
                use_container_width=True,
                config={
                    "displayModeBar": False,
                    "scrollZoom": False
                }
            )

        else:

            st.warning("Data unavailable")

st.divider()

st.header("Indian Sector Indices")

sector_indices = [
    "BANK NIFTY",
    "NIFTY IT",
    "NIFTY AUTO",
    "NIFTY FMCG",
    "NIFTY PHARMA",
    "NIFTY METAL",
    "NIFTY REALTY",
    "NIFTY ENERGY",
    "NIFTY MEDIA",
    "NIFTY PSU BANK"
]

for sector in sector_indices:

    metrics = calculate_metrics(symbols[sector])

    if metrics is None:
        st.warning(f"Unable to fetch data for {sector}")
        continue

    if metrics["position"] >= 80:
        status = "🟢 Near 52W High"
    elif metrics["position"] >= 40:
        status = "🟡 Mid Range"
    else:
        status = "🔴 Near 52W Low"

    with st.expander(f"{sector}   |   {status}", expanded=False):

        c1, c2, c3, c4 = st.columns(4)

        with c1:
            st.metric(
                "Current",
                f"{metrics['current']:.2f}",
                f"{metrics['today']:.2f}%"
            )

        with c2:
            st.metric(
                "52 Week High",
                f"{metrics['52high']:.2f}"
            )

        with c3:
            st.metric(
                "52 Week Low",
                f"{metrics['52low']:.2f}"
            )

        with c4:
            st.metric(
                "52W Position",
                f"{metrics['position']:.1f}%"
            )

        st.progress(
            max(
                0,
                min(
                    int(metrics["position"]),
                    100
                )
            ) / 100
        )

        st.divider()

        d1, d2 = st.columns(2)

        with d1:

            st.metric(
                "All Time High",
                f"{metrics['ath']:.2f}"
            )

            st.metric(
                "% From ATH",
                f"{metrics['from_ath']:.2f}%"
            )

        with d2:

            st.metric(
                "All Time Low",
                f"{metrics['atl']:.2f}"
            )

            st.metric(
                "% From ATL",
                f"{metrics['from_atl']:.2f}%"
            )

        st.divider()

        st.subheader("5 Year Performance")

        fig = build_chart(
            metrics["history"],
            sector
        )

        st.plotly_chart(
            fig,
            use_container_width=True,
            config={
                "displayModeBar": False,
                "scrollZoom": False
            }
        )

        st.divider()

        st.subheader("Top Constituents")

        if sector in constituents:

            cols = st.columns(2)

            companies = constituents[sector]

            for i, company in enumerate(companies):

                with cols[i % 2]:
                    st.write("•", company)

        else:

            st.write("Constituents not available")

        st.divider()

        st.subheader("Investment Summary")

        summary = []

        if metrics["from_ath"] < -25:
            summary.append(
                "• Trading more than 25% below its All Time High."
            )
        elif metrics["from_ath"] < -10:
            summary.append(
                "• Trading moderately below its All Time High."
            )
        else:
            summary.append(
                "• Trading close to its All Time High."
            )

        if metrics["position"] > 80:
            summary.append(
                "• Sector is near the top of its 52-week range."
            )

        elif metrics["position"] > 50:
            summary.append(
                "• Sector is trading in the middle of its yearly range."
            )

        else:
            summary.append(
                "• Sector is closer to the lower end of its yearly range."
            )

        if metrics["today"] > 1:
            summary.append(
                "• Strong positive momentum today."
            )
        elif metrics["today"] < -1:
            summary.append(
                "• Weak momentum today."
            )
        else:
            summary.append(
                "• Limited movement today."
            )

        for line in summary:
            st.write(line)

        st.caption(
            "Data Source: Yahoo Finance"
        )