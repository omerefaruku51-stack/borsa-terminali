import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import time

# 1. PREMIUM UI AYARLARI
st.set_page_config(page_title="Borsa Pro Terminal", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    .stApp { background-color: #0f111a; color: #f0f2f6; }
    [data-testid="stSidebar"] { background-color: #161a25; border-right: 1px solid rgba(255,255,255,0.1); }
    
    .data-card {
        background: #1e222d;
        border: 1px solid #2a2e39;
        border-radius: 16px;
        padding: 25px;
        margin: 10px auto;
        max-width: 600px;
        text-align: center;
        transition: transform 0.3s;
    }
    .data-card:hover { border-color: #3772ff; transform: translateY(-2px); }
    
    .symbol-name { font-size: 2rem; font-weight: 800; color: #3772ff; }
    .price-now { font-size: 3rem; font-weight: 700; margin: 5px 0; }
    
    .details-row { 
        display: flex; 
        justify-content: space-around; 
        margin-top: 15px; 
        border-top: 1px solid rgba(255,255,255,0.1); 
        padding-top: 15px; 
    }
    .detail-item { flex: 1; }
    .detail-label { font-size: 0.8rem; color: #848e9c; }
    .detail-value { font-size: 1.1rem; font-weight: 600; color: #ffffff; }

    header, footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# 2. DİL VE YAN PANEL
DIL_PAKETI = {
    "Türkçe": {
        "baslik": "BORSA PRO TERMİNAL",
        "ayar": "⚙️ Terminal Ayarları",
        "para": "Para Birimi",
        "yenile": "10sn Otomatik Yenile",
        "ara": "Hisse Ara (THYAO.IS, BTC-USD...)",
        "kapanis": "Dünkü Kapanış",
        "son_24": "Son 24 Saat Özeti",
        "detay_btn": "📈 Detaylı Grafik İncele",
        "grafik_baslik": "Fiyat Hareketleri (Uygulama İçi)"
    },
    "English": {
        "baslik": "STOCK PRO TERMINAL",
        "ayar": "⚙️ Settings",
        "para": "Currency",
        "yenile": "10s Auto Refresh",
        "ara": "Search (AAPL, BTC-USD...)",
        "kapanis": "Prev. Close",
        "son_24": "Last 24h Summary",
        "detay_btn": "📈 Detailed Analysis",
        "grafik_baslik": "Price Action (Native)"
    }
}

with st.sidebar:
    lang_choice = st.selectbox("Language / Dil", ["Türkçe", "English"])
    D = DIL_PAKETI[lang_choice]
    st.divider()
    para_birimi = st.radio(D["para"], ["₺ TRY", "$ USD"])
    oto_taze = st.checkbox(D["yenile"], value=True)

# 3. VERİ MOTORU
@st.cache_data(ttl=600)
def get_usd():
    try: return float(yf.Ticker("USDTRY=X").history(period="1d")['Close'].iloc[-1])
    except: return 34.50
usd_kur = get_usd()

st.markdown(f"<h1 style='text-align: center;'>{D['baslik']}</h1>", unsafe_allow_html=True)
search = st.text_input("", placeholder=D["ara"], key="main_search")
symbols = [s.strip().upper() for s in search.split(",") if s.strip()]

# 4. GÖRÜNTÜLEME VE GRAFİK
if not symbols:
    st.markdown(f"<div style='text-align: center; padding: 50px; color: #434651;'>{D['ara']}</div>", unsafe_allow_html=True)
else:
    for sym in symbols:
        try:
            t = yf.Ticker(sym)
            # Grafik için daha uzun veri (1 aylık)
            hist = t.history(period="1mo")
            if hist.empty: continue
            
            p_now, p_prev = hist['Close'].iloc[-1], hist['Close'].iloc[-2]
            change = ((p_now - p_prev) / p_prev) * 100
            
            is_bist = sym.endswith(".IS")
            unit = "₺" if "TRY" in para_birimi else "$"
            
            d_now = p_now * usd_kur if ("TRY" in para_birimi and not is_bist) else (p_now / usd_kur if ("USD" in para_birimi and is_bist) else p_now)
            d_prev = p_prev * usd_kur if ("TRY" in para_birimi and not is_bist) else (p_prev / usd_kur if ("USD" in para_birimi and is_bist) else p_prev)
            color = "#00e676" if change >= 0 else "#ff1744"

            # ANA KART
            st.markdown(f"""
                <div class="data-card">
                    <div class="symbol-name">{sym}</div>
                    <div class="price-now">{d_now:,.2f} {unit}</div>
                    <div class="details-row">
                        <div class="detail-item">
                            <div class="detail-label">{D['kapanis']}</div>
                            <div class="detail-value">{d_prev:,.2f} {unit}</div>
                        </div>
                        <div style="width:1px; background: rgba(255,255,255,0.1);"></div>
                        <div class="detail-item">
                            <div class="detail-label">{D['son_24']}</div>
                            <div class="detail-value" style="color:{color}">{change:+.2f}%</div>
                        </div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

            # --- GÖMÜLÜ DETAYLI GRAFİK (BUTONLA AÇILIR) ---
            with st.expander(D["detay_btn"]):
                fig = go.Figure()
                # Mum grafiği (Candlestick) yerine daha şık bir Area Chart
                fig.add_trace(go.Scatter(
                    x=hist.index, y=hist['Close'] * (usd_kur if ("TRY" in para_birimi and not is_bist) else (1/usd_kur if ("USD" in para_birimi and is_bist) else 1)),
                    mode='lines', fill='tozeroy',
                    line=dict(color='#3772ff', width=3),
                    fillcolor='rgba(55, 114, 255, 0.1)'
                ))
                fig.update_layout(
                    title=f"{sym} {D['grafik_baslik']}",
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    margin=dict(l=0, r=0, t=40, b=0),
                    height=350,
                    xaxis=dict(showgrid=False, color='#848e9c'),
                    yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.05)', side='right', color='#848e9c')
                )
                st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

            st.markdown("<br>", unsafe_allow_html=True)
            
        except Exception as e:
            st.error(f"{sym}: Veri alınamadı.")

# 5. REFRESH
if oto_taze:
    time.sleep(10)
    st.rerun()
