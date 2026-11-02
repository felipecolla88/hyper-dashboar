import streamlit as st
import requests
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime

st.set_page_config(
    page_title="Hyperliquid & Binance - Ecossistema Quantitativo Real",
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

# --- FUNÇÕES DE CONEXÃO REAL ÀS APIS (HYPERLIQUID & BINANCE) ---

@st.cache_data(ttl=10)
def get_hyperliquid_real_data(target_asset="BTC"):
    """Busca preço mark real e Open Interest direto da API oficial da Hyperliquid."""
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
                    return float(ctx["markPx"]), float(ctx["openInterest"]), float(ctx.get("prevDayPx", ctx["markPx"]))
    except Exception:
        pass
    return 0.0, 0.0, 0.0

@st.cache_data(ttl=5)
def get_hyperliquid_orderbook(target_asset="BTC"):
    """Busca o Livro de Ofertas L2 real (Bids e Asks) da Hyperliquid."""
    try:
        url = "https://api.hyperliquid.xyz/info"
        payload = {"type": "l2Book", "coin": target_asset}
        response = requests.post(url, json=payload, timeout=3)
        if response.status_code == 200:
            data = response.json()
            levels = data.get("levels", [[], []])
            bids = levels[0]
            asks = levels[1]
            
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

@st.cache_data(ttl=15)
def get_binance_futures_ticker(symbol="BTCUSDT"):
    """Busca dados de 24h reais da API pública de Futuros da Binance."""
    try:
        url = f"https://fapi.binance.com/fapi/v1/ticker/24hr?symbol={symbol}"
        response = requests.get(url, timeout=3)
        if response.status_code == 200:
            data = response.json()
            return float(data.get("lastPrice", 0)), float(data.get("priceChangePercent", 0)), float(data.get("volume", 0))
    except Exception:
        pass
    return 0.0, 0.0, 0.0

# --- BARRA LATERAL ---
st.sidebar.title("⚡ Data Feed Hub (Real)")
st.sidebar.markdown("---")
pagina = st.sidebar.radio(
    "Navegação:",
    [
        "🎯 Livro de Ofertas e Liquidez (API Real)",
        "🌐 Monitor Multiativos (Hyperliquid & Binance)"
    ]
)
st.sidebar.markdown("---")
st.sidebar.info("Conectado diretamente aos endpoints públicos oficiais de mercado.")

# =====================================================================
# PÁGINA 1: LIVRO DE OFERTAS E PROFUNDIDADE REAL (L2 BOOK)
# =====================================================================
if pagina == "🎯 Livro de Ofertas e Liquidez (API Real)":
    st.markdown("### 🐋 Profundidade e Liquidez Real de Mercado (Hyperliquid L2)")
    
    col_sym, col_ex = st.columns([2, 3])
    with col_sym:
        sym = st.selectbox("Ativo:", ["BTC", "ETH", "SOL", "XRP", "SUI"], index=0)
    with col_ex:
        st.markdown("**Fonte:** `API Hyperliquid /l2Book` (Dados Reais)")

    price, oi, prev_px = get_hyperliquid_real_data(sym)
    df_bids, df_asks = get_hyperliquid_orderbook(sym)
    
    col_m1, col_m2, col_m3 = st.columns(3)
    col_m1.metric("Preço Mark Atual", f"US$ {price:,.2f}" if price else "Indisponível")
    col_m2.metric("Open Interest (Contratos)", f"{oi:,.2f}" if oi else "Indisponível")
    change_24h = ((price - prev_px) / prev_px * 100) if prev_px > 0 else 0.0
    col_m3.metric("Variação 24h", f"{change_24h:+.2f}%")

    st.markdown("---")
    
    c_bid, c_ask = st.columns(2)
    
    with c_bid:
        st.markdown(f"#### 🟢 Ordens de Compra (Bids) — {sym}")
        fig_bids = go.Figure()
        if not df_bids.empty:
            fig_bids.add_trace(go.Bar(
                x=df_bids["px"], y=df_bids["sz"],
                marker_color="#00C853", name="Bids"
            ))
        fig_bids.add_vline(x=price, line_dash="dash", line_color="white", annotation_text=f"Preço: {price:,.2f}")
        fig_bids.update_layout(
            template="plotly_dark", paper_bgcolor="#0c0e12", plot_bgcolor="#0c0e12",
            height=400, margin=dict(t=20, b=20, l=30, r=30), showlegend=False,
            xaxis=dict(gridcolor="rgba(255,255,255,0.05)", title="Preço (US$)"),
            yaxis=dict(gridcolor="rgba(255,255,255,0.05)", title="Volume / Tamanho")
        )
        st.plotly_chart(fig_bids, use_container_width=True)

    with c_ask:
        st.markdown(f"#### 🔴 Ordens de Venda (Asks) — {sym}")
        fig_asks = go.Figure()
        if not df_asks.empty:
            fig_asks.add_trace(go.Bar(
                x=df_asks["px"], y=df_asks["sz"],
                marker_color="#FF5252", name="Asks"
            ))
        fig_asks.add_vline(x=price, line_dash="dash", line_color="white", annotation_text=f"Preço: {price:,.2f}")
        fig_asks.update_layout(
            template="plotly_dark", paper_bgcolor="#0c0e12", plot_bgcolor="#0c0e12",
            height=400, margin=dict(t=20, b=20, l=30, r=30), showlegend=False,
            xaxis=dict(gridcolor="rgba(255,255,255,0.05)", title="Preço (US$)"),
            yaxis=dict(gridcolor="rgba(255,255,255,0.05)", title="Volume / Tamanho")
        )
        st.plotly_chart(fig_asks, use_container_width=True)

# =====================================================================
# PÁGINA 2: MONITOR MULTIATIVOS (HYPERLIQUID & BINANCE FUTURES)
# =====================================================================
elif pagina == "🌐 Monitor Multiativos (Hyperliquid & Binance)":
    st.markdown("### 📊 Comparativo de Ativos em Tempo Real (APIs Oficiais)")
    
    ativos = ["BTC", "ETH", "SOL", "XRP", "SUI", "AVAX"]
    
    dados_tabela = []
    for a in ativos:
        # Dados Hyperliquid
        hp_price, hp_oi, hp_prev = get_hyperliquid_real_data(a)
        hp_chg = ((hp_price - hp_prev) / hp_prev * 100) if hp_prev > 0 else 0.0
        
        # Dados Binance Futures equivalents
        bn_symbol = f"{a}USDT"
        bn_price, bn_chg, bn_vol = get_binance_futures_ticker(bn_symbol)
        
        dados_tabela.append({
            "Ativo": a,
            "Hyperliquid Preço (US$)": f"${hp_price:,.2f}" if hp_price else "N/A",
            "Hyperliquid Variação 24h": f"{hp_chg:+.2f}%" if hp_price else "N/A",
            "Open Interest (HL)": f"{hp_oi:,.0f}" if hp_oi else "N/A",
            "Binance Fut. Preço (US$)": f"${bn_price:,.2f}" if bn_price else "N/A",
            "Binance Fut. Variação 24h": f"{bn_chg:+.2f}%" if bn_price else "N/A"
        })
        
    df_comparativo = pd.DataFrame(dados_tabela)
    st.dataframe(df_comparativo, use_container_width=True, hide_index=True)
    
    st.markdown("---")
    st.caption("Nota: Todos os valores exibidos são consultados diretamente das APIs públicas das exchanges no momento do carregamento da página.")
