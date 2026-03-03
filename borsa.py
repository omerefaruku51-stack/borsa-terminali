import streamlit as st
import yfinance as yf
import pandas as pd
import time

# 1. TASARIM AYARLARI (Sidebar Kilitli)
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

# 2. YAN PANEL (SIDEBAR)
with st.sidebar:
    lang = st.selectbox("Language / Dil", ["Türkçe", "English"], key="app_lang")
    st.divider()
    st.write(f"**Para Birimi / Currency**")
    curr = st.radio("C_Select", ["₺ TRY", "$ USD"], label_visibility="collapsed", key="curr_sel")
    st.divider()
    
    # KUTUCUK SOLDA, YAZI SAĞDA (Senin özel tasarımın)
    c1, c2 = st.columns([0.15, 0.85])
    with c1:
        refresh = st.checkbox("R_Tog", value=True, label_visibility="collapsed", key="ref_tog")
    with c2:
        st.markdown('<span class="aligned-text">Otomatik Yenile (15s)</span>', unsafe_allow_html=True)

# 3. VERİ ÇEKME FONKSİYONU
def get_live_price(sym):
    try:
        # Cache yok, doğrudan çekiyoruz
        d = yf.Ticker(sym).history(period="2d")
        if d.empty: return None
        return d
    except: return None

# 4. ANA LİSTE (DOĞRUDAN KODA ÇAKILI - HAFIZADAN BAĞIMSIZ)
# Bu liste session_state'den gelmiyor, o yüzden gelmeme ihtimali sıfır.
ANA_BIRIMLER = ["USDTRY=X", "EURTRY=X", "BTC-TRY"]

# Eğer kullanıcı manuel bir şey eklediyse onu da listeye dahil et
if 'user_watchlist' not in st.session_state:
    st.session_state.user_watchlist = []

# EKLEME PANELİ
col_in, col_bt = st.columns([0.85, 0.15])
with col_in:
    new_asset = st.text_input("", placeholder="Eklemek istediğin hisse (Örn: THYAO)").upper()
with col_bt:
    st.write("##")
    if st.button("EKLE"):
        if new_asset and new_asset not in st.session_state.user_watchlist:
            final = new_asset if any(x in new_asset for x in ["=", "-"]) or "." in new_asset else f"{new_asset}.IS"
            st.session_state.user_watchlist.append(final)
            st.rerun()

# 5. EKRANA BASMA (Önce Ana Birimler, Sonra Kullanıcının Hisseleri)
tum_liste = ANA_BIRIMLER + st.session_state.user_watchlist

for item in tum_liste:
    df = get_live_price(item)
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
        
        # Kur Çevrimi
        u_char = "₺" if "TRY" in curr else "$"
        if "USD" in curr and ("TRY" in item or ".IS" in item):
            # TL bazlıyı dolara çevir
            try: u_rate = yf.Ticker("USDTRY=X").history(period="1d")['Close'].iloc[-1]
            except: u_rate = 34.50
            now = now / u_rate

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
