import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# -----------------------------
# 기본 설정
# -----------------------------
st.set_page_config(layout="wide")
st.title("📊 자산 비교 대시보드")

# -----------------------------
# 자산 정의
# -----------------------------
ASSETS = {
    "Bitcoin": "BTC-USD",
    "S&P500": "^GSPC",
    "Nasdaq": "^IXIC",
    "Gold": "GC=F",
    "SCHD": "SCHD"
}

# -----------------------------
# 사이드바: 색상 선택
# -----------------------------
st.sidebar.header("🎨 색상 선택")

colors = {}
default_colors = {
    "Bitcoin": "#2dd4bf",
    "S&P500": "#ef4444",
    "Nasdaq": "#f97316",
    "Gold": "#eab308",
    "SCHD": "#dc2626",
}

for asset in ASSETS:
    colors[asset] = st.sidebar.color_picker(
        asset, default_colors[asset]
    )

# -----------------------------
# 기간 선택
# -----------------------------
period = st.selectbox(
    "기간 선택",
    ["1mo", "3mo", "6mo", "1y", "2y", "5y"],
    index=0
)

# -----------------------------
# 자산 선택
# -----------------------------
selected_assets = st.multiselect(
    "보고 싶은 자산 선택",
    list(ASSETS.keys()),
    default=list(ASSETS.keys())
)

# -----------------------------
# 데이터 다운로드
# -----------------------------
@st.cache_data
def load_data(period):
    data = {}
    for name, ticker in ASSETS.items():
        df = yf.download(ticker, period=period)
        data[name] = df["Close"]
    return pd.DataFrame(data)

price_df = load_data(period).dropna()

# -----------------------------
# 가격 차트 (A단계 핵심: 선 그래프)
# -----------------------------
st.subheader("📈 가격 차트")

fig = go.Figure()

for asset in selected_assets:
    fig.add_trace(
        go.Scatter(
            x=price_df.index,
            y=price_df[asset],
            mode="lines",          # 🔥 핵심: 점 → 선
            name=asset,
            line=dict(color=colors[asset], width=2)
        )
    )

fig.update_layout(
    height=500,
    xaxis_title="날짜",
    yaxis_title="가격",
    hovermode="x unified",
    legend_title="자산"
)

st.plotly_chart(fig, use_container_width=True)

# -----------------------------
# 상관계수
# -----------------------------
st.subheader("📊 상관계수")

corr = price_df[selected_assets].corr()
st.dataframe(corr.style.format("{:.3f}"))
