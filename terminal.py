import streamlit as st
import yfinance as yf
import pandas as pd
import time
import plotly.graph_objects as go

# 1. PREMIUM UI & STYLE
st.set_page_config(page_title="Borsa Pro Terminal", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #0f111a; color: #f0f2f6; }
    [data-testid="stSidebar"] { background-color: #161a25; }
    
    .market-section { 
        background: #1e222d; 
        padding: 10px 20px; 
        border-radius: 10px; 
        margin: 20px 0;
        border-left: 5px solid #3772ff;
        font-size: 1.5rem;
        font-weight: bold;
    }
    
    .data-card {
        background: #1e222d;
        border: 1px solid #2a2e39;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 10px;
    }
    
    .symbol-name { font-size: 1.4rem; font-weight: 800; color: #3772ff; }
    .price-now { font-size: 1.8rem; font-weight: 700; }
    
    .details-row { 
        display: flex; 
        justify-content: space-between; 
        margin-top: 10px; 
        border-top: 1px solid rgba(255,255,255,0.05); 
        padding-top: 10px; 
    }
    .detail-label { font-size: 0.75rem; color: #848e9c; }
    .detail-value { font-size: 1rem; font-weight: 600; }

    header, footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# 2. HİSSE LİSTELERİ (Alfabetik)
# Not: Buraya en önemli hisseleri ekledim, listeyi dilediğin kadar uzatabilirsin.
BIST_LIST = sorted(["THYAO.IS", "ASELS.IS", "EREGL.IS", "KCHOL.IS", "TUPRS.IS", "SISE.IS", "BIMAS.IS", "AKBNK.IS", "ISCTR.IS", "SAHOL.IS", "GARAN.IS", "YKBNK.IS"])
US_LIST = sorted(["AAPL", "AMZN", "GOOGL", "MSFT", "NVDA", "TSLA", "META", "NFLX", "AMD", "INTC", "PYPL", "BABA"])

# 3. YAN PANEL
with st.sidebar:
    st.title("⚙️ Terminal")
    lang = st.selectbox("Dil / Language", ["Türkçe", "English"])
    curr = st.radio("Para Birimi", ["₺ TRY", "$ USD"])
    refresh = st.checkbox("Canlı Güncelle (15s)", value=True)

D = {
    "Türkçe": {"tr_h": "🇹🇷 TÜRKİYE BORSASI (BIST)", "us_h": "🇺🇸 ABD BORSALARI (NASDAQ/NYSE)", "prev": "Kapanış", "change": "24s Değişim", "detay": "Grafiği Göster"},
    "English": {"tr_h": "🇹🇷 TURKISH MARKET", "us_h": "🇺🇸 US MARKETS", "prev": "Prev. Close", "change": "24h Change", "detay": "Show Chart"}
}[lang]

# 4. VERİ ÇEKME FONKSİYONU
@st.cache_data(ttl=600)
def get_usd_rate():
    try: return yf.Ticker("USDTRY=X").history(period="1d")['Close'].iloc[-1]
    except: return 34.50
usd_rate = get_usd_rate()

def display_stock_list(symbol_list, is_bist):
    for sym in symbol_list:
        try:
            t = yf.Ticker(sym)
            df = t.history(period="1mo")
            if df.empty: continue
            
            now, prev = df['Close'].iloc[-1], df['Close'].iloc[-2]
            pct = ((now - prev) / prev) * 100
            
            # Kur Çevrimi
            u_char = "₺" if "TRY" in curr else "$"
            d_now = now * usd_rate if ("TRY" in curr and not is_bist) else (now / usd_rate if ("USD" in curr and is_bist) else now)
            d_prev = prev * usd_rate if ("TRY" in curr and not is_bist) else (prev / usd_rate if ("USD" in curr and is_bist) else prev)
            
            color = "#00e676" if pct >= 0 else "#ff1744"

            # KART TASARIMI
            with st.container():
                st.markdown(f"""
                <div class="data-card">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div class="symbol-name">{sym.replace('.IS', '')}</div>
                        <div class="price-now">{d_now:,.2f} {u_char}</div>
                    </div>
                    <div class="details-row">
                        <div class="detail-item">
                            <div class="detail-label">{D['prev']}</div>
                            <div class="detail-value">{d_prev:,.2f} {u_char}</div>
                        </div>
                        <div class="detail-item">
                            <div class="detail-label">{D['change']}</div>
                            <div class="detail-value" style="color:{color}">{pct:+.2f}%</div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Gömülü Grafik Expander
                with st.expander(D['detay']):
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(x=df.index, y=df['Close'], line=dict(color='#3772ff', width=2), fill='tozeroy', fillcolor='rgba(55, 114, 255, 0.05)'))
                    fig.update_layout(height=200, margin=dict(l=0,r=0,t=0,b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', xaxis=dict(visible=False), yaxis=dict(side='right', color='#848e9c'))
                    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        except:
            continue

# 5. ANA EKRAN AKIŞI
st.markdown(f"<div class='market-section'>{D['tr_h']}</div>", unsafe_allow_html=True)
display_stock_list(BIST_LIST, is_bist=True)

st.markdown(f"<div class='market-section'>{D['us_h']}</div>", unsafe_allow_html=True)
display_stock_list(US_LIST, is_bist=False)

# 6. AUTO REFRESH
if refresh:
    time.sleep(15)
    st.rerun()
