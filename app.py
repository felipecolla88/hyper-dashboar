import streamlit as st
import requests
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import time
from datetime import datetime, timedelta

st.set_page_config(
    page_title="Hyperliquid - Ecossistema Quantitativo",
    page_icon="⚡",
    layout="wide"
)

# Estilo global escuro estilo Terminal Quant
st.markdown("""
    <style>
    .stApp {
        background-color: #0c0e12;
        color: #ffffff;
    }
    
    header[data-testid="stHeader"] {
        background-color: transparent !important;
        visibility: visible !important;
    }
    
    button[kind="header"], button[kind="header"] svg, [data-testid="stSidebarNav"] svg {
        color: #ffffff !important;
        fill: #ffffff !important;
        visibility: visible !important;
    }

    div.stButton > button {
        background-color: #1a1d24 !important;
        color: #ffffff !important;
        border: 1px solid #2d3139 !important;
        border-radius: 6px !important;
        font-weight: 600 !important;
    }
    div.stButton > button:hover {
        background-color: #2d3139 !important;
        border-color: #4b5563 !important;
        color: #00ff66 !important;
    }

    section[data-testid="stSidebar"] {
        background-color: #11141a !important;
    }
    section[data-testid="stSidebar"] * {
        color: #ffffff !important;
    }

    div[data-baseweb="select"] > div {
        background-color: #1a1d24 !important;
        color: #ffffff !important;
        border-color: #2d3139 !important;
    }
    
    hr {
        border-color: #2d3139 !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- ESTADO GLOBAL ---
if "grupo_detalhado" not in st.session_state:
    st.session_state["grupo_detalhado"] = None

def get_hyperliquid_data(target_asset="ETH"):
    try:
        url = "https://api.hyperliquid.xyz/info"
        payload = {"type": "metaAndAssetCtxs"}
        response = requests.post(url, json=payload, timeout=3)
        if response.status_code == 200:
            data = response.json()
            universe = data[0]["universe"]
            contexts = data[1]
            for i, asset in enumerate(universe):
                if asset["name"] == target_asset:
                    ctx = contexts[i]
                    return float(ctx["markPx"]), float(ctx["openInterest"])
    except Exception:
        pass
     
    fallbacks = {"BTC": 81500.0, "ETH": 2271.2, "SOL": 195.0, "AVAX": 35.0, "XRP": 1.5, "SUI": 3.0}
    return fallbacks.get(target_asset, 2271.2), 50000.0

@st.cache_data(ttl=30)
def get_market_changes():
    target_coins = ["BTC", "ETH", "XRP", "WLD", "ONDO", "CRV", "JUP", "FIL", "TIA", "DOT", "APT"]
    coins_result = []
    try:
        url = "https://api.hyperliquid.xyz/info"
        payload = {"type": "metaAndAssetCtxs"}
        response = requests.post(url, json=payload, timeout=3)
        if response.status_code == 200:
            data = response.json()
            universe = data[0]["universe"]
            contexts = data[1]
            
            live_data = {}
            for i, asset in enumerate(universe):
                name = asset["name"]
                ctx = contexts[i]
                prev_day_px = float(ctx.get("prevDayPx", ctx["markPx"]))
                mark_px = float(ctx["markPx"])
                change_pct = ((mark_px - prev_day_px) / prev_day_px) * 100
                live_data[name] = change_pct

            for coin in target_coins:
                if coin in live_data:
                    val = live_data[coin]
                    sign = "+" if val >= 0 else ""
                    coins_result.append({"name": coin, "change": f"{sign}{val:.2f}%"})
                else:
                    coins_result.append({"name": coin, "change": "+0.00%"})
            return coins_result
    except Exception:
        pass
        
    for coin in target_coins:
        coins_result.append({"name": coin, "change": "+1.5%"})
    return coins_result

# =====================================================================
# 1. DEFINIÇÃO DA BARRA LATERAL (PRECISA VIR ANTES DA VARIÁVEL 'pagina')
# =====================================================================
st.sidebar.title("⚡ Hyperliquid Hub")
st.sidebar.markdown("---")
pagina = st.sidebar.radio(
    "Navegação:",
    [
        "🎯 Captura & Rompimentos (Baleias)",
        "📈 Stacks, Liquidações & Books", 
        "🐋 Distribuição de Carteiras (Backes View)"
    ]
)
st.sidebar.markdown("---")
st.sidebar.info("Plataforma integrada de análise quantitativa e on-chain desenvolvida para monitoramento de derivativos.")


# =====================================================================
# 2. VERIFICAÇÃO DAS PÁGINAS (AGORA A VARIÁVEL 'pagina' JÁ EXISTE)
# =====================================================================

if pagina == "🎯 Captura & Rompimentos (Baleias)":
    # Barra de Ferramentas Superior estilo terminal
    t1, t2, t3, t4, t5 = st.columns(5)
    t1.button("📈 VIRADAS DE TENDÊNCIA", use_container_width=True)
    t2.button("🤖 ROBÔ SIMULADO", use_container_width=True)
    t3.button("📌 PLANOS CONDICIONAIS", use_container_width=True)
    t4.button("📋 RELATÓRIO DIÁRIO", use_container_width=True)
    t5.button("🔔 ALERTAS (142)", use_container_width=True)
    
    st.markdown("### 🐋 Análise de Captura de Liquidez (1 Dia vs 1 Semana)")
    
    col_sym, col_tf = st.columns([2, 3])
    with col_sym:
        sym = st.selectbox("Ativo em Análise:", ["ETH", "BTC", "SOL", "XRP"], index=0)
    with col_tf:
        st.markdown("**Modo de Janela:** `1 Dia / 1 Semana`")
    
    price, _ = get_hyperliquid_data(sym)
    
    col_1d, col_1w = st.columns(2)
    
    with col_1d:
        st.markdown("#### 1 dia <span style='font-size:12px; color:#9ca3af;'>posições abertas nas últimas 24 h</span>", unsafe_allow_html=True)
        st.error("▼ **72% captura abaixo primeiro em 1 dia**\nzona 2.250–2.264 | ▲ 28% | nenhuma <1%")
        st.caption("Binance - faixa ±50% · US$ (est.) · 📈 **lateral 64%** · ⚡ possível cascata se liquidar 2.299")
        
        def make_chart_1d(base_price):
            np.random.seed(24)
            prices = np.linspace(1500, 3200, 50)
            longs = [np.random.uniform(5, 45) if p < base_price else 0 for p in prices]
            shorts = [np.random.uniform(5, 50) if p > base_price else 0 for p in prices]
            
            fig = go.Figure()
            fig.add_trace(go.Bar(x=prices, y=longs, marker_color="#1E88E5", name="Longs"))
            fig.add_trace(go.Bar(x=prices, y=shorts, marker_color="#FF7043", name="Shorts"))
            fig.add_vline(x=base_price, line_dash="dash", line_color="white")
            fig.add_annotation(x=base_price, y=55, text=f"agora {base_price:,.1f}", showarrow=False, font=dict(color="white"))
            fig.add_annotation(x=2160, y=30, text="Δ vácuo 2.120-2.200", showarrow=False, font=dict(color="#FFD54F", size=10))
            
            fig.update_layout(
                template="plotly_dark", paper_bgcolor="#0c0e12", plot_bgcolor="#0c0e12",
                height=360, margin=dict(t=20, b=20, l=30, r=30), showlegend=False,
                xaxis=dict(gridcolor="rgba(255,255,255,0.05)"),
                yaxis=dict(gridcolor="rgba(255,255,255,0.05)", title="US$ 60,0 mi")
            )
            return fig
            
        st.plotly_chart(make_chart_1d(price), use_container_width=True)
        m_l1d, m_s1d = st.columns(2)
        m_l1d.caption("▼ longs US$ 188,7 mi (est.)")
        m_s1d.caption("shorts US$ 214,7 mi (est.) ▲")

    with col_1w:
        st.markdown("#### 1 semana <span style='font-size:12px; color:#9ca3af;'>posições abertas nos últimos 7 dias</span>", unsafe_allow_html=True)
        st.success("▲ **59% captura acima primeiro em 1 sem**\nzona 2.319–2.333 | ▼ 41% | nenhuma <1%")
        st.caption("Binance - faixa ±50% · US$ (est.) · 📈 **lateral 64%** · ⚡ possível cascata se liquidar 2.304")
        
        def make_chart_1w(base_price):
            np.random.seed(168)
            prices = np.linspace(1500, 3200, 50)
            longs = [np.random.uniform(10, 80) if p < base_price else 0 for p in prices]
            shorts = [np.random.uniform(10, 95) if p > base_price else 0 for p in prices]
            
            fig = go.Figure()
            fig.add_trace(go.Bar(x=prices, y=longs, marker_color="#1E88E5", name="Longs"))
            fig.add_trace(go.Bar(x=prices, y=shorts, marker_color="#00C853", name="Shorts"))
            fig.add_vline(x=base_price, line_dash="dash", line_color="white")
            fig.add_annotation(x=base_price, y=100, text=f"agora {base_price:,.1f}", showarrow=False, font=dict(color="white"))
            fig.add_annotation(x=2160, y=50, text="Δ vácuo 2.120-2.200", showarrow=False, font=dict(color="#FFD54F", size=10))
            
            fig.update_layout(
                template="plotly_dark", paper_bgcolor="#0c0e12", plot_bgcolor="#0c0e12",
                height=360, margin=dict(t=20, b=20, l=30, r=30), showlegend=False,
                xaxis=dict(gridcolor="rgba(255,255,255,0.05)"),
                yaxis=dict(gridcolor="rgba(255,255,255,0.05)", title="US$ 200,0 mi")
            )
            return fig
            
        st.plotly_chart(make_chart_1w(price), use_container_width=True)
        m_l1w, m_s1w = st.columns(2)
        m_l1w.caption("▼ longs US$ 995,6 mi (est.)")
        m_s1w.caption("shorts US$ 1,26 bi (est.) ▲")

elif pagina == "📈 Stacks, Liquidações & Books":
    st.title("⚡ Hyperliquid - Painel Quantitativo Profissional")
    st.info("Painel de Stacks e Livro de Ordens Ativo.")

elif pagina == "🐋 Distribuição de Carteiras (Backes View)":
    st.title("📊 Hyperliquid - Análise de Posições e PnL por Carteiras")
    st.info("Painel de distribuição on-chain.")
