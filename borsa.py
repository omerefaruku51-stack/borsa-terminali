import streamlit as st
import yfinance as yf
import pandas as pd
import time

# 1. MODERN & MINIMALIST UI CONFIG
st.set_page_config(page_title="Borsa Intelligence", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    /* Global Stil: Karanlık ama yumuşak bir tema */
    .stApp { background-color: #0f111a; color: #f0f2f6; }
    [data-testid="stAppViewBlockContainer"] { opacity: 1 !important; padding-top: 2rem; }
    
    /* Kart Tasarımı: Glassmorphism etkisi */
    div[data-testid="stMetric"] {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        padding: 20px;
        backdrop-filter: blur(10px);
    }
    
    /* Trend Kutucukları: Zarif ve Modern */
    .status-badge {
        padding: 8px 16px;
        border-radius: 30px;
        font-size: 0.85rem;
        font-weight: 600;
        letter-spacing: 0.5px;
        display: inline-block;
        margin-top: 10px;
    }
    .bullish { 
        background-color: rgba(0, 230, 118, 0.1); 
        color: #00e676; 
        border: 1px solid rgba(0, 230, 118, 0.3);
        box-shadow: 0 0 15px rgba(0, 230, 118, 0.1);
    }
    .bearish { 
        background-color: rgba(255, 23, 68, 0.1); 
        color: #ff1744; 
        border: 1px solid rgba(255, 23, 68, 0.3);
        box-shadow: 0 0 15px rgba(255, 23, 68, 0.1);
    }
    
    /* Hisse Başlığı */
    .symbol-title {
        font-size: 1.8rem;
        font-weight: 700;
        color: #ffffff;
        margin-bottom: -10px;
    }
    .symbol-subtitle {
        font-size: 0.9rem;
        color
