import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import smtplib
from email.mime.text import MIMEText
from datetime import datetime

st.set_page_config(layout="wide")
st.title("🚨 US Market Risk Early Warning System")

# ===============================
# USER SETTINGS
# ===============================
EMAIL_RECEIVER = "rjsfyd413@naver.com"

# ===============================
# Sidebar
# ===============================
period = st.sidebar.selectbox(
    "Analysis Period",
    ["3mo", "6mo", "1y", "3y"],
    index=2
)

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
    series = []
    for name, ticker in assets.items():
        df = yf.download(ticker, period=period, interval="1d", progress=False)
        if df.empty:
            continue
        close = df["Close"]
        if isinstance(close, pd.DataFrame):
            close = close.iloc[:, 0]
        series.append(close.rename(name))
    return pd.concat(series, axis=1, join="outer").sort_index()

price = load_data(period)

# ===============================
# Normalize
# ===============================
norm = price.copy()
for c in norm.columns:
    base = norm[c].dropna().iloc[0]
    norm[c] = norm[c] / base * 100

# ===============================
# 200D MA
# ===============================
ma200 = price.rolling(200).mean()

# ===============================
# SIGNAL LOGIC
# ===============================
btc_20d = norm["Bitcoin"].iloc[-1] - norm["Bitcoin"].iloc[-20]
gold_20d = norm["Gold"].iloc[-1] - norm["Gold"].iloc[-20]
ratio = price["Nasdaq"] / price["S&P 500"]
ratio_down = ratio.iloc[-1] < ratio.iloc[-20]

sp_below_200 = price["S&P 500"].iloc[-1] < ma200["S&P 500"].iloc[-1]
nas_below_200 = price["Nasdaq"].iloc[-1] < ma200["Nasdaq"].iloc[-1]

# ===============================
# SIGNAL STATE
# ===============================
signal = "NORMAL"

if btc_20d < -5 and gold_20d > 3 and ratio_down:
    signal = "EARLY WARNING"

if signal == "EARLY WARNING" and sp_below_200 and nas_below_200:
    signal = "CONFIRMED DRAWDOWN"

# ===============================
# EMAIL FUNCTION
# ===============================
def send_email(subject, body):
    try:
        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = st.secrets["EMAIL_SENDER"]
        msg["To"] = EMAIL_RECEIVER

        server = smtplib.SMTP_SSL("smtp.naver.com", 465)
        server.login(
            st.secrets["EMAIL_SENDER"],
            st.secrets["EMAIL_PASSWORD"]
        )
        server.send_message(msg)
        server.quit()
    except:
        pass

# ===============================
# EMAIL TRIGGER (1/day)
# ===============================
today = datetime.now().strftime("%Y-%m-%d")
if st.session_state.get("last_mail") != today:
    if signal in ["EARLY WARNING", "CONFIRMED DRAWDOWN"]:
        send_email(
            f"[Market Alert] {signal}",
            f"""
Risk Level: {signal}

- Bitcoin momentum collapse
- Gold defensive rotation
- Nasdaq/S&P ratio weakening
- 200D MA status:
  S&P500: {'Below' if sp_below_200 else 'Above'}
  Nasdaq: {'Below' if nas_below_200 else 'Above'}

Action: Reduce risk / Delay entry
"""
        )
        st.session_state["last_mail"] = today

# ===============================
# VISUAL
# ===============================
fig = go.Figure()
for c in norm.columns:
    fig.add_trace(go.Scatter(
        x=norm.index,
        y=norm[c],
        name=c,
        mode="lines"
    ))

st.plotly_chart(fig, use_container_width=True)

# ===============================
# STATUS
# ===============================
st.markdown("## 🚨 Current Market Status")

if signal == "CONFIRMED DRAWDOWN":
    st.error("🔴 CONFIRMED MARKET DRAWDOWN – Avoid new equity positions")
elif signal == "EARLY WARNING":
    st.warning("🟠 EARLY RISK WARNING – Stay defensive")
else:
    st.success("🟢 Market Stable – No systemic risk detected")
