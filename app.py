import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(layout="wide")
st.title("📉 US Market Risk Signal Dashboard")
st.caption("Detect potential drawdown signals before investing in US equities")

# -----------------------
# Sidebar
# -----------------------
period = st.sidebar.selectbox(
    "Analysis Period",
    ["1mo", "3mo", "6mo", "1y", "3y"]
)

interval_map = {
    "1mo": "1d",
    "3mo": "1d",
    "6mo": "1d",
    "1y": "1d",
    "3y": "1wk"
}

interval = interval_map[period]

# -----------------------
# Assets (role-based)
# -----------------------
assets = {
    "S&P 500 (Market Core)": "^GSPC",
    "Nasdaq (Growth Risk)": "^IXIC",
    "Bitcoin (High Risk Lead)": "BTC-USD",
    "Gold (Safe Haven)": "GC=F"
}

@st.cache_data
def load_close(ticker):
    df = yf.download(ticker, period=period, interval=interval, progress=False)
    return df["Close"]

data = pd.DataFrame()

for name, ticker in assets.items():
    s = load_close(ticker)
    if not s.empty:
        data[name] = s

data = data.dropna()

# Normalize
normalized = data / data.iloc[0] * 100

# -----------------------
# Main Trend Chart
# -----------------------
fig = go.Figure()

for col in normalized.columns:
    fig.add_trace(
        go.Scatter(
            x=normalized.index,
            y=normalized[col],
            name=col,
            mode="lines"
        )
    )

fig.update_layout(
    height=600,
    hovermode="x unified",
    yaxis_title="Relative Performance (Base = 100)",
    template="plotly_white"
)

st.plotly_chart(fig, use_container_width=True)

# -----------------------
# Interpretation Guide
# -----------------------
st.markdown("## 🔍 How to read this chart (Trader perspective)")

st.markdown("""
- **Bitcoin falls first** → Risk-off signal may be forming  
- **Nasdaq underperforms S&P500** → Growth stocks losing strength  
- **Gold rises while stocks stall** → Capital moving to safety  
- **S&P500 breaks trend last** → Often confirms real drawdown phase  

This dashboard is designed to help you **delay entry or reduce exposure**
when early warning signals appear.
""")

st.warning(
    "This is NOT a buy/sell tool. "
    "Use it to adjust exposure timing before entering US equities."
)
