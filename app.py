import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px

st.set_page_config(layout="wide")
st.title("Macro Market Regime Dashboard")

# =====================
# Sidebar
# =====================
freq = st.sidebar.selectbox(
    "Timeframe",
    ["Daily", "Weekly", "Monthly"]
)

freq_map = {
    "Daily": "1d",
    "Weekly": "1wk",
    "Monthly": "1mo"
}

# =====================
# Data Loader (FIXED)
# =====================
@st.cache_data
def load_prices(interval):
    tickers = {
        "Bitcoin": "BTC-USD",
        "S&P 500": "^GSPC",
        "Nasdaq": "^IXIC",
        "Gold": "GC=F"
    }

    series = []

    for name, ticker in tickers.items():
        df = yf.download(
            ticker,
            period="10y",
            interval=interval,
            auto_adjust=True,
            progress=False
        )

        close = df["Close"]

        # 🔧 핵심 수정: Close가 DataFrame이면 Series로 변환
        if isinstance(close, pd.DataFrame):
            close = close.iloc[:, 0]

        close.name = name
        series.append(close)

    df = pd.concat(series, axis=1)

    # 🔧 거래일 차이로 생긴 끊김 제거
    df = df.ffill().dropna()

    return df


price_df = load_prices(freq_map[freq])

# =====================
# 1️⃣ Normalized Trend
# =====================
norm_df = price_df / price_df.iloc[0] * 100

fig1 = px.line(
    norm_df,
    title="Normalized Performance (Trend Comparison)"
)

st.plotly_chart(fig1, use_container_width=True)

# =====================
# 2️⃣ Nasdaq vs S&P500 Relative Strength
# =====================
rs_df = pd.DataFrame(index=price_df.index)
rs_df["Nasdaq / S&P500"] = price_df["Nasdaq"] / price_df["S&P 500"]

fig2 = px.line(
    rs_df,
    title="Relative Strength: Nasdaq vs S&P 500"
)

st.plotly_chart(fig2, use_container_width=True)

# =====================
# 3️⃣ Market Risk Signal
# =====================
signal_df = pd.DataFrame(index=price_df.index)

signal_df["Risk_On"] = (
    price_df["S&P 500"].pct_change(20) +
    price_df["Nasdaq"].pct_change(20)
) / 2

signal_df["Safe_Haven"] = price_df["Gold"].pct_change(20)

signal_df["Risk_Signal"] = signal_df["Risk_On"] - signal_df["Safe_Haven"]

fig3 = px.line(
    signal_df,
    y="Risk_Signal",
    title="Market Risk Regime Signal (Risk-On minus Safe-Haven)"
)

st.plotly_chart(fig3, use_container_width=True)
