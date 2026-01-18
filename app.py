import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(layout="wide")
st.title("📊 자산 비교 대시보드")

ASSETS = {
    "Bitcoin": "BTC-USD",
    "S&P500": "^GSPC",
    "Nasdaq": "^IXIC",
    "Gold": "GC=F",
    "SCHD": "SCHD"
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
    "SCHD": "#dc2626",
}

colors = {
    k: st.sidebar.color_picker(k, v)
    for k, v in default_colors.items()
}

# -----------------------------
# 기간 / 자산 선택
# -----------------------------
period = st.selectbox(
    "기간 선택",
    ["1mo", "3mo", "6mo", "1y", "2y", "5y"],
    index=0
)

selected_assets = st.multiselect(
    "보고 싶은 자산 선택",
    list(ASSETS.keys()),
    default=list(ASSETS.keys())
)

# -----------------------------
# 데이터 로드 (🔥 완전 방탄)
# -----------------------------
@st.cache_data
def load_data(period):
    valid_series = []

    for name, ticker in ASSETS.items():
        df = yf.download(ticker, period=period, progress=False)

        if df is None or df.empty:
            continue

        close = df.get("Close")

        # 🔥 핵심 방어
        if not isinstance(close, pd.Series):
            continue
        if len(close) < 2:
            continue

        close.name = name
        valid_series.append(close)

    if not valid_series:
        return pd.DataFrame()

    return pd.concat(valid_series, axis=1)

price_df = load_data(period)

if price_df.empty:
    st.error("데이터를 불러오지 못했습니다. 기간을 바꿔보세요.")
    st.stop()

# -----------------------------
# 가격 차트 (라인)
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
    hovermode="x unified",
    xaxis_title="날짜",
    yaxis_title="가격"
)

st.plotly_chart(fig, use_container_width=True)

# -----------------------------
# 상관계수
# -----------------------------
st.subheader("📊 상관계수")

corr = price_df[selected_assets].dropna().corr()
st.dataframe(corr.style.format("{:.3f}"))
