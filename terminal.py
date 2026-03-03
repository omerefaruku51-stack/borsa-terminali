import streamlit as st
import yfinance as yf
import pandas as pd
import time

# 1. TASARIM VE SAYFA AYARLARI
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
        max-width: 600px;
        text-align: center;
    }
    
    .symbol-name { font-size: 2rem; font-weight: 800; color: #3772ff; margin-bottom: 5px; }
    .price-now { font-size: 3.2rem; font-weight: 700; margin: 10px 0; }
    
    /* SENİN PAYLAŞTIĞIN YAPININ CSS KARŞILIĞI */
    .details-row { 
        display: flex; 
        justify-content: space-around; 
        margin-top: 20px; 
        border-top: 1px solid rgba(255,255,255,0.1); 
        padding-top: 20px; 
    }
    .detail-item { flex: 1; }
    .detail-label { font-size: 0.85rem; color: #848e9c; margin-bottom: 5px; }
    .detail-value { font-size: 1.2rem; font-weight: 600; color: #ffffff; }

    header, footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# 2. DİL VE YAN PANEL SİSTEMİ
DIL_PAKETI = {
    "Türkçe": {
        "baslik": "BORSA PRO TERMİNAL",
        "ayar": "⚙️ Terminal Ayarları",
        "para": "Para Birimi",
        "yenile": "10sn Otomatik Yenile",
        "ara": "Hisse Ara (THYAO.IS, BTC-USD...)",
        "kapanis": "Dünkü Kapanış",
        "son_24": "Son 24 Saat Özeti",
        "hata": "Veri çekilemedi"
    },
    "English": {
        "baslik": "STOCK PRO TERMINAL",
        "ayar": "⚙️ Terminal Settings",
        "para": "Currency Selection",
        "yenile": "10s Auto Refresh",
        "ara": "Search (AAPL, BTC-USD...)",
        "kapanis": "Prev. Close",
        "son_24": "Last 24h Summary",
        "hata": "Data error"
    }
}

with st.sidebar:
    # Dil seçimi: Seçildiği an tüm panel ve ana ekran değişir
    dil_secim = st.selectbox("Language / Dil", ["Türkçe", "English"])
    D = DIL_PAKETI[dil_secim]
    
    st.divider()
    st.markdown(f"### {D['ayar']}")
    
    # Para Birimi ve Yenileme Kontrolleri
    para_birimi = st.radio(D["para"], ["₺ TRY", "$ USD"])
    oto_taze = st.checkbox(D["yenile"], value=True)
    
    st.divider()
    st.caption("v1.0 Pro - Play Store Ready")

# 3. VERİ MOTORU (KUR HESAPLAMA)
@st.cache_data(ttl=600)
def get_usd():
    try: return float(yf.Ticker("USDTRY=X").history(period="1d")['Close'].iloc[-1])
    except: return 34.50
usd_kuru = get_usd()

# 4. ANA EKRAN
st.markdown(f"<h1 style='text-align: center; color: #ffffff;'>{D['baslik']}</h1>", unsafe_allow_html=True)
search_input = st.text_input("", placeholder=D["ara"])
symbols = [s.strip().upper() for s in search_input.split(",") if s.strip()]

# 5. GÖRÜNTÜLEME (TAMAMEN SENİN YAPINLA)
if not symbols:
    st.markdown(f"<div style='text-align: center; padding: 50px; color: #434651;'>{D['ara']}</div>", unsafe_allow_html=True)
else:
    for sym in symbols:
        try:
            ticker = yf.Ticker(sym)
            data = ticker.history(period="2d")
            if data.empty: continue
            
            p_now, p_prev = data['Close'].iloc[-1], data['Close'].iloc[-2]
            change = ((p_now - p_prev) / p_prev) * 100
            
            # Kur Hesaplama Mantığı
            is_bist = sym.endswith(".IS")
            unit = "₺" if "TRY" in para_birimi else "$"
            
            d_now = p_now * usd_kuru if ("TRY" in para_birimi and not is_bist) else (p_now / usd_kuru if ("USD" in para_birimi and is_bist) else p_now)
            d_prev = p_prev * usd_kuru if ("TRY" in para_birimi and not is_bist) else (p_prev / usd_kuru if ("USD" in para_birimi and is_bist) else p_prev)

            # RENK MANTIĞI
            color = "#00e676" if change >= 0 else "#ff1744"
            
            # EKRAN KARTI (SENİN HTML YAPIN)
            st.markdown(f"""
                <div class="data-card">
                    <div class="symbol-name">{sym}</div>
                    <div class="price-now">{d_now:,.2f} {unit}</div>
                    
                    <div class="details-row">
                        <div class="detail-item">
                            <div class="detail-label">{D['kapanis']}</div>
                            <div class="detail-value">{d_prev:,.2f} {unit}</div>
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

# 6. REFRESH SİSTEMİ (10 SANİYE)
if oto_taze:
    time.sleep(10)
    st.rerun()
