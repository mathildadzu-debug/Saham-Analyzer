import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from ta.momentum import RSIIndicator
from ta.trend import MACD, SMAIndicator

st.title("Analisis Saham Indonesia: Teknis & Fundamental")
st.write("Masukkan kode saham Indonesia (mis: BBCA.JK untuk BCA) dan pilih periode analisis.")

# Input dari pengguna
ticker = st.text_input("Kode Saham", "BBCA.JK")
period = st.selectbox("Periode Data", ["1mo", "3mo", "6mo", "1y", "2y"], index=3)

if st.button("Analisis"):
    try:
        # Ambil data saham
        stock = yf.Ticker(ticker)
        data = stock.history(period=period)
        
        if data.empty:
            st.error("Data saham tidak ditemukan. Periksa kode saham.")
            return
        
        # Analisis Teknis
        data['SMA50'] = SMAIndicator(data['Close'], window=50).sma_indicator()
        data['SMA200'] = SMAIndicator(data['Close'], window=200).sma_indicator()
        data['RSI'] = RSIIndicator(data['Close']).rsi()
        macd = MACD(data['Close'])
        data['MACD'] = macd.macd()
        data['MACD_Signal'] = macd.macd_signal()
        
        # Analisis Fundamental
        info = stock.info
        pe_ratio = info.get('trailingPE', 'N/A')
        roe = info.get('returnOnEquity', 'N/A')
        eps = info.get('trailingEps', 'N/A')
        
        st.subheader("Analisis Fundamental")
        st.write(f"**P/E Ratio:** {pe_ratio}")
        st.write(f"**ROE:** {roe}")
        st.write(f"**EPS:** {eps}")
        
        # Sinyal Buy/Sell
        latest = data.iloc[-1]
        if latest['RSI'] < 30 and latest['Close'] > latest['SMA50']:
            signal = "BUY (Oversold dan tren naik)"
            st.success(f"Sinyal: {signal}")
        elif latest['RSI'] > 70 and latest['Close'] < latest['SMA50']:
            signal = "SELL (Overbought dan tren turun)"
            st.error(f"Sinyal: {signal}")
        else:
            signal = "HOLD"
            st.info(f"Sinyal: {signal}")
        
        # Plot Grafik Teknis
        st.subheader("Grafik Analisis Teknis")
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.plot(data.index, data['Close'], label='Harga Penutupan')
        ax.plot(data.index, data['SMA50'], label='SMA50')
        ax.plot(data.index, data['SMA200'], label='SMA200')
        ax.set_title(f'Harga Saham {ticker} dengan Moving Averages')
        ax.legend()
        st.pyplot(fig)
        
        # Tabel Data Teknis (opsional)
        st.subheader("Data Teknis Terbaru")
        st.dataframe(data.tail(10)[['Close', 'SMA50', 'SMA200', 'RSI', 'MACD', 'MACD_Signal']])
        
    except Exception as e:
        st.error(f"Terjadi kesalahan: {str(e)}")

st.write("---")
st.write("**Catatan:** Sinyal ini berdasarkan aturan sederhana dan tidak menjamin hasil. Gunakan untuk edukasi saja.")