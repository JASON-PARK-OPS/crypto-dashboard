import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.express as px

st.set_page_config(layout="wide")
st.title("📊 글로벌 자산 추세 & 하락장 신호 대시보드")

# ===============================
# 자산 설정
# ===============================
ASSETS = {
    "Bitcoin": "BTC-USD",
    "S&P 500": "^GSPC",
    "Nasdaq": "^IXIC",
    "Gold": "GC=F"
}

# ===============================
# 사이드바 설정
# ===============================
freq = st.sidebar.selectbox("차트 단위", ["일", "주", "월", "연"])
period = st.sidebar.selectbox("분석 기간", ["1y", "3y", "5y", "10y", "max"])

freq_map = {
    "일": "1d",
    "주": "1wk",
    "월": "1mo",
    "연": "3mo"
}

# ===============================
# 데이터 로드
# ===============================
@st.cache_data
def load_prices(interval, period):
    series_list = []

    for name, ticker in ASSETS.items():
        df = yf.download(
            ticker,
            interval=interval,
            period=period,
            auto_adjust=True,
            progress=False
        )

        if df is None or df.empty or "Close" not in df.columns:
            continue

        s = df["Close"].copy()
        s.name = name
        series_list.append(s)

    if not series_list:
        return pd.DataFrame()

    return pd.concat(series_list, axis=1).dropna()

# ✅ price_df는 여기서 처음 생성됨
price_df = load_prices(freq_map[freq], period)

if price_df.empty:
    st.error("데이터를 불러오지 못했습니다. 다른 기간/단위를 선택하세요.")
    st.stop()

# ===============================
# 1️⃣ 상대 강도 기반 추세 (기준점 없음)
# ===============================
def relative_strength(series, window=200):
    ma = series.rolling(window).mean()
    return (series - ma) / ma

rs_df = pd.DataFrame(index=price_df.index)

for col in price_df.columns:
    rs_df[col] = relative_strength(price_df[col])

fig1 = px.line(
    rs_df,
    title="📈 자산별 상대 강도 (200일 평균 대비)"
)

st.plotly_chart(fig1, use_container_width=True)

st.markdown("""
**설명**  
- 기준점(출발점) 없이 현재 위치만 평가  
- 0 위: 평균보다 강함  
- 0 아래: 평균보다 약함
""")

# ===============================
# 2️⃣ 변동성 (시장 불안도)
# ===============================
vol_df = price_df.pct_change().rolling(20).std() * 100

fig2 = px.line(
    vol_df,
    title="🌊 20일 변동성 (시장 불안도)"
)

st.plotly_chart(fig2, use_container_width=True)

st.markdown("""
**설명**  
- 변동성 급등 = 시장 불안  
- 주식 변동성 상승은 하락장의 전조
""")

# ===============================
# 3️⃣ 하락장 위험 신호 (주식 vs 금)
# ===============================
signal_df = pd.DataFrame(index=price_df.index)

equity = []
if "S&P 500" in rs_df.columns:
    equity.append(rs_df["S&P 500"])
if "Nasdaq" in rs_df.columns:
    equity.append(rs_df["Nasdaq"])

if equity and "Gold" in rs_df.columns:
    signal_df["Market Risk Signal"] = (
        pd.concat(equity, axis=1).mean(axis=1) - rs_df["Gold"]
    )

    fig3 = px.line(
        signal_df,
        y="Market Risk Signal",
        title="🚨 하락장 위험 신호 (주식 − 금 상대강도)"
    )
    fig3.add_hline(y=0, line_dash="dash")
    st.plotly_chart(fig3, use_container_width=True)

    st.markdown("""
**설명**  
- 0 아래: 방어 자산 선호 → 하락 위험  
- 주식이 약해지고 금이 강해질수록 위험 증가
""")
else:
    st.warning("주식 또는 금 데이터가 부족해 위험 신호를 계산할 수 없습니다.")
