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

default_colors = {
    "Bitcoin": "#2dd4bf",
    "S&P500": "#ef4444",
    "Nasdaq": "#f97316",
    "Gold": "#eab308",
    "SCHD": "#dc2626",
}

colors = {
    asset: st.sidebar.color_picker(asset, default_colors[asset])
    for asset in ASSETS
}

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
# 데이터 다운로드 (🔥 에러 방어 핵심)
# -----------------------------
@st.cache_data
def load_data(period):
    series_dict = {}

    for name, ticker in ASSETS.items():
        df = yf.download(ticker, period=period, progress=False)

        if df is not None and not df.empty:
            series_dict[name] = df["Close"]

    return pd.DataFrame(series_dict)

price_df = load_data(period)

if price_df.empty:
    st.error("데이터를 불러올 수 없습니다. 기간을 변경해 주세요.")
    st.stop()

# -----------------------------
# 가격 차트 (선 그래프)
# -----------------------------
st.subheader("📈 가격 차트")

fig = go.Figure()

for asset in selected_assets:
    if asset in price_df.columns:
        fig.add_trace(
            go.Scatter(
                x=price_df.index,
                y=price_df[asset],
                mode="lines",
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

corr = price_df[selected_assets].dropna().corr()
st.dataframe(corr.style.format("{:.3f}"))
