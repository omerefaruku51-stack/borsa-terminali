import streamlit as st
import yfinance as yf
import pandas as pd
import time

# 1. SAYFA VE TASARIM AYARLARI
st.set_page_config(page_title="Borsa Intelligence", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    .stApp { background-color: #0f111a; color: #f0f2f6; }
    [data-testid="stSidebar"] { background-color: #161a25; border-right: 1px solid rgba(255,255,255,0.05); }
    
    /* Trend Okları */
    .trend-indicator {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 50px;
        height: 50px;
        border-radius: 12px;
        font-size: 24px;
        font-weight: bold;
    }
    .up-arrow { background-color: rgba(0, 230, 118, 0.1); color: #00e676; border: 2px solid #00e676; }
    .down-arrow { background-color: rgba(255, 23, 68, 0.1); color: #ff1744; border: 2px solid #ff1744; }
    
    .symbol-title { font-size: 1.8rem; font-weight: 700; color: #ffffff; margin-bottom: 5px; }
    header, footer {visibility: hidden;}
    hr { border-top: 1px solid rgba(255,255,255,0.05); margin: 1.5rem 0; }
    </style>
    """, unsafe_allow_html=True)

# 2. DİL PAKETLERİ (SİDEBAR DAHİL)
dil_ayarlari = {
    "Türkçe": {
        "ana_baslik": "BORSA INTELLIGENCE",
        "ayar_baslik": "⚙️ Ayarlar",
        "dil_sec": "Dil / Language",
        "para_birimi": "Para Birimi",
        "oto_yenile": "10sn Otomatik Güncelle",
        "liste_baslik": "İzleme Listesi",
        "ara_placeholder": "Sembolleri virgülle ayırın (THYAO.IS, BTC-USD...)",
        "fiyat_etiket": "Fiyat",
        "yon_etiket": "Yön",
        "bos_uyari": "🔍 Listenize bir sembol ekleyerek başlayın.",
        "hata": "Veri bulunamadı"
    },
    "English": {
        "ana_baslik": "STOCK INTELLIGENCE",
        "ayar_baslik": "⚙️ Settings",
        "dil_sec": "Language / Dil",
        "para_birimi": "Currency",
        "oto_yenile": "Auto-Refresh 10s",
        "liste_baslik": "Watchlist",
        "ara_placeholder": "Separate symbols with commas...",
        "fiyat_etiket": "Price",
        "yon_etiket": "Trend",
        "bos_uyari": "🔍 Add a symbol to your list to start.",
        "hata": "Data not found"
    }
}

# 3. YAN PANEL (SIDEBAR) GÜNCELLEMESİ
with st.sidebar:
    # Önce dil seçimini alıyoruz ki diğer her şey ona göre şekillensin
    temp_lang = st.selectbox("Language Selection", ["Türkçe", "English"], index=0)
    D = dil_ayarlari[temp_lang]
    
    st.divider()
    st.markdown(f"### {D['ayar_baslik']}")
    para_birimi = st.radio(D["para_birimi"], ["₺ TRY", "$ USD"])
    oto_taze = st.checkbox(D["oto_yenile"], value=True)
    
    st.divider()
    if temp_lang == "Türkçe":
        st.info("BIST hisseleri için sonuna .IS eklemeyi unutmayın.")
    else:
        st.info("Add .IS suffix for BIST (Istanbul) stocks.")

# 4. ANA EKRAN VE VERİ MOTORU
st.markdown(f"<h1 style='text-align: center; color: #3772ff;'>{D['ana_baslik']}</h1>", unsafe_allow_html=True)

search_input = st.text_input(D["liste_baslik"], placeholder=D["ara_placeholder"])
symbols = [s.strip().upper() for s in search_input.split(",") if s.strip()]

@st.cache_data(ttl=600)
def get_live_usd():
    try: return float(yf.Ticker("USDTRY=X").history(period="1d")['Close'].iloc[-1])
    except: return 34.45
usd_curr = get_live_usd()

# 5. GÖRSELLEŞTİRME
if not symbols:
    st.markdown(f"<div style='text-align: center; padding: 50px; color: #434651;'>{D['bos_uyari']}</div>", unsafe_allow_html=True)
else:
    for sym in symbols:
        try:
            t = yf.Ticker(sym)
            df = t.history(period="5d")
            if df.empty: continue
            
            last_p = df['Close'].iloc[-1]
            prev_c = df['Close'].iloc[-2]
            change_pct = ((last_p - prev_c) / prev_c) * 100
            
            # Kur Dönüşüm Mantığı
            is_bist = sym.endswith(".IS")
            unit_sym = "₺" if "TRY" in para_birimi else "$"
            final_p = last_p
            
            if "TRY" in para_birimi and not is_bist: final_p *= usd_curr
            elif "USD" in para_birimi and is_bist: final_p /= usd_curr

            # Arayüz Kartı
            st.markdown(f"<div class='symbol-title'>{sym}</div>", unsafe_allow_html=True)
            c1, c2, c3 = st.columns([1, 0.8, 2.5])
            
            with c1:
                st.metric(D["fiyat_etiket"], f"{final_p:,.2f} {unit_sym}", f"{change_pct:+.2f}%")
            
            with c2:
                st.write(f"**{D['yon_etiket']}**")
                # Ok doğrudan anlık değişime (bugünkü kâr/zarar) bakar
                if change_pct >= 0:
                    st.markdown('<div class="trend-indicator up-arrow">▲</div>', unsafe_allow_html=True)
                else:
                    st.markdown('<div class="trend-indicator down-arrow">▼</div>', unsafe_allow_html=True)
            
            with c3:
                st.line_chart(df['Close'], height=150)
            
            st.markdown("<hr>", unsafe_allow_html=True)
        except:
            st.warning(f"{sym}: {D['hata']}")

# 6. AUTO-REFRESH SİSTEMİ
if oto_taze:
    time.sleep(10)
    st.rerun()
