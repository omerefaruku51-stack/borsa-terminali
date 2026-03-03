import streamlit as st
import yfinance as yf
import pandas as pd
import time

# 1. SAYFA AYARLARI VE SİLİKLEŞME KARŞITI TASARIM
st.set_page_config(page_title="Borsa Pro Terminal", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    /* Silikleşmeyi (Gray-out) Engelle */
    .stApp, [data-testid="stAppViewBlockContainer"] { opacity: 1 !important; filter: none !important; }
    
    /* Modern Kart Tasarımı */
    .stMetric {
        background-color: #1e222d;
        padding: 20px;
        border-radius: 15px;
        border: 1px solid #363c4e;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }
    
    /* Hisse Başlıkları */
    .hisse-baslik {
        font-size: 28px;
        font-weight: 800;
        color: #d1d4dc;
        display: flex;
        align-items: center;
        gap: 15px;
        margin-bottom: 5px;
    }
    
    /* Grafik Alanı Arka Planı */
    .stPlotlyChart { background-color: transparent; }
    
    /* Alt Bilgi Gizleme */
    header, footer {visibility: hidden;}
    
    /* Giriş Kutusu Tasarımı */
    .stTextInput > div > div > input {
        background-color: #2a2e39;
        color: white;
        border-radius: 10px;
        border: 1px solid #434651;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. DİL VE PARA BİRİMİ FONKSİYONLARI
dil_destegi = {
    "Türkçe": {
        "ana_baslik": "BORSA PRO TERMİNAL",
        "input_etiket": "İzlenecek Semboller (Örn: THYAO.IS, AAPL, BTC-USD)",
        "fiyat": "Anlık Fiyat",
        "durum": "Trend",
        "yukari": "BOĞA 🚀",
        "asagi": "AYI 📉",
        "bos_mesaj": "🔍 İzleme listesi boş. Yukarıdaki kutuya bir sembol yazarak başlayın."
    },
    "English": {
        "ana_baslik": "STOCK PRO TERMINAL",
        "input_etiket": "Symbols to Track (e.g., AAPL, NVDA, BTC-USD)",
        "fiyat": "Live Price",
        "durum": "Trend",
        "yukari": "BULLISH 🚀",
        "asagi": "BEARISH 📉",
        "bos_mesaj": "🔍 Watchlist is empty. Type a symbol above to start."
    }
}

# Yan Panel Ayarları
with st.sidebar:
    st.title("⚙️ Ayarlar")
    dil = st.selectbox("Dil / Language", ["Türkçe", "English"])
    L = dil_destegi[dil]
    para_birimi = st.radio("Para Birimi", ["₺ TRY", "$ USD"])
    st.divider()
    oto_taze = st.checkbox("10sn Otomatik Güncelle", value=True)

# 3. ANA EKRAN
st.title(f"📈 {L['ana_baslik']}")

# Arama Kutusu (Boş Başlar)
arama = st.text_input(L["input_etiket"], value="", placeholder="Sembolleri virgülle ayırarak yazın...")
hisseler = [h.strip().upper() for h in arama.split(",") if h.strip()]

@st.cache_data(ttl=600)
def kur_getir():
    try: return float(yf.Ticker("USDTRY=X").history(period="1d")['Close'].iloc[-1])
    except: return 34.20
usd = kur_getir()

# 4. VERİ GÖSTERİMİ
if not hisseler:
    st.info(L["bos_mesaj"])
else:
    for sembol in hisseler:
        try:
            t = yf.Ticker(sembol)
            df = t.history(period="1mo")
            if df.empty: continue
            
            fiyat_raw = df['Close'].iloc[-1]
            degisim = ((fiyat_raw - df['Open'].iloc[-1]) / df['Open'].iloc[-1]) * 100
            ma20 = df['Close'].rolling(window=20).mean().iloc[-1]
            
            # Para Birimi Hesaplama
            is_bist = ".IS" in sembol
            birim = "₺" if "TRY" in para_birimi else "$"
            gosterge_fiyat = fiyat_raw
            if "TRY" in para_birimi and not is_bist: gosterge_fiyat *= usd
            elif "USD" in para_birimi and is_bist: gosterge_fiyat /= usd

            # Arayüz Kartı
            with st.container():
                st.markdown(f'<div class="hisse-baslik">📊 {sembol}</div>', unsafe_allow_html=True)
                col1, col2, col3 = st.columns([1, 1, 2])
                
                col1.metric(L["fiyat"], f"{gosterge_fiyat:,.2f} {birim}", f"{degisim:+.2f}%")
                
                if fiyat_raw > ma20:
                    col2.success(L["yukari"])
                else:
                    col2.error(L["asagi"])
                
                # Grafik
                col3.line_chart(df['Close'].tail(15), height=180, use_container_width=True)
                st.divider()
        except:
            st.warning(f"⚠️ {sembol} verisi alınamadı.")

# 5. OTO-REFRESH
if oto_taze:
    time.sleep(10)
    st.rerun()
