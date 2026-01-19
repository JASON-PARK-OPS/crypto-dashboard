import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

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
# 2. 데이터 로드 (✔️ 에러 완전 해결 구조)
# =========================
@st.cache_data
def load_data():
    series_list = []

    for name, ticker in ASSETS.items():
        df = yf.download(ticker, start=START_DATE, progress=False)

        if not df.empty and "Close" in df.columns:
            s = df["Close"].copy()
            s.name = name
            series_list.append(s)

    if len(series_list) == 0:
        return pd.DataFrame()

    return pd.concat(series_list, axis=1)

price_df = load_data()

if price_df.empty:
    st.error("데이터를 불러오지 못했습니다.")
    st.stop()

price_df = price_df.dropna(how="all")

# =========================
# 3. 정규화 가격 (가장 직관적인 비교)
# =========================
normalized = price_df / price_df.iloc[0] * 100

st.subheader("📈 자산 가격 추세 (정규화 · 시작=100)")

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
    yaxis_title="Normalized Price",
    height=500
)

st.plotly_chart(fig_price, use_container_width=True)

st.markdown("""
**설명**
- 모든 자산을 같은 출발선(100)에서 시작
- 위로 갈수록 상대적으로 강한 자산
- 비트코인 / 금 / 미국 주식의 장기 추세 비교에 최적
""")

# =========================
# 4. 변동성 (20일, 시장 위험 핵심 지표)
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
**변동성 해석**
- 변동성 상승 = 시장 불안 신호
- 주가 하락은 항상 변동성 상승이 선행
""")

# =========================
# 5. 미국 주식시장 자동 판단
# =========================
latest_vol = vol.dropna().iloc[-1]

if "S&P 500" in latest_vol and "Nasdaq" in latest_vol:
    avg_vol = (latest_vol["S&P 500"] + latest_vol["Nasdaq"]) / 2

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
- 미국 주식시장의 핵심은 S&P 500 + Nasdaq
- 두 지수가 동시에 변동성 상승 → 하락장 진입 확률 증가
- 현재는 “공포 전조인지 / 안정 구간인지”를 구분하는 단계

</span>
""", unsafe_allow_html=True)

else:
    st.warning("미국 주식 변동성 계산에 필요한 데이터가 부족합니다.")
