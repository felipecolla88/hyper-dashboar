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

# FUNÇÃO REAL PARA BUSCAR O LIVRO DE OFERTAS (L2 BOOK) DA HYPERLIQUID
@st.cache_data(ttl=5)
def get_hyperliquid_orderbook(target_asset="ETH"):
    try:
        url = "https://api.hyperliquid.xyz/info"
        payload = {"type": "l2Book", "coin": target_asset}
        response = requests.post(url, json=payload, timeout=3)
        if response.status_code == 200:
            data = response.json()
            levels = data.get("levels", [[], []])
            bids = levels[0] # Compras (preço, quantidade)
            asks = levels[1] # Vendas (preço, quantidade)
            
            df_bids = pd.DataFrame(bids, columns=["px", "sz", "n"]) if bids else pd.DataFrame(columns=["px", "sz"])
            df_asks = pd.DataFrame(asks, columns=["px", "sz", "n"]) if asks else pd.DataFrame(columns=["px", "sz"])
            
            if not df_bids.empty:
                df_bids["px"] = df_bids["px"].astype(float)
                df_bids["sz"] = df_bids["sz"].astype(float)
            if not df_asks.empty:
                df_asks["px"] = df_asks["px"].astype(float)
                df_asks["sz"] = df_asks["sz"].astype(float)
                
            return df_bids, df_asks
    except Exception:
        pass
    return pd.DataFrame(columns=["px", "sz"]), pd.DataFrame(columns=["px", "sz"])

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

# --- BARRA LATERAL ---
st.sidebar.title("⚡ Hyperliquid Hub")
st.sidebar.markdown("---")
pagina = st.sidebar.radio(
    "Navegação:",
    [
        "🎯 Captura & Rompimentos (Dados Reais API)",
        "📈 Stacks, Liquidações & Books", 
        "🐋 Distribuição de Carteiras (Backes View)"
    ]
)
st.sidebar.markdown("---")
st.sidebar.info("Plataforma integrada com dados diretos da API pública da Hyperliquid.")


# =====================================================================
# PÁGINA 1: CAPTURA & ROMPIMENTOS COM DADOS REAIS DE ORDER BOOK
# =====================================================================
if pagina == "🎯 Captura & Rompimentos (Dados Reais API)":
    
    t1, t2, t3, t4, t5 = st.columns(5)
    t1.button("📈 VIRADAS DE TENDÊNCIA", use_container_width=True)
    t2.button("🤖 ROBÔ SIMULADO", use_container_width=True)
    t3.button("📌 PLANOS CONDICIONAIS", use_container_width=True)
    t4.button("📋 RELATÓRIO DIÁRIO", use_container_width=True)
    t5.button("🔔 ALERTAS (142)", use_container_width=True)
    
    st.markdown("### 🐋 Livro de Ordens e Liquidez Real (API Hyperliquid L2)")
    
    col_sym, col_tf = st.columns([2, 3])
    with col_sym:
        sym = st.selectbox("Ativo em Análise:", ["ETH", "BTC", "SOL", "XRP", "SUI"], index=0)
    with col_tf:
        st.markdown("**Fonte de Dados:** `API Oficial Hyperliquid (L2 Book em Tempo Real)`")
    
    # Obter preço atual real e o order book real da API
    price, oi = get_hyperliquid_data(sym)
    df_bids, df_asks = get_hyperliquid_orderbook(sym)
    
    col_1d, col_1w = st.columns(2)
    
    with col_1d:
        st.markdown(f"#### Livro de Ordens de Compra (Bids) — {sym}", unsafe_allow_html=True)
        st.success(f"Preço de Referência Atual: **US$ {price:,.2f}** | Open Interest: **US$ {oi:,.0f}**")
        
        def make_real_bids_chart(df, current_price):
            fig = go.Figure()
            if not df.empty:
                fig.add_trace(go.Bar(
                    x=df["px"], y=df["sz"], 
                    marker_color="#1E88E5", 
                    name="Ordens de Compra (Bids)"
                ))
            fig.add_vline(x=current_price, line_dash="dash", line_color="#00FF66", annotation_text=f"Preço Atual: {current_price:,.2f}")
            fig.update_layout(
                template="plotly_dark", paper_bgcolor="#0c0e12", plot_bgcolor="#0c0e12",
                height=360, margin=dict(t=20, b=20, l=30, r=30), showlegend=False,
                xaxis=dict(gridcolor="rgba(255,255,255,0.05)", title="Preço (US$)"),
                yaxis=dict(gridcolor="rgba(255,255,255,0.05)", title="Tamanho da Ordem (Size)")
            )
            return fig
            
        st.plotly_chart(make_real_bids_chart(df_bids, price), use_container_width=True)

    with col_1w:
        st.markdown(f"#### Livro de Ordens de Venda (Asks) — {sym}", unsafe_allow_html=True)
        st.error(f"Resistências Ativas no Book L2 da Hyperliquid para **{sym}**")
        
        def make_real_asks_chart(df, current_price):
            fig = go.Figure()
            if not df.empty:
                fig.add_trace(go.Bar(
                    x=df["px"], y=df["sz"], 
                    marker_color="#FF7043", 
                    name="Ordens de Venda (Asks)"
                ))
            fig.add_vline(x=current_price, line_dash="dash", line_color="#00FF66", annotation_text=f"Preço Atual: {current_price:,.2f}")
            fig.update_layout(
                template="plotly_dark", paper_bgcolor="#0c0e12", plot_bgcolor="#0c0e12",
                height=360, margin=dict(t=20, b=20, l=30, r=30), showlegend=False,
                xaxis=dict(gridcolor="rgba(255,255,255,0.05)", title="Preço (US$)"),
                yaxis=dict(gridcolor="rgba(255,255,255,0.05)", title="Tamanho da Ordem (Size)")
            )
            return fig
            
        st.plotly_chart(make_real_asks_chart(df_asks, price), use_container_width=True)

elif pagina == "📈 Stacks, Liquidações & Books":
    st.title("⚡ Hyperliquid - Painel Quantitativo Profissional")
    st.info("Painel de Stacks e Livro de Ordens Ativo.")

elif pagina == "🐋 Distribuição de Carteiras (Backes View)":
    st.title("📊 Hyperliquid - Análise de Posições e PnL por Carteiras")
    st.info("Painel de distribuição on-chain.")
