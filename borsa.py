import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import time

# 1. PREMIUM UI AYARLARI
st.set_page_config(page_title="Borsa Intelligence Pro", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    .stApp { background-color: #0f111a; color: #f0f2f6; }
    [data-testid="stSidebar"] { background-color: #161a25; }
    
    /* Modern Veri Kartı */
    .data-card {
        background: #1e222d;
        border-radius: 15px;
        padding: 25px;
        border: 1px solid #2a2e39;
        margin-bottom: 20px;
    }
    
    .symbol-header { 
        font-size: 2.2rem; 
        font-weight: 800; 
        color: #ffffff; 
        margin-bottom: 10px;
        display: flex;
        align-items: center;
    }
    
    .price-main { font-size: 2.5rem; font-weight: 700; color: #ffffff; }
    .price-sub { font-size: 1.1rem; color: #848e9c; }
    
    header, footer {visibility: hidden;}
    /* Streamlit'in varsayılan grafik yazılarını gizle */
    .modebar { display: none !important; }
    </style>
    """, unsafe_allow_html=True)

# 2. DİL VE AYARLAR
D_LIST = {
    "Türkçe": {
        "title": "BORSA TERMINAL PRO",
        "search": "Sembol Arama",
        "close": "Kapanış",
        "current": "Güncel",
        "change": "Değişim",
        "chart_title": "7 Günlük Performans (Uygulama İçi)",
        "detail": "🔍 Gelişmiş Teknik Analiz Panelini Aç"
    },
    "English": {
        "title": "STOCK TERMINAL PRO",
        "search": "Symbol Search",
        "close": "Close",
        "current": "Live",
        "change": "Change",
        "chart_title": "7-Day Performance (Native)",
        "detail": "🔍 Open Advanced Technical Panel"
    }
}

with st.sidebar:
    lang = st.selectbox("Language", ["Türkçe", "English"])
    D = D_LIST[lang]
    st.divider()
    curr = st.radio("Para Birimi", ["₺ TRY", "$ USD"])
    auto_ref = st.checkbox("Canlı Akış (15s)", value=True)

# 3. VERİ MOTORU
@st.cache_data(ttl=600)
def get_rate():
    try: return yf.Ticker("USDTRY=X").history(period="1d")['Close'].iloc[-1]
    except: return 34.50
usd = get_rate()

st.title(f"🚀 {D['title']}")
search = st.text_input(D["search"], placeholder="THYAO.IS, BTC-USD, NVDA...")
symbols = [s.strip().upper() for s in search.split(",") if s.strip()]

# 4. GÖRÜNTÜLEME
if not symbols:
    st.info("İzleme listenize bir sembol ekleyin.")
else:
    for sym in symbols:
        try:
            t = yf.Ticker(sym)
            df = t.history(period="7d")
            if df.empty: continue
            
            p_now, p_prev = df['Close'].iloc[-1], df['Close'].iloc[-2]
            pct = ((p_now - p_prev) / p_prev) * 100
            
            # Para Birimi Dönüşümü
            is_b = sym.endswith(".IS")
            u = "₺" if "TRY" in curr else "$"
            d_now = p_now * usd if ("TRY" in curr and not is_b) else (p_now / usd if ("USD" in curr and is_b) else p_now)
            d_prev = p_prev * usd if ("TRY" in curr and not is_b) else (p_prev / usd if ("USD" in curr and is_b) else p_prev)

            # EKRAN TASARIMI
            st.markdown(f"<div class='symbol-header'>{sym}</div>", unsafe_allow_html=True)
            
            col1, col2 = st.columns([1, 2])
            
            with col1:
                st.markdown(f"""
                <div class="data-card">
                    <div class="price-sub">{D['current']}</div>
                    <div class="price-main">{d_now:,.2f} {u}</div>
                    <div style="color:{'#00e676' if pct>=0 else '#ff1744'}; font-size:1.2rem; font-weight:bold;">
                        {pct:+.2f}%
                    </div>
                    <hr style="opacity:0.1">
                    <div class="price-sub">{D['close']}</div>
                    <div style="font-size:1.2rem;">{d_prev:,.2f} {u}</div>
                </div>
                """, unsafe_allow_html=True)

            with col2:
                # KENDİ GRAFİĞİMİZ (Plotly - Hiçbir dış bağlantı/reklam içermez)
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=df.index, y=df['Close'],
                    mode='lines+markers',
                    line=dict(color='#3772ff', width=3),
                    fill='tozeroy',
                    fillcolor='rgba(55, 114, 255, 0.1)'
                ))
                fig.update_layout(
                    margin=dict(l=0, r=0, t=30, b=0),
                    height=250,
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    xaxis=dict(showgrid=False, color='#434651'),
                    yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.05)', side='right'),
                    title=D['chart_title'],
                    title_font=dict(size=14, color='#848e9c')
                )
                st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

            # TEKNİK ANALİZ (GİZLİ PANEL)
            with st.expander(D['detail']):
                st.caption("Uluslararası standartlarda TradingView veri motoru kullanılmaktadır.")
                # Buraya sadece iframe gelecek, Rackspace vb. görünmez.
                pass 
                
            st.markdown("<hr style='opacity:0.1'>", unsafe_allow_html=True)
        except:
            st.error(f"{sym}: {D['hata']}")

# 5. REFRESH
if auto_ref:
    time.sleep(15)
    st.rerun()
