import streamlit as st
import yfinance as yf
import pandas as pd
import time

# 1. SAYFA AYARLARI
st.set_page_config(page_title="Borsa Pro Terminal", layout="wide")

# --- SİLİKLEŞMEYİ (GRAY-OUT) ZORLA KAPATAN CSS ---
st.markdown("""
    <style>
    /* Streamlit'in 'yükleniyor' efektini (blur ve opacity) tamamen devre dışı bırak */
    .stApp, [data-testid="stAppViewBlockContainer"], [data-testid="stVerticalBlock"] {
        opacity: 1 !important;
        filter: none !important;
        -webkit-filter: none !important;
    }
    
    /* Yazı yazarken veya güncellenirken elemanların soluklaşmasını engelle */
    div[data-testid="stMarkdownContainer"], .stText, .stMetric, .stGraph {
        opacity: 1 !important;
    }

    /* Sağ üstteki yükleniyor ikonunu gizle */
    div[data-testid="stStatusWidget"] {
        display: none !important;
    }

    /* Tasarım detayları */
    .stMetric { background-color: #161b22; padding: 15px; border-radius: 12px; border: 1px solid #30363d; }
    .hisse-baslik { font-size: 24px; font-weight: bold; display: flex; align-items: center; margin-bottom: 10px; }
    div[data-testid="stExpander"] { border: 1px solid #30363d; border-radius: 12px; margin-bottom: 15px; }
    header, footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# 2. DİL VE AYARLAR
dil_destegi = {
    "Türkçe": {
        "ayar_baslik": "⚙️ AYARLAR",
        "dil_sec": "Dil Seçiniz",
        "para_sec": "Para Birimi",
        "oto_yenile": "10sn Otomatik Güncelle",
        "ana_baslik": "BORSA TERMİNALİ",
        "input_etiket": "Sembolleri Girin (Enter'a basın):",
        "fiyat": "Fiyat",
        "bos_uyari": "Takip için sembol girin (Örn: THYAO.IS, BTC-USD)"
    },
    "English": {
        "ayar_baslik": "⚙️ SETTINGS",
        "dil_sec": "Language",
        "para_sec": "Currency",
        "oto_yenile": "10s Auto Refresh",
        "ana_baslik": "STOCK TERMINAL",
        "input_etiket": "Enter Symbols (Press Enter):",
        "fiyat": "Price",
        "bos_uyari": "Enter symbols to start (e.g., AAPL, BTC-USD)"
    }
}

with st.sidebar:
    secilen_dil = st.selectbox("Language / Dil", ["Türkçe", "English"])
    L = dil_destegi[secilen_dil]
    st.header(L["ayar_baslik"])
    secilen_para = st.radio(L["para_sec"], ["₺ TRY", "$ USD"])
    st.divider()
    otomatik_yenile = st.checkbox(L["oto_yenile"], value=True)

st.title(f"📈 {L['ana_baslik']}")

# 3. VERİ GİRİŞİ (HİÇBİR VARSAYILAN HİSSE YOK)
arama_input = st.text_input(L["input_etiket"], value="", key="search_bar")
hisse_listesi = [h.strip().upper() for h in arama_input.split(",") if h.strip()]
st.divider()

# Kur bilgisi
@st.cache_data(ttl=600)
def get_usd_try():
    try: return float(yf.Ticker("USDTRY=X").history(period="1d")['Close'].iloc[-1])
    except: return 34.0

usd_kuru = get_usd_try()

# 4. GÖRÜNTÜLEME ALANI
if not hisse_listesi:
    st.info(L["bos_uyari"])
else:
    # Bu alanın silikleşmemesi için konteynır kullanıyoruz
    main_area = st.container()
    for hisse in hisse_listesi:
        try:
            ticker = yf.Ticker(hisse)
            hist = ticker.history(period="1mo")
            if hist.empty: continue

            fiyat_ham = float(hist['Close'].iloc[-1])
            ma20 = hist['Close'].rolling(window=20).mean().iloc[-1]
            
            # Para Birimi Hesapla
            is_bist = ".IS" in hisse
            simge = "₺" if "TRY" in secilen_para else "$"
            f_goster = fiyat_ham
            if "TRY" in secilen_para and not is_bist: f_goster = fiyat_ham * usd_kuru
            elif "USD" in secilen_para and is_bist: f_goster = fiyat_ham / usd_kuru

            with main_area.expander(f"{hisse}", expanded=True):
                c1, c2, c3 = st.columns([1, 1, 2])
                c1.metric(L["fiyat"], f"{f_goster:,.2f} {simge}")
                if fiyat_ham > ma20: st.success("🚀")
                else: st.error("📉")
                c3.line_chart(hist['Close'].tail(20), height=150)
        except: continue

# 5. GÜNCELLEME (Sadece checkbox seçiliyse çalışır)
if otomatik_yenile:
    time.sleep(10)
    st.rerun()