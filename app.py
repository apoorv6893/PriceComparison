import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import datetime
import plotly.graph_objects as go
import plotly.express as px
from datetime import timedelta

# ========== PAGE CONFIG & STYLING ==========
st.set_page_config(
    page_title="Global Market Dashboard | Professional",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "About": "Professional Market Analysis Dashboard v1.0"
    }
)

# Custom CSS Styling
st.markdown("""
    <style>
        /* Main background */
        .main { background-color: #f8f9fa; }
        
        /* Headers styling */
        h1 { color: #1a1a2e; font-weight: 700; text-align: center; margin-bottom: 30px; }
        h2 { color: #16213e; font-weight: 600; border-bottom: 3px solid #0f3460; padding-bottom: 10px; }
        h3 { color: #16213e; font-weight: 500; }
        
        /* Metric card styling */
        .metric-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }
        
        /* Section containers */
        .section-container {
            background: white;
            padding: 25px;
            border-radius: 12px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
            margin: 20px 0;
            border-left: 4px solid #0f3460;
        }
        
        /* Filter panel */
        .filter-panel {
            background: linear-gradient(to right, #f5f7fa, #c3cfe2);
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
            border: 1px solid #e0e7ff;
        }
        
        /* Button styling */
        .stButton > button {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 10px 30px;
            border-radius: 6px;
            font-weight: 600;
            transition: all 0.3s ease;
        }
        
        .stButton > button:hover {
            box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
            transform: translateY(-2px);
        }
        
        /* Chart container */
        .chart-container {
            background: white;
            padding: 15px;
            border-radius: 10px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.04);
        }
        
        /* Alert messages */
        .stWarning, .stError { 
            background: #fff3cd !important; 
            border-left: 4px solid #ffc107 !important;
        }
        
        .stSuccess { 
            background: #d4edda !important; 
            border-left: 4px solid #28a745 !important;
        }
        
        .stInfo { 
            background: #d1ecf1 !important; 
            border-left: 4px solid #17a2b8 !important;
        }
        
        /* Tabs styling */
        .stTabs [data-baseweb="tab-list"] {
            gap: 2px;
        }
        
        .stTabs [data-baseweb="tab"] {
            background: #f0f2f6;
            border-radius: 6px 6px 0 0;
        }
        
        .stTabs [aria-selected="true"] {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white !important;
        }
        
        /* Sidebar */
        .sidebar .sidebar-content { background: #f8f9fa; }
        
        /* Radio buttons */
        .stRadio > label { font-weight: 500; color: #16213e; }
        
        /* Multiselect */
        .stMultiSelect { border-radius: 6px; }
        
    </style>
""", unsafe_allow_html=True)

# ========== HELPER FUNCTIONS ==========

@st.cache_data
def get_data(ticker, start, end, interval):
    """Fetch market data with error handling"""
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
        data["MA_20"] = data["Close"].rolling(window=20).mean()
        data["MA_50"] = data["Close"].rolling(window=50).mean()
        return data
    except:
        return None

def get_quick_range(option):
    """Convert quick select options to date ranges"""
    end = datetime.date.today()
    ranges = {
        "1M": 30,
        "2M": 60,
        "6M": 180,
        "1Y": 365,
        "3Y": 365 * 3,
        "5Y": 365 * 5
    }
    start = end - timedelta(days=ranges.get(option, 30))
    return start, end

def calculate_metrics(data):
    """Calculate key metrics for display"""
    if data is None or data.empty:
        return None
    
    current_price = data["Close"].iloc[-1]
    prev_price = data["Close"].iloc[0]
    change = current_price - prev_price
    change_pct = (change / prev_price) * 100
    
    return {
        "current": current_price,
        "change": change,
        "change_pct": change_pct,
        "high": data["Close"].max(),
        "low": data["Close"].min(),
        "avg_return": data["Returns"].mean() * 100
    }

