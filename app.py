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
# 기간 / 주기 선택
# ===============================
freq = st.sidebar.selectbox(
    "📅 차트 단위",
    ["일", "주", "월", "연"]
)

freq_map = {
    "일": "1d",
    "주": "1wk",
    "월": "1mo",
    "연": "3mo"
}

period = st.sidebar.selectbox(
    "📆 분석 기간",
    ["1y", "3y", "5y", "10y", "max"]
)

# ===============================
# 데이터 로드 (안정 버전)
# ===============================
@st.cache_data
def load_prices(interval):
    series_list = []

    for name, ticker in ASSETS.items():
        df = yf.download(
            ticker,
            period=period,
            interval=interval,
            auto_adjust=True,
            progress=False
        )

        if df is None or df.empty:
            continue

        if "Close" not in df.columns:
            continue

        s = df["Close"].copy()
        s.name = name
        series_list.append(s)

    if not series_list:
        return pd.DataFrame()

    return pd.concat(series_list, axis=1).dropna()

price_df = load_prices(freq_map[freq])

if price_df.empty:
    st.error("데이터를 불러오지 못했습니다. 기간이나 단위를 바꿔보세요.")
    st.stop()

# ===============================
# 1️⃣ 로그 누적 수익률 (추세 비교)
# ===============================
log_return_df = np.log(price_df / price_df.iloc[0])

fig1 = px.line(
    log_return_df,
    title="📈 누적 수익률 비교 (로그 스케일)"
)

fig1.update_layout(
    yaxis_title="Log Return",
    xaxis_title="Date"
)

st.plotly_chart(fig1, use_container_width=True)

st.markdown("""
**설명**  
- 모든 자산을 같은 출발선에서 비교  
- 비트코인 때문에 주식·금이 평평해 보이던 문제 해결  
- 장기 추세 비교에 가장 적합
""")

# ===============================
# 2️⃣ 변동성 (시장 불안도)
# ===============================
vol_df = price_df.pct_change().rolling(20).std() * 100

fig2 = px.line(
    vol_df,
    title="🌊 20일 변동성 비교 (시장 불안도)"
)

fig2.update_layout(
    yaxis_title="Volatility (%)",
    xaxis_title="Date"
)

st.plotly_chart(fig2, use_container_width=True)

st.markdown("""
**설명**  
- 변동성 급증 = 시장 불안  
- 하락장은 항상 변동성 상승이 먼저 발생  
- 주식 변동성이 먼저 튀면 경계 필요
""")

# ===============================
# 3️⃣ 하락장 신호 (주식 vs 금)
# ===============================
signal_df = pd.DataFrame(index=price_df.index)

signal_df["Equity Momentum"] = (
    price_df["S&P 500"].pct_change(20) +
    price_df["Nasdaq"].pct_change(20)
) / 2

signal_df["Gold Momentum"] = price_df["Gold"].pct_change(20)

signal_df["Market Risk Signal"] = (
    signal_df["Equity Momentum"] - signal_df["Gold Momentum"]
)

fig3 = px.line(
    signal_df,
    y="Market Risk Signal",
    title="🚨 시장 위험 신호 (주식 vs 금)"
)

fig3.add_hline(y=0, line_dash="dash")

st.plotly_chart(fig3, use_container_width=True)

st.markdown("""
**설명**  
- 0 아래 → 위험 회피 국면  
- 금이 강하고 주식이 약하면 하락장 확률 상승  
- 장기 투자자는 이 구간에서 비중 조절 고려
""")
