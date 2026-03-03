import streamlit as st
import yfinance as yf
import time

# 1. TASARIM (Sidebar Hizalaması Sabit)
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
    
    /* SIDEBAR MİLİMETRİK HİZALAMA */
    .aligned-text { display: inline-block; padding-top: 5px; font-size: 0.9rem; vertical-align: middle; }
    [data-testid="stHorizontalBlock"] { align-items: center; }
    
    header, footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# 2. HAFIZA TEMİZLEME MOTORU (ZORUNLU)
if st.sidebar.button("⚠️ SİSTEMİ SIFIRLA"):
    st.session_state.clear()
    st.rerun()

# Ana Listeyi Zorla Tanımla
if 'watchlist' not in st.session_state or len(st.session_state.watchlist) == 0:
    st.session_state.watchlist = ["USDTRY=X", "EURTRY=X", "BTC-TRY"]

# 3. YAN PANEL (SIDEBAR)
with st.sidebar:
    lang = st.selectbox("Language / Dil", ["Türkçe", "English"])
    st.divider()
    st.write("**Para Birimi / Currency**")
    curr = st.radio("C_Select", ["₺ TRY", "$ USD"], label_visibility="collapsed")
    st.divider()
    
    # KUTUCUK SOLDA, YAZI SAĞDA (Senin özel tasarımın)
    c1, c2 = st.columns([0.15, 0.85])
    with c1:
        refresh = st.checkbox("R_Tog", value=True, label_visibility="collapsed")
    with c2:
        st.markdown('<span class="aligned-text">Otomatik Yenile (15s)</span>', unsafe_allow_html=True)

# 4. VERİ ÇEKME VE BASMA
def draw_watchlist():
    # Güncel kur (çevrim için)
    try:
        u_rate = yf.Ticker("USDTRY=X").history(period="1d")['Close'].iloc[-1]
    except:
        u_rate = 34.50

    for sym in st.session_state.watchlist:
        try:
            # Önbelleksiz canlı veri
            ticker = yf.Ticker(sym)
            df = ticker.history(period="2d")
            
            if df.empty:
                # Veri boşsa alternatif yöntem dene (Bazen yfinance takılıyor)
                st.warning(f"Veri çekilemedi: {sym}")
                continue
                
            now = df['Close'].iloc[-1]
            prev = df['Close'].iloc[-2]
            pct = ((now - prev) / prev) * 100
            
            # İsimlendirme
            if sym == "USDTRY=X": name = "USD / TRY"
            elif sym == "EURTRY=X": name = "EUR / TRY"
            elif sym == "BTC-TRY": name = "BTC / TRY"
            else: name = sym.replace('.IS','')
            
            # Para Birimi ve Fiyat Ayarı
            symbol_char = "₺" if "TRY" in curr else "$"
            display_price = now
            
            if "USD" in curr and ("TRY" in sym or ".IS" in sym):
                display_price = now / u_rate
            elif "TRY" in curr and ("-USD" in sym or (".IS" not in sym and "TRY" not in sym)):
                display_price = now * u_rate

            st.markdown(f"""
                <div class="stock-row">
                    <div class="sym-name">{name}</div>
                    <div class="price-val">{display_price:,.2f} {symbol_char}</div>
                    <div class="pct-val" style="color:{'#00e676' if pct >= 0 else '#ff1744'}">{pct:+.2f}%</div>
                </div>
            """, unsafe_allow_html=True)
        except:
            st.error(f"Hata oluştu: {sym}")

# 5. ÜST PANEL VE EKLEME
col_in, col_bt = st.columns([0.8, 0.2])
with col_in:
    new_asset = st.text_input("", placeholder="Hisse Ekle (THYAO vb.)").upper()
with col_bt:
    st.write("##")
    if st.button("EKLE"):
        if new_asset and new_asset not in st.session_state.watchlist:
            final = new_asset if any(x in new_asset for x in ["=", "-"]) or "." in new_asset else f"{new_asset}.IS"
            st.session_state.watchlist.append(final)
            st.rerun()

# Listeyi Çiz
draw_watchlist()

# 6. YENİLEME
if refresh:
    time.sleep(15)
    st.rerun()