def plot_professional_chart(data, title, symbol):
    """Create professional-grade Plotly chart"""
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
    
    # Candlestick or Line chart
    fig.add_trace(
        go.Scatter(
            x=data.index,
            y=data["Close"],
            mode="lines",
            name=f"{title} Price",
            line=dict(color="#667eea", width=2.5),
            hovertemplate="<b>%{x|%b %d, %Y}</b><br>Price: $%{y:.2f}<extra></extra>"
        )
    )
    
    # Add Moving Averages if available
    if "MA_20" in data.columns:
        fig.add_trace(
            go.Scatter(
                x=data.index,
                y=data["MA_20"],
                mode="lines",
                name="MA 20",
                line=dict(color="rgba(255, 165, 0, 0.7)", width=1.5, dash="dash"),
                hovertemplate="<b>MA 20</b><br>%{y:.2f}<extra></extra>"
            )
        )
    
    if "MA_50" in data.columns:
        fig.add_trace(
            go.Scatter(
                x=data.index,
                y=data["MA_50"],
                mode="lines",
                name="MA 50",
                line=dict(color="rgba(255, 20, 147, 0.7)", width=1.5, dash="dash"),
                hovertemplate="<b>MA 50</b><br>%{y:.2f}<extra></extra>"
            )
        )
    
    fig.update_layout(
        title=dict(text=f"<b>{title} Price Analysis</b>", x=0.5, xanchor="center"),
        height=450,
        template="plotly_white",
        hovermode="x unified",
        xaxis=dict(
            showgrid=True,
            gridwidth=1,
            gridcolor="rgba(0,0,0,0.05)",
            zeroline=False
        ),
        yaxis=dict(
            showgrid=True,
            gridwidth=1,
            gridcolor="rgba(0,0,0,0.05)",
            zeroline=False,
            title="Price ($)"
        ),
        margin=dict(l=60, r=30, t=50, b=40),
        font=dict(family="Arial, sans-serif", size=11, color="#16213e"),
        plot_bgcolor="rgba(255,255,255,0.5)",
        paper_bgcolor="white"
    )
    
    fig.update_xaxes(showline=True, linewidth=1, linecolor="rgba(0,0,0,0.1)")
    fig.update_yaxes(showline=True, linewidth=1, linecolor="rgba(0,0,0,0.1)")
    
    return fig

def plot_correlation_heatmap(corr):
    """Professional correlation heatmap"""
    fig = px.imshow(
        corr,
        text_auto=".2f",
        color_continuous_scale="RdBu",
        zmin=-1,
        zmax=1,
        aspect="auto",
        title="<b>Asset Correlation Matrix</b>",
        labels=dict(color="Correlation")
    )
    
    fig.update_layout(
        height=500,
        template="plotly_white",
        font=dict(family="Arial, sans-serif", size=11),
        title=dict(x=0.5, xanchor="center"),
        plot_bgcolor="white"
    )
    
    return fig

