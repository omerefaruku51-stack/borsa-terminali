import streamlit as st
import yfinance as yf
import pandas as pd
import time

# 1. TEMİZ VE MARKASIZ UI (PLAY STORE UYUMLU)
st.set_page_config(page_title="Borsa Pro", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    .stApp { background-color: #0f111a; color: #f0f2f6; }
    [data-testid="stSidebar"] { background-color: #161a25; }
    
    /* Tüm grafikleri ve dış bağlantıları engelleyen temiz kart */
    .clean-card {
        background: #1e222d;
        border-radius: 12px;
        padding: 30px;
        border: 1px solid #2a2e39;
        text-align: center;
        max-width: 800px;
        margin: auto;
    }
    
    .symbol-text { font-size: 2.5rem; font-weight: 800; color: #3772ff; }
    .price-big { font-size: 3rem; font-weight: 700; margin: 10px 0; }
    .change-text { font-size: 1.5rem; font-weight: bold; }
    .sub-text { color: #848e9c; font-size: 1rem; margin-top: 20px; }
    
    header, footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# 2. AYARLAR
with st.sidebar:
    st.title("⚙️ Ayarlar")
    lang = st.selectbox("Dil", ["Türkçe", "English"])
    curr = st.radio("Para Birimi", ["₺ TRY", "$ USD"])
    ref = st.checkbox("Canlı Güncelleme", value=True)

# 3. VERİ ÇEKME
@st.cache_data(ttl=60)
def get_rate():
    try: return yf.Ticker("USDTRY=X").history(period="1d")['Close'].iloc[-1]
    except: return 34.50
usd = get_rate()

st.markdown("<h1 style='text-align: center;'>BORSA TERMİNALİ</h1>", unsafe_allow_html=True)
search = st.text_input("Hisse/Kripto Ara", placeholder="Örn: THYAO.IS, BTC-USD")
symbols = [s.strip().upper() for s in search.split(",") if s.strip()]

# 4. GÖRÜNTÜLEME (KESİN OLARAK SADECE RAKAMLAR)
if not symbols:
    st.info("İzlemek için sembol girin.")
else:
    for sym in symbols:
        try:
            t = yf.Ticker(sym)
            df = t.history(period="2d")
            if df.empty: continue
            
            now, prev = df['Close'].iloc[-1], df['Close'].iloc[-2]
            diff = ((now - prev) / prev) * 100
            
            is_b = sym.endswith(".IS")
            u = "₺" if "TRY" in curr else "$"
            d_now = now * usd if ("TRY" in curr and not is_b) else (now / usd if ("USD" in curr and is_b) else now)
            d_prev = prev * usd if ("TRY" in curr and not is_b) else (prev / usd if ("USD" in curr and is_b) else prev)

            st.markdown(f"""
                <div class="clean-card">
                    <div class="symbol-text">{sym}</div>
                    <div class="price-big">{d_now:,.2f} {u}</div>
                    <div class="change-text" style="color:{'#00e676' if diff>=0 else '#ff1744'}">
                        {'▲' if diff>=0 else '▼'} {diff:+.2f}%
                    </div>
                    <div class="sub-text">Önceki Kapanış: {d_prev:,.2f} {u}</div>
                </div>
                <br>
            """, unsafe_allow_html=True)
        except:
            st.error(f"{sym} verisi çekilemedi.")

if ref:
    time.sleep(15)
    st.rerun()
