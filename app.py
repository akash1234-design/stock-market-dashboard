import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import yfinance as yf
import plotly.graph_objects as go
import time

st.set_page_config(page_title="Stock Market Dashboard", layout="wide")

# Custom CSS
st.markdown("""
<style>
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    .stButton > button {
        background-color: #4CAF50;
        color: white;
        border-radius: 10px;
        padding: 10px 24px;
    }
    .stock-card {
        background: white;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin: 10px;
        text-align: center;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 20px;
        border-radius: 15px;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.title("📈 Stock Market Dashboard")
st.markdown("### Real-Time Stock Prices · Charts · Analysis")

# Sidebar
st.sidebar.header("⚙️ Settings")

# Use caching to avoid rate limits
@st.cache_data(ttl=300)  # Cache for 5 minutes
def get_stock_data(symbol, period="1mo"):
    """Fetch stock data with error handling"""
    try:
        # Add small delay to be respectful
        time.sleep(0.5)
        stock = yf.Ticker(symbol)
        
        # Get historical data
        hist = stock.history(period=period)
        
        # Get current info
        info = stock.info
        
        if hist.empty:
            return None, None, None
            
        current_price = hist['Close'].iloc[-1]
        
        # Calculate changes
        if len(hist) > 1:
            prev_close = hist['Close'].iloc[-2]
            change = current_price - prev_close
            change_percent = (change / prev_close) * 100
        else:
            change = 0
            change_percent = 0
            
        return hist, current_price, {"change": change, "change_percent": change_percent, "info": info}
    except Exception as e:
        return None, None, {"error": str(e)}

# Indian stocks list (with correct NSE symbols)
indian_stocks = {
    "Reliance Industries": "RELIANCE.NS",
    "Tata Consultancy Services (TCS)": "TCS.NS",
    "HDFC Bank": "HDFCBANK.NS",
    "Infosys": "INFY.NS",
    "ICICI Bank": "ICICIBANK.NS",
    "State Bank of India": "SBIN.NS",
    "Bharti Airtel": "BHARTIARTL.NS",
    "Hindustan Unilever": "HINDUNILVR.NS",
    "ITC Ltd": "ITC.NS",
    "Wipro": "WIPRO.NS"
}

# US stocks option
us_stocks = {
    "Apple": "AAPL",
    "Microsoft": "MSFT",
    "Google": "GOOGL",
    "Amazon": "AMZN",
    "Tesla": "TSLA",
    "Meta (Facebook)": "META",
    "NVIDIA": "NVDA",
    "Netflix": "NFLX"
}

# Stock selection
market = st.sidebar.radio("Select Market", ["🇮🇳 Indian Stocks (NSE)", "🇺🇸 US Stocks"])

if market == "🇮🇳 Indian Stocks (NSE)":
    stock_dict = indian_stocks
else:
    stock_dict = us_stocks

selected_stock_name = st.sidebar.selectbox("Select Stock", list(stock_dict.keys()))
selected_symbol = stock_dict[selected_stock_name]

# Time period selection
period = st.sidebar.selectbox(
    "Select Time Period",
    ["1mo", "3mo", "6mo", "1y", "2y"],
    format_func=lambda x: {"1mo": "1 Month", "3mo": "3 Months", "6mo": "6 Months", "1y": "1 Year", "2y": "2 Years"}[x]
)

# Refresh button
if st.sidebar.button("🔄 Refresh Data", type="primary"):
    st.cache_data.clear()
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.info("""
💡 **Tips:**
- Data refreshes every 5 minutes (to avoid rate limits)
- Click refresh button for latest data
- Data source: Yahoo Finance (free)
- Use .NS suffix for NSE stocks
""")

# Main content
try:
    # Fetch data
    with st.spinner("Fetching stock data..."):
        hist, current_price, metrics = get_stock_data(selected_symbol, period)
    
    if current_price and hist is not None:
        # Top metrics row
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Current Price", f"₹{current_price:.2f}" if "NS" in selected_symbol else f"${current_price:.2f}")
        
        with col2:
            change = metrics.get('change', 0)
            change_percent = metrics.get('change_percent', 0)
            st.metric("Daily Change", 
                     f"{change:+.2f}" if "NS" in selected_symbol else f"{change:+.2f}",
                     delta=f"{change_percent:+.2f}%")
        
        with col3:
            if 'info' in metrics and metrics['info']:
                high = metrics['info'].get('dayHigh', hist['High'].iloc[-1] if not hist.empty else 0)
                st.metric("Day High", f"₹{high:.2f}" if "NS" in selected_symbol else f"${high:.2f}")
        
        with col4:
            if 'info' in metrics and metrics['info']:
                low = metrics['info'].get('dayLow', hist['Low'].iloc[-1] if not hist.empty else 0)
                st.metric("Day Low", f"₹{low:.2f}" if "NS" in selected_symbol else f"${low:.2f}")
        
        # Charts section
        st.subheader("📊 Price Chart")
        
        chart_type = st.radio("Chart Type", ["Line Chart", "Candlestick Chart"], horizontal=True)
        
        if chart_type == "Line Chart":
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=hist.index, y=hist['Close'], 
                                    mode='lines', 
                                    name='Close Price',
                                    line=dict(color='#667eea', width=2)))
            fig.update_layout(title=f"{selected_stock_name} - Price Trend",
                             xaxis_title="Date",
                             yaxis_title="Price",
                             hovermode='x unified',
                             height=500)
            st.plotly_chart(fig, use_container_width=True)
        else:
            fig = go.Figure(data=[go.Candlestick(x=hist.index,
                                                open=hist['Open'],
                                                high=hist['High'],
                                                low=hist['Low'],
                                                close=hist['Close'])])
            fig.update_layout(title=f"{selected_stock_name} - Candlestick Chart",
                             xaxis_title="Date",
                             yaxis_title="Price",
                             height=500)
            st.plotly_chart(fig, use_container_width=True)
        
        # Volume chart
        st.subheader("📊 Trading Volume")
        fig_vol = go.Figure()
        fig_vol.add_trace(go.Bar(x=hist.index, y=hist['Volume'], name='Volume'))
        fig_vol.update_layout(height=300)
        st.plotly_chart(fig_vol, use_container_width=True)
        
        # Technical Indicators
        st.subheader("📈 Technical Indicators")
        
        col1, col2, col3 = st.columns(3)
        
        # Calculate moving averages
        if len(hist) >= 20:
            sma20 = hist['Close'].rolling(window=20).mean().iloc[-1]
            with col1:
                st.metric("20-Day SMA", f"₹{sma20:.2f}" if "NS" in selected_symbol else f"${sma20:.2f}")
        
        if len(hist) >= 50:
            sma50 = hist['Close'].rolling(window=50).mean().iloc[-1]
            with col2:
                st.metric("50-Day SMA", f"₹{sma50:.2f}" if "NS" in selected_symbol else f"${sma50:.2f}")
        
        # RSI calculation (simplified)
        if len(hist) >= 14:
            delta = hist['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs)).iloc[-1]
            
            with col3:
                rsi_color = "🟢" if 30 <= rsi <= 70 else "🔴"
                st.metric(f"{rsi_color} RSI (14)", f"{rsi:.1f}")
        
        # Stock Information Table
        with st.expander("📋 Company Information"):
            info = metrics.get('info', {})
            if info:
                info_data = {
                    "Company Name": info.get('longName', selected_stock_name),
                    "Sector": info.get('sector', 'N/A'),
                    "Industry": info.get('industry', 'N/A'),
                    "Market Cap": f"₹{info.get('marketCap', 0)/1e7:.2f} Cr" if "NS" in selected_symbol else f"${info.get('marketCap', 0)/1e9:.2f}B",
                    "P/E Ratio": info.get('trailingPE', 'N/A'),
                    "52 Week High": f"₹{info.get('fiftyTwoWeekHigh', 'N/A')}" if "NS" in selected_symbol else f"${info.get('fiftyTwoWeekHigh', 'N/A')}",
                    "52 Week Low": f"₹{info.get('fiftyTwoWeekLow', 'N/A')}" if "NS" in selected_symbol else f"${info.get('fiftyTwoWeekLow', 'N/A')}",
                    "Dividend Yield": f"{info.get('dividendYield', 0) * 100:.2f}%" if info.get('dividendYield') else 'N/A'
                }
                df_info = pd.DataFrame(list(info_data.items()), columns=["Metric", "Value"])
                st.table(df_info)
        
        # Recent Data Table
        with st.expander("📅 Recent Price Data"):
            recent_data = hist.tail(10)[['Open', 'High', 'Low', 'Close', 'Volume']].round(2)
            recent_data.index = recent_data.index.strftime('%Y-%m-%d')
            st.dataframe(recent_data, use_container_width=True)
        
    else:
        st.error(f"⚠️ Could not fetch data for {selected_symbol}")
        st.info("""
        **Possible reasons:**
        1. Rate limit - Wait 1-2 minutes and click refresh
        2. Wrong symbol - Use .NS for Indian stocks (e.g., RELIANCE.NS)
        3. Stock market closed - Data updates when market is open
        
        **Try these steps:**
        - Select a different stock
        - Wait 2 minutes and click refresh
        - Check internet connection
        """)
        
except Exception as e:
    st.error(f"An error occurred: {str(e)}")
    st.info("""
    🔧 **Fix:**
    1. Install required packages: `pip install yfinance pandas plotly streamlit`
    2. Restart the app: `streamlit run app.py`
    3. If error persists, use demo mode below 👇
    """)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: gray;">
    Made with ❤️ using Streamlit | Data from Yahoo Finance (Free API)
    <br>
    <small>Note: Data may be delayed by 15-20 minutes for Indian stocks</small>
</div>
""", unsafe_allow_html=True)
