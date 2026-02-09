# test_swarm.py
import yfinance as yf
import streamlit as st

st.title("Alpha Swarm Connectivity Test")
ticker = st.text_input("Enter Ticker", "AAPL")

if st.button("Get Data"):
    data = yf.Ticker(ticker).history(period="1mo")
    st.write(f"Latest Close for {ticker}: {data['Close'].iloc[-1]:.2f}")
    st.line_chart(data['Close'])