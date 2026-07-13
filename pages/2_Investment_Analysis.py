import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import datetime

st.set_page_config(
    page_title="Investment Analysis",
    layout="wide"
)

st.title("📊 Investment Analysis")
st.caption("AI-powered investment stage analysis using the last 6 months of historical market behaviour.")

# ==========================================================
# INDEX MAP
# ==========================================================

symbols = {
    "NIFTY 50": "^NSEI",
    "SENSEX": "^BSESN",
    "NIFTY NEXT 50": "^NSMIDCP",
    "NIFTY MIDCAP 100": "^CNXMIDCAP",
    "NIFTY SMALLCAP 100": "^CNXSMLCAP",
    "NIFTY LARGE MIDCAP 250": "^NIFTYLARGEMID250",

    "NIFTY AUTO": "^CNXAUTO",
    "NIFTY BANK": "^NSEBANK",
    "NIFTY FMCG": "^CNXFMCG",
    "NIFTY IT": "^CNXIT",
    "NIFTY METAL": "^CNXMETAL",
    "NIFTY PHARMA": "^CNXPHARMA",
    "NIFTY REALTY": "^CNXREALTY",
    "NIFTY MEDIA": "^CNXMEDIA",
    "NIFTY PSU BANK": "^CNXPSUBANK",
    "NIFTY OIL & GAS": "^CNXOILGAS",
    "NIFTY CONSUMER DURABLES": "^CNXCONSUM",
    "NIFTY HEALTHCARE": "^CNXHEALTHCARE",
    "NIFTY PRIVATE BANK": "^NIFTYPVTBANK"
}

# ==========================================================
# DATA
# ==========================================================

@st.cache_data(ttl=3600)
def get_data(symbol):

    end = datetime.date.today()
    start = end - datetime.timedelta(days=185)

    df = yf.download(
        symbol,
        start=start,
        end=end,
        progress=False,
        auto_adjust=True
    )

    if df.empty:
        return None

    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    return df.dropna()


# ==========================================================
# CHART
# ==========================================================

def trend_chart(df):

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df["Close"],
            mode="lines",
            line=dict(width=2)
        )
    )

    fig.update_layout(
        height=320,
        margin=dict(l=10,r=10,t=20,b=10),
        dragmode=False,
        hovermode="x unified",
        showlegend=False,
        xaxis=dict(
            rangeslider=dict(visible=True),
            fixedrange=True
        ),
        yaxis=dict(
            fixedrange=True
        )
    )

    return fig
    
# ==========================================================
# ANALYSIS ENGINE
# ==========================================================

