import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import datetime
from scipy.signal import argrelextrema

st.set_page_config(
    page_title="Investment Analysis",
    layout="wide"
)

st.title("📊 Investment Analysis")
st.caption("Investment Stage Analysis based on the last 6 months of market behaviour.")

# ============================================================
# INDEX MAP
# ============================================================

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

# ============================================================
# DATA
# ============================================================

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


# ============================================================
# CHART
# ============================================================

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


# ============================================================
# ANALYSIS ENGINE
# ============================================================

def analyse(df):

    close = df["Close"].copy()

    current = float(close.iloc[-1])

    high52 = float(close.max())

    low52 = float(close.min())

    ath = high52

    below_ath = ((ath-current)/ath)*100

    position52 = ((current-low52)/(high52-low52))*100
    
        # ======================================================
    # TREND QUALITY
    # ======================================================

    sma20 = close.rolling(20).mean()

    sma50 = close.rolling(50).mean()

    trend_score = 0

    if current > sma20.iloc[-1]:
        trend_score += 25

    if current > sma50.iloc[-1]:
        trend_score += 25

    if sma20.iloc[-1] > sma50.iloc[-1]:
        trend_score += 25

    if sma50.iloc[-1] > sma50.iloc[-10]:
        trend_score += 25

    # ======================================================
    # MARKET STRUCTURE
    # ======================================================

    maxima = argrelextrema(
        close.values,
        np.greater,
        order=5
    )[0]

    minima = argrelextrema(
        close.values,
        np.less,
        order=5
    )[0]

    swing_highs = close.iloc[maxima].tail(5).tolist()

    swing_lows = close.iloc[minima].tail(5).tolist()

    structure_score = 50

    higher_highs = False

    higher_lows = False

    if len(swing_highs) >= 3:

        higher_highs = (

            swing_highs[-1] >
            swing_highs[-2] >
            swing_highs[-3]

        )

    if len(swing_lows) >= 3:

        higher_lows = (

            swing_lows[-1] >
            swing_lows[-2] >
            swing_lows[-3]

        )

    if higher_highs:
        structure_score += 25

    if higher_lows:
        structure_score += 25

    structure_score = min(structure_score,100)

    # ======================================================
    # MOMENTUM
    # ======================================================

    monthly_returns = []

    for d in [21,42,63,84,105,126]:

        if len(close) > d:

            monthly_returns.append(

                (
                    current /
                    float(close.iloc[-d])
                    -1
                )*100

            )

    acceleration = 0

    consistency = 0

    if len(monthly_returns) >= 6:

        for i in range(1,6):

            if monthly_returns[i] > monthly_returns[i-1]:

                acceleration += 1

        positive = sum(
            r > 0
            for r in monthly_returns
        )

        consistency = positive / 6

    momentum_score = int(

        (
            (acceleration/5)*70

        ) +

        (

            consistency*30

        )

    )

    # ======================================================
    # PULLBACK QUALITY
    # ======================================================

    rolling_high = close.cummax()

    drawdown = (

        (rolling_high-close)

        /

        rolling_high

    )*100

    max_drawdown = drawdown.max()

    pullback_score = 100

    if max_drawdown > 8:
        pullback_score = 80

    if max_drawdown > 12:
        pullback_score = 60

    if max_drawdown > 18:
        pullback_score = 40

    if max_drawdown > 25:
        pullback_score = 20
        
            # ======================================================
    # RECOVERY STRENGTH
    # ======================================================

    recovery_score = 50

    recent_drawdown = drawdown.tail(60)

    deepest = recent_drawdown.max()

    if deepest < 5:

        recovery_score = 100

    elif deepest < 8:

        recovery_score = 85

    elif deepest < 12:

        recovery_score = 70

    elif deepest < 18:

        recovery_score = 50

    else:

        recovery_score = 30

    # ======================================================
    # EXTENSION
    # ======================================================

    extension = (

        (current - sma50.iloc[-1])

        /

        sma50.iloc[-1]

    ) * 100

    extension_score = 100

    if extension > 5:

        extension_score = 85

    if extension > 10:

        extension_score = 70

    if extension > 15:

        extension_score = 50

    if extension > 20:

        extension_score = 30

    # ======================================================
    # STABILITY
    # ======================================================

    volatility = (

        close.pct_change()

        .rolling(20)

        .std()

        .iloc[-1]

    ) * 100

    stability_score = 100

    if volatility > 1:

        stability_score = 85

    if volatility > 1.5:

        stability_score = 70

    if volatility > 2:

        stability_score = 50

    if volatility > 3:

        stability_score = 30

    # ======================================================
    # INVESTMENT STAGE ENGINE
    # ======================================================

    stage = "Weak Trend"

    if trend_score < 50 or structure_score < 50:

        stage = "Weak Trend"

    elif (

        trend_score >= 70

        and structure_score >= 75

        and momentum_score >= 70

        and recovery_score >= 70

        and extension_score >= 80

    ):

        stage = "Early Accumulation"

    elif (

        trend_score >= 80

        and structure_score >= 80

        and momentum_score >= 75

        and recovery_score >= 70

        and extension_score >= 50

    ):

        stage = "Expansion"

    elif (

        trend_score >= 70

        and structure_score >= 70

        and momentum_score >= 45

    ):

        stage = "Mature Trend"

    else:

        stage = "Exhaustion"

    # ======================================================
    # ANALYSIS CONFIDENCE
    # ======================================================

    supporting_signals = []

    supporting_signals.append(trend_score >= 70)
    supporting_signals.append(structure_score >= 70)
    supporting_signals.append(momentum_score >= 60)
    supporting_signals.append(recovery_score >= 60)
    supporting_signals.append(extension_score >= 60)
    supporting_signals.append(stability_score >= 60)
    supporting_signals.append(pullback_score >= 60)

    confidence = int(

        (

            sum(supporting_signals)

            /

            len(supporting_signals)

        ) * 100

    )

    # ======================================================
    # KEY INSIGHTS
    # ======================================================

    insights = []

    if trend_score >= 80:
        insights.append(
            "Trend remains healthy with price trading above key moving averages."
        )

    if higher_highs:
        insights.append(
            "Higher highs indicate buyers continue to push prices upward."
        )

    if higher_lows:
        insights.append(
            "Higher lows suggest accumulation on market declines."
        )

    if momentum_score >= 70:
        insights.append(
            "Momentum has strengthened consistently over the last six months."
        )

    elif momentum_score >= 50:
        insights.append(
            "Momentum remains positive but is no longer accelerating."
        )

    else:
        insights.append(
            "Momentum has weakened and requires monitoring."
        )

    if pullback_score >= 80:
        insights.append(
            "Recent corrections have remained shallow and well supported."
        )

    if recovery_score >= 80:
        insights.append(
            "The market has recovered quickly after recent pullbacks."
        )

    if extension_score <= 50:
        insights.append(
            "Price is becoming extended above its long-term trend."
        )

    elif below_ath > 10:
        insights.append(
            f"The index is still {below_ath:.1f}% below its recent high, leaving room for further upside."
        )
        
            # ======================================================
    # RETURN
    # ======================================================

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

        "pullback": pullback_score,

        "recovery": recovery_score,

        "extension": extension_score,

        "stability": stability_score,

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

