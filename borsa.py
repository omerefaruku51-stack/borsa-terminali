import streamlit as st
import yfinance as yf
import time

# --- 1. SAYFA YAPILANDIRMASI VE TASARIM ---
st.set_page_config(page_title="Borsa Pro Terminal", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    .stApp { background-color: #0f111a; color: #f0f2f6; }
    [data-testid="stSidebar"] { background-color: #161926; border-right: 1px solid #2a2e39; }
    
    /* SIDEBAR MİLİMETRİK HİZALAMA: KUTUCUK SOLDA, YAZI SAĞDA */
    .sidebar-label { display: inline-block; padding-top: 2px; font-size: 14px; vertical-align: middle; margin-left: 8px; }
    [data-testid="stHorizontalBlock"] { align-items: center; }
    
    /* HİSSE KARTI TASARIMI */
    .stock-card {
        background: #1e222d; border: 1px solid #2a2e39; padding: 15px;
        border-radius: 8px; margin-bottom: 10px;
    }
    .sym-name { font-weight: 800; color: #3772ff; font-size: 1.1rem; }
    .price-val { font-weight: 700; font-size: 1.1rem; text-align: right; }
    
    header, footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- 2. DİL VE ÇEVİRİ PAKETİ ---
L = {
    "Türkçe": {
        "settings": "Ayarlar", "lang": "Dil", "curr": "Para Birimi", "ref": "Otomatik Yenile (15s)",
        "search": "Hisse Ara (THYAO, AAPL, BTC-USD...)", "add": "EKLE", "watchlist": "Sadece İzleme Listesi",
        "market_cap": "Piyasa Değ.", "vol": "Hacim", "detail": "Detayları Gör"
    },
    "English": {
        "settings": "Settings", "lang": "Language", "curr": "Currency", "ref": "Auto Refresh (15s)",
        "search": "Search Symbol...", "add": "ADD", "watchlist": "Watchlist Only",
        "market_cap": "Mkt Cap", "vol": "Volume", "detail": "View Details"
    },
    "العربية": {
        "settings": "إعدادات", "lang": "لغة", "curr": "عملة", "ref": "تحديث تلقائي (15 ثانية)",
        "search": "بحث عن سهم...", "add": "إضافة", "watchlist": "قائمة المراقبة فقط",
        "market_cap": "القيمة السوقية", "vol": "حجم التداول", "detail": "عرض التفاصيل"
    }
}

# --- 3. SIDEBAR (AYARLAR PANELİ) ---
with st.sidebar:
    st.markdown(f"### ⚙️ {L['Türkçe']['settings']}") # Not: Dişli ikonuna tıklandığında açılan panel
    lang_sel = st.selectbox("Dil / Language / لغة", ["Türkçe", "English", "العربية"], index=0)
    D = L[lang_sel] # Seçili dil paketi
    
    currency_sel = st.selectbox(D['curr'], ["₺ TRY", "$ USD"], index=0)
    st.divider()
    
    # MİLİMETRİK HİZALAMA: KUTUCUK SOLDA, YAZI SAĞDA
    c1, c2 = st.columns([0.15, 0.85])
    with c1:
        auto_refresh = st.checkbox("R", value=True, label_visibility="collapsed")
    with c2:
        st.markdown(f'<span class="sidebar-label">{D["ref"]}</span>', unsafe_allow_html=True)
    
    st.divider()
    only_favs = st.toggle(D['watchlist'], value=False)

# --- 4. VERİ VE HAFIZA YÖNETİMİ ---
if 'watchlist' not in st.session_state:
    st.session_state.watchlist = ["USDTRY=X", "EURTRY=X", "BTC-USD", "THYAO.IS", "AAPL", "TSLA"]

@st.cache_data(ttl=300)
def get_usd_rate():
    try: return yf.Ticker("USDTRY=X").history(period="1d")['Close'].iloc[-1]
    except: return 34.50

usd_rate = get_usd_rate()

def format_big_num(num):
    if num >= 1e12: return f"{num/1e12:.2f}T"
    elif num >= 1e9: return f"{num/1e9:.2f}B"
    elif num >= 1e6: return f"{num/1e6:.2f}M"
    return f"{num:,.0f}"

# --- 5. ANA EKRAN (ARAMA VE LİSTELEME) ---
st.title("📈 Borsa Pro Terminal")

# Arama Çubuğu
col_search, col_add = st.columns([0.85, 0.15])
with col_search:
    query = st.text_input("", placeholder=D['search'], label_visibility="collapsed").upper()
with col_add:
    if st.button(D['add'], use_container_width=True):
        if query and query not in st.session_state.watchlist:
            # Otomatik .IS ekleme mantığı (Türk hisseleri için)
            final_q = query if any(x in query for x in ["=", "-", "."]) else f"{query}.IS"
            st.session_state.watchlist.append(final_q)
            st.rerun()

# Listeleme
display_list = st.session_state.watchlist if not only_favs else st.session_state.watchlist # (Geliştirilebilir favori mantığı)

for sym in display_list:
    try:
        t = yf.Ticker(sym)
        hist = t.history(period="2d")
        if hist.empty: continue
        
        info = t.fast_info
        price = hist['Close'].iloc[-1]
        change = ((price - hist['Close'].iloc[-2]) / hist['Close'].iloc[-2]) * 100
        
        # Para Birimi Dönüşümü
        unit = "₺" if "TRY" in currency_sel else "$"
        d_price = price if "TRY" in currency_sel or any(x in sym for x in ["TRY", ".IS"]) else price * usd_rate # Basit mantık
        if "USD" in currency_pref and (".IS" in sym or "TRY" in sym): d_price = price / usd_rate
        
        # Kart Tasarımı
        color = "#00e676" if change >= 0 else "#ff1744"
        
        with st.container():
            col_info, col_fav = st.columns([0.9, 0.1])
            with col_info:
                with st.expander(f"{sym}  |  {price:,.2f} {unit}  |  {change:+.2f}%"):
                    # Detay Modalı (Expander içi)
                    c1, c2, c3 = st.columns(3)
                    c1.metric(D['market_cap'], format_big_num(info.get('market_cap', 0)))
                    c2.metric(D['vol'], format_big_num(info.get('last_volume', 0)))
                    c3.write(f"**Low/High:**\n{hist['Low'].iloc[-1]:,.2f} - {hist['High'].iloc[-1]:,.2f}")
            with col_fav:
                if st.button("⭐", key=f"fav_{sym}"):
                    st.session_state.watchlist.remove(sym)
                    st.rerun()
    except:
        continue

# --- 6. OTOMATİK YENİLEME ---
if auto_refresh:
    time.sleep(15)
    st.rerun()
