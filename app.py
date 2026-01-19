# ===============================
# 3️⃣ 시장 위험 신호 (기준점 제거 버전)
# ===============================
signal_df = pd.DataFrame(index=price_df.index)

def relative_strength(series, window=200):
    ma = series.rolling(window).mean()
    return (series - ma) / ma

# 존재하는 자산만 사용
equity_components = []

if "S&P 500" in price_df.columns:
    equity_components.append(relative_strength(price_df["S&P 500"]))

if "Nasdaq" in price_df.columns:
    equity_components.append(relative_strength(price_df["Nasdaq"]))

if equity_components:
    signal_df["Equity Strength"] = pd.concat(equity_components, axis=1).mean(axis=1)

if "Gold" in price_df.columns:
    signal_df["Gold Strength"] = relative_strength(price_df["Gold"])

# 둘 다 있을 때만 신호 계산
if {"Equity Strength", "Gold Strength"}.issubset(signal_df.columns):
    signal_df["Market Risk Signal"] = (
        signal_df["Equity Strength"] - signal_df["Gold Strength"]
    )

    fig3 = px.line(
        signal_df,
        y="Market Risk Signal",
        title="🚨 시장 위험 신호 (주식 상대강도 − 금 상대강도)"
    )

    fig3.add_hline(y=0, line_dash="dash")
    st.plotly_chart(fig3, use_container_width=True)

    st.markdown("""
**설명**  
- 주식이 자기 평균보다 약해지고  
- 금이 자기 평균보다 강해지면  
→ 하락장 위험 신호  
- 기준점에 의존하지 않아 왜곡이 없음
""")
else:
    st.warning("주식 또는 금 데이터가 부족해 위험 신호를 계산할 수 없습니다.")
