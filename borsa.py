import streamlit as st
import yfinance as yf
import pandas as pd
import time
import plotly.graph_objects as go

# 1. TASARIM VE KURAL SETİ (Sidebar Kilitli)
st.set_page_config(page_title="Borsa Pro Terminal", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #0f111a; color: #f0f2f6; }
    .stock-row {
        background: #1e222d; border-bottom: 1px solid #2a2e39;
        padding: 10px 15px; display: flex; justify-content: space-between; align-items: center;
        border-radius: 4px; margin-bottom: 5px; cursor: pointer;
    }
    .sym-name { flex: 2; font-weight: 800; color: #3772ff; font-size: 1.1rem; }
    .price-val { flex: 2; text-align: right; font-weight: 700; font-size: 1.1rem; }
    .pct-val { flex: 1.5; text-align: right; font-weight: bold; font-size: 1rem; }
    
    /* Sidebar Milimetrik Hizalama - Kilitli */
    .aligned-text { display: inline-block; padding-top: 5px; font-size: 0.9rem; vertical-align: middle; }
    [data-testid="stHorizontalBlock"] { align-items: center; }
    
    /* Buton ve Girdi Alanları */
    .stButton>button { background-color: #3772ff; color: white; border-radius: 5px; width: 100%; border:none; height: 3rem;}
    .stButton>button:hover { background-color: #2a58c7; }
    .stTextInput>div>div>input { background-color: #1e222d; color: white; border: 1px solid #2a2e39; height: 3rem;}
    
    header, footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# 2. DİL VE SABİT VERİLER
DIL = {
    "Türkçe": {"para": "Para Birimi", "yenile": "Otomatik Yenile (15s)", "ara": "Hisse/Kripto Ekle...", "ekle": "EKLE", "bos": "Liste boş."},
    "English": {"para": "Currency", "yenile": "Auto Refresh (15s)", "ara": "Add Asset...", "ekle": "ADD", "bos": "List empty."}
}

# 3. SIDEBAR (TASARIM KORUNDU)
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

# 4. TAKİP LİSTESİ YÖNETİMİ (Zorunlu Başlangıç)
TARGET_START = ["USDTRY=X", "EURTRY=X", "BTC-USD"]
if 'watchlist' not in st.session_state:
    st.session_state.watchlist = TARGET_START.copy()

# 5. ÜST PANEL (EKLEME)
col_in, col_bt = st.columns([0.8, 0.2])
with col_in:
    new_asset = st.text_input("", placeholder=D['ara'], key="add_input").upper()
with col_bt:
    if st.button(D['ekle']):
        if new_asset and new_asset not in st.session_state.watchlist:
            final_sym = new_asset if any(x in new_asset for x in ["=", "-"]) or "." in new_asset else f"{new_asset}.IS"
            st.session_state.watchlist.append(final_sym)
            st.rerun()

# 6. VERİ MOTORU VE GÖMÜLÜ GRAFİK
@st.cache_data(ttl=60)
def get_data(sym):
    try:
        data = yf.Ticker(sym).history(period="1mo", interval="1d")
        return data if not data.empty else None
    except: return None

@st.cache_data(ttl=60)
def get_rate():
    try: return yf.Ticker("USDTRY=X").history(period="1d")['Close'].iloc[-1]
    except: return 34.50
usd_rate = get_rate()

def draw_row(sym):
    df = get_data(sym)
    if df is None: return

    now = df['Close'].iloc[-1]
    prev = df['Close'].iloc[-2]
    pct = ((now - prev) / prev) * 100
    color = "#00e676" if pct >= 0 else "#ff1744"
    
    # İsimlendirme
    p_label = "TRY" if "TRY" in curr else "USD"
    if sym == "USDTRY=X": name = "USD / TRY"
    elif sym == "EURTRY=X": name = "EUR / TRY"
    elif sym == "BTC-USD": name = f"BTC / {p_label}"
    else: name = sym.replace('.IS','')

    # Kur Çevrimi
    u_char = "₺" if "TRY" in curr else "$"
    if "TRY" in curr:
        val = now if any(x in sym for x in ["TRY", ".IS"]) else now * usd_rate
    else:
        val = now if "-USD" in sym or (".IS" not in sym and "TRY" not in sym) else now / usd_rate

    # ARAYÜZ
    with st.container():
        st.markdown(f"""
            <div class="stock-row">
                <div class="sym-name">{name}</div>
                <div class="price-val">{val:,.2f} {u_char}</div>
                <div class="pct-val" style="color:{color}">{pct:+.2f}%</div>
            </div>
        """, unsafe_allow_html=True)
        
        # Gömülü Grafik (Aşağı açılır Expander içinde)
        with st.expander("Grafik / Chart"):
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=df.index, y=df['Close'],
                line=dict(color='#3772ff', width=3),
                fill='tozeroy', fillcolor='rgba(55, 114, 255, 0.1)'
            ))
            fig.update_layout(
                height=250, margin=dict(l=0,r=0,t=10,b=0),
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                xaxis=dict(showgrid=False, color="#848e9c"),
                yaxis=dict(side="right", showgrid=True, gridcolor="#2a2e39", color="#848e9c")
            )
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
            
            # Silme butonu grafik altında
            if st.button(f"Sil / Remove {name}", key=f"del_{sym}"):
                st.session_state.watchlist.remove(sym)
                st.rerun()

# 7. ÇALIŞTIRMA
for asset in st.session_state.watchlist:
    draw_row(asset)

if refresh:
    time.sleep(15)
    st.rerun()
