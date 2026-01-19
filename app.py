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

        if df.empty:
            continue

        # 🔧 핵심 수정 부분
        close = df["Close"]
        if isinstance(close, pd.DataFrame):
            close = close.iloc[:, 0]

        s = close.rename(name)
        series_list.append(s)

    if not series_list:
        return pd.DataFrame()

    price_df = pd.concat(series_list, axis=1, join="outer")
    price_df = price_df.sort_index()

    return price_df

price_df = load_data(period)

if price_df.empty:
    st.error("데이터를 불러오지 못했습니다. 기간을 바꿔보세요.")
    st.stop()

# -----------------------
# Normalize
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
# Explanation
# -----------------------
st.markdown("""
### 📌 How to interpret (US stock risk detection)

- **Bitcoin weakens first** → speculative risk is leaving
- **Nasdaq underperforms S&P500** → growth stocks vulnerable
- **Gold rises while stocks stall** → defensive rotation
- **S&P500 breaks last** → confirms real drawdown

This tool is designed to help you **avoid entering US equities too early**.
""")
