import streamlit as st
import yfinance as yf
import pandas as pd
import time

# 1. SAYFA VE MODERN TASARIM AYARLARI
st.set_page_config(page_title="Borsa Intelligence", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    .stApp { background-color: #0f111a; color: #f0f2f6; }
    [data-testid="stAppViewBlockContainer"] { opacity: 1 !important; padding-top: 2rem; }
    
    /* Yan Menü (Sidebar) Tasarımı */
    [data-testid="stSidebar"] { background-color: #161a25; border-right: 1px solid rgba(255,255,255,0.05); }

    /* Trend Okları İçin CSS */
    .trend-indicator {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 45px;
        height: 45px;
        border-radius: 50%;
        font-size: 22px;
        font-weight: bold;
    }
    .up-arrow { 
        background-color: rgba(0, 230, 118, 0.15); 
        color: #00e676; 
        border: 2px solid #00e676;
        box-shadow: 0 0 10px rgba(0, 230, 118, 0.2);
    }
    .down-arrow { 
        background-color: rgba(255, 23, 68, 0.15); 
        color: #ff1744; 
        border: 2px solid #ff1744;
        box-shadow: 0 0 10px rgba(255, 23, 68, 0.2);
    }
    
    .symbol-title { font-size: 1.8rem; font-weight: 700; color: #ffffff; }
    header, footer {visibility: hidden;}
    hr { border-top: 1px solid rgba(255,255,255,0.05); margin: 1.5rem 0; }
    </style>
    """, unsafe_allow_html=True)

# 2. DİL VE YAN PANEL AYARLARI (Geri Geldi)
dil_paketleri = {
    "Türkçe": {
        "baslik": "BORSA INTELLIGENCE",
        "liste": "İzleme Listesi",
        "ara": "Sembolleri virgülle ayırın (THYAO.IS, BTC-USD...)",
        "fiyat": "Fiyat",
        "trend": "Yön",
        "hata": "Veri bulunamadı"
    },
    "English": {
        "baslik": "STOCK INTELLIGENCE",
        "liste": "Watchlist",
        "ara": "Separate symbols with commas...",
        "fiyat": "Price",
        "trend": "Trend",
        "hata": "Data not found"
    }
}

with st.sidebar:
    st.markdown("### ⚙️ Terminal Ayarları")
    secili_dil = st.selectbox("Dil / Language", ["Türkçe", "English"])
    D = dil_paketleri[secili_dil]
    
    para_birimi = st.radio("Para Birimi", ["₺ TRY", "$ USD"])
    oto_taze = st.checkbox("10sn'de Bir Yenile", value=True)
    st.divider()
    st.info("İpucu: BIST hisseleri için sonuna .IS ekleyin.")

# 3. ANA EKRAN
st.markdown(f"<h1 style='text-align: center; color: #3772ff;'>{D['baslik']}</h1>", unsafe_allow_html=True)

search_input = st.text_input(D["liste"], placeholder=D["ara"])
symbols = [s.strip().upper() for s in search_input.split(",") if s.strip()]

@st.cache_data(ttl=600)
def get_usd_rate():
    try: return float(yf.Ticker("USDTRY=X").history(period="1d")['Close'].iloc[-1])
    except: return 34.40
usd_rate = get_usd_rate()

# 4. GÖRSELLEŞTİRME
if not symbols:
    st.markdown("<div style='text-align: center; padding: 50px; color: #434651;'>Listenize bir sembol ekleyerek başlayın.</div>", unsafe_allow_html=True)
else:
    for sym in symbols:
        try:
            ticker = yf.Ticker(sym)
            data = ticker.history(period="1mo")
            if data.empty: continue
            
            last_price = data['Close'].iloc[-1]
            change = ((last_price - data['Close'].iloc[-2]) / data['Close'].iloc[-2]) * 100
            ma20 = data['Close'].rolling(window=20).mean().iloc[-1]
            
            # Para Birimi Hesaplama
            is_bist = ".IS" in sym
            unit = "₺" if "TRY" in para_birimi else "$"
            final_price = last_price
            if "TRY" in para_birimi and not is_bist: final_price *= usd_rate
            elif "USD" in currency and is_bist: final_price /= usd_rate if 'currency' in locals() else final_price # Hata önleme

            # Arayüz Kartı
            st.markdown(f"<div class='symbol-title'>{sym}</div>", unsafe_allow_html=True)
            
            c1, c2, c3 = st.columns([1, 0.8, 2.5])
            
            with c1:
                st.metric(D["fiyat"], f"{final_price:,.2f} {unit}", f"{change:+.2f}%")
            
            with c2:
                st.write(f"**{D['trend']}**")
                if last_price > ma20:
                    st.markdown('<div class="trend-indicator up-arrow">▲</div>', unsafe_allow_html=True)
                else:
                    st.markdown('<div class="trend-indicator down-arrow">▼</div>', unsafe_allow_html=True)
            
            with c3:
                st.line_chart(data['Close'].tail(20), height=150)
            
            st.markdown("<hr>", unsafe_allow_html=True)
        except:
            st.warning(f"{sym}: {D['hata']}")

# 5. OTO-REFRESH
if oto_taze:
    time.sleep(10)
    st.rerun()
