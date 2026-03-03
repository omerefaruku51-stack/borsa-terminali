import streamlit as st
import yfinance as yf
import time

# --- 1. SAYFA VE SIDEBAR AYARLARI ---
st.set_page_config(page_title="Borsa Pro Terminal", layout="wide")

# CSS: Sidebar Hizalaması (Kutucuk Solda, Yazı Sağda) ve Genel Tema
st.markdown("""
    <style>
    .stApp { background-color: #0f111a; color: #f0f2f6; }
    
    /* Sidebar Milimetrik Hizalama */
    .sidebar-text { 
        display: inline-block; 
        padding-top: 4px; 
        font-size: 0.9rem; 
        vertical-align: middle; 
    }
    [data-testid="stHorizontalBlock"] { align-items: center; }
    
    /* Satır Tasarımı */
    .stock-row {
        background: #1e222d; border-bottom: 1px solid #2a2e39;
        padding: 18px 25px; display: flex; justify-content: space-between; align-items: center;
        border-radius: 6px; margin-bottom: 8px;
    }
    .sym-name { flex: 2; font-weight: 800; color: #3772ff; font-size: 1.1rem; }
    .price-val { flex: 2; text-align: right; font-weight: 700; font-size: 1.1rem; }
    .pct-val { flex: 1.5; text-align: right; font-weight: bold; font-size: 1rem; }
    
    header, footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- 2. SIDEBAR (HİÇ KAPANMAYACAK SABİT YAPI) ---
with st.sidebar:
    st.title("⚙️ Kontrol Paneli")
    lang = st.selectbox("Language / Dil", ["Türkçe", "English"], key="lang_opt")
    st.divider()
    
    st.write("**Para Birimi / Currency**")
    curr = st.radio("C_Sel", ["₺ TRY", "$ USD"], label_visibility="collapsed", key="curr_opt")
    st.divider()
    
    # SENİN İSTEDİĞİN ÖZEL HİZALAMA: KUTUCUK SOLDA, YAZI SAĞDA
    c1, c2 = st.columns([0.15, 0.85])
    with c1:
        refresh_toggle = st.checkbox("Ref", value=True, label_visibility="collapsed", key="ref_check")
    with c2:
        label = "Otomatik Yenile (15s)" if lang == "Türkçe" else "Auto Refresh (15s)"
        st.markdown(f'<span class="sidebar-text">{label}</span>', unsafe_allow_html=True)

# --- 3. ANA LİSTE VE VERİ MOTORU ---
# Sabit liste (Asla kaybolmaz)
ANA_LISTE = [
    {"sym": "USDTRY=X", "name": "USD / TRY"},
    {"sym": "EURTRY=X", "name": "EUR / TRY"},
    {"sym": "BTC-TRY",  "name": "BTC / TRY"}
]

def get_data(ticker_sym):
    try:
        data = yf.Ticker(ticker_sym).history(period="2d")
        if not data.empty:
            return data
    except:
        return None
    return None

# --- 4. EKRAN ÇIKTISI ---
st.subheader("📊 Canlı Piyasa İzleme")

# USD Kuru (Çevrim için)
try:
    usd_price = yf.Ticker("USDTRY=X").history(period="1d")['Close'].iloc[-1]
except:
    usd_price = 34.50

for item in ANA_LISTE:
    df = get_data(item['sym'])
    if df is not None:
        price_now = df['Close'].iloc[-1]
        price_prev = df['Close'].iloc[-2]
        change = ((price_now - price_prev) / price_prev) * 100
        
        # Para Birimi Mantığı
        display_symbol = "₺" if "TRY" in curr else "$"
        # USD seçiliyse ve veri TL bazlıysa çevir
        final_price = price_now / usd_price if "USD" in curr else price_now
        
        color = "#00e676" if change >= 0 else "#ff1744"
        
        st.markdown(f"""
            <div class="stock-row">
                <div class="sym-name">{item['name']}</div>
                <div class="price-val">{final_price:,.2f} {display_symbol}</div>
                <div class="pct-val" style="color:{color}">{change:+.2f}%</div>
            </div>
        """, unsafe_allow_html=True)

# --- 5. EKLEME PANELİ ---
st.divider()
col_add_in, col_add_btn = st.columns([0.8, 0.2])
with col_add_in:
    manual = st.text_input("", placeholder="Hisse Ekle (Örn: THYAO)").upper()
with col_add_btn:
    st.write("##")
    if st.button("EKLE"):
        st.info("Ekleme özelliği bir sonraki adımda stabilize edilecektir.")

# --- 6. YENİLEME ---
if refresh_toggle:
    time.sleep(15)
    st.rerun()
