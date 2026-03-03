import streamlit as st
import yfinance as yf
import pandas as pd
import time

# 1. MODERN & MINIMALIST UI CONFIG
st.set_page_config(page_title="Borsa Intelligence", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    /* Global Stil */
    .stApp { background-color: #0f111a; color: #f0f2f6; }
    [data-testid="stAppViewBlockContainer"] { opacity: 1 !important; padding-top: 2rem; }
    
    /* Kart Tasarımı */
    div[data-testid="stMetric"] {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        padding: 20px;
        backdrop-filter: blur(10px);
    }
    
    /* Trend Kutucukları */
    .status-badge {
        padding: 8px 16px;
        border-radius: 30px;
        font-size: 0.85rem;
        font-weight: 600;
        display: inline-block;
        margin-top: 10px;
    }
    .bullish { 
        background-color: rgba(0, 230, 118, 0.1); 
        color: #00e676; 
        border: 1px solid rgba(0, 230, 118, 0.3);
    }
    .bearish { 
        background-color: rgba(255, 23, 68, 0.1); 
        color: #ff1744; 
        border: 1px solid rgba(255, 23, 68, 0.3);
    }
    
    /* Hisse Başlığı */
    .symbol-title { font-size: 1.8rem; font-weight: 700; color: #ffffff; margin-bottom: 5px; }
    .symbol-subtitle { font-size: 0.9rem; color: #848e9c; margin-bottom: 20px; }

    header, footer {visibility: hidden;}
    hr { border-top: 1px solid rgba(255,255,255,0.05); margin: 2rem 0; }
    </style>
    """, unsafe_allow_html=True)

# 2. DİL VE AYARLAR
with st.sidebar:
    st.markdown("### ⚙️ Ayarlar")
    currency = st.radio("Para Birimi", ["₺ TRY", "$ USD"])
    refresh = st.checkbox("Canlı Veri", value=True)

# 3. ANA EKRAN
st.markdown("<h1 style='text-align: center; color: #3772ff;'>BORSA INTELLIGENCE</h1>", unsafe_allow_html=True)

# Veri Girişi
search_input = st.text_input("İzleme Listesi", placeholder="Örn: THYAO.IS, BTC-USD, AAPL")
symbols = [s.strip().upper() for s in search_input.split(",") if s.strip()]

@st.cache_data(ttl=600)
def get_usd_rate():
    try: return float(yf.Ticker("USDTRY=X").history(period="1d")['Close'].iloc[-1])
    except: return 34.35
usd_rate = get_usd_rate()

# 4. GÖRSELLEŞTİRME
if not symbols:
    st.markdown("<div style='text-align: center; padding: 50px; color: #434651;'>İzlemek istediğiniz hisseleri virgülle ayırarak yazın.</div>", unsafe_allow_html=True)
else:
    for sym in symbols:
        try:
            ticker = yf.Ticker(sym)
            data = ticker.history(period="1mo")
            if data.empty: continue
            
            price = data['Close'].iloc[-1]
            change = ((price - data['Close'].iloc[-2]) / data['Close'].iloc[-2]) * 100
            ma20 = data['Close'].rolling(window=20).mean().iloc[-1]
            
            # Kur Dönüşümü
            is_bist = ".IS" in sym
            unit = "₺" if "TRY" in currency else "$"
            d_price = price
            if "TRY" in currency and not is_bist: d_price *= usd_rate
            elif "USD" in currency and is_bist: d_price /= usd_rate

            # Kart Yapısı
            st.markdown(f"<div class='symbol-title'>{sym}</div>", unsafe_allow_html=True)
            
            c1, c2, c3 = st.columns([1, 1, 2.5])
            with c1:
                st.metric("Fiyat", f"{d_price:,.2f} {unit}", f"{change:+.2f}%")
            with c2:
                st.write("**Trend**")
                if price > ma20:
                    st.markdown(f"<span class='status-badge bullish'>● POZİTİF İVME</span>", unsafe_allow_html=True)
                else:
                    st.markdown(f"<span class='status-badge bearish'>● NEGATİF İVME</span>", unsafe_allow_html=True)
            with c3:
                st.line_chart(data['Close'].tail(20), height=150)
            
            st.markdown("<hr>", unsafe_allow_html=True)
        except:
            st.warning(f"{sym} verisi bulunamadı.")

# 5. AUTO-REFRESH
if refresh:
    time.sleep(10)
    st.rerun()
