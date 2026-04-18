# 📊 Global Market Dashboard

A professional-grade financial market analysis platform built with Streamlit, featuring real-time market data visualization, correlation analysis, and statistical insights.

## ✨ Features

### 📈 Market Trends
- Real-time price tracking for 11+ global indices and commodities
- Interactive charts with moving averages (MA 20 & MA 50)
- Multi-timeframe analysis (4H, 1D, 1M, 1Y)
- Key metrics display (Price, Change %, High, Low)
- Country-flagged asset labels for better UX

### 🔗 Correlation Analysis
- Calculate correlations between multiple assets
- Professional heatmap visualization
- Key correlation matrix display
- Daily returns comparison charts
- Support for up to 8 assets simultaneously

### 📊 Statistical Analysis
- Mean returns calculation
- Volatility (Standard Deviation)
- Sharpe Ratio computation
- Maximum daily gains/losses
- Win rate percentage

### 🎨 Professional UI/UX
- Modern gradient-based design system
- Dark theme ready
- Responsive tab-based navigation
- Custom CSS styling with hover effects
- Professional metric cards
- Mobile-optimized charts

## 🏆 Asset Coverage

**Indian Indices:**
- NIFTY 50 (🇮🇳)
- SENSEX (🇮🇳)
- BANK NIFTY (🇮🇳)

**US Indices:**
- S&P 500 (🇺🇸)
- NASDAQ (🇺🇸)
- DOW JONES (🇺🇸)

**Asian Indices:**
- NIKKEI 225 (🇯🇵)
- HANG SENG (🇭🇰)
- SHANGHAI (🇨🇳)

**Commodities:**
- GOLD (🏆)
- CRUDE OIL (⛽)

## 🚀 Installation

```bash
# Clone the repository
git clone https://github.com/apoorv6893/PriceComparison.git
cd PriceComparison

# Install dependencies
pip install -r requirements.txt

# Run the application
streamlit run app.py
```

## 📋 Requirements

- Python 3.8+
- streamlit >= 1.28.0
- yfinance >= 0.2.0
- pandas >= 1.5.0
- numpy >= 1.23.0
- plotly >= 5.0.0
- matplotlib >= 3.5.0

## 🎯 Quick Start

1. Launch the dashboard:
   ```bash
   streamlit run app.py
   ```

2. **Market Trends Tab:**
   - Select your preferred time period (1M - 5Y)
   - Choose assets to analyze
   - Adjust time intervals for each asset
   - View key metrics and interactive charts

3. **Correlation Analysis Tab:**
   - Select 2-8 assets
   - Analyze correlation strength
   - View heatmap and returns comparison

4. **Statistics Tab:**
   - Select an asset
   - Choose analysis period
   - View detailed statistical metrics

## 🔗 Data Source

Market data is powered by **Yahoo Finance** via the `yfinance` library, providing real-time and historical pricing data.

## 📱 Responsive Design

- Optimized for desktop viewing
- Professional layout with proper spacing
- Download chart capability
- Interactive hover tooltips

## ⚠️ Disclaimer

This dashboard is for informational purposes only and should not be considered as financial advice. Always consult with a financial advisor before making investment decisions.

## 📧 Contact

For questions or suggestions, please open an issue on GitHub.

## 📄 License

This project is open source and available under the MIT License.

---

**Last Updated:** 2026-04-18 | **Version:** 2.0 (Professional UI)