import streamlit as st
import yfinance as yf
import pandas as pd
import time

# 1. TASARIM (Sidebar Hizalaması Kilitli)
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
    .aligned-text { display: inline-block; padding-top: 5px; font-size: 0.9rem; vertical-align: middle; }
    [data-testid="stHorizontalBlock"] { align-items: center; }
    header, footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# 2. DİL PAKETLERİ
DIL = {
    "Türkçe": {
        "para": "Para Birimi", "yenile": "Otomatik Yenile (15s)",
        "ara": "Hisse/Döviz/Altın Ekle (Örn: THYAO, BTC-USD, GC=F)",
        "ekle": "Listeye Ekle", "sil": "Sil", "detay": "Grafik", "bos": "Takip listesi boş."
    },
    "English": {
        "para": "Currency", "yenile": "Auto Refresh (15s)",
        "ara": "Add Stock/Forex/Gold (e.g. AAPL, EURTRY=X, BTC-USD)",
        "ekle": "Add to List", "sil": "Remove", "detay": "Chart", "bos": "Watchlist is empty."
    }
}

# 3. SIDEBAR (TASARIM SABİT)
with st.sidebar:
    lang = st.selectbox("Language / Dil", ["Türkçe", "English"], key="app_lang")
    D = DIL[lang]
    st.divider()
    st.write(f"**{D['para']}**")
    curr = st.radio("C_Select", ["₺ TRY", "$ USD"], label_visibility="collapsed", key="curr_sel")
    st.divider()
    c1, c2 = st.columns([0.15, 0.85])
    with c1:
        refresh = st.checkbox("R_Tog", value=True, label_visibility="collapsed", key="ref_tog")
    with c2:
        st.markdown(f'<span class="aligned-text">{D["yenile"]}</span>', unsafe_allow_html=True)

# 4. TAKİP LİSTESİ YÖNETİMİ (Session State)
if 'watchlist' not in st.session_state:
    # Başlangıç değerleri: USD/TRY, EUR/TRY, BTC, Gram Altın (GC=F ons üzerinden hesaplanır ama biz sembol ekliyoruz)
    st.session_state.watchlist = ["USDTRY=X", "EURTRY=X", "BTC-USD", "GC=F"]

# 5. EKLEME ÜST PANELİ
col_a, col_b = st.columns([0.8, 0.2])
with col_a:
    new_stock = st.text_input("", placeholder=D['ara'], key="add_input").upper()
with col_b:
    st.write("##") # Hizalama için boşluk
    if st.button(D['ekle']):
        if new_stock and new_stock not in st.session_state.watchlist:
            # BIST kontrolü: Sadece harf girilirse sonuna .IS eklemeyi dene (Opsiyonel)
            if new_stock.isalpha() and len(new_stock) <= 5 and not any(x in new_stock for x in ["=", "-"]):
                 # Kullanıcı THYAO yazdıysa hem THYAO hem THYAO.IS denemesi yapacak yapı
                 st.session_state.watchlist.append(f"{new_stock}.IS")
            else:
                st.session_state.watchlist.append(new_stock)
            st.rerun()

# 6. VERİ VE LİSTELEME
@st.cache_data(ttl=3600)
def get_usd_rate():
    try: return yf.Ticker("USDTRY=X").history(period="1d")['Close'].iloc[-1]
    except: return 34.50
usd_val = get_usd_rate()

def render_watchlist():
    if not st.session_state.watchlist:
        st.info(D['bos'])
        return

    for sym in st.session_state.watchlist:
        try:
            t = yf.Ticker(sym)
            df = t.history(period="1mo")
            if df.empty: continue
            
            now, prev = df['Close'].iloc[-1], df['Close'].iloc[-2]
            pct = ((now - prev) / prev) * 100
            
            # Sembol ismini güzelleştir
            clean_name = sym.replace('.IS','').replace('=X','').replace('-USD','')
            if sym == "GC=F": clean_name = "Altın / Gold"
            
            u_char = "₺" if "TRY" in curr else "$"
            # Basit kur çevrimi (BIST hissesi değilse ve TRY seçiliyse USD'den çevir)
            if "TRY" in curr and ".IS" not in sym and "TRY" not in sym:
                d_now = now * usd_val
            elif "USD" in curr and (".IS" in sym or "TRY" in sym):
                d_now = now / usd_val
            else:
                d_now = now
                
            color = "#00e676" if pct >= 0 else "#ff1744"

            # SATIR VE SİLME BUTONU
            c_row, c_del = st.columns([0.9, 0.1])
            with c_row:
                st.markdown(f"""
                <div class="stock-row">
                    <div class="sym-name">{clean_name}</div>
                    <div class="price-val">{d_now:,.2f} {u_char}</div>
                    <div class="pct-val" style="color:{color}">{pct:+.2f}%</div>
                </div>
                """, unsafe_allow_html=True)
            with c_del:
                st.write("##")
                if st.button("X", key=f"del_{sym}"):
                    st.session_state.watchlist.remove(sym)
                    st.rerun()
            
            with st.expander(D['detay']):
                if HAS_PLOTLY:
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(x=df.index, y=df['Close'], line=dict(color='#3772ff', width=2), fill='tozeroy', fillcolor='rgba(55, 114, 255, 0.05)'))
                    fig.update_layout(height=140, margin=dict(l=0,r=0,t=0,b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', xaxis=dict(visible=False), yaxis=dict(visible=False))
                    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        except: continue

render_watchlist()

if refresh:
    time.sleep(15)
    st.rerun()
