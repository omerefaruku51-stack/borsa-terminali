import streamlit as st
import yfinance as yf
import pandas as pd
import time

# 1. TASARIM VE KURAL SETİ (Sidebar Kilitli)
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
    
    /* Sidebar Milimetrik Hizalama - KİLİTLİ */
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

# 3. YAN PANEL (SIDEBAR) - TASARIM KESİNLİKLE BOZULMADI
with st.sidebar:
    lang = st.selectbox("Language / Dil", ["Türkçe", "English"], key="app_lang")
    D = DIL[lang]
    st.divider()
    st.write(f"**{D['para']}**")
    curr = st.radio("C_Select", ["₺ TRY", "$ USD"], label_visibility="collapsed", key="curr_sel")
    st.divider()
    
    # Kutucuk solda, yazı sağda hizalama
    c1, c2 = st.columns([0.15, 0.85])
    with c1:
        refresh = st.checkbox("R_Tog", value=True, label_visibility="collapsed", key="ref_tog")
    with c2:
        st.markdown(f'<span class="aligned-text">{D["yenile"]}</span>', unsafe_allow_html=True)

# 4. TAKİP LİSTESİ - ZORUNLU SIFIRLAMA
# Hayaletlerden kurtulmak için listeyi doğrudan burada tanımlıyoruz.
# TRY/USD için "USDTRY=X" (1 dolar kaç tl), TRY/EUR için "EURTRY=X", BTC/TRY için "BTC-TRY"
START_LIST = ["USDTRY=X", "EURTRY=X", "BTC-TRY"]

if 'watchlist' not in st.session_state:
    st.session_state.watchlist = START_LIST.copy()

# 5. EKLEME PANELİ
col_in, col_bt = st.columns([0.85, 0.15])
with col_in:
    new_asset = st.text_input("", placeholder=D['ara'], key="add_input").upper()
with col_bt:
    st.write("##")
    if st.button(D['ekle'], use_container_width=True):
        if new_asset and new_asset not in st.session_state.watchlist:
            # BIST kontrolü
            final_sym = new_asset if any(x in new_asset for x in ["=", "-"]) or "." in new_asset else f"{new_asset}.IS"
            st.session_state.watchlist.append(final_sym)
            st.rerun()

# 6. VERİ MOTORU (Cache kaldırıldı, doğrudan çekiyor)
def render_row(sym):
    try:
        # Veriyi taze çekiyoruz
        t = yf.Ticker(sym)
        df = t.history(period="2d")
        if df.empty: return

        now = df['Close'].iloc[-1]
        prev = df['Close'].iloc[-2]
        pct = ((now - prev) / prev) * 100
        color = "#00e676" if pct >= 0 else "#ff1744"

        # İsimlendirme Formatı: TRY / USD vb.
        if sym == "USDTRY=X": name = "USD / TRY"
        elif sym == "EURTRY=X": name = "EUR / TRY"
        elif sym == "BTC-TRY": name = "BTC / TRY"
        else: name = sym.replace('.IS','')

        # Birim Simgesi
        u_char = "₺" if "TRY" in curr else "$"
        
        # Basit Kur Çevrimi (Sadece dolar bazlı eklenenler için)
        # USDTRY ve EURTRY zaten TL bazlı gelir.
        price = now 
        if "USD" in curr and ("TRY" in sym or ".IS" in sym):
            # TL'den Dolar'a çevirmek için güncel kuru al
            rate = yf.Ticker("USDTRY=X").history(period="1d")['Close'].iloc[-1]
            price = now / rate
        elif "TRY" in curr and ("-USD" in sym or (".IS" not in sym and "TRY" not in sym)):
            # Dolar'dan TL'ye çevir
            rate = yf.Ticker("USDTRY=X").history(period="1d")['Close'].iloc[-1]
            price = now * rate

        st.markdown(f"""
            <div class="stock-row">
                <div class="sym-name">{name}</div>
                <div class="price-val">{price:,.2f} {u_char}</div>
                <div class="pct-val" style="color:{color}">{pct:+.2f}%</div>
            </div>
        """, unsafe_allow_html=True)
        
        # Silme seçeneği (Manuel eklenenler için)
        if sym not in START_LIST:
            if st.button(f"X - {name}", key=f"del_{sym}"):
                st.session_state.watchlist.remove(sym)
                st.rerun()
    except Exception as e:
        pass

# 7. ÇALIŞTIR
# Eğer watchlist hala boşsa veya 3'lü yoksa zorla ekle
for s in START_LIST:
    if s not in st.session_state.watchlist:
        st.session_state.watchlist.insert(0, s)

for item in st.session_state.watchlist:
    render_row(item)

if refresh:
    time.sleep(15)
    st.rerun()
