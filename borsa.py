import streamlit as st
import yfinance as yf
import pandas as pd
import time

# 1. HAFIZA TEMİZLİĞİ VE SIFIRLAMA (En Üstte Olmalı)
# Eğer liste boşsa veya 3 ana birimden biri eksikse hafızayı temizle
if 'watchlist' not in st.session_state or "USDTRY=X" not in st.session_state.watchlist:
    st.session_state.clear() # Tüm eski hayalet verileri siler
    st.session_state.watchlist = ["USDTRY=X", "EURTRY=X", "BTC-TRY"]

# 2. TASARIM AYARLARI (Sidebar Kilitli)
st.set_page_config(page_title="Borsa Pro Terminal", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #0f111a; color: #f0f2f6; }
    .stock-row {
        background: #1e222d; border-bottom: 1px solid #2a2e39;
        padding: 20px; display: flex; justify-content: space-between; align-items: center;
        border-radius: 4px; margin-bottom: 8px;
    }
    .sym-name { flex: 2; font-weight: 800; color: #3772ff; font-size: 1.2rem; }
    .price-val { flex: 2; text-align: right; font-weight: 700; font-size: 1.2rem; }
    .pct-val { flex: 1.5; text-align: right; font-weight: bold; font-size: 1.1rem; }
    
    /* Sidebar Milimetrik Hizalama */
    .aligned-text { display: inline-block; padding-top: 5px; font-size: 0.9rem; vertical-align: middle; }
    [data-testid="stHorizontalBlock"] { align-items: center; }
    
    header, footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# 3. SIDEBAR (TASARIM KORUNDU)
with st.sidebar:
    lang = st.selectbox("Language / Dil", ["Türkçe", "English"], key="app_lang")
    st.divider()
    st.write(f"**Para Birimi / Currency**")
    curr = st.radio("C_Select", ["₺ TRY", "$ USD"], label_visibility="collapsed", key="curr_sel")
    st.divider()
    
    # Kutucuk solda, yazı sağda (Senin istediğin hizalama)
    c1, c2 = st.columns([0.15, 0.85])
    with c1:
        refresh = st.checkbox("R_Tog", value=True, label_visibility="collapsed", key="ref_tog")
    with c2:
        st.markdown('<span class="aligned-text">Otomatik Yenile (15s)</span>', unsafe_allow_html=True)

# 4. EKLEME PANELİ
col_in, col_bt = st.columns([0.85, 0.15])
with col_in:
    new_asset = st.text_input("", placeholder="Varlık Ara/Ekle (Örn: THYAO, AAPL, BTC-USD)", key="add_input").upper()
with col_bt:
    st.write("##")
    if st.button("EKLE / ADD", use_container_width=True):
        if new_asset and new_asset not in st.session_state.watchlist:
            final_sym = new_asset if any(x in new_asset for x in ["=", "-"]) or "." in new_asset else f"{new_asset}.IS"
            st.session_state.watchlist.append(final_sym)
            st.rerun()

# 5. VERİ ÇEKME VE GÖSTERME
def get_live_data(sym):
    try:
        data = yf.Ticker(sym).history(period="2d")
        if data.empty: return None
        return data
    except: return None

# Listeyi döngüye al
for item in st.session_state.watchlist:
    df = get_live_data(item)
    if df is not None:
        now = df['Close'].iloc[-1]
        prev = df['Close'].iloc[-2]
        pct = ((now - prev) / prev) * 100
        color = "#00e676" if pct >= 0 else "#ff1744"
        
        # İsimlendirme
        if item == "USDTRY=X": name = "USD / TRY"
        elif item == "EURTRY=X": name = "EUR / TRY"
        elif item == "BTC-TRY": name = "BTC / TRY"
        else: name = item.replace('.IS','')
        
        # Fiyat ve Sembol
        u_char = "₺" if "TRY" in curr else "$"
        # Dolar seçiliyse TL bazlıları dolara çevir
        if "USD" in curr and ("TRY" in item or ".IS" in item):
            # Basit çevrim için USD kurunu kullan
            usd_rate = yf.Ticker("USDTRY=X").history(period="1d")['Close'].iloc[-1]
            now = now / usd_rate

        st.markdown(f"""
            <div class="stock-row">
                <div class="sym-name">{name}</div>
                <div class="price-val">{now:,.2f} {u_char}</div>
                <div class="pct-val" style="color:{color}">{pct:+.2f}%</div>
            </div>
        """, unsafe_allow_html=True)

# 6. YENİLEME
if refresh:
    time.sleep(15)
    st.rerun()