# ========== HEADER & NAVIGATION ==========
col1, col2, col3 = st.columns([1, 3, 1])
with col2:
    st.markdown("""
        <div style='text-align: center;'>
            <h1 style='margin-bottom: 10px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                       -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-size: 48px;'>
                📊 Global Market Dashboard
            </h1>
            <p style='color: #666; font-size: 14px; margin-top: -20px;'>Professional Financial Analysis Platform</p>
        </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# ========== SIDEBAR ==========
with st.sidebar:
    st.markdown("### ⚙️ Dashboard Settings")
    
    theme = st.radio(
        "Select Theme",
        ["Light", "Dark (Coming Soon)"],
        index=0
    )
    
    st.markdown("---")
    st.markdown("### 📍 Asset Categories")
    st.markdown("""
    - **Indian Indices**: NIFTY 50, SENSEX, BANK NIFTY
    - **US Indices**: S&P 500, NASDAQ, DOW JONES
    - **Asian Indices**: NIKKEI 225, HANG SENG, SHANGHAI
    - **Commodities**: GOLD, CRUDE OIL
    """)
    
    st.markdown("---")
    st.markdown("### 📌 Quick Links")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("[Yahoo Finance](https://finance.yahoo.com)")
    with col2:
        st.markdown("[NSE India](https://www.nseindia.com)")

# ========== SYMBOL MAPPING ==========
symbols = {
    "🇮🇳 NIFTY 50": "^NSEI",
    "🇮🇳 SENSEX": "^BSESN",
    "🇮🇳 BANK NIFTY": "^NSEBANK",
    "🇺🇸 S&P 500": "^GSPC",
    "🇺🇸 NASDAQ": "^IXIC",
    "🇺🇸 DOW JONES": "^DJI",
    "🇯🇵 NIKKEI 225": "^N225",
    "🇭🇰 HANG SENG": "^HSI",
    "🇨🇳 SHANGHAI": "000001.SS",
    "🏆 GOLD": "GC=F",
    "⛽ CRUDE OIL": "CL=F"
}

interval_map = {
    "4H": "1h",
    "1D": "1d",
    "1M": "1d",
    "1Y": "1d"
}

# ========== TAB NAVIGATION ==========
tab1, tab2, tab3 = st.tabs(["📈 Market Trends", "🔗 Correlation Analysis", "📊 Statistics"])

# ========== TAB 1: MARKET TRENDS ==========
with tab1:
    st.markdown("### 📈 Market Trends Analysis")
    
    with st.container():
        st.markdown('<div class="filter-panel">', unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            quick_option = st.selectbox(
                "Quick Select Duration",
                ["1M", "2M", "6M", "1Y", "3Y", "5Y"],
                index=2
            )
        
        with col2:
            start_date, end_date = get_quick_range(quick_option)
            start_date = st.date_input("Start Date", start_date, key="start_trends")
        
        with col3:
            end_date = st.date_input("End Date", end_date, key="end_trends")
        
        col1, col2 = st.columns(2)
        with col1:
            select_all = st.checkbox("📌 Select All Assets", value=False, key="select_all_trends")
        
        with col2:
            if select_all:
                selected_assets = list(symbols.keys())
            else:
                selected_assets = st.multiselect(
                    "Select Assets",
                    list(symbols.keys()),
                    default=["🇮🇳 NIFTY 50", "🇺🇸 S&P 500", "🇺🇸 NASDAQ"]
                )
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    if not selected_assets:
        st.info("👉 Please select at least one asset to display charts")
    else:
        for i in range(0, len(selected_assets), 2):
            cols = st.columns(2)
            
            for j in range(2):
                if i + j < len(selected_assets):
                    asset = selected_assets[i + j]
                    
                    with cols[j]:
                        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
                        
                        col_a, col_b, col_c, col_d = st.columns([2, 1, 1, 1])
                        
                        with col_a:
                            st.markdown(f"**{asset}**")
                        
                        with col_b:
                            interval_label = st.radio(
                                "Interval",
                                ["4H", "1D", "1M", "1Y"],
                                horizontal=True,
                                key=f"interval_{asset}",
                                label_visibility="collapsed"
                            )
                        
                        interval = interval_map[interval_label]
                        data = get_data(symbols[asset], start_date, end_date, interval)
                        metrics = calculate_metrics(data)
                        
                        if metrics:
                            col_price, col_change, col_high, col_low = st.columns(4)
                            
                            with col_price:
                                st.metric("Price", f"${metrics['current']:.2f}")
                            with col_change:
                                st.metric(
                                    "Change",
                                    f"${metrics['change']:.2f}",
                                    f"{metrics['change_pct']:.2f}%",
                                    delta_color="inverse" if metrics['change_pct'] < 0 else "normal"
                                )
                            with col_high:
                                st.metric("52W High", f"${metrics['high']:.2f}")
                            with col_low:
                                st.metric("52W Low", f"${metrics['low']:.2f}")
                        
                        fig = plot_professional_chart(data, asset, symbols[asset])
                        
                        if fig:
                            st.plotly_chart(
                                fig,
                                use_container_width=True,
                                config={
                                    "scrollZoom": False,
                                    "displayModeBar": True,
                                    "doubleClick": "autosize",
                                    "toImageButtonOptions": {"format": "png", "filename": f"{asset}_chart"}
                                }
                            )
                        else:
                            st.warning(f"⚠️ Unable to fetch data for {asset}")
                        
                        st.markdown('</div>', unsafe_allow_html=True)

# ========== TAB 2: CORRELATION ANALYSIS ==========
with tab2:
    st.markdown("### 🔗 Correlation Analysis")
    
    with st.container():
        st.markdown('<div class="filter-panel">', unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            quick_option_corr = st.selectbox(
                "Quick Select Duration (Correlation)",
                ["1M", "2M", "6M", "1Y", "3Y", "5Y"],
                index=2,
                key="corr_quick_select"
            )
        
        with col2:
            start_date_corr, end_date_corr = get_quick_range(quick_option_corr)
            start_date_corr = st.date_input("Start Date", start_date_corr, key="start_corr")
        
        with col3:
            end_date_corr = st.date_input("End Date", end_date_corr, key="end_corr")
        
        select_all_corr = st.checkbox("📌 Select All Assets (Correlation)", value=False, key="select_all_corr")
        
        if select_all_corr:
            selected_corr_assets = list(symbols.keys())[:8]
        else:
            selected_corr_assets = st.multiselect(
                "Select Assets for Correlation",
                list(symbols.keys()),
                default=["🇮🇳 NIFTY 50", "🇺🇸 S&P 500", "🏆 GOLD"],
                key="corr_multiselect"
            )
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    if len(selected_corr_assets) > 8:
        st.warning(f"⚠️ Maximum 8 assets allowed. Showing first 8 assets.")
        selected_corr_assets = selected_corr_assets[:8]
    
    if len(selected_corr_assets) < 2:
        st.info("👉 Please select at least 2 assets to perform correlation analysis")
    else:
        with st.spinner("📊 Calculating correlations..."):
            df = pd.DataFrame()
            
            for asset in selected_corr_assets:
                data = get_data(symbols[asset], start_date_corr, end_date_corr, "1d")
                if data is not None:
                    df[asset] = data["Returns"]
            
            df = df.dropna()
            
            if df.empty:
                st.error("❌ Not enough overlapping data for selected assets")
            else:
                corr = df.corr()
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("#### 📊 Correlation Matrix")
                    st.dataframe(
                        corr.style.format("{:.3f}").background_gradient(cmap="RdBu_r", vmin=-1, vmax=1),
                        use_container_width=True
                    )
                
                with col2:
                    st.markdown("#### 📈 Key Correlations")
                    corr_values = []
                    for i in range(len(corr.columns)):
                        for j in range(i+1, len(corr.columns)):
                            corr_values.append({
                                "Asset 1": corr.columns[i],
                                "Asset 2": corr.columns[j],
                                "Correlation": corr.iloc[i, j]
                            })
                    
                    corr_df = pd.DataFrame(corr_values).sort_values("Correlation", ascending=False)
                    st.dataframe(corr_df.style.format({"Correlation": "{:.3f}"}), use_container_width=True, hide_index=True)
                
                st.markdown("---")
                
                st.markdown("#### 🔥 Heatmap Visualization")
                fig = plot_correlation_heatmap(corr)
                st.plotly_chart(fig, use_container_width=True)
                
                st.markdown("#### 📉 Returns Comparison")
                fig_returns = go.Figure()
                for col in df.columns:
                    fig_returns.add_trace(
                        go.Scatter(
                            x=df.index,
                            y=df[col],
                            mode="lines",
                            name=col,
                            hovertemplate="<b>%{x|%b %d}</b><br>Return: %{y:.4f}<extra></extra>"
                        )
                    )
                
                fig_returns.update_layout(
                    title="<b>Daily Returns Comparison</b>",
                    height=400,
                    template="plotly_white",
                    hovermode="x unified",
                    yaxis_title="Daily Return",
                    font=dict(family="Arial, sans-serif", size=11)
                )
                
                st.plotly_chart(fig_returns, use_container_width=True)

# ========== TAB 3: STATISTICS ==========
with tab3:
    st.markdown("### 📊 Statistical Summary")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Select Asset for Statistics")
        stat_asset = st.selectbox(
            "Choose Asset",
            list(symbols.keys()),
            key="stat_asset"
        )
        
        stat_period = st.radio(
            "Select Period",
            ["1M", "3M", "6M", "1Y"],
            horizontal=True,
            key="stat_period"
        )
    
    with col2:
        start_stat, end_stat = get_quick_range(stat_period)
        stat_data = get_data(symbols[stat_asset], start_stat, end_stat, "1d")
        
        if stat_data is not None and not stat_data.empty:
            st.markdown(f"#### {stat_asset} Statistics ({stat_period})")
            
            stats_dict = {
                "Mean Return": f"{stat_data['Returns'].mean() * 100:.4f}%",
                "Std Deviation": f"{stat_data['Returns'].std() * 100:.4f}%",
                "Sharpe Ratio": f"{(stat_data['Returns'].mean() / stat_data['Returns'].std()) if stat_data['Returns'].std() > 0 else 0:.4f}",
                "Max Daily Gain": f"{stat_data['Returns'].max() * 100:.4f}%",
                "Max Daily Loss": f"{stat_data['Returns'].min() * 100:.4f}%",
                "Win Rate": f"{(stat_data['Returns'] > 0).sum() / len(stat_data['Returns']) * 100:.2f}%"
            }
            
            for key, value in stats_dict.items():
                st.metric(key, value)
        else:
            st.error("Unable to fetch data for statistics")

# ========== FOOTER ==========
st.markdown("---")
st.markdown("""
    <div style='text-align: center; color: #666; font-size: 12px; padding: 20px;'>
        <p>📊 Global Market Dashboard | Professional Financial Analysis Platform</p>
        <p>Data powered by Yahoo Finance | Last updated: """ + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + """</p>
        <p>⚠️ Disclaimer: This dashboard is for informational purposes only. Not financial advice.</p>
    </div>
""", unsafe_allow_html=True)
