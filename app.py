import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="Asset Trend Comparison", layout="wide")

st.title("📈 Bitcoin vs S&P500 vs Nasdaq vs Gold")
st.caption("Normalized trend comparison (base = 100)")

# -----------------------------
# Sidebar controls
# -----------------------------
timeframe = st.sidebar.selectbox(
    "Timeframe",
    ["1Y", "3Y", "5Y", "MAX"]
)

interval_map = {
    "1Y": "1d",
    "3Y": "1d",
    "5Y": "1d",
    "MAX": "1wk"
}

period_map = {
    "1Y": "1y",
    "3Y": "3y",
    "5Y": "5y",
    "MAX": "max"
}

interval = interval_map[timeframe]
period = period_map[timeframe]

# -----------------------------
# Tickers
# -----------------------------
tickers = {
    "Bitcoin": "BTC-USD",
    "S&P 500": "^GSPC",
    "Nasdaq": "^IXIC",
    "Gold": "GC=F"
}

@st.cache_data
def load_data(ticker, period, interval):
    df = yf.download(ticker, period=period, interval=interval, progress=False)
    return df["Close"]

# -----------------------------
# Load & normalize
# -----------------------------
data = pd.DataFrame()

for name, ticker in tickers.items():
    series = load_data(ticker, period, interval)
    if not series.empty:
        data[name] = series

# 날짜 정렬 & 결측 제거
data = data.dropna()
data = data / data.iloc[0] * 100  # Normalize to 100

# -----------------------------
# Plot
# -----------------------------
fig = go.Figure()

for col in data.columns:
    fig.add_trace(
        go.Scatter(
            x=data.index,
            y=data[col],
            mode="lines",
            name=col
        )
    )

fig.update_layout(
    height=600,
    xaxis_title="Date",
    yaxis_title="Normalized Value (Base = 100)",
    hovermode="x unified",
    template="plotly_white"
)

st.plotly_chart(fig, use_container_width=True)

st.info(
    "All assets are normalized to 100 at the starting point "
    "to clearly compare long-term trends."
)
