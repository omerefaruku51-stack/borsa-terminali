import streamlit as st
import yfinance as yf
import pandas as pd
import time

# 1. TASARIM (Sidebar Kilitli - Grafik Kaldırıldı)
st.set_page_config(page_title="Borsa Pro Terminal", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #0f111a; color: #f0f2f6; }
    .stock-row {
        background: #1e222d; border-bottom: 1px solid #2a2e39;
        padding: 15px 20px; display: flex; justify-content: space-between; align-items: center;
        border-radius: 4px; margin-bottom: 5px;
    }
    .sym-name { flex: 2; font-weight: 800; color: #3772ff; font-size: 1.1rem; }
    .price-val { flex: 2; text-align: right; font-weight: 700; font-size: 1.1rem; }
    .pct-val { flex: 1.5; text-align: right; font-weight: bold; font-size: 1rem; }
    
    /* Sidebar Milimetrik Hizalama */
    .aligned-text { display: inline-block; padding-top: 5px; font-size: 0.9rem; vertical-align: middle; }
    [data-testid="stHorizontalBlock"] { align-items: center; }
    
    header, footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# 2. DİL VE AYARLAR
DIL = {
    "Türkçe": {"para": "Para Birimi", "yenile": "Otomatik Yenile (15s)", "ara": "Varlık Ara/Ekle...", "ekle": "EKLE"},
    "English": {"para": "Currency", "yenile": "Auto Refresh (15s)", "ara": "Add Asset...", "ekle": "ADD"}
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

# 4. TAKİP LİSTESİ (Sadece senin istediğin 3'lü)
# Önceki hayaletleri temizlemek için session_state'i bu 3'lüye zorluyoruz
TARGET_START = ["TRYUSD=X", "TRYEUR=X", "BTC-TRY"]
if 'watchlist' not in st.session_state or st.session_state.get('reset_needed', True):
    st.session_state.watchlist = TARGET_START.copy()
    st.session_state.reset_needed = False

# 5. EKLEME PANELİ
col_in, col_bt = st.columns([0.85, 0.15])
with col_in:
    new_asset = st.text_input("", placeholder=D['ara'], key="add_input").upper()
with col_bt:
    st.write("##")
    if st.button(D['ekle'], use_container_width=True):
        if new_asset and new_asset not in st.session_state.watchlist:
            final_sym = new_asset if any(x in new_asset for x in ["=", "-"]) or "." in new_asset else f"{new_asset}.IS"
            st.session_state.watchlist.append(final_sym)
            st.rerun()

# 6. VERİ MOTORU
@st.cache_data(ttl=60)
def get_rate():
    try: return yf.Ticker("USDTRY=X").history(period="1d")['Close'].iloc[-1]
    except: return 34.50
usd_val = get_rate()

def render_row(sym):
    try:
        t = yf.Ticker(sym)
        df = t.history(period="2d")
        if df.empty: return

        now = df['Close'].iloc[-1]
        prev = df['Close'].iloc[-2]
        pct = ((now - prev) / prev) * 100
        color = "#00e676" if pct >= 0 else "#ff1744"

        # İsimlendirme Formmatı: TRY / USD vb.
        if sym == "TRYUSD=X": display_name = "TRY / USD"
        elif sym == "TRYEUR=X": display_name = "TRY / EUR"
        elif sym == "BTC-TRY": display_name = "BTC / TRY"
        else: display_name = sym.replace('.IS','')

        # Birim Simgesi
        u_char = "₺" if "TRY" in curr else "$"
        
        # Fiyat Gösterimi (Sidebar seçimine göre basit çevrim)
        # Eğer varlık zaten TRY bazlıysa ve sidebar USD ise böl, tam tersiyse çarp
        if "USD" in curr and ("TRY" in sym or ".IS" in sym):
            price = now / usd_val
        elif "TRY" in curr and ("TRY" not in sym and ".IS" not in sym):
            price = now * usd_val
        else:
            price = now

        st.markdown(f"""
            <div class="stock-row">
                <div class="sym-name">{display_name}</div>
                <div class="price-val">{price:,.4f if price < 1 else :,.2f} {u_char}</div>
                <div class="pct-val" style="color:{color}">{pct:+.2f}%</div>
            </div>
        """, unsafe_allow_html=True)
        
        # Silme seçeneği (Opsiyonel, sadece manuel eklenenler için kalsın istersen kalsın)
        if sym not in TARGET_START:
            if st.button(f"Sil {display_name}", key=f"del_{sym}"):
                st.session_state.watchlist.remove(sym)
                st.rerun()
    except: pass

# 7. ÇALIŞTIR
for item in st.session_state.watchlist:
    render_row(item)

if refresh:
    time.sleep(15)
    st.rerun()
