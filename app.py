import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import numpy as np

st.set_page_config(layout="wide")

st.title("📊 글로벌 자산 가격 & 미국 주식시장 위험도 대시보드")

# ===============================
# 1️⃣ 데이터 설정
# ===============================
ASSETS = {
    "Bitcoin": "BTC-USD",
    "S&P 500": "^GSPC",
    "Nasdaq": "^IXIC",
    "Gold": "GC=F"
}

START_DATE = "2020-01-01"

# ===============================
# 2️⃣ 데이터 로드
# ===============================
@st.cache_data
def load_prices():
    series = []

    for name, ticker in ASSETS.items():
        df = yf.download(ticker, start=START_DATE, progress=False)

        if df.empty or "Close" not in df:
            continue

        s = df["Close"].copy()
        s.name = name
        series.append(s)

    return pd.concat(series, axis=1)

price_df = load_prices()

if price_df.empty:
    st.error("데이터를 불러오지 못했습니다.")
    st.stop()

# ===============================
# 3️⃣ 가격 차트 (로그 스케일)
# ===============================
st.subheader("📈 자산 가격 추세 (로그 스케일)")

fig_price = go.Figure()

for col in price_df.columns:
    fig_price.add_trace(
        go.Scatter(
            x=price_df.index,
            y=price_df[col],
            mode="lines",
            name=col
        )
    )

fig_price.update_layout(
    yaxis_type="log",
    xaxis_title="Date",
    yaxis_title="Price (Log Scale)",
    legend_title="Asset",
    height=500
)

st.plotly_chart(fig_price, use_container_width=True)

st.markdown("""
**설명 (로그 차트)**  
- 실제 가격을 그대로 사용  
- 로그 스케일 → 비율 변화가 잘 보임  
- 비트코인 때문에 주식·금이 눌려 보이던 문제 해결  
- 장기 추세 비교에 가장 적합
""")

# ===============================
# 4️⃣ 변동성 계산 (20일)
# ===============================
returns = price_df.pct_change()
vol_df = returns.rolling(20).std() * 100  # %

st.subheader("⚠️ 20일 변동성 (시장 위험도)")

fig_vol = go.Figure()

for col in vol_df.columns:
    fig_vol.add_trace(
        go.Scatter(
            x=vol_df.index,
            y=vol_df[col],
            mode="lines",
            name=col
        )
    )

# 위험 구간 수평선
levels = {
    "매우 안정": 1.2,
    "안정": 2.0,
    "주의": 3.0
}

for label, y in levels.items():
    fig_vol.add_hline(
        y=y,
        line_dash="dash",
        annotation_text=label,
        annotation_position="top left"
    )

fig_vol.update_layout(
    xaxis_title="Date",
    yaxis_title="Volatility (%)",
    height=500
)

st.plotly_chart(fig_vol, use_container_width=True)

st.markdown("""
**설명 (변동성 차트)**  
- 20일간 가격 흔들림의 크기  
- 변동성 상승 = 시장 불안 증가  
- 하락장은 항상 변동성 상승이 먼저 나타남
""")

# ===============================
# 5️⃣ 미국 주식시장 자동 판단
# ===============================
latest = vol_df.dropna().iloc[-1]

sp = latest.get("S&P 500", np.nan)
nas = latest.get("Nasdaq", np.nan)

def judge(sp, nas):
    avg = (sp + nas) / 2

    if avg < 1.2:
        return "🟢 매우 안정", avg
    elif avg < 2.0:
        return "🟡 안정", avg
    elif avg < 3.0:
        return "🟠 주의", avg
    else:
        return "🔴 위험", avg

if not np.isnan(sp) and not np.isnan(nas):
    status, avg_vol = judge(sp, nas)

    st.markdown("---")
    st.subheader("📌 현재 미국 주식시장 변동성 판단")

    st.markdown(f"""
### **결론: {status}**
최근 20일 기준 평균 변동성: **{avg_vol:.2f}%**
""")

    st.markdown("""
<span style="font-size:0.85em; color:gray">

**판단 로직 설명**  
- S&P 500 + Nasdaq 변동성을 사용  
- 변동성은 하락장의 가장 빠른 선행 신호  
- 두 지수를 평균 내 시장 전체 위험도를 단순화  
- 낮은 변동성 → 추세 유지 가능성 높음  
- 급등 시 → 조정·하락 가능성 증가  

</span>
""", unsafe_allow_html=True)
