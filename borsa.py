import streamlit as st
import yfinance as yf
import time

# 1. TEMEL SAYFA AYARLARI (Sidebar her zaman açık)
st.set_page_config(page_title="Borsa Terminali", layout="wide", initial_sidebar_state="expanded")

# CSS: Sidebar Hizalaması ve Modern Arayüz
st.markdown("""
    <style>
    .stApp { background-color: #0f111a; color: #f0f2f6; }
    
    /* SIDEBAR: Kutucuk Solda, Yazı Sağda Tam Hizalı */
    .sidebar-label {
        display: inline-block;
        padding-top: 2px;
        font-size: 14px;
        vertical-align: middle;
        margin-left: 5px;
    }
    [data-testid="stHorizontalBlock"] { align-items: center; }
    
    /* Satır Tasarımı */
    .stock-row {
        background: #1e222d; border-bottom: 1px solid #2a2e39;
        padding: 20px; display: flex; justify-content: space-between; align-items: center;
        border-radius: 8px; margin-bottom: 10px;
    }
    .sym-name { flex: 2; font-weight: 800; color: #3772ff; font-size: 1.1rem; }
    .price-val { flex: 2; text-align: right; font-weight: 700; font-size: 1.1rem; }
    .pct-val { flex: 1.5; text-align: right; font-weight: bold; font-size: 1rem; }
    
    header, footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# 2. SIDEBAR (AYARLAR PANELİ)
with st.sidebar:
    st.markdown("### ⚙️ Ayarlar")
    
    # Dil ve Para Birimi Seçimi
    lang = st.selectbox("Dil / Language", ["Türkçe", "English"], key="lang_key")
    currency_pref = st.selectbox("Para Birimi", ["₺ TRY", "$ USD", "€ EUR"], key="curr_key")
    
    st.divider()
    
    # OTOMATİK YENİLEME: Kutucuk Solda, Yazı Sağda Hizalı
    col_check, col_text = st.columns([0.2, 0.8])
    with col_check:
        auto_refresh = st.checkbox("Ref", value=True, label_visibility="collapsed", key="auto_ref_key")
    with col_text:
        label_text = "Otomatik Yenile (15s)" if lang == "Türkçe" else "Auto Refresh (15s)"
        st.markdown(f'<span class="sidebar-label">{label_text}</span>', unsafe_allow_html=True)

# 3. VERİ MOTORU VE SABİT LİSTE
# Bu liste hafızadan (cache) bağımsızdır, doğrudan ekrana basılır.
WATCHLIST = [
    {"symbol": "USDTRY=X", "name": "USD / TRY"},
    {"symbol": "EURTRY=X", "name": "EUR / TRY"},
    {"symbol": "BTC-TRY",  "name": "BTC / TRY"}
]

def render_market_data():
    # Kur çevrimleri için veriyi çek
    try:
        usd_try = yf.Ticker("USDTRY=X").history(period="1d")['Close'].iloc[-1]
        eur_try = yf.Ticker("EURTRY=X").history(period="1d")['Close'].iloc[-1]
    except:
        usd_try, eur_try = 34.50, 36.50

    st.subheader("📊 Canlı Piyasa Verileri")

    for item in WATCHLIST:
        try:
            # Canlı veri çekimi
            ticker = yf.Ticker(item['symbol'])
            df = ticker.history(period="2d")
            
            if df.empty: continue
            
            price_now = df['Close'].iloc[-1]
            price_prev = df['Close'].iloc[-2]
            change_pct = ((price_now - price_prev) / price_prev) * 100
            
            # Para Birimi Dönüşümü
            display_price = price_now
            unit = "₺"
            
            if "$ USD" in currency_pref:
                display_price = price_now / usd_try
                unit = "$"
            elif "€ EUR" in currency_pref:
                display_price = price_now / eur_try
                unit = "€"
                
            color = "#00e676" if change_pct >= 0 else "#ff1744"

            st.markdown(f"""
                <div class="stock-row">
                    <div class="sym-name">{item['name']}</div>
                    <div class="price-val">{display_price:,.2f} {unit}</div>
                    <div class="pct-val" style="color:{color}">{change_pct:+.2f}%</div>
                </div>
            """, unsafe_allow_html=True)
        except:
            continue

# 4. UYGULAMAYI ÇALIŞTIR
render_market_data()

# 5. YENİLEME MANTIĞI
if auto_refresh:
    time.sleep(15)
    st.rerun()
