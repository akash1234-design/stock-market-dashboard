import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta
import time
import json

# Page config
st.set_page_config(
    page_title="Stock Market Dashboard",
    page_icon="📈",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    .main-header {
        text-align: center;
        color: white;
        padding: 20px;
        border-radius: 10px;
        background: rgba(0,0,0,0.3);
        margin-bottom: 20px;
    }
    .stock-card {
        background: white;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        text-align: center;
    }
    .metric-value {
        font-size: 24px;
        font-weight: bold;
    }
    .positive {
        color: #00ff00;
    }
    .negative {
        color: #ff0000;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<div class="main-header"><h1>📈 STOCK MARKET DASHBOARD</h1><p>Real-Time Stock Prices · Charts · Analysis</p></div>', unsafe_allow_html=True)

# Sidebar
st.sidebar.header("⚙️ Settings")

# Try to import yfinance with error handling
try:
    import yfinance as yf
    YFINANCE_AVAILABLE = True
except ImportError:
    YFINANCE_AVAILABLE = False
    st.sidebar.error("⚠️ yfinance not installed")

# Use sample data if yfinance fails
@st.cache_data(ttl=300)
def get_sample_data():
    """Generate sample data for demo"""
    dates = pd.date_range(start='2024-01-01', end='2024-12-31', freq='D')
    data = {
        'RELIANCE.NS': np.random.normal(2500, 100, len(dates)),
        'TCS.NS': np.random.normal(3500, 150, len(dates)),
        'HDFCBANK.NS': np.random.normal(1600, 80, len(dates)),
        'INFY.NS': np.random.normal(1400, 70, len(dates))
    }
    df = pd.DataFrame(data, index=dates)
    return df

@st.cache_data(ttl=300)
def get_stock_data(symbol, period="1mo"):
    """Fetch stock data with fallback to sample data"""
    if YFINANCE_AVAILABLE:
        try:
            stock = yf.Ticker(symbol)
            hist = stock.history(period=period)
            if not hist.empty:
                current_price = hist['Close'].iloc[-1]
                if len(hist) > 1:
                    prev_close = hist['Close'].iloc[-2]
                    change = current_price - prev_close
                    change_percent = (change / prev_close) * 100
                else:
                    change = 0
                    change_percent = 0
                return hist, current_price, change, change_percent
        except:
            pass
    
    # Fallback to sample data
    sample_data = get_sample_data()
    if symbol in sample_data.columns:
        hist = pd.DataFrame(sample_data[symbol])
        hist.columns = ['Close']
        current_price = hist['Close'].iloc[-1]
        change = np.random.uniform(-50, 50)
        change_percent = (change / current_price) * 100
        return hist, current_price, change, change_percent
    else:
        return None, None, None, None

# Stock selection
st.sidebar.subheader("📊 Select Stocks")

# Indian Stocks
indian_stocks = {
    "Reliance Industries": "RELIANCE.NS",
    "Tata Consultancy Services": "TCS.NS",
    "HDFC Bank": "HDFCBANK.NS",
    "Infosys": "INFY.NS",
    "ICICI Bank": "ICICIBANK.NS",
    "State Bank of India": "SBIN.NS"
}

# US Stocks
us_stocks = {
    "Apple": "AAPL",
    "Microsoft": "MSFT",
    "Google": "GOOGL",
    "Amazon": "AMZN",
    "Tesla": "TSLA"
}

market_type = st.sidebar.radio("Select Market", ["🇮🇳 Indian Stocks", "🇺🇸 US Stocks"])

if market_type == "🇮🇳 Indian Stocks":
    stock_options = indian_stocks
    currency = "₹"
else:
    stock_options = us_stocks
    currency = "$"

selected_stock = st.sidebar.selectbox("Choose Stock", list(stock_options.keys()))
symbol = stock_options[selected_stock]

# Time period
period = st.sidebar.selectbox(
    "Time Period",
    ["1mo", "3mo", "6mo", "1y"],
    format_func=lambda x: {"1mo": "1 Month", "3mo": "3 Months", "6mo": "6 Months", "1y": "1 Year"}[x]
)

# Refresh button
if st.sidebar.button("🔄 Refresh Data", type="primary"):
    st.cache_data.clear()
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.info("""
💡 **Tips:**
- Data updates every 5 minutes
- Click refresh for latest data
- Demo mode works without internet
""")

# Main content
try:
    # Fetch data
    with st.spinner("Loading stock data..."):
        hist, current_price, change, change_percent = get_stock_data(symbol, period)
    
    if current_price:
        # Display current price
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div class="stock-card">
                <h3>Current Price</h3>
                <div class="metric-value">{currency}{current_price:.2f}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            color_class = "positive" if change >= 0 else "negative"
            arrow = "▲" if change >= 0 else "▼"
            st.markdown(f"""
            <div class="stock-card">
                <h3>Daily Change</h3>
                <div class="metric-value {color_class}">{arrow} {currency}{abs(change):.2f}</div>
                <div class="{color_class}">{change_percent:+.2f}%</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            if hist is not None:
                high = hist['Close'].max()
                st.markdown(f"""
                <div class="stock-card">
                    <h3>Period High</h3>
                    <div class="metric-value">{currency}{high:.2f}</div>
                </div>
                """, unsafe_allow_html=True)
        
        with col4:
            if hist is not None:
                low = hist['Close'].min()
                st.markdown(f"""
                <div class="stock-card">
                    <h3>Period Low</h3>
                    <div class="metric-value">{currency}{low:.2f}</div>
                </div>
                """, unsafe_allow_html=True)
        
        # Chart
        st.subheader("📈 Price Chart")
        
        if hist is not None:
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=hist.index,
                y=hist['Close'],
                mode='lines',
                name='Close Price',
                line=dict(color='#667eea', width=2)
            ))
            
            fig.update_layout(
                title=f"{selected_stock} - Price Trend",
                xaxis_title="Date",
                yaxis_title=f"Price ({currency})",
                hovermode='x unified',
                height=500,
                template='plotly_dark'
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Volume chart if available
            if 'Volume' in hist.columns:
                st.subheader("📊 Trading Volume")
                fig_vol = go.Figure()
                fig_vol.add_trace(go.Bar(
                    x=hist.index,
                    y=hist['Volume'],
                    name='Volume',
                    marker_color='#764ba2'
                ))
                fig_vol.update_layout(height=300, template='plotly_dark')
                st.plotly_chart(fig_vol, use_container_width=True)
            
            # Statistics
            with st.expander("📊 Statistical Summary"):
                stats = hist['Close'].describe()
                col1, col2 = st.columns(2)
                with col1:
                    st.write("**Price Statistics:**")
                    st.write(f"Mean: {currency}{stats['mean']:.2f}")
                    st.write(f"Std Dev: {currency}{stats['std']:.2f}")
                with col2:
                    st.write("**Range:**")
                    st.write(f"Min: {currency}{stats['min']:.2f}")
                    st.write(f"Max: {currency}{stats['max']:.2f}")
            
            # Recent data table
            with st.expander("📅 Recent Price Data"):
                recent = hist.tail(10)[['Close']].round(2)
                recent.index = recent.index.strftime('%Y-%m-%d')
                st.dataframe(recent, use_container_width=True)
        
    else:
        st.warning(f"⚠️ Could not fetch data for {selected_stock}")
        st.info("""
        **Possible reasons:**
        - Stock symbol might be incorrect
        - API rate limit reached (wait 2 minutes)
        - No internet connection
        
        **Try:**
        - Click refresh button after 2 minutes
        - Select a different stock
        - Check your internet connection
        """)

except Exception as e:
    st.error(f"An error occurred: {str(e)}")
    st.info("""
    🔧 **Quick Fix:**
    1. Refresh the page
    2. Wait 2 minutes and try again
    3. Check if all packages are installed
    """)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: gray;">
    Made with ❤️ using Streamlit | Data from Yahoo Finance
    <br>
    <small>📌 Tip: If data doesn't load, wait 2 minutes and click refresh</small>
</div>
""", unsafe_allow_html=True)
