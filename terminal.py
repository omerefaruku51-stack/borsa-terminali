import streamlit as st
import yfinance as yf
import pandas as pd
import time

# 1. PREMIUM UI AYARLARI
st.set_page_config(page_title="Borsa Pro Terminal", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    .stApp { background-color: #0f111a; color: #f0f2f6; }
    [data-testid="stSidebar"] { background-color: #161a25; border-right: 1px solid rgba(255,255,255,0.1); }
    
    /* Ana Kart Tasarımı */
    .data-card {
        background: #1e222d;
        border: 1px solid #2a2e39;
        border-radius: 16px;
        padding: 30px;
        margin: 20px auto;
        text-align: center;
        max-width: 800px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.3);
    }
    
    .symbol-name { font-size: 2.2rem; font-weight: 800; color: #3772ff; margin-bottom: 5px; }
    .price-now { font-size: 3.5rem; font-weight: 700; margin: 15px 0; letter-spacing: -1px; }
    
    /* Senin paylaştığın Details Row yapısının CSS karşılığı */
    .details-row { 
        display: flex; 
        justify-content: space-around; 
        margin-top: 25px; 
        border-top: 1px solid rgba(255,255,255,0.1); 
        padding-top: 20px; 
    }
    .detail-item { flex: 1; }
    .detail-label { font-size: 0.9rem; color: #848e9c; margin-bottom: 8px; text-transform: uppercase; }
    .detail-value { font-size: 1.3rem; font-weight: 600; color: #ffffff; }

    header, footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# 2. DİL VE SIDEBAR (YAN PANEL) SİSTEMİ
dil_paketleri = {
    "Türkçe": {
        "baslik": "BORSA PRO TERMİNAL",
        "ayar": "⚙️ Terminal Ayarları",
        "para": "Para Birimi",
        "yenile": "Otomatik Güncelle (15sn)",
        "ara": "Hisse veya Kripto Ara...",
        "kapanis": "Dünkü Kapanış",
        "son_24": "Son 24 Saat Özeti",
        "guncel": "Anlık Fiyat",
        "hata": "Sembol bulunamadı veya veri çekilemiyor."
    },
    "English": {
        "baslik": "STOCK PRO TERMINAL",
        "ayar": "⚙️ Terminal Settings",
        "para": "Currency Selection",
        "yenile": "Auto Refresh (15s)",
        "ara": "Search Stocks or Crypto...",
        "kapanis": "Prev. Close",
        "son_24": "Last 24h Summary",
        "guncel": "Live Price",
        "hata": "Symbol not found or data error."
    }
}

with st.sidebar:
    # Dil seçimi tüm panelin dilini belirler
    secilen_dil = st.selectbox("Language / Dil", ["Türkçe", "English"])
    D = dil_paketleri[secilen_dil]
    
    st.divider()
    st.markdown(f"### {D['ayar']}")
    para_birimi = st.radio(D["para"], ["₺ TRY", "$ USD"])
    oto_taze = st.checkbox(D["yenile"], value=True)
    
    st.divider()
    st.info("BIST: THYAO.IS | NASDAQ: AAPL | Kripto: BTC-USD")

# 3. VERİ MOTORU
@st.cache_data(ttl=600)
def get_usd():
    try: return float(yf.Ticker("USDTRY=X").history(period="1d")['Close'].iloc[-1])
    except: return 34.40
usd_kuru = get_usd()

# 4. ANA EKRAN
st.markdown(f"<h1 style='text-align: center; color: #ffffff;'>{D['baslik']}</h1>", unsafe_allow_html=True)
search_input = st.text_input("", placeholder=D["ara"])
symbols = [s.strip().upper() for s in search_input.split(",") if s.strip()]

# 5. VERİ GÖSTERİMİ
if not symbols:
    st.markdown(f"<div style='text-align: center; padding: 100px; color: #434651;'>{D['ara']}</div>", unsafe_allow_html=True)
else:
    for sym in symbols:
        try:
            ticker = yf.Ticker(sym)
            data = ticker.history(period="2d")
            if data.empty: continue
            
            p_now = data['Close'].iloc[-1]
            p_prev = data['Close'].iloc[-2]
            change = ((p_now - p_prev) / p_prev) * 100
            
            # Kur Hesaplama
            is_bist = sym.endswith(".IS")
            unit = "₺" if "TRY" in para_birimi else "$"
            
            # Dönüşüm Mantığı
            disp_now = p_now * usd_kuru if ("TRY" in para_birimi and not is_bist) else (p_now / usd_kuru if ("USD" in para_birimi and is_bist) else p_now)
            disp_prev = p_prev * usd_kuru if ("TRY" in para_birimi and not is_bist) else (p_prev / usd_kuru if ("USD" in para_birimi and is_bist) else p_prev)

            # GÖRSELLEŞTİRME (Tam istediğin HTML yapısı ile)
            color = "#00e676" if change >= 0 else "#ff1744"
            
            st.markdown(f"""
                <div class="data-card">
                    <div class="symbol-name">{sym}</div>
                    <div class="price-now">{disp_now:,.2f} {unit}</div>
                    
                    <div class="details-row">
                        <div class="detail-item">
                            <div class="detail-label">{D['kapanis']}</div>
                            <div class="detail-value">{disp_prev:,.2f} {unit}</div>
                        </div>
                        <div style="width:1px; background: rgba(255,255,255,0.1);"></div>
                        <div class="detail-item">
                            <div class="detail-label">{D['son_24']}</div>
                            <div class="detail-value" style="color:{color}">{change:+.2f}%</div>
                        </div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
        except:
            st.error(f"{sym}: {D['hata']}")

# 6. AUTO REFRESH
if oto_taze:
    time.sleep(15)
    st.rerun()