default_selection = [
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
        default=default_selection
    )

if len(selected_indices) == 0:

    st.stop()


# ==========================================================
# MAIN LOOP
# ==========================================================

for index_name in selected_indices:

    st.markdown("---")

    st.header(index_name)

    df = get_data(symbols[index_name])

    if df is None:

        st.warning("Unable to fetch data.")

        continue

    analysis = analyse(df)

    # ------------------------------------------------------
    # SUMMARY
    # ------------------------------------------------------

    c1, c2, c3 = st.columns(3)

    day_change = (

        (
            df["Close"].iloc[-1]

            -

            df["Close"].iloc[-2]

        )

        /

        df["Close"].iloc[-2]

    ) * 100

    with c1:

        st.metric(

            "Current",

            f"{analysis['current']:,.2f}"

        )

        st.metric(

            "Today's Change",

            f"{day_change:.2f}%"

        )

    with c2:

        st.metric(

            "ATH",

            f"{analysis['ath']:,.2f}"

        )

        st.metric(

            "Below ATH",

            f"{analysis['below_ath']:.2f}%"

        )

    with c3:

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

    a1, a2, a3 = st.columns(3)

    with a1:

        st.metric(

            "Investment Stage",

            analysis["stage"]

        )

    with a2:

        st.metric(

            "Momentum",

            f"{analysis['momentum']}/100"

        )

    with a3:

        st.metric(

            "Analysis Confidence",

            f"{analysis['confidence']}%"

        )

    # ------------------------------------------------------
    # INSIGHTS
    # ------------------------------------------------------

    st.subheader("Key Insights")

    for insight in analysis["insights"]:

        st.markdown(f"✅ {insight}")

    # ------------------------------------------------------
    # TECHNICAL BREAKDOWN
    # ------------------------------------------------------

    with st.expander("Technical Breakdown"):

        score_df = pd.DataFrame({

            "Metric": [

                "Trend Quality",

                "Market Structure",

                "Momentum",

                "Pullback Quality",

                "Recovery Strength",

                "Extension",

                "Stability"

            ],

            "Score": [

                analysis["trend"],

                analysis["structure"],

                analysis["momentum"],

                analysis["pullback"],

                analysis["recovery"],

                analysis["extension"],

                analysis["stability"]

            ]

        })

        st.dataframe(

            score_df,

            use_container_width=True,

            hide_index=True

        )

st.markdown("---")

st.info(

    "Investment Stage is determined using seven independent signals: Trend Quality, "
    "Market Structure, Momentum, Pullback Quality, Recovery Strength, Extension and Stability. "
    "Analysis is based on the previous six months of historical market behaviour."

)
        
        
    
    
    
    