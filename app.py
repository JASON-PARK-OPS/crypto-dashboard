import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta

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
# 기간 선택 (일수 기반)
# -----------------------------
period_label = st.selectbox(
    "기간 선택",
    ["1개월", "3개월", "6개월", "1년", "2년", "5년"],
    index=0
)

DAYS_MAP = {
    "1개월": 30,
    "3개월": 90,
    "6개월": 180,
    "1년": 365,
    "2년": 730,
    "5년": 1825
}

days = DAYS_MAP[period_label]
end_date = datetime.today()
start_date = end_date - timedelta(days=days)

# -----------------------------
# 자산 선택
# -----------------------------
selected_assets = st.multiselect(
    "보고 싶은 자산 선택",
    list(ASSETS.keys()),
    default=list(ASSETS.keys())
)

# -----------------------------
# 데이터 로드 (🔥 안정판)
# -----------------------------
@st.cache_data
def load_data(start, end):
    series_list = []

    for name, ticker in ASSETS.items():
        df = yf.download(
            ticker,
            start=start,
            end=end,
            progress=False,
            auto_adjust=True
        )

        if df is None or df.empty:
            continue

        close = df.get("Close")
        if isinstance(close, pd.Series) and len(close) > 1:
            close.name = name
            series_list.append(close)

    if not series_list:
        return pd.DataFrame()

    return pd.concat(series_list, axis=1)

price_df = load_data(start_date, end_date)

if price_df.empty:
    st.error("❌ 데이터 수신 실패. 잠시 후 다시 시도하세요.")
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
