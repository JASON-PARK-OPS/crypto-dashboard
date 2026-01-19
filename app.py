import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import numpy as np

st.set_page_config(layout="wide")
st.title("📊 글로벌 자산 비교 & 미국 주식시장 위험도")

# =========================
# 1. 자산 정의 (표시 이름 고정)
# =========================
ASSETS = {
    "Bitcoin": "BTC-USD",
    "S&P 500": "^GSPC",
    "Nasdaq": "^IXIC",
    "Gold": "GC=F"
}

START_DATE = "2020-01-01"

# =========================
# 2. 데이터 로드
# =========================
@st.cache_data
def load_data():
    data = {}
    for name, ticker in ASSETS.items():
        df = yf.download(ticker, start=START_DATE, progress=False)
        if not df.empty:
            data[name] = df["Close"]
    return pd.DataFrame(data)

price_df = load_data()

if price_df.empty:
    st.error("데이터 로드 실패")
    st.stop()

# =========================
# 3. 정규화 가격 (가장 반응 좋았던 방식)
# =========================
normalized = price_df / price_df.iloc[0] * 100

st.subheader("📈 자산 가격 추세 (정규화, 시작=100)")

fig_price = go.Figure()
for col in normalized.columns:
    fig_price.add_trace(
        go.Scatter(
            x=normalized.index,
            y=normalized[col],
            mode="lines",
            name=col
        )
    )

fig_price.update_layout(
    xaxis_title="Date",
    yaxis_title="Normalized Price (Start = 100)",
    height=500
)

st.plotly_chart(fig_price, use_container_width=True)

st.markdown("""
**그래프 설명 (고등학생도 이해 가능)**  
- 모든 자산을 같은 출발선(100)에서 시작  
- 위로 갈수록 → 상대적으로 더 강한 자산  
- 비트코인·금·주식의 **추세 차이**가 명확히 보임  
""")

# =========================
# 4. 변동성 (20일, 위험 신호 핵심)
# =========================
returns = price_df.pct_change()
vol = returns.rolling(20).std() * 100

st.subheader("⚠️ 20일 변동성 (시장 위험도)")

fig_vol = go.Figure()
for col in vol.columns:
    fig_vol.add_trace(
        go.Scatter(
            x=vol.index,
            y=vol[col],
            mode="lines",
            name=col
        )
    )

# 위험 기준선
fig_vol.add_hline(y=1.2, line_dash="dash", annotation_text="매우 안정")
fig_vol.add_hline(y=2.0, line_dash="dash", annotation_text="안정")
fig_vol.add_hline(y=3.0, line_dash="dash", annotation_text="주의")
fig_vol.add_hline(y=4.0, line_dash="dash", annotation_text="위험")

fig_vol.update_layout(
    xaxis_title="Date",
    yaxis_title="Volatility (%)",
    height=500
)

st.plotly_chart(fig_vol, use_container_width=True)

st.markdown("""
**변동성 해석 방법**  
- 변동성 상승 = 시장 불안 증가  
- 하락장은 항상 변동성 상승이 먼저 발생  
- “조용히 무너지는 장”은 거의 없음  
""")

# =========================
# 5. 미국 주식시장 자동 판단
# =========================
latest = vol.dropna().iloc[-1]
sp = latest["S&P 500"]
nas = latest["Nasdaq"]
avg_vol = (sp + nas) / 2

if avg_vol < 1.2:
    status = "🟢 매우 안정"
elif avg_vol < 2.0:
    status = "🟡 안정"
elif avg_vol < 3.0:
    status = "🟠 주의"
else:
    status = "🔴 위험"

st.markdown("---")
st.subheader("📌 현재 미국 주식시장 판단")

st.markdown(f"""
### 결론: **{status}**
S&P 500 + Nasdaq 평균 변동성: **{avg_vol:.2f}%**
""")

st.markdown("""
<span style="font-size:0.85em; color:gray">

**판단 로직**  
- 미국 주식시장의 본질은 S&P 500 + Nasdaq  
- 두 지수의 변동성이 동시에 오르면 → 하락 확률 급증  
- 현재는 “공포 단계 전인지 / 이미 위험한지”를 구분하는 구간  

</span>
""", unsafe_allow_html=True)
