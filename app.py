import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(layout="wide")
st.title("📉 US Market Risk Signal Dashboard")

# -----------------------
# Sidebar
# -----------------------
period = st.sidebar.selectbox(
    "Analysis Period",
    ["1mo", "3mo", "6mo", "1y", "3y"],
    index=3
)

interval = "1d"

# -----------------------
# Assets
# -----------------------
assets = {
    "S&P 500": "^GSPC",
    "Nasdaq": "^IXIC",
    "Bitcoin": "BTC-USD",
    "Gold": "GC=F"
}

@st.cache_data
def load_data(period):
    series_list = []

    for name, ticker in assets.items():
        df = yf.download(
            ticker,
            period=period,
            interval=interval,
            progress=False
        )

        if not df.empty:
            s = df["Close"].rename(name)
            series_list.append(s)

    # OUTER JOIN (중요!)
    price_df = pd.concat(series_list, axis=1, join="outer")

    # 날짜 정렬
    price_df = price_df.sort_index()

    return price_df

price_df = load_data(period)

# -----------------------
# Normalize (자산별 첫 유효값 기준)
# -----------------------
normalized = price_df.copy()

for col in normalized.columns:
    first_valid = normalized[col].dropna().iloc[0]
    normalized[col] = normalized[col] / first_valid * 100

# -----------------------
# Plot
# -----------------------
fig = go.Figure()

for col in normalized.columns:
    fig.add_trace(
        go.Scatter(
            x=normalized.index,
            y=normalized[col],
            name=col,
            mode="lines",
            line=dict(width=2),
            connectgaps=True
        )
    )

fig.update_layout(
    height=650,
    hovermode="x unified",
    template="plotly_white",
    yaxis_title="Relative Performance (Base = 100)"
)

st.plotly_chart(fig, use_container_width=True)

# -----------------------
# Interpretation
# -----------------------
st.markdown("""
### 📌 How to use this (US stock investor perspective)

- **Bitcoin weakens first** → speculative risk is leaving
- **Nasdaq underperforms S&P500** → growth stocks vulnerable
- **Gold rises while equities stall** → defensive positioning
- **S&P500 breaks trend last** → confirms real market drawdown

This dashboard is designed to help you **delay entry or reduce exposure**
before major US equity corrections.
""")