def analyse(df):

    close = df["Close"].copy()

    # ------------------------------------------------------
    # BASIC METRICS
    # ------------------------------------------------------

    current = float(close.iloc[-1])

    ath = float(close.max())

    high52 = float(close.max())

    low52 = float(close.min())

    below_ath = ((ath - current) / ath) * 100

    position52 = (
        (current - low52)
        /
        (high52 - low52)
    ) * 100

    # ------------------------------------------------------
    # MOVING AVERAGES
    # ------------------------------------------------------

    sma20 = close.rolling(20).mean()

    sma50 = close.rolling(50).mean()

    sma100 = close.rolling(100).mean()

    # ------------------------------------------------------
    # TREND
    # ------------------------------------------------------

    trend_score = 0

    if current > sma20.iloc[-1]:
        trend_score += 1

    if current > sma50.iloc[-1]:
        trend_score += 1

    if sma20.iloc[-1] > sma50.iloc[-1]:
        trend_score += 1

    if sma50.iloc[-1] > sma100.iloc[-1]:
        trend_score += 1

    if sma20.iloc[-1] > sma20.iloc[-20]:
        trend_score += 1

    trend_score = trend_score * 20

    # ------------------------------------------------------
    # MARKET STRUCTURE
    # ------------------------------------------------------

    highs = []

    lows = []

    for i in range(20, len(close), 20):

        chunk = close.iloc[i - 20:i]

        highs.append(chunk.max())

        lows.append(chunk.min())

    higher_highs = 0

    higher_lows = 0

    for i in range(1, len(highs)):

        if highs[i] > highs[i - 1]:
            higher_highs += 1

    for i in range(1, len(lows)):

        if lows[i] > lows[i - 1]:
            higher_lows += 1

    structure_score = (
        higher_highs +
        higher_lows
    )

    structure_score = min(
        structure_score * 15,
        100
    )

    # ------------------------------------------------------
    # MOMENTUM
    # ------------------------------------------------------

    periods = [21, 42, 63, 84, 105, 126]

    monthly_returns = []

    for p in periods:

        if len(close) > p:

            monthly_returns.append(

                (
                    current
                    /
                    float(close.iloc[-p])
                    - 1
                ) * 100

            )

    momentum_score = 0

    if len(monthly_returns) >= 6:

        for i in range(1, len(monthly_returns)):

            if monthly_returns[i] > monthly_returns[i - 1]:

                momentum_score += 20

    # ------------------------------------------------------
    # VOLATILITY
    # ------------------------------------------------------

    volatility = (

        close.pct_change().std()

        * 100

    )

    stability_score = 100

    if volatility > 1:

        stability_score = 80

    if volatility > 1.5:

        stability_score = 60

    if volatility > 2:

        stability_score = 40

    if volatility > 3:

        stability_score = 20

    # ------------------------------------------------------
    # PULLBACK QUALITY
    # ------------------------------------------------------

    rolling_high = close.cummax()

    drawdown = (

        rolling_high - close

    ) / rolling_high

    max_drawdown = drawdown.max() * 100

    if max_drawdown < 8:

        pullback_score = 100

    elif max_drawdown < 12:

        pullback_score = 80

    elif max_drawdown < 18:

        pullback_score = 60

    elif max_drawdown < 25:

        pullback_score = 40

    else:

        pullback_score = 20

    # ------------------------------------------------------
    # RECOVERY
    # ------------------------------------------------------

    last_peak = rolling_high.iloc[-1]

    recovery_ratio = current / last_peak

    recovery_score = int(

        recovery_ratio * 100

    )

    recovery_score = max(

        min(recovery_score, 100),

        0

    )

    # ------------------------------------------------------
    # STAGE ENGINE
    # ------------------------------------------------------

    stage = "🔴 Weak Trend"

    if (

        trend_score >= 80

        and structure_score >= 70

    ):

        if (

            momentum_score >= 80

            and below_ath > 12

            and recovery_score >= 90

        ):

            stage = "🌱 Early Accumulation"

        elif (

            momentum_score >= 60

            and recovery_score >= 85

        ):

            stage = "🚀 Expansion"

        elif (

            momentum_score >= 40

        ):

            stage = "🟡 Mature Trend"

        else:

            stage = "🔴 Exhaustion"

    # ------------------------------------------------------
    # CONFIDENCE
    # ------------------------------------------------------

    evidence = [

        trend_score,

        structure_score,

        momentum_score,

        stability_score,

        pullback_score,

        recovery_score

    ]

    confidence = int(

        np.mean(evidence)

    )

    # ------------------------------------------------------
    # INSIGHTS
    # ------------------------------------------------------

    insights = []

    if trend_score >= 80:

        insights.append(
            "Trend remains firmly positive across short and medium-term moving averages."
        )

    if structure_score >= 70:

        insights.append(
            "Higher highs and higher lows indicate healthy market structure."
        )

    if momentum_score >= 80:

        insights.append(
            "Momentum has accelerated consistently over recent months."
        )

    elif momentum_score >= 60:

        insights.append(
            "Momentum remains positive and continues to support the trend."
        )

    else:

        insights.append(
            "Momentum is flattening and requires monitoring."
        )

    if pullback_score >= 80:

        insights.append(
            "Recent pullbacks have remained shallow, indicating strong buying support."
        )

    if recovery_score >= 90:

        insights.append(
            "The market has recovered quickly after corrections."
        )

    if below_ath > 12:

        insights.append(
            f"The index is still {below_ath:.1f}% below its recent high, leaving room for further upside."
        )

    else:

        insights.append(
            "The index is trading close to its recent high, suggesting a more mature phase."
        )

    # ------------------------------------------------------
    # RETURN
    # ------------------------------------------------------

    return {

        "current": current,

        "ath": ath,

        "high52": high52,

        "low52": low52,

        "below_ath": below_ath,

        "position52": position52,

        "trend": trend_score,

        "structure": structure_score,

        "momentum": momentum_score,

        "stability": stability_score,

        "pullback": pullback_score,

        "recovery": recovery_score,

        "confidence": confidence,

        "stage": stage,

        "volatility": volatility,

        "insights": insights

    }
    
    # ==========================================================
# UI
# ==========================================================

st.markdown("---")

