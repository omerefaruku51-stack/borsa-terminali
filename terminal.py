import streamlit as st
import yfinance as yf
import pandas as pd
import time

# Plotly kontrolü (Hata devam ederse uygulama çökmesin diye)
try:
    import plotly.graph_objects as go
    HAS_PLOTLY = True
except ImportError:
    HAS_PLOTLY = False

# 1. KOMPAKT TASARIM (CSS)
st.set_page_config(page_title="Borsa Pro Terminal", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #0f111a; color: #f0f2f6; }
    
    /* İnce Satır Tasarımı */
    .stock-row {
        background: #1e222d;
        border-bottom: 1px solid #2a2e39;
        padding: 8px 15px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .sym-name { flex: 2; font-weight: 800; color: #3772ff; font-size: 1rem; }
    .price-val { flex: 2; text-align: right; font-weight: 700; font-size: 1rem; }
    .pct-val { flex: 1.5; text-align: right; font-weight: bold; font-size: 0.9rem; }
    
    .market-header {
        background: #2a2e39;
        padding: 4px 15px;
        font-size: 0.8rem;
        font-weight: bold;
        color: #848e9c;
        margin-top: 10px;
    }

    /* Arama Çubuğu */
    .stTextInput input {
        background-color: #1e222d !important;
        border: 1px solid #3772ff !important;
        color: white !important;
    }
    header, footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# 2. HİSSE LİSTELERİ
BIST_LIST = sorted(["THYAO.IS", "ASELS.IS", "EREGL.IS", "KCHOL.IS", "TUPRS.IS", "SISE.IS", "BIMAS.IS", "AKBNK.IS", "GARAN.IS", "SASA.IS", "HEKTS.IS", "PGSUS.IS"])
US_LIST = sorted(["AAPL", "TSLA", "NVDA", "AMZN", "MSFT", "GOOGL", "META", "AMD", "NFLX", "COIN"])

# 3. YAN PANEL
with st.sidebar:
    st.title("📊 Ayarlar")
    lang = st.selectbox("Dil", ["Türkçe", "English"])
    curr = st.radio("Para Birimi", ["₺ TRY", "$ USD"])
    refresh = st.checkbox("Otomatik Yenile (15s)", value=True)

D = {
    "Türkçe": {"ara": "Hisse Ara...", "detay": "Grafiği Göster", "tr": "BIST HİSSELERİ", "us": "ABD HİSSELERİ"},
    "English": {"ara": "Search...", "detay": "Show Chart", "tr": "TURKISH STOCKS", "us": "US STOCKS"}
}[lang]

# 4. ARAMA MOTORU
search_input = st.text_input("", placeholder=D['ara']).upper()

# 5. KUR VERİSİ
@st.cache_data(ttl=3600)
def get_rate():
    try: return yf.Ticker("USDTRY=X").history(period="1d")['Close'].iloc[-1]
    except: return 34.55
usd_rate = get_rate()

def render_list(stock_list, is_tr):
    # Arama Filtresi
    filtered = [s for s in stock_list if search_input in s.replace('.IS','')]
    
    for sym in filtered:
        try:
            t = yf.Ticker(sym)
            df = t.history(period="1mo")
            if df.empty: continue
            
            now, prev = df['Close'].iloc[-1], df['Close'].iloc[-2]
            pct = ((now - prev) / prev) * 100
            
            u_char = "₺" if "TRY" in curr else "$"
            d_now = now * usd_rate if ("TRY" in curr and not is_tr) else (now / usd_rate if ("USD" in curr and is_tr) else now)
            color = "#00e676" if pct >= 0 else "#ff1744"

            # KOMPAKT SATIR GÖRÜNÜMÜ
            st.markdown(f"""
            <div class="stock-row">
                <div class="sym-name">{sym.replace('.IS','')}</div>
                <div class="price-val">{d_now:,.2f} {u_char}</div>
                <div class="pct-val" style="color:{color}">{pct:+.2f}%</div>
            </div>
            """, unsafe_allow_html=True)
            
            # GRAFİK EXPANDER
            with st.expander(D['detay']):
                if HAS_PLOTLY:
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(x=df.index, y=df['Close'], line=dict(color='#3772ff', width=2), fill='tozeroy', fillcolor='rgba(55, 114, 255, 0.05)'))
                    fig.update_layout(height=140, margin=dict(l=0,r=0,t=0,b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', xaxis=dict(visible=False), yaxis=dict(visible=False))
                    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
                else:
                    st.info("Kütüphane yükleniyor...")
        except: continue

# 6. ANA AKIŞ
if search_input:
    st.markdown(f"<div class='market-header'>ARAMA SONUÇLARI</div>", unsafe_allow_html=True)
    render_list(BIST_LIST + US_LIST, True)
else:
    st.markdown(f"<div class='market-header'>{D['tr']}</div>", unsafe_allow_html=True)
    render_list(BIST_LIST, True)
    st.markdown(f"<div class='market-header'>{D['us']}</div>", unsafe_allow_html=True)
    render_list(US_LIST, False)

if refresh:
    time.sleep(15)
    st.rerun()
