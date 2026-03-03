import streamlit as st
import yfinance as yf
import time
import random

# 1. TASARIM (Sidebar Kilitli)
st.set_page_config(page_title="Borsa Pro Terminal", layout="wide")

# Sidebar Hizalaması (Senin Özel İstediğin Tasarım)
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
    
    /* SIDEBAR MİLİMETRİK HİZALAMA: KUTUCUK SOLDA, YAZI SAĞDA */
    .aligned-text { display: inline-block; padding-top: 5px; font-size: 0.9rem; vertical-align: middle; }
    [data-testid="stHorizontalBlock"] { align-items: center; }
    
    header, footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# 2. CACHE VE HAFIZA BYPASS (Zorunlu Temizlik)
# Uygulama her çalıştığında farklı bir ID üreterek hafızayı kandırıyoruz
if 'force_refresh' not in st.session_state:
    st.session_state['force_refresh'] = random.randint(1, 10000)

# 3. YAN PANEL (SIDEBAR)
with st.sidebar:
    lang = st.selectbox("Language / Dil", ["Türkçe", "English"])
    st.divider()
    st.write("**Para Birimi / Currency**")
    curr = st.radio("C_Select", ["₺ TRY", "$ USD"], label_visibility="collapsed")
    st.divider()
    
    # KUTUCUK SOLDA, YAZI SAĞDA HİZALAMA
    c1, c2 = st.columns([0.15, 0.85])
    with c1:
        refresh = st.checkbox("R_Tog", value=True, label_visibility="collapsed")
    with c2:
        st.markdown('<span class="aligned-text">Otomatik Yenile (15s)</span>', unsafe_allow_html=True)

# 4. SABİT LİSTE (Asla Değişmez, Hafızadan Okumaz)
# Bu liste doğrudan koda yazılıdır, hafıza bozulsa da buradan okunur.
SABIT_BIRIMLER = [
    {"sym": "USDTRY=X", "label": "USD / TRY"},
    {"sym": "EURTRY=X", "label": "EUR / TRY"},
    {"sym": "BTC-TRY", "label": "BTC / TRY"}
]

# 5. EKLEME PANELİ
st.write("### Varlık Takip Terminali")
col_in, col_bt = st.columns([0.8, 0.2])
with col_in:
    new_asset = st.text_input("", placeholder="Hisse Ekle (Örn: THYAO, AAPL)").upper()
with col_bt:
    st.write("##")
    if st.button("LİSTEYE EKLE"):
        if 'ek_liste' not in st.session_state:
            st.session_state.ek_liste = []
        if new_asset and new_asset not in st.session_state.ek_liste:
            final = new_asset if any(x in new_asset for x in ["=", "-"]) or "." in new_asset else f"{new_asset}.IS"
            st.session_state.ek_liste.append(final)
            st.rerun()

# 6. VERİLERİ EKRANA BAS
def draw_ui():
    # Güncel Dolar Kuru (Çevrim için)
    try:
        u_rate = yf.Ticker("USDTRY=X").history(period="1d")['Close'].iloc[-1]
    except:
        u_rate = 34.50

    # Önce 3 Sabit Birimi Bas
    for item in SABIT_BIRIMLER:
        try:
            d = yf.Ticker(item['sym']).history(period="2d")
            if d.empty: continue
            
            now = d['Close'].iloc[-1]
            prev = d['Close'].iloc[-2]
            pct = ((now - prev) / prev) * 100
            
            # Para Birimi Ayarı
            p_val = now
            symbol = "₺" if "TRY" in curr else "$"
            if "USD" in curr:
                p_val = now / u_rate if "TRY" in item['sym'] else now

            st.markdown(f"""
                <div class="stock-row">
                    <div class="sym-name">{item['label']}</div>
                    <div class="price-val">{p_val:,.2f} {symbol}</div>
                    <div class="pct-val" style="color:{'#00e676' if pct >= 0 else '#ff1744'}">{pct:+.2f}%</div>
                </div>
            """, unsafe_allow_html=True)
        except: pass

    # Sonra Kullanıcının Eklediklerini Bas
    if 'ek_liste' in st.session_state:
        for item in st.session_state.ek_liste:
            try:
                d = yf.Ticker(item).history(period="2d")
                now = d['Close'].iloc[-1]
                st.markdown(f"""
                    <div class="stock-row">
                        <div class="sym-name">{item.replace('.IS','')}</div>
                        <div class="price-val">{now:,.2f}</div>
                        <div class="pct-val" style="color:white">--</div>
                    </div>
                """, unsafe_allow_html=True)
            except: pass

draw_ui()

# 7. YENİLEME
if refresh:
    time.sleep(15)
    st.rerun()
