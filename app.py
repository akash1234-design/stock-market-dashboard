import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta

st.set_page_config(page_title="Stock Market Dashboard", page_icon="📈", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Inter:wght@400;600;700&display=swap');
html, body, [class*="css"] { background-color: #0a0a1a; color: #fff; font-family: 'Inter', sans-serif; }
.stApp { background-color: #0a0a1a; }
.hero {
    background: linear-gradient(135deg, #00FF00 0%, #00CC00 50%, #1a0a4a 100%);
    padding: 2.5rem; border-radius: 20px; margin-bottom: 2rem; text-align: center;
    box-shadow: 0 8px 32px rgba(0,255,0,0.3);
}
.hero h1 { font-family:'Bebas Neue',sans-serif; font-size:3.5rem; letter-spacing:4px; color:#fff; margin:0; }
.hero p { color:#99ff99; margin-top:0.5rem; }
.metric-card {
    background: linear-gradient(135deg,#1a1a2e,#16213e); border:1px solid #00FF00;
    border-radius:16px; padding:1.3rem; text-align:center; margin-bottom:1rem;
    box-shadow:0 4px 15px rgba(0,255,0,0.15);
}
.metric-number { font-family:'Bebas Neue',sans-serif; font-size:2.5rem; color:#00FF00; }
.metric-label { color:#aaa; font-size:0.8rem; text-transform:uppercase; letter-spacing:2px; }
.section-title {
    font-family:'Bebas Neue',sans-serif; font-size:1.8rem; color:#00FF00;
    letter-spacing:3px; border-left:4px solid #00FF00; padding-left:12px; margin:1.5rem 0 1rem 0;
}
[data-testid="stSidebar"] { background-color:#0d0d1a !important; border-right:1px solid #00FF00; }
.stTabs [data-baseweb="tab-list"] { background-color:#1a1a2e; border-radius:10px; }
.stTabs [aria-selected="true"] { color:#00FF00 !important; border-bottom:2px solid #00FF00; }
.stButton > button {
    background:linear-gradient(135deg,#00FF00,#00CC00); color:#000; border:none;
    border-radius:10px; font-weight:700; padding:0.6rem 2rem; transition:all 0.2s;
}
.stButton > button:hover { transform:scale(1.03); }
#MainMenu, footer, header { visibility:hidden; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero">
    <h1>📈 STOCK MARKET DASHBOARD</h1>
    <p>Real-Time Stock Prices • Charts • Analysis • Portfolio</p>
</div>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("## 📊 Stock Search")
    stock = st.text_input("Stock Symbol (e.g., RELIANCE.NS)", "RELIANCE.NS", label_visibility="collapsed")
    period = st.selectbox("Time Period", ["1mo","3mo","6mo","1y","2y","5y"])
    st.markdown("---")
    st.info("Indian Stocks: RELIANCE.NS, TCS.NS, INFY.NS, HDFC.NS, WIPRO.NS")

try:
    ticker = yf.Ticker(stock)
    hist = ticker.history(period=period)
    info = ticker.info
    
    if len(hist) > 0:
        current_price = hist['Close'].iloc[-1]
        prev_price = hist['Close'].iloc[0]
        change = current_price - prev_price
        change_pct = (change / prev_price * 100) if prev_price != 0 else 0
        
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.markdown(f'<div class="metric-card"><div class="metric-number">₹{current_price:.2f}</div><div class="metric-label">Current Price</div></div>', unsafe_allow_html=True)
        with c2:
            color = "🟢" if change >= 0 else "🔴"
            st.markdown(f'<div class="metric-card"><div class="metric-number">{color} {change:.2f}</div><div class="metric-label">Change</div></div>', unsafe_allow_html=True)
        with c3:
            st.markdown(f'<div class="metric-card"><div class="metric-number">{change_pct:.2f}%</div><div class="metric-label">Change %</div></div>', unsafe_allow_html=True)
        with c4:
            market_cap = info.get('marketCap', 0)
            if market_cap > 0:
                st.markdown(f'<div class="metric-card"><div class="metric-number">₹{market_cap/100000000:.0f}Cr</div><div class="metric-label">Market Cap</div></div>', unsafe_allow_html=True)
        
        tab1, tab2, tab3, tab4 = st.tabs(["📊 Chart", "📈 Stats", "💼 Info", "🔍 Details"])
        
        GREEN = "#00FF00"
        
        with tab1:
            st.markdown('<div class="section-title">PRICE CHART</div>', unsafe_allow_html=True)
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=hist.index, y=hist['Close'],
                                    mode='lines', name='Price',
                                    line=dict(color=GREEN, width=3),
                                    fill='tozeroy', fillcolor='rgba(0,255,0,0.1)'))
            fig.update_layout(
                plot_bgcolor="rgba(0,0,0,0)", 
                paper_bgcolor="rgba(0,0,0,0)",
                font=dict(color="white"), 
                hovermode='x unified',
                xaxis=dict(gridcolor="#222"),
                yaxis=dict(gridcolor="#222")
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with tab2:
            st.markdown('<div class="section-title">TECHNICAL STATS</div>', unsafe_allow_html=True)
            ma_50 = hist['Close'].rolling(50).mean().iloc[-1] if len(hist) >= 50 else 0
            ma_200 = hist['Close'].rolling(200).mean().iloc[-1] if len(hist) >= 200 else 0
            
            stats_df = pd.DataFrame({
                "Metric": ["52 Week High", "52 Week Low", "200 Day MA", "50 Day MA", "Volume Avg", "PE Ratio"],
                "Value": [
                    f"₹{info.get('fiftyTwoWeekHigh', 'N/A')}",
                    f"₹{info.get('fiftyTwoWeekLow', 'N/A')}",
                    f"₹{ma_200:.2f}" if ma_200 > 0 else "N/A",
                    f"₹{ma_50:.2f}" if ma_50 > 0 else "N/A",
                    f"{info.get('averageVolume', 'N/A'):,}",
                    f"{info.get('trailingPE', 'N/A')}"
                ]
            })
            st.dataframe(stats_df, use_container_width=True, hide_index=True)
        
        with tab3:
            st.markdown('<div class="section-title">COMPANY INFO</div>', unsafe_allow_html=True)
            info_df = pd.DataFrame({
                "Field": ["Sector", "Industry", "Website", "Employees", "Dividend Yield"],
                "Value": [
                    info.get('sector', 'N/A'),
                    info.get('industry', 'N/A'),
                    info.get('website', 'N/A'),
                    info.get('fullTimeEmployees', 'N/A'),
                    f"{info.get('dividendYield', 0)*100:.2f}%" if info.get('dividendYield') else 'N/A'
                ]
            })
            st.dataframe(info_df, use_container_width=True, hide_index=True)
        
        with tab4:
            st.markdown('<div class="section-title">HISTORICAL DATA</div>', unsafe_allow_html=True)
            display_df = hist[['Open','High','Low','Close','Volume']].tail(30).reset_index()
            display_df['Date'] = display_df['Date'].dt.date
            st.dataframe(display_df, use_container_width=True, hide_index=True, height=450)
            
            csv = hist[['Open','High','Low','Close','Volume']].to_csv().encode('utf-8')
            st.download_button("⬇️ Download CSV", csv, f"{stock}_data.csv", "text/csv")
    
    else:
        st.error(f"Stock '{stock}' nahi mila!")
        st.info("Valid symbols: RELIANCE.NS, TCS.NS, INFY.NS, HDFC.NS, WIPRO.NS")

except Exception as e:
    st.error(f"Error: {str(e)}")
    st.info("Check your stock symbol. Use .NS for India stocks (e.g., RELIANCE.NS)")

st.markdown("---")
st.markdown('<p style="text-align:center;color:#444;font-size:0.8rem;">📈 Stock Market Dashboard | Powered by Yahoo Finance</p>', unsafe_allow_html=True)
