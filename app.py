import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import numpy as np

# Page config
st.set_page_config(
    page_title="Stock Market Dashboard",
    page_icon="📈",
    layout="wide"
)

# Title
st.title("📊 Stock Market Dashboard")
st.markdown("---")

# Sidebar
with st.sidebar:
    st.header("⚙️ Settings")
    
    # Stock selection
    stock_symbol = st.text_input("Stock Symbol", "AAPL").upper()
    
    # Date range
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Start Date", datetime.now() - timedelta(days=365))
    with col2:
        end_date = st.date_input("End Date", datetime.now())
    
    # Indicators
    st.subheader("Technical Indicators")
    show_ma = st.checkbox("Moving Average", True)
    ma_period = st.slider("MA Period", 5, 200, 50) if show_ma else None
    
    show_rsi = st.checkbox("RSI", False)
    show_macd = st.checkbox("MACD", False)
    
    # Refresh button
    refresh = st.button("🔄 Refresh Data")

# Main content
try:
    # Fetch data
    @st.cache_data(ttl=300)
    def load_data(symbol, start, end):
        stock = yf.Ticker(symbol)
        df = stock.history(start=start, end=end)
        return df, stock.info
    
    df, info = load_data(stock_symbol, start_date, end_date)
    
    if df.empty:
        st.error(f"No data found for {stock_symbol}")
        st.stop()
    
    # Top metrics
    col1, col2, col3, col4, col5 = st.columns(5)
    
    current_price = df['Close'].iloc[-1]
    prev_close = df['Close'].iloc[-2] if len(df) > 1 else current_price
    change = current_price - prev_close
    change_pct = (change / prev_close) * 100
    
    with col1:
        st.metric("Current Price", f"${current_price:.2f}", 
                 f"{change_pct:+.2f}%", delta_color="normal")
    
    with col2:
        st.metric("Day High", f"${df['High'].iloc[-1]:.2f}")
    
    with col3:
        st.metric("Day Low", f"${df['Low'].iloc[-1]:.2f}")
    
    with col4:
        st.metric("Volume", f"{df['Volume'].iloc[-1]:,.0f}")
    
    with col5:
        avg_volume = df['Volume'].tail(20).mean()
        st.metric("Avg Volume (20d)", f"{avg_volume:,.0f}")
    
    st.markdown("---")
    
    # Company info
    with st.expander("📋 Company Information"):
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**Name:** {info.get('longName', 'N/A')}")
            st.write(f"**Sector:** {info.get('sector', 'N/A')}")
            st.write(f"**Industry:** {info.get('industry', 'N/A')}")
        with col2:
            st.write(f"**Market Cap:** ${info.get('marketCap', 0):,.0f}")
            st.write(f"**P/E Ratio:** {info.get('trailingPE', 'N/A')}")
            st.write(f"**52W High/Low:** ${info.get('fiftyTwoWeekHigh', 'N/A')} / ${info.get('fiftyTwoWeekLow', 'N/A')}")
    
    # Candlestick chart
    st.subheader("📈 Price Chart")
    
    fig = go.Figure()
    
    # Candlestick
    fig.add_trace(go.Candlestick(
        x=df.index,
        open=df['Open'],
        high=df['High'],
        low=df['Low'],
        close=df['Close'],
        name='Price'
    ))
    
    # Moving Average
    if show_ma:
        ma = df['Close'].rolling(window=ma_period).mean()
        fig.add_trace(go.Scatter(
            x=df.index,
            y=ma,
            name=f'MA {ma_period}',
            line=dict(color='orange', width=1)
        ))
    
    fig.update_layout(
        title=f'{stock_symbol} - Stock Price',
        yaxis_title='Price (USD)',
        xaxis_title='Date',
        height=500,
        template='plotly_dark'
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # RSI Indicator
    if show_rsi:
        st.subheader("📊 RSI Indicator")
        
        # Calculate RSI
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        fig_rsi = go.Figure()
        fig_rsi.add_trace(go.Scatter(
            x=df.index,
            y=rsi,
            name='RSI',
            line=dict(color='purple', width=2)
        ))
        fig_rsi.add_hline(y=70, line_dash="dash", line_color="red", annotation_text="Overbought")
        fig_rsi.add_hline(y=30, line_dash="dash", line_color="green", annotation_text="Oversold")
        fig_rsi.update_layout(height=300, template='plotly_dark')
        st.plotly_chart(fig_rsi, use_container_width=True)
    
    # Volume chart
    st.subheader("📊 Volume Analysis")
    
    # Color volume bars based on price change
    colors = ['green' if close >= open_ else 'red' 
              for close, open_ in zip(df['Close'], df['Open'])]
    
    fig_volume = go.Figure()
    fig_volume.add_trace(go.Bar(
        x=df.index,
        y=df['Volume'],
        name='Volume',
        marker_color=colors
    ))
    fig_volume.update_layout(height=300, template='plotly_dark')
    st.plotly_chart(fig_volume, use_container_width=True)
    
    # MACD
    if show_macd:
        st.subheader("📈 MACD Indicator")
        
        # Calculate MACD
        exp1 = df['Close'].ewm(span=12, adjust=False).mean()
        exp2 = df['Close'].ewm(span=26, adjust=False).mean()
        macd = exp1 - exp2
        signal = macd.ewm(span=9, adjust=False).mean()
        histogram = macd - signal
        
        fig_macd = go.Figure()
        fig_macd.add_trace(go.Scatter(x=df.index, y=macd, name='MACD', line=dict(color='blue')))
        fig_macd.add_trace(go.Scatter(x=df.index, y=signal, name='Signal', line=dict(color='red')))
        fig_macd.add_trace(go.Bar(x=df.index, y=histogram, name='Histogram', marker_color='gray'))
        fig_macd.update_layout(height=300, template='plotly_dark')
        st.plotly_chart(fig_macd, use_container_width=True)
    
    # Statistical Summary
    with st.expander("📊 Statistical Summary"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Price Statistics**")
            stats_df = pd.DataFrame({
                'Metric': ['Mean', 'Std Dev', 'Min', 'Max'],
                'Value': [
                    f"${df['Close'].mean():.2f}",
                    f"${df['Close'].std():.2f}",
                    f"${df['Close'].min():.2f}",
                    f"${df['Close'].max():.2f}"
                ]
            })
            st.dataframe(stats_df, use_container_width=True)
        
        with col2:
            st.write("**Returns Statistics**")
            returns = df['Close'].pct_change().dropna()
            returns_df = pd.DataFrame({
                'Metric': ['Daily Return Mean', 'Daily Return Std', 'Volatility (Annual)', 'Sharpe Ratio'],
                'Value': [
                    f"{returns.mean()*100:.2f}%",
                    f"{returns.std()*100:.2f}%",
                    f"{returns.std() * (252**0.5) * 100:.2f}%",
                    f"{returns.mean() / returns.std() * (252**0.5):.2f}"
                ]
            })
            st.dataframe(returns_df, use_container_width=True)
    
    # Download data
    st.markdown("---")
    csv = df.to_csv()
    st.download_button(
        label="📥 Download Data as CSV",
        data=csv,
        file_name=f"{stock_symbol}_data.csv",
        mime="text/csv"
    )
    
except Exception as e:
    st.error(f"Error: {str(e)}")
    st.info("Please check the stock symbol and try again. Examples: AAPL, GOOGL, TSLA, MSFT")

# Footer
st.markdown("---")
st.markdown("Made with ❤️ using Streamlit | Data from Yahoo Finance")
