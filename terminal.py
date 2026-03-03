import streamlit as st
import yfinance as yf
import pandas as pd
import time

# 1. TASARIM AYARLARI (Göz yormayan, modern ve sade)
st.set_page_config(page_title="Borsa Pro Terminal", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    .stApp { background-color: #0f111a; color: #f0f2f6; }
    [data-testid="stSidebar"] { background-color: #161a25; border-right: 1px solid rgba(255,255,255,0.1); }
    
    /* Veri Kartı: Grafiksiz, sadece rakam odaklı */
    .data-card {
        background: #1e222d;
        border: 1px solid #2a2e39;
        border-radius: 12px;
        padding: 25px;
        margin-bottom: 20px;
        text-align: center;
        max-width: 700px;
        margin-left: auto;
        margin-right: auto;
    }
    
    .symbol-name { font-size: 2rem; font-weight: 800; color: #3772ff; margin-bottom: 10px; }
    .price-now { font-size: 3rem; font-weight: 700; margin: 10px 0; }
    .change-badge { font-size: 1.2rem; font-weight: bold; padding: 5px 15px; border-radius: 30px; display: inline-block; }
    .details-row { display: flex; justify-content: space-around; margin-top: 20px; border-top: 1px solid rgba(255,255,255,0.05); padding-top: 15px; }
    .detail-item { flex: 1; }
    .detail-label { font-size: 0.8rem; color: #848e9c; }
    .detail-value { font-size: 1.1rem; font-weight: 600; color: #ffffff; }

    header, footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# 2. DİL PAKETLERİ VE YAN PANEL (SIDEBAR)
dil_ayarlari = {
    "Türkçe": {
        "baslik": "BORSA PRO TERMİNAL",
        "ayar": "⚙️ Ayarlar",
        "dil": "Dil Seçimi",
        "para": "Para Birimi",
        "yenile": "Otomatik Yenile (15sn)",
        "ara": "Hisse Ara (THYAO.IS, BTC-USD, AAPL...)",
        "kapanis": "Dünkü Kapanış",
        "guncel": "Güncel Fiyat",
        "son_24": "Son 24 Saat Özeti",
        "hata": "Veri bulunamadı"
    },
    "English": {
        "baslik": "STOCK PRO TERMINAL",
        "ayar": "⚙️ Settings",
        "dil": "Language Selection",
        "para": "Currency",
        "yenile": "Auto Refresh (15s)",
        "ara": "Search Symbol (AAPL, BTC-USD...)",
        "kapanis": "Prev. Close",
        "guncel": "Current Price",
        "son_24": "Last 24h Summary",
        "hata": "Data not found"
    }
}

with st.sidebar:
    # Dil Seçimi (En Üstte)
    secili_dil = st.selectbox("Language / Dil", ["Türkçe", "English"])
    D = dil_ayarlari[secili_dil]
    
    st.divider()
    st.markdown(f"### {D['ayar']}")
    
    # Para Birimi Seçimi
    para_birimi = st.radio(D["para"], ["₺ TRY", "$ USD"])
    
    # Yenileme Seçeneği
    oto_taze = st.checkbox(D["yenile"], value=True)
    
    st.divider()
    if secili_dil == "Türkçe":
        st.caption("BIST hisseleri için .IS ekleyin.")
    else:
        st.caption("Add .IS for Istanbul Stocks.")

# 3. VERİ MOTORU (KUR HESAPLAMA)
@st.cache_data(ttl=600)
def get_usd_rate():
    try: return float(yf.Ticker("USDTRY=X").history(period="1d")['Close'].iloc[-1])
    except: return 34.55
usd_kuru = get_usd_rate()

# 4. ANA EKRAN
st.markdown(f"<h1 style='text-align: center;'>{D['baslik']}</h1>", unsafe_allow_html=True)

search_input = st.text_input("", placeholder=D["ara"])
symbols = [s.strip().upper() for s in search_input.split(",") if s.strip()]

# 5. VERİ GÖSTERİMİ (GRAFİKSİZ VE TEMİZ)
if not symbols:
    st.markdown(f"<div style='text-align: center; padding: 50px; color: #434651;'>{D['ara']}</div>", unsafe_allow_html=True)
else:
    for sym in symbols:
        try:
            ticker = yf.Ticker(sym)
            data = ticker.history(period="2d")
            if data.empty: continue
            
            fiyat_simdi = data['Close'].iloc[-1]
            fiyat_once = data['Close'].iloc[-2]
            degisim = ((fiyat_simdi - fiyat_once) / fiyat_once) * 100
            
            # Para Birimi Dönüşümü
            is_bist = sym.endswith(".IS")
            birim_isareti = "₺" if "TRY" in para_birimi else "$"
            
            # Hesaplama Mantığı
            g_simdi = fiyat_simdi * usd_kuru if ("TRY" in para_birimi and not is_bist) else (fiyat_simdi / usd_kuru if ("USD" in para_birimi and is_bist) else fiyat_simdi)
            g_once = fiyat_once * usd_kuru if ("TRY" in para_birimi and not is_bist) else (fiyat_once / usd_kuru if ("USD" in para_birimi and is_bist) else fiyat_once)

            # MODERN VERİ KARTI (GRAFİK YOK)
            color = "#00e676" if degisim >= 0 else "#ff1744"
            arrow = "▲" if degisim >= 0 else "▼"
            
            st.markdown(f"""
                <div class="data-card">
                    <div class="symbol-name">{sym}</div>
                    <div class="price-now">{g_simdi:,.2f} {birim_isareti}</div>
                    <div class="change-badge" style="background: {color}15; color: {color}; border: 1px solid {color}44;">
                        {arrow} {degisim:+.2f}%
                    </div>
                    
                    <div class="details-row">
                        <div class="detail-item">
                            <div class="detail-label">{D['kapanis']}</div>
                            <div class="detail-value">{g_once:,.2f} {birim_isareti}</div>
                        </div>
                        <div style="width:1px; background: rgba(255,255,255,0.1);"></div>
                        <div class="detail-item">
                            <div class="detail-label">{D['son_24']}</div>
                            <div class="detail-value" style="color:{color}">{degisim:+.2f}%</div>
                        </div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
        except:
            st.error(f"{sym}: {D['hata']}")

# 6. OTO YENİLEME
if oto_taze:
    time.sleep(15)
    st.rerun()
