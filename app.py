import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(layout="wide")
st.title("📉 US Market Risk Signal Dashboard")

# -----------------------
# Sidebar (FIXED)
# -----------------------
period = st.sidebar.selectbox(
    "Analysis Period",
    ["1mo", "3mo", "6mo", "1y", "3y"],
    index=3
)

# 항상 일봉 사용 (스무스함 우선)
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
    df_all = pd.DataFrame()

    for name, ticker in assets.items():
        df = yf.download(
            ticker,
            period=period,
            interval=interval,
            progress=False
        )

        if not df.empty:
            df_all[name] = df["Close"]

    # 날짜 기준으로 정렬 + 보간
    df_all = df_all.sort_index()
    df_all = df_all.interpolate(method="time")

    return df_all

price_df = load_data(period)

# -----------------------
# Normalize
# -----------------------
normalized = price_df / price_df.iloc[0] * 100

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
### 📌 How to interpret (for US stock investors)

- **Bitcoin weakens first** → risk appetite shrinking
- **Nasdaq underperforms S&P500** → growth stocks losing momentum
- **Gold rising while stocks stall** → defensive rotation
- **S&P500 breaks last** → confirms real drawdown

This chart helps you **avoid entering US equities too early**,
not to trade Bitcoin itself.
""")
