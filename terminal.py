import streamlit as st
import yfinance as yf
import pandas as pd
import time

# 1. TASARIM VE STRATEJİ (Sidebar tasarımı KİLİTLİ)
st.set_page_config(page_title="Borsa Pro Terminal", layout="wide")

try:
    import plotly.graph_objects as go
    HAS_PLOTLY = True
except ImportError:
    HAS_PLOTLY = False

st.markdown("""
    <style>
    .stApp { background-color: #0f111a; color: #f0f2f6; }
    .stock-row {
        background: #1e222d; border-bottom: 1px solid #2a2e39;
        padding: 8px 15px; display: flex; justify-content: space-between; align-items: center;
    }
    .sym-name { flex: 2; font-weight: 800; color: #3772ff; font-size: 1rem; }
    .price-val { flex: 2; text-align: right; font-weight: 700; font-size: 1rem; }
    .pct-val { flex: 1.5; text-align: right; font-weight: bold; font-size: 0.9rem; }
    .market-header {
        background: #2a2e39; padding: 4px 15px; font-size: 0.8rem;
        font-weight: bold; color: #848e9c; margin-top: 10px;
    }
    .aligned-text {
        display: inline-block; padding-top: 5px; 
        font-size: 0.9rem; vertical-align: middle;
    }
    [data-testid="stHorizontalBlock"] { align-items: center; }
    header, footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# 2. DİL PAKETLERİ
DIL_VERISI = {
    "Türkçe": {
        "para": "Para Birimi", "yenile": "Otomatik Yenile (15s)",
        "ara": "Tüm Hisseleri Ara... (Örn: THYAO, SASA, NVDA, TSLA)", 
        "detay": "Grafiği Göster", "tr": "BIST (TÜM HİSSELER)", "us": "ABD (TÜM HİSSELER)", 
        "sonuc": "ARAMA SONUÇLARI", "bos": "Aradığınız hisse bulunamadı."
    },
    "English": {
        "para": "Currency", "yenile": "Auto Refresh (15s)",
        "ara": "Search All Stocks... (e.g. AAPL, NVDA, THYAO)", 
        "detay": "Show Chart", "tr": "BIST (ALL STOCKS)", "us": "US (ALL STOCKS)", 
        "sonuc": "SEARCH RESULTS", "bos": "No stocks found."
    }
}

# 3. YAN PANEL (SIDEBAR) - TASARIM KİLİTLİ KORUNDU
with st.sidebar:
    lang = st.selectbox("Language / Dil", ["Türkçe", "English"], key="app_language")
    D = DIL_VERISI[lang]
    st.divider()
    
    st.write(f"**{D['para']}**")
    curr = st.radio("C_Select", ["₺ TRY", "$ USD"], label_visibility="collapsed", key="currency_selector")
    
    st.divider()

    # KUTUCUK SOLDA, YAZI SAĞDA (MİLİMETRİK HİZALI)
    c1, c2 = st.columns([0.15, 0.85])
    with c1:
        refresh = st.checkbox("R_Toggle", value=True, label_visibility="collapsed", key="refresh_toggle")
    with c2:
        st.markdown(f'<span class="aligned-text">{D["yenile"]}</span>', unsafe_allow_html=True)

# 4. HİSSE LİSTESİ YÖNETİMİ
# Ana ekranda kalabalık yapmasın diye en popüler 50'şer hisseyi varsayılan tutuyoruz
BIST_DEFAULT = sorted(["THYAO.IS", "ASELS.IS", "EREGL.IS", "KCHOL.IS", "TUPRS.IS", "SISE.IS", "BIMAS.IS", "AKBNK.IS", "GARAN.IS", "SASA.IS", "HEKTS.IS", "ASTOR.IS", "KONTR.IS", "SMRTG.IS", "YEOTK.IS", "ISCTR.IS", "YKBNK.IS", "SAHOL.IS", "FROTO.IS", "TOASO.IS"])
US_DEFAULT = sorted(["AAPL", "TSLA", "NVDA", "AMZN", "MSFT", "GOOGL", "META", "AMD", "NFLX", "COIN", "PLTR", "MSTR", "UBER", "PYPL", "BABA", "AMD", "DIS", "NKE"])

# 5. ARAMA MOTORU (TÜM VERİ TABANINI KAPSAR)
search_input = st.text_input("", placeholder=D['ara'], key="search_main").upper()

# 6. KUR VE VERİ MOTORU
@st.cache_data(ttl=3600)
def get_rate():
    try: return yf.Ticker("USDTRY=X").history(period="1d")['Close'].iloc[-1]
    except: return 34.50
usd_rate = get_rate()

def render_list(stock_list, is_tr):
    for sym in stock_list:
        try:
            t = yf.Ticker(sym)
            df = t.history(period="1mo")
            if df.empty: continue
            
            now, prev = df['Close'].iloc[-1], df['Close'].iloc[-2]
            pct = ((now - prev) / prev) * 100
            
            u_char = "₺" if "TRY" in curr else "$"
            d_now = now * usd_rate if ("TRY" in curr and not is_tr) else (now / usd_rate if ("USD" in curr and is_tr) else now)
            color = "#00e676" if pct >= 0 else "#ff1744"

            st.markdown(f"""
            <div class="stock-row">
                <div class="sym-name">{sym.replace('.IS','')}</div>
                <div class="price-val">{d_now:,.2f} {u_char}</div>
                <div class="pct-val" style="color:{color}">{pct:+.2f}%</div>
            </div>
            """, unsafe_allow_html=True)
            
            with st.expander(D['detay']):
                if HAS_PLOTLY:
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(x=df.index, y=df['Close'], line=dict(color='#3772ff', width=2), fill='tozeroy', fillcolor='rgba(55, 114, 255, 0.05)'))
                    fig.update_layout(height=140, margin=dict(l=0,r=0,t=0,b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', xaxis=dict(visible=False), yaxis=dict(visible=False))
                    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        except: continue

# 7. ANA AKIŞ (DİNAMİK ARAMA)
if search_input:
    st.markdown(f"<div class='market-header'>{D['sonuc']}</div>", unsafe_allow_html=True)
    # Arama yapıldığında hem .IS ekleyerek hem de orijinal haliyle yfinance'a sorar
    search_targets = [f"{search_input}.IS", search_input]
    render_list(search_targets, True) # True/False burada kur çevrimi için kullanılır
else:
    st.markdown(f"<div class='market-header'>{D['tr']}</div>", unsafe_allow_html=True)
    render_list(BIST_DEFAULT, True)
    st.markdown(f"<div class='market-header'>{D['us']}</div>", unsafe_allow_html=True)
    render_list(US_DEFAULT, False)

if refresh:
    time.sleep(15)
    st.rerun()
