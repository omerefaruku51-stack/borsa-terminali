import streamlit as st
import yfinance as yf
import pandas as pd
import time
import plotly.graph_objects as go

# 1. COMPACT UI STYLE
st.set_page_config(page_title="Borsa Pro Terminal", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #0f111a; color: #f0f2f6; }
    [data-testid="stSidebar"] { background-color: #161a25; }
    
    /* Kompakt Satır Tasarımı */
    .stock-row {
        background: #1e222d;
        border-bottom: 1px solid #2a2e39;
        padding: 10px 15px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        transition: background 0.2s;
    }
    .stock-row:hover { background: #252a3d; }
    
    .sym-box { flex: 2; font-weight: 800; color: #3772ff; font-size: 1.1rem; }
    .price-box { flex: 2; text-align: right; font-weight: 700; font-size: 1.1rem; }
    .change-box { flex: 1.5; text-align: right; font-weight: bold; font-size: 1rem; }
    
    .market-label {
        background: #2a2e39;
        padding: 5px 15px;
        font-size: 0.9rem;
        font-weight: bold;
        color: #848e9c;
        margin-top: 15px;
    }

    /* Arama Kutusu Stili */
    .stTextInput input {
        background-color: #1e222d !important;
        color: white !important;
        border: 1px solid #3772ff !important;
        border-radius: 8px !important;
    }

    header, footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# 2. GENİŞLETİLMİŞ HİSSE LİSTESİ
BIST_BASE = sorted(["THYAO.IS", "ASELS.IS", "EREGL.IS", "KCHOL.IS", "TUPRS.IS", "SISE.IS", "BIMAS.IS", "AKBNK.IS", "GARAN.IS", "SASA.IS", "HEKTS.IS", "PETKM.IS", "KOZAL.IS", "PGSUS.IS", "DOAS.IS"])
US_BASE = sorted(["AAPL", "TSLA", "NVDA", "AMZN", "MSFT", "GOOGL", "META", "AMD", "NFLX", "COIN", "BABA", "PLTR", "MSTR", "UBER", "PYPL"])

# 3. YAN PANEL & DİL
with st.sidebar:
    st.title("📊 Terminal")
    lang = st.selectbox("Dil", ["Türkçe", "English"])
    curr = st.radio("Para Birimi", ["₺ TRY", "$ USD"])
    refresh = st.checkbox("Canlı Akış (15s)", value=True)

D = {
    "Türkçe": {"tr": "🇹🇷 BIST", "us": "🇺🇸 US", "ara": "Hisse Ara...", "detay": "Detay & Grafik", "prev": "Dün"},
    "English": {"tr": "🇹🇷 BIST", "us": "🇺🇸 US", "ara": "Search...", "detay": "Detail & Chart", "prev": "Prev"}
}[lang]

# 4. ARAMA MOTORU (ANA EKRAN ÜSTÜ)
search_query = st.text_input("", placeholder=D['ara']).upper()

# 5. KUR VERİSİ
@st.cache_data(ttl=3600)
def get_rate():
    try: return yf.Ticker("USDTRY=X").history(period="1d")['Close'].iloc[-1]
    except: return 34.50
usd_rate = get_rate()

def render_compact_list(base_list, is_tr):
    # Filtreleme
    filtered = [s for s in base_list if search_query in s.replace('.IS', '')]
    
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

            # KOMPAKT SATIR
            st.markdown(f"""
            <div class="stock-row">
                <div class="sym-box">{sym.replace('.IS','')}</div>
                <div class="price-now">{d_now:,.2f} {u_char}</div>
                <div class="change-box" style="color:{color}">{pct:+.2f}%</div>
            </div>
            """, unsafe_allow_html=True)
            
            # Detay Expander (Grafik için)
            with st.expander(D['detay']):
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=df.index, y=df['Close'], line=dict(color='#3772ff', width=2), fill='tozeroy', fillcolor='rgba(55, 114, 255, 0.05)'))
                fig.update_layout(height=150, margin=dict(l=0,r=0,t=0,b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', xaxis=dict(visible=False), yaxis=dict(visible=False))
                st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        except: continue

# 6. AKIŞ
if search_query:
    st.markdown(f"<div class='market-label'>ARAMA SONUÇLARI</div>", unsafe_allow_html=True)
    render_compact_list(BIST_BASE + US_BASE, is_tr=True) # Karma arama
else:
    st.markdown(f"<div class='market-label'>{D['tr']}</div>", unsafe_allow_html=True)
    render_compact_list(BIST_BASE, is_tr=True)
    st.markdown(f"<div class='market-label'>{D['us']}</div>", unsafe_allow_html=True)
    render_compact_list(US_BASE, is_tr=False)

if refresh:
    time.sleep(15)
    st.rerun()
