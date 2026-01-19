import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px

st.set_page_config(layout="wide")
st.title("📊 글로벌 자산 가격 & 시장 위험도 대시보드")

# ===============================
# 자산 설정 (표시 이름 고정)
# ===============================
ASSETS = {
    "Bitcoin": "BTC-USD",
    "S&P 500": "^GSPC",
    "Nasdaq": "^IXIC",
    "Gold": "GC=F"
}

# ===============================
# 사이드바
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

    for display_name, ticker in ASSETS.items():
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
        s.name = display_name  # ✅ 범례 이름 고정
        series_list.append(s)

    if not series_list:
        return pd.DataFrame()

    return pd.concat(series_list, axis=1)

price_df = load_prices(freq_map[freq], period)

if price_df.empty:
    st.error("데이터를 불러오지 못했습니다.")
    st.stop()

# ===============================
# 1️⃣ 가격 차트 (로그 스케일)
# ===============================
fig_price = px.line(
    price_df,
    title="📈 자산 가격 추세 (로그 스케일)"
)

fig_price.update_yaxes(type="log", title="Price (Log Scale)")
fig_price.update_xaxes(title="Date")

st.plotly_chart(fig_price, use_container_width=True)

st.markdown("""
**설명 (가격 로그 차트)**  
- 실제 가격 흐름을 그대로 사용  
- 로그 스케일 → 비율 변화가 잘 보임  
- 장기 비교에 가장 자연스러운 방식  
- 비트코인 때문에 주식·금이 눌려 보이던 문제 해결
""")

# ===============================
# 2️⃣ 변동성 + 위험 단계 표시
# ===============================
vol_df = price_df.pct_change().rolling(20).std() * 100

fig_vol = px.line(
    vol_df,
    title="🌊 20일 변동성 (시장 위험도)"
)

# 위험 단계 수평선
fig_vol.add_hline(y=1, line_dash="dot", annotation_text="매우 안정")
fig_vol.add_hline(y=2, line_dash="dot", annotation_text="안정")
fig_vol.add_hline(y=4, line_dash="dot", annotation_text="위험")
fig_vol.add_hline(y=6, line_dash="dot", annotation_text="매우 위험")

fig_vol.update_yaxes(title="Volatility (%)")
fig_vol.update_xaxes(title="Date")

st.plotly_chart(fig_vol, use_container_width=True)

st.markdown("""
**설명 (변동성 & 위험 단계)**  
- 변동성 = 가격이 얼마나 흔들리는지  
- 1% 이하: 매우 안정  
- 1~2%: 안정  
- 2~4%: 주의 필요  
- 4% 이상: 하락장 위험 구간  
- 주식 변동성이 먼저 상승하면 조정 가능성 ↑
""")
