import streamlit as st
import yfinance as yf
import pandas as pd
import time

# 1. TASARIM VE HAYALET TEMİZLİĞİ (Sidebar Kilitli)
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
        border-radius: 4px; margin-bottom: 2px;
    }
    .sym-name { flex: 2; font-weight: 800; color: #3772ff; font-size: 1rem; }
    .price-val { flex: 2; text-align: right; font-weight: 700; font-size: 1rem; }
    .pct-val { flex: 1.5; text-align: right; font-weight: bold; font-size: 0.9rem; }
    
    /* Sidebar Milimetrik Hizalama - Kilitli */
    .aligned-text { display: inline-block; padding-top: 5px; font-size: 0.9rem; vertical-align: middle; }
    [data-testid="stHorizontalBlock"] { align-items: center; }
    
    /* Silme Butonu */
    .stButton>button { background-color: transparent; border: none; color: #ff1744; font-weight: bold; }
    .stButton>button:hover { color: white; background-color: #ff1744; }
    
    header, footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# 2. DİL PAKETLERİ
DIL = {
    "Türkçe": {
        "para": "Para Birimi", "yenile": "Otomatik Yenile (15s)",
        "ara": "Ekle (THYAO, AAPL, BTC-USD...)", "ekle": "EKLE",
        "detay": "Grafik", "bos": "Liste boş.", "altin": "Gram Altın"
    },
    "English": {
        "para": "Currency", "yenile": "Auto Refresh (15s)",
        "ara": "Add (Symbol Name...)", "ekle": "ADD",
        "detay": "Chart", "bos": "List empty.", "altin": "Gold Gram"
    }
}

# 3. YAN PANEL (SIDEBAR) - TASARIM KORUNDU
with st.sidebar:
    lang = st.selectbox("Language / Dil", ["Türkçe", "English"], key="app_lang")
    D = DIL[lang]
    st.divider()
    
    st.write(f"**{D['para']}**")
    curr = st.radio("C_Select", ["₺ TRY", "$ USD"], label_visibility="collapsed", key="curr_sel")
    st.divider()
    
    # Kutucuk solda, yazı sağda milimetrik hizalama
    c1, c2 = st.columns([0.15, 0.85])
    with c1:
        refresh = st.checkbox("R_Tog", value=True, label_visibility="collapsed", key="ref_tog")
    with c2:
        st.markdown(f'<span class="aligned-text">{D["yenile"]}</span>', unsafe_allow_html=True)

# 4. TAKİP LİSTESİ (Hayalet Yazıları Silmek İçin Liste Temizlendi)
# SADECE senin istediğin ana birimler.
if 'watchlist' not in st.session_state:
    st.session_state.watchlist = ["USDTRY=X", "EURTRY=X", "BTC-USD", "GRAM_ALTIN"]

# 5. EKLEME PANELİ
col_input, col_btn = st.columns([0.85, 0.15])
with col_input:
    new_asset = st.text_input("", placeholder=D['ara'], key="add_input").upper()
with col_btn:
    st.write("##")
    if st.button(D['ekle'], use_container_width=True):
        if new_asset and new_asset not in st.session_state.watchlist:
            # BIST kontrolü
            final_sym = new_asset if any(x in new_asset for x in ["=", "-"]) or "." in new_asset else f"{new_asset}.IS"
            st.session_state.watchlist.append(final_sym)
            st.rerun()

# 6. VERİ MOTORU (Gram Altın Hesaplamalı)
@st.cache_data(ttl=60)
def get_market_data(sym):
    try:
        if sym == "GRAM_ALTIN":
            # Gram Altın = (Ons Altın / 31.1035) * Dolar/TL
            ons = yf.Ticker("GC=F").history(period="1mo")
            kur = yf.Ticker("USDTRY=X").history(period="1mo")
            df = (ons['Close'] / 31.1035) * kur['Close']
            return pd.DataFrame({'Close': df})
        else:
            return yf.Ticker(sym).history(period="1mo")
    except: return pd.DataFrame()

@st.cache_data(ttl=60)
def get_usd_rate():
    try: return yf.Ticker("USDTRY=X").history(period="1d")['Close'].iloc[-1]
    except: return 34.50

usd_val = get_usd_rate()

def render_item(sym):
    df = get_market_data(sym)
    if df.empty: return

    now, prev = df['Close'].iloc[-1], df['Close'].iloc[-2]
    pct = ((now - prev) / prev) * 100
    
    # İsimlendirme ve Döviz Çevrimi
    p_birimi = "TRY" if "TRY" in curr else "USD"
    u_char = "₺" if "TRY" in curr else "$"
    
    if sym == "USDTRY=X": display_name = "USD / TRY"
    elif sym == "EURTRY=X": display_name = "EUR / TRY"
    elif sym == "BTC-USD": display_name = f"BTC / {p_birimi}"
    elif sym == "GRAM_ALTIN": display_name = f"{D['altin']} / {p_birimi}"
    else: display_name = sym.replace('.IS','')

    # Kur Çevrim Mantığı
    if "TRY" in curr:
        # Zaten TL olanlar: USDTRY, EURTRY, GRAM_ALTIN (bizim hesapladığımız), BIST(.IS)
        if any(x in sym for x in ["TRY", ".IS"]) or sym == "GRAM_ALTIN":
            d_now = now
        else: # USD bazlı olanlar (BTC-USD, AAPL vb.)
            d_now = now * usd_val
    else: # USD seçiliyse
        # Zaten USD olanlar: BTC-USD, AAPL vb.
        if "-USD" in sym or (".IS" not in sym and "TRY" not in sym and sym != "GRAM_ALTIN"):
            d_now = now
        else: # TL bazlı olanlar (USDTRY, EURTRY, BIST, GRAM_ALTIN) USD'ye çevrilir
            d_now = now / usd_val
            
    color = "#00e676" if pct >= 0 else "#ff1744"

    row_col, del_col = st.columns([0.92, 0.08])
    with row_col:
        st.markdown(f"""
        <div class="stock-row">
            <div class="sym-name">{display_name}</div>
            <div class="price-val">{d_now:,.2f} {u_char}</div>
            <div class="pct-val" style="color:{color}">{pct:+.2f}%</div>
        </div>
        """, unsafe_allow_html=True)
        with st.expander(D['detay']):
            if HAS_PLOTLY:
                fig = go.Figure(go.Scatter(x=df.index, y=df['Close'], line=dict(color='#3772ff', width=2), fill='tozeroy'))
                fig.update_layout(height=120, margin=dict(l=0,r=0,t=0,b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', xaxis=dict(visible=False), yaxis=dict(visible=False))
                st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
    with del_col:
        st.write("##")
        if st.button("X", key=f"btn_{sym}"):
            st.session_state.watchlist.remove(sym)
            st.rerun()

# 7. ANA LİSTE (Hayaletleri engellemek için sadece bu listeden çizilir)
if 'watchlist' in st.session_state:
    for item in st.session_state.watchlist:
        render_item(item)

if refresh:
    time.sleep(15)
    st.rerun()
