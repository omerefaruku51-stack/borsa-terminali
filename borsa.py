import streamlit as st
import yfinance as yf
import pandas as pd
import time
import streamlit.components.v1 as components

# 1. SAYFA VE TASARIM AYARLARI
st.set_page_config(page_title="Borsa Intelligence Pro", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    .stApp { background-color: #0f111a; color: #f0f2f6; }
    [data-testid="stSidebar"] { background-color: #161a25; }
    
    /* Veri Kutusu Tasarımı */
    .data-box {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        display: flex;
        justify-content: space-around;
        align-items: center;
    }
    .price-item { flex: 1; }
    .price-label { font-size: 0.85rem; color: #848e9c; margin-bottom: 5px; }
    .price-value { font-size: 1.3rem; font-weight: 700; }
    
    .symbol-title { font-size: 2rem; font-weight: 800; color: #3772ff; margin-bottom: 10px; }
    header, footer {visibility: hidden;}
    hr { border-top: 1px solid rgba(255,255,255,0.05); margin: 2rem 0; }
    
    /* Expander Buton Şıklığı */
    .streamlit-expanderHeader {
        background-color: #1e222d !important;
        border: 1px solid #3772ff !important;
        border-radius: 10px !important;
        color: #3772ff !important;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. DİL PAKETLERİ
dil_ayarlari = {
    "Türkçe": {
        "ana_baslik": "BORSA INTELLIGENCE PRO",
        "ayar": "Ayarlar", "para": "Para Birimi",
        "yenile": "15sn Otomatik Güncelle", "son_24": "Son 24 Saat Özeti",
        "kapanis": "Önceki Kapanış", "guncel": "Anlık Fiyat",
        "detay": "🔍 Detaylı Teknik Analiz Grafiği ve İndikatörler",
        "ara": "Hisse Ara (THYAO.IS, BTC-USD, AAPL...)", "hata": "Veri bulunamadı"
    },
    "English": {
        "ana_baslik": "STOCK INTELLIGENCE PRO",
        "ayar": "Settings", "para": "Currency",
        "yenile": "Auto-Refresh 15s", "son_24": "Last 24h Summary",
        "kapanis": "Prev. Close", "guncel": "Current Price",
        "detay": "🔍 Detailed Technical Chart & Indicators",
        "ara": "Search (AAPL, NVDA, BTC-USD...)", "hata": "Data not found"
    }
}

# 3. SIDEBAR
with st.sidebar:
    sel_lang = st.selectbox("Language / Dil", ["Türkçe", "English"])
    D = dil_ayarlari[sel_lang]
    st.divider()
    curr = st.radio(D["para"], ["₺ TRY", "$ USD"])
    refresh_on = st.checkbox(D["yenile"], value=True)

# 4. KUR VERİSİ
@st.cache_data(ttl=600)
def get_usd():
    try: return float(yf.Ticker("USDTRY=X").history(period="1d")['Close'].iloc[-1])
    except: return 34.45
usd_rate = get_usd()

st.markdown(f"<h1 style='text-align: center; letter-spacing: 2px;'>{D['ana_baslik']}</h1>", unsafe_allow_html=True)
search = st.text_input("", placeholder=D["ara"])
symbols = [s.strip().upper() for s in search.split(",") if s.strip()]

# 5. GÖRÜNTÜLEME (GRAFİKSİZ SADE TASARIM)
if not symbols:
    st.markdown("<div style='text-align: center; padding: 50px; color: #434651;'>İzlemek istediğiniz sembolleri girerek analiz etmeye başlayın.</div>", unsafe_allow_html=True)
else:
    for sym in symbols:
        try:
            t = yf.Ticker(sym)
            df = t.history(period="2d")
            if df.empty: continue
            
            p_now, p_prev = df['Close'].iloc[-1], df['Close'].iloc[-2]
            change = ((p_now - p_prev) / p_prev) * 100
            
            # Kur Çevrimi
            is_bist = sym.endswith(".IS")
            unit = "₺" if "TRY" in curr else "$"
            d_now = p_now * usd_rate if ("TRY" in curr and not is_bist) else (p_now / usd_rate if ("USD" in curr and is_bist) else p_now)
            d_prev = p_prev * usd_rate if ("TRY" in curr and not is_bist) else (p_prev / usd_rate if ("USD" in curr and is_bist) else p_prev)

            # BAŞLIK
            st.markdown(f"<div class='symbol-title'>{sym}</div>", unsafe_allow_html=True)
            
            # ANA VERİ SATIRI
            col_main, col_spacer = st.columns([3, 1])
            
            with col_main:
                st.markdown(f"""
                <div class="data-box">
                    <div class="price-item">
                        <div class="price-label">{D['kapanis']}</div>
                        <div class="price-value">{d_prev:,.2f} {unit}</div>
                    </div>
                    <div style="height: 40px; border-left: 1px solid rgba(255,255,255,0.1);"></div>
                    <div class="price-item">
                        <div class="price-label">{D['guncel']}</div>
                        <div class="price-value" style="color:{'#00e676' if change>=0 else '#ff1744'}">
                            {d_now:,.2f} {unit} 
                            <span style="font-size: 0.9rem; margin-left: 10px;">({change:+.2f}%)</span>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

            # --- TRADINGVIEW ENTEGRASYONU ---
            with st.expander(D["detay"]):
                tv_sym = sym.replace(".IS", "")
                if is_bist: tv_sym = f"BIST:{tv_sym}"
                elif "-" in sym: tv_sym = f"BINANCE:{tv_sym.replace('-', '')}"
                else: tv_sym = f"NASDAQ:{tv_sym}"
                
                tv_html = f"""
                <div id="tv_chart_container" style="height:550px;">
                    <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
                    <script type="text/javascript">
                    new TradingView.widget({{
                      "autosize": true, "symbol": "{tv_sym}",
                      "interval": "60", "timezone": "Europe/Istanbul",
                      "theme": "dark", "style": "1", "locale": "tr",
                      "toolbar_bg": "#f1f3f6", "enable_publishing": false,
                      "hide_side_toolbar": false, "allow_symbol_change": true,
                      "container_id": "tv_chart_container"
                    }});
                    </script>
                </div>
                """
                components.html(tv_html, height=560)
            
            st.markdown("<hr>", unsafe_allow_html=True)
        except:
            st.error(f"{sym}: {D['hata']}")

# 6. REFRESH
if refresh_on:
    time.sleep(15)
    st.rerun()
