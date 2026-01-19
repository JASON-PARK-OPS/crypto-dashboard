import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
import requests

st.set_page_config(layout="wide")
st.title("📊 자산 비교 대시보드")

# -----------------------------
# 자산 정의
# -----------------------------
STOOQ_ASSETS = {
    "S&P500": "^SPX",
    "Nasdaq": "^NDQ",
    "Gold": "XAUUSD",
}

CRYPTO_ASSETS = {
    "Bitcoin": "BTC-USD"
}

# -----------------------------
# 색상 선택
# -----------------------------
st.sidebar.header("🎨 색상 선택")

default_colors = {
    "Bitcoin": "#2dd4bf",
    "S&P500": "#ef4444",
    "Nasdaq": "#f97316",
    "Gold": "#eab308",
}

colors = {
    k: st.sidebar.color_picker(k, v)
    for k, v in default_colors.items()
}

# -----------------------------
# 기간 선택
# -----------------------------
period_label = st.selectbox(
    "기간 선택",
    ["1개월", "3개월", "6개월", "1년", "2년"],
    index=0
)

DAYS_MAP = {
    "1개월": 30,
    "3개월": 90,
    "6개월": 180,
    "1년": 365,
    "2년": 730,
}

days = DAYS_MAP[period_label]
start_date = datetime.today() - timedelta(days=days)

# -----------------------------
# Stooq 데이터
# -----------------------------
@st.cache_data
def load_stooq(start):
    series = []

    for name, ticker in STOOQ_ASSETS.items():
        url = f"https://stooq.com/q/d/l/?s={ticker.lower()}&i=d"
        df = pd.read_csv(url)
        df["Date"] = pd.to_datetime(df["Date"])
        df = df[df["Date"] >= start]

        close = df.set_index("Date")["Close"]
        close.name = name
        series.append(close)

    return pd.concat(series, axis=1)

# -----------------------------
# 비트코인 (Coinbase)
# -----------------------------
@st.cache_data
def load_bitcoin(start):
    url = "https://api.exchange.coinbase.com/products/BTC-USD/candles"
    params = {"granularity": 86400}  # 하루
    data = requests.get(url, params=params).json()

    df = pd.DataFrame(data, columns=["time", "low", "high", "open", "close", "volume"])
    df["Date"] = pd.to_datetime(df["time"], unit="s")
    df = df[df["Date"] >= start]

    close = df.set_index("Date")["close"].sort_index()
    close.name = "Bitcoin"
    return close.to_frame()

# -----------------------------
# 데이터 합치기
# -----------------------------
price_df = load_stooq(start_date)
btc_df = load_bitcoin(start_date)

price_df = pd.concat([price_df, btc_df], axis=1)

# -----------------------------
# 차트
# -----------------------------
st.subheader("📈 가격 차트")

fig = go.Figure()

for asset in price_df.columns:
    fig.add_trace(
        go.Scatter(
            x=price_df.index,
            y=price_df[asset],
            mode="lines",
            name=asset,
            line=dict(color=colors.get(asset, "#999999"), width=2)
        )
    )

fig.update_layout(
    height=500,
    hovermode="x unified",
    xaxis_title="날짜",
    yaxis_title="가격"
)

st.plotly_chart(fig, use_container_width=True)

# -----------------------------
# 상관계수
# -----------------------------
st.subheader("📊 상관계수")

corr = price_df.dropna().corr()
st.dataframe(corr.style.format("{:.3f}"))
