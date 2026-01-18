import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go

st.set_page_config(page_title="Asset Dashboard", layout="wide")

st.title("📊 자산 비교 대시보드")

assets = {
    "Bitcoin": "BTC-USD",
    "S&P500": "^GSPC",
    "Nasdaq": "^IXIC",
    "Gold": "GC=F",
    "SCHD": "SCHD"
}

period = st.selectbox(
    "기간 선택",
    ["1mo", "3mo", "6mo", "1y", "2y"],
    index=3
)

interval = "1d"

selected = st.multiselect(
    "보고 싶은 자산 선택",
    list(assets.keys()),
    default=list(assets.keys())
)

colors = {}
st.sidebar.header("🎨 색상 선택")
for a in selected:
    colors[a] = st.sidebar.color_picker(a, "#ffaa00")

@st.cache_data(ttl=300)
def load_data():
    data = {}
    for name, ticker in assets.items():
        df = yf.download(ticker, period=period, interval=interval)
        df["Return"] = df["Close"].pct_change()
        data[name] = df
    return data

data = load_data()

fig = go.Figure()
for a in selected:
    fig.add_trace(go.Scatter(
        x=data[a].index,
        y=data[a]["Close"],
        name=a,
        line=dict(color=colors[a], width=2)
    ))

fig.update_layout(
    height=500,
    title="가격 차트",
    xaxis_title="날짜",
    yaxis_title="가격"
)

st.plotly_chart(fig, use_container_width=True)

if len(selected) >= 2:
    st.subheader("📈 상관계수")
    returns = pd.concat(
        [data[a]["Return"] for a in selected],
        axis=1
    ).dropna()
    returns.columns = selected
    corr = returns.corr()
    st.dataframe(corr)
