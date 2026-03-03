import streamlit as st
import yfinance as yf
import time

# 1. TASARIM AYARLARI (Sidebar Kilitli)
st.set_page_config(page_title="Borsa Terminali", layout="wide")

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

# 2. YAN PANEL (SIDEBAR)
with st.sidebar:
    lang = st.selectbox("Language / Dil", ["Türkçe", "English"])
    st.divider()
    st.write("**Para Birimi / Currency**")
    curr = st.radio("C_Select", ["₺ TRY", "$ USD"], label_visibility="collapsed")
    st.divider()
    
    # SENİN ÖZEL HİZALAMAN (KUTUCUK SOLDA, YAZI SAĞDA)
    c1, c2 = st.columns([0.15, 0.85])
    with c1:
        refresh = st.checkbox("R_Tog", value=True, label_visibility="collapsed")
    with c2:
        st.markdown('<span class="aligned-text">Otomatik Yenile (15s)</span>', unsafe_allow_html=True)

# 3. VERİ ÇEKME MOTORU
def get_price(sym):
    try:
        # Cache kullanmıyoruz, her saniye canlı sorgu
        d = yf.Ticker(sym).history(period="2d")
        if d.empty: return None
        return d
    except: return None

# 4. ANA EKRAN (HAFIZAYI BYPASS EDEN ÇİVİLİ LİSTE)
st.write("### Canlı Varlık Takibi")

# Bu liste asla session_state kullanmaz, doğrudan koda gömülüdür.
ANA_LISTE = [
    {"sym": "USDTRY=X", "name": "USD / TRY"},
    {"sym": "EURTRY=X", "name": "EUR / TRY"},
    {"sym": "BTC-TRY",  "name": "BTC / TRY"}
]

# Güncel dolar kurunu bir kere çek (USD çevrimi için)
try:
    current_usd_rate = yf.Ticker("USDTRY=X").history(period="1d")['Close'].iloc[-1]
except:
    current_usd_rate = 34.50

# Ekrana Basma Döngüsü
for item in ANA_LISTE:
    df = get_price(item['sym'])
    if df is not None:
        now = df['Close'].iloc[-1]
        prev = df['Close'].iloc[-2]
        pct = ((now - prev) / prev) * 100
        
        # Para Birimi Sembolü ve Fiyat Hesaplama
        symbol_char = "₺" if "TRY" in curr else "$"
        # Eğer Sidebar'dan USD seçiliyse ve veri TRY bazlıysa (bizim 3 birim de öyle), kurla bölüyoruz.
        final_price = now / current_usd_rate if "USD" in curr else now

        st.markdown(f"""
            <div class="stock-row">
                <div class="sym-name">{item['name']}</div>
                <div class="price-val">{final_price:,.2f} {symbol_char}</div>
                <div class="pct-val" style="color:{'#00e676' if pct >= 0 else '#ff1744'}">{pct:+.2f}%</div>
            </div>
        """, unsafe_allow_html=True)

# 5. MANUEL EKLEME KISMI (Yalnızca burası hafızada tutulur)
st.divider()
if 'user_extra' not in st.session_state:
    st.session_state.user_extra = []

col_in, col_bt = st.columns([0.8, 0.2])
with col_in:
    extra = st.text_input("", placeholder="Ekstra Hisse Ekle (Örn: THYAO)").upper()
with col_bt:
    st.write("##")
    if st.button("EKLE"):
        if extra and extra not in st.session_state.user_extra:
            final_ex = extra if any(x in extra for x in ["=", "-"]) or "." in extra else f"{extra}.IS"
            st.session_state.user_extra.append(final_ex)
            st.rerun()

for ex_item in st.session_state.user_extra:
    ex_df = get_price(ex_item)
    if ex_df is not None:
        st.markdown(f'<div class="stock-row"><div class="sym-name">{ex_item}</div><div class="price-val">{ex_df["Close"].iloc[-1]:,.2f}</div></div>', unsafe_allow_html=True)

# 6. YENİLEME
if refresh:
    time.sleep(15)
    st.rerun()