select_all = st.checkbox(
    "Select All Indices",
    value=False
)

default_indices = [
    "NIFTY 50",
    "NIFTY MIDCAP 100",
    "NIFTY SMALLCAP 100",
    "NIFTY BANK",
    "NIFTY IT",
    "NIFTY PHARMA"
]

if select_all:
    selected_indices = list(symbols.keys())
else:
    selected_indices = st.multiselect(
        "Select Indices",
        list(symbols.keys()),
        default=default_indices
    )

if len(selected_indices) == 0:
    st.stop()

# ==========================================================
# MAIN LOOP
# ==========================================================

for index_name in selected_indices:

    st.markdown("---")

    df = get_data(symbols[index_name])

    if df is None:
        st.warning(f"Unable to load data for {index_name}")
        continue

    analysis = analyse(df)

    st.header(index_name)

    # ------------------------------------------------------
    # TOP METRICS
    # ------------------------------------------------------

    m1, m2, m3 = st.columns(3)

    day_change = (
        (
            df["Close"].iloc[-1]
            - df["Close"].iloc[-2]
        )
        /
        df["Close"].iloc[-2]
    ) * 100

    with m1:

        st.metric(
            "Current",
            f"{analysis['current']:,.2f}"
        )

        st.metric(
            "Today's Change",
            f"{day_change:.2f}%"
        )

    with m2:

        st.metric(
            "ATH",
            f"{analysis['ath']:,.2f}"
        )

        st.metric(
            "Below ATH",
            f"{analysis['below_ath']:.2f}%"
        )

    with m3:

        st.metric(
            "52W Low",
            f"{analysis['low52']:,.2f}"
        )

        st.metric(
            "52W Position",
            f"{analysis['position52']:.1f}%"
        )

    # ------------------------------------------------------
    # CHART
    # ------------------------------------------------------

    st.subheader("📈 6 Month Trend")

    st.plotly_chart(
        trend_chart(df),
        use_container_width=True,
        config={
            "displayModeBar": False,
            "scrollZoom": False,
            "doubleClick": False
        }
    )

    # ------------------------------------------------------
    # ANALYSIS
    # ------------------------------------------------------

    st.subheader("Investment Analysis")

    c1, c2, c3 = st.columns(3)

    with c1:

        st.metric(
            "Investment Stage",
            analysis["stage"]
        )

    with c2:

        st.metric(
            "Momentum",
            f"{analysis['momentum']}/100"
        )

    with c3:

        st.metric(
            "Analysis Confidence",
            f"{analysis['confidence']}%"
        )

    # ------------------------------------------------------
    # KEY INSIGHTS
    # ------------------------------------------------------

    st.subheader("Key Insights")

    for insight in analysis["insights"]:

        st.markdown(f"✅ {insight}")

    # ------------------------------------------------------
    # ENGINE BREAKDOWN
    # ------------------------------------------------------

    with st.expander("Analysis Breakdown"):

        score_df = pd.DataFrame({

            "Metric": [
                "Trend",
                "Market Structure",
                "Momentum",
                "Stability",
                "Pullback Quality",
                "Recovery Strength"
            ],

            "Score": [
                analysis["trend"],
                analysis["structure"],
                analysis["momentum"],
                analysis["stability"],
                analysis["pullback"],
                analysis["recovery"]
            ]

        })

        st.dataframe(
            score_df,
            use_container_width=True,
            hide_index=True
        )

        st.markdown("---")

        s1, s2 = st.columns(2)

        with s1:

            st.write(
                f"**Current:** {analysis['current']:,.2f}"
            )

            st.write(
                f"**ATH:** {analysis['ath']:,.2f}"
            )

            st.write(
                f"**52W High:** {analysis['high52']:,.2f}"
            )

            st.write(
                f"**52W Low:** {analysis['low52']:,.2f}"
            )

        with s2:

            st.write(
                f"**Below ATH:** {analysis['below_ath']:.2f}%"
            )

            st.write(
                f"**52W Position:** {analysis['position52']:.2f}%"
            )

            st.write(
                f"**Volatility:** {analysis['volatility']:.2f}%"
            )

            st.write(
                f"**Confidence:** {analysis['confidence']}%"
            )

st.markdown("---")

st.info(
    "The Investment Stage is derived from six months of historical price action using market structure, trend quality, momentum, pullback behaviour, recovery strength and stability. This analysis is intended as research support and not investment advice."
)







    
    
    
    