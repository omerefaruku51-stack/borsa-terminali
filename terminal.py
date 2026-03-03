import streamlit as st
import yfinance as yf
import pandas as pd
import time

# Plotly kontrolü (Hata almamak için)
try:
    import plotly.graph_objects as go
    HAS_PLOTLY = True
except ImportError:
    HAS_PLOTLY = False

# 1. TASARIM AYARLARI
st.set_page_config(page_title="Borsa Pro Terminal", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #0f111a; color: #f0f2f6; }
    [data-testid="stSidebar"] { background-color: #161a25; }
    
    .market-section { 
        background: #1e222d; padding: 12px 20px; border-radius: 10px; 
        margin: 25px 0 15px 0; border-left: 5px solid #3772ff;
        font-size: 1.4rem; font-weight: bold; color: #ffffff;
    }
    
    .data-card {
        background: #1e222d; border: 1px solid #2a2e39;
        border-radius: 12px; padding: 18px; margin-bottom: 8px;
    }
    
    .symbol-name { font-size: 1.3rem; font-weight: 800; color: #3772ff; }
    .price-now { font-size: 1.6rem; font-weight: 700; color: #ffffff; }
    
    .details-row { 
        display: flex; justify-content: space-between; 
        margin-top: 10px; border-top: 1px solid rgba(255,255,255,0.05); padding-top: 10px; 
    }
    .detail-label { font-size: 0.8rem; color: #848e9c; }
    .detail-value { font-size: 1.1rem; font-weight: 600; }
    header, footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# 2. HİSSE LİSTELERİ (Alfabetik Hazır Liste)
# Buraya istediğin kadar hisse ekleyebilirsin, sistem otomatik sıralar.
BIST_LIST = sorted(["THYAO.IS", "ASELS.IS", "EREGL.IS", "KCHOL.IS", "TUPRS.IS", "SISE.IS", "BIMAS.IS", "AKBNK.IS", "GARAN.IS", "SASA.IS", "HEKTS.IS"])
US_LIST = sorted(["AAPL", "TSLA", "NVDA", "AMZN", "MSFT", "GOOGL", "META", "AMD", "NFLX", "COIN"])

# 3. YAN PANEL
with st.sidebar:
    st.title("⚙️ Ayarlar")
    lang = st.selectbox("Dil / Language", ["Türkçe", "English"])
    curr = st.radio("Para Birimi", ["₺ TRY", "$ USD"])
    refresh = st.checkbox("Canlı Akış (15s)", value=True)

D = {
    "Türkçe": {"tr": "🇹🇷 TÜRKİYE (BIST)", "us": "🇺🇸 ABD BORSALARI", "prev": "Dünkü Kapanış", "ch": "24s Değişim", "dt": "Grafiği İncele"},
    "English": {"tr": "🇹🇷 TURKISH MARKET", "us": "🇺🇸 US MARKETS", "prev": "Prev. Close", "ch": "24h Change", "dt": "View Chart"}
}[lang]

# 4. KUR VERİSİ
@st.cache_data(ttl=3600)
def get_rate():
    try: return yf.Ticker("USDTRY=X").history(period="1d")['Close'].iloc[-1]
    except: return 34.50
usd_rate = get_rate()

def show_stocks(list_data, is_tr):
    for sym in list_data:
        try:
            t = yf.Ticker(sym)
            df = t.history(period="1mo")
            if df.empty: continue
            
            now, prev = df['Close'].iloc[-1], df['Close'].iloc[-2]
            pct = ((now - prev) / prev) * 100
            
            # Kur Çevrimleri
            u_char = "₺" if "TRY" in curr else "$"
            d_now = now * usd_rate if ("TRY" in curr and not is_tr) else (now / usd_rate if ("USD" in curr and is_tr) else now)
            d_prev = prev * usd_rate if ("TRY" in curr and not is_tr) else (prev / usd_rate if ("USD" in curr and is_tr) else prev)
            
            color = "#00e676" if pct >= 0 else "#ff1744"

            st.markdown(f"""
            <div class="data-card">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div class="symbol-name">{sym.replace('.IS','')}</div>
                    <div class="price-now">{d_now:,.2f} {u_char}</div>
                </div>
                <div class="details-row">
                    <div class="detail-item">
                        <div class="detail-label">{D['prev']}</div>
                        <div class="detail-value">{d_prev:,.2f} {u_char}</div>
                    </div>
                    <div class="detail-item">
                        <div class="detail-label">{D['ch']}</div>
                        <div class="detail-value" style="color:{color}">{pct:+.2f}%</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            with st.expander(D['dt']):
                if HAS_PLOTLY:
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(x=df.index, y=df['Close'], line=dict(color='#3772ff', width=2), fill='tozeroy', fillcolor='rgba(55, 114, 255, 0.05)'))
                    fig.update_layout(height=180, margin=dict(l=0,r=0,t=0,b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', xaxis=dict(visible=False), yaxis=dict(visible=False))
                    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
                else:
                    st.warning("Grafik yükleniyor...")
        except: continue

# 5. ANA AKIŞ
st.markdown(f"<div class='market-section'>{D['tr']}</div>", unsafe_allow_html=True)
show_stocks(BIST_LIST, True)

st.markdown(f"<div class='market-section'>{D['us']}</div>", unsafe_allow_html=True)
show_stocks(US_LIST, False)

if refresh:
    time.sleep(15)
    st.rerun()
