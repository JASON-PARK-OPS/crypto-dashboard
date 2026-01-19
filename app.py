import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(layout="wide")
st.title("📉 US Market Risk Signal Dashboard")

# ===============================
# Sidebar
# ===============================
period = st.sidebar.selectbox(
    "Analysis Period",
    ["1mo", "3mo", "6mo", "1y", "3y"],
    index=3
)

interval = "1d"

# ===============================
# Assets
# ===============================
assets = {
    "S&P 500": "^GSPC",
    "Nasdaq": "^IXIC",
    "Bitcoin": "BTC-USD",
    "Gold": "GC=F"
}

@st.cache_data
def load_data(period):
    series_list = []

    for name, ticker in assets.items():
        df = yf.download(ticker, period=period, interval=interval, progress=False)

        if df.empty:
            continue

        close = df["Close"]
        if isinstance(close, pd.DataFrame):
            close = close.iloc[:, 0]

        series_list.append(close.rename(name))

    return pd.concat(series_list, axis=1, join="outer").sort_index()

price_df = load_data(period)

# ===============================
# Normalize
# ===============================
normalized = price_df.copy()
for col in normalized.columns:
    base = normalized[col].dropna().iloc[0]
    normalized[col] = normalized[col] / base * 100

# ===============================
# MAIN TREND CHART
# ===============================
fig = go.Figure()
for col in normalized.columns:
    fig.add_trace(go.Scatter(
        x=normalized.index,
        y=normalized[col],
        name=col,
        mode="lines",
        line=dict(width=2),
        connectgaps=True
    ))

fig.update_layout(
    height=600,
    hovermode="x unified",
    template="plotly_white",
    yaxis_title="Relative Performance (Base = 100)"
)

st.plotly_chart(fig, use_container_width=True)

# ===============================
# SIGNAL 1: Nasdaq / S&P Ratio
# ===============================
ratio = price_df["Nasdaq"] / price_df["S&P 500"]

fig_ratio = go.Figure()
fig_ratio.add_trace(go.Scatter(
    x=ratio.index,
    y=ratio,
    name="Nasdaq / S&P500",
    mode="lines",
    line=dict(color="purple", width=2)
))

fig_ratio.update_layout(
    height=300,
    title="📊 Growth vs Market Strength (Nasdaq / S&P500)",
    template="plotly_white"
)

st.plotly_chart(fig_ratio, use_container_width=True)

# ===============================
# SIGNAL LOGIC (CORE)
# ===============================
latest = price_df.iloc[-1]
btc_change = normalized["Bitcoin"].iloc[-1] - normalized["Bitcoin"].iloc[-20]
gold_change = normalized["Gold"].iloc[-1] - normalized["Gold"].iloc[-20]
ratio_trend = ratio.iloc[-1] < ratio.iloc[-20]

# ===============================
# SIGNAL INTERPRETATION
# ===============================
st.markdown("## 🚨 Market Risk Signal")

if btc_change < -5 and gold_change > 3 and ratio_trend:
    st.error(
        "⚠️ STRONG RISK-OFF SIGNAL\n\n"
        "- Bitcoin dropping fast\n"
        "- Gold rising\n"
        "- Nasdaq underperforming S&P500\n\n"
        "→ Avoid aggressive US equity entry"
    )

elif btc_change < -3 and ratio_trend:
    st.warning(
        "⚠️ EARLY RISK WARNING\n\n"
        "- Speculative assets weakening\n"
        "- Growth stocks losing momentum"
    )

else:
    st.success(
        "✅ NO MAJOR RISK SIGNAL\n\n"
        "- Market still stable\n"
        "- No clear defensive rotation detected"
    )

# ===============================
# GUIDE
# ===============================
st.markdown("""
### 📌 How to use this dashboard (Trader mindset)

- **BTC drops first** → speculative money exits
- **Nasdaq/S&P ratio falls** → growth risk rising
- **Gold rises early** → defensive rotation
- **Stocks fall last** → confirmation stage

This tool is for **timing & risk control**, not prediction.
""")
