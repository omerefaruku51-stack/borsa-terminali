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
    
    .data-box {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 15px;
        text-align: center;
    }
    .price-label { font-size: 0.8rem; color: #848e9c; }
    .price-value { font-size: 1.1rem; font-weight: 600; }
    
    .symbol-title { font-size: 1.8rem; font-weight: 700; color: #3772ff; margin-bottom: 5px; }
    header, footer {visibility: hidden;}
    hr { border-top: 1px solid rgba(255,255,255,0.05); margin: 1.5rem 0; }
    </style>
    """, unsafe_allow_html=True)

# 2. DİL PAKETLERİ
dil_ayarlari = {
    "Türkçe": {
        "ana_baslik": "BORSA INTELLIGENCE PRO",
        "ayar": "Ayarlar", "para": "Para Birimi",
        "yenile": "15sn Otomatik Güncelle", "son_24": "Son 24 Saat",
        "kapanis": "Dünkü Kapanış", "guncel": "Güncel Fiyat",
        "detay": "📈 Detaylı Teknik Analiz Grafiği",
        "ara": "Hisse Ara (THYAO.IS, BTC-USD, AAPL...)", "hata": "Veri bulunamadı"
    },
    "English": {
        "ana_baslik": "STOCK INTELLIGENCE PRO",
        "ayar": "Settings", "para": "Currency",
        "yenile": "Auto-Refresh 15s", "son_24": "Last 24 Hours",
        "kapanis": "Prev. Close", "guncel": "Current Price",
        "detay": "📈 Show Detailed Technical Chart",
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

st.markdown(f"<h1 style='text-align: center;'>{D['ana_baslik']}</h1>", unsafe_allow_html=True)
search = st.text_input("", placeholder=D["ara"])
symbols = [s.strip().upper() for s in search.split(",") if s.strip()]

# 5. GÖRÜNTÜLEME
if not symbols:
    st.markdown("<div style='text-align: center; padding: 50px; color: #434651;'>İzlemek istediğiniz sembolleri girin.</div>", unsafe_allow_html=True)
else:
    for sym in symbols:
        try:
            t = yf.Ticker(sym)
            df = t.history(period="5d")
            if df.empty: continue
            
            p_now, p_prev = df['Close'].iloc[-1], df['Close'].iloc[-2]
            change = ((p_now - p_prev) / p_prev) * 100
            
            # Kur Çevrimi
            is_bist = sym.endswith(".IS")
            unit = "₺" if "TRY" in curr else "$"
            d_now = p_now * usd_rate if ("TRY" in curr and not is_bist) else (p_now / usd_rate if ("USD" in curr and is_bist) else p_now)
            d_prev = p_prev * usd_rate if ("TRY" in curr and not is_bist) else (p_prev / usd_rate if ("USD" in curr and is_bist) else p_prev)

            st.markdown(f"<div class='symbol-title'>{sym}</div>", unsafe_allow_html=True)
            c1, c2, c3 = st.columns([1.2, 2, 2])
            
            with c1:
                st.metric(D["guncel"], f"{d_now:,.2f} {unit}", f"{change:+.2f}%")
            
            with c2:
                st.markdown(f"**{D['son_24']}**")
                st.markdown(f"""
                <div class="data-box">
                    <div class="price-label">{D['kapanis']}</div>
                    <div class="price-value">{d_prev:,.2f} {unit}</div>
                    <div style="margin: 8px 0; border-top: 1px solid rgba(255,255,255,0.1);"></div>
                    <div class="price-label">{D['guncel']}</div>
                    <div class="price-value" style="color:{'#00e676' if change>=0 else '#ff1744'}">{d_now:,.2f} {unit}</div>
                </div>
                """, unsafe_allow_html=True)
            
            with c3:
                st.line_chart(df['Close'], height=180)

            # --- TRADINGVIEW ENTEGRASYONU ---
            with st.expander(D["detay"]):
                # Sembol Formatlama
                tv_sym = sym.replace(".IS", "")
                if is_bist: tv_sym = f"BIST:{tv_sym}"
                elif "-" in sym: tv_sym = f"BINANCE:{tv_sym.replace('-', '')}"
                else: tv_sym = f"NASDAQ:{tv_sym}"
                
                # TradingView HTML Widget
                tv_html = f"""
                <div style="height:500px;">
                <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
                <script type="text/javascript">
                new TradingView.widget({{
                  "width": "100%", "height": 500, "symbol": "{tv_sym}",
                  "interval": "H", "timezone": "Europe/Istanbul",
                  "theme": "dark", "style": "1", "locale": "tr",
                  "toolbar_bg": "#f1f3f6", "enable_publishing": false,
                  "hide_top_toolbar": false, "allow_symbol_change": true,
                  "container_id": "tv_chart"
                }});
                </script>
                <div id="tv_chart"></div>
                </div>
                """
                components.html(tv_html, height=520)
            
            st.markdown("<hr>", unsafe_allow_html=True)
        except:
            st.error(f"{sym}: {D['hata']}")

# 6. REFRESH
if refresh_on:
    time.sleep(15)
    st.rerun()
