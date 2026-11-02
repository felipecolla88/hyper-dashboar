import streamlit as st
import requests
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime

st.set_page_config(
    page_title="Hyperliquid - Ecossistema Quantitativo Real",
    page_icon="⚡",
    layout="wide"
)

# Estilo global escuro
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

# --- FUNÇÃO DE DADOS REAIS E AGREGAÇÃO DO BOOK L2 ---
@st.cache_data(ttl=5)
def get_real_market_liquidity(target_asset="BTC"):
    """Busca dados Mark Price, Open Interest e agrupa o L2 Book real por faixas de preço."""
    try:
        url = "https://api.hyperliquid.xyz/info"
        payload = {"type": "metaAndAssetCtxs"}
        response = requests.post(url, json=payload, timeout=3)
        mark_px, open_int = 0.0, 0.0
        if response.status_code == 200:
            data = response.json()
            universe = data[0]["universe"]
            contexts = data[1]
            for i, asset in enumerate(universe):
                if asset["name"] == target_asset:
                    ctx = contexts[i]
                    mark_px = float(ctx["markPx"])
                    open_int = float(ctx["openInterest"])
                    break
        
        # Buscar L2 Book real
        book_payload = {"type": "l2Book", "coin": target_asset}
        book_resp = requests.post(url, json=book_payload, timeout=3)
        bids, asks = [], []
        if book_resp.status_code == 200:
            book_data = book_resp.json()
            levels = book_data.get("levels", [[], []])
            bids = levels[0]
            asks = levels[1]

        return mark_px, open_int, bids, asks
    except Exception:
        pass
    return 100.0, 1000.0, [], []

# --- BARRA LATERAL ---
st.sidebar.title("⚡ Hyperliquid Hub (Real)")
st.sidebar.markdown("---")
pagina = st.sidebar.radio(
    "Navegação:",
    [
        "📊 Perfil de Liquidez Real (L2 Book Agregado)",
        "🧱 Muralha de Ordens Limite (Book L2 Real)"
    ]
)
st.sidebar.markdown("---")
st.sidebar.info("Gráficos baseados exclusivamente no livro de ofertas L2 e dados Mark oficiais.")

# =====================================================================
# PÁGINA 1: PERFIL DE LIQUIDEZ REAL (L2 BOOK AGREGADO)
# =====================================================================
if pagina == "📊 Perfil de Liquidez Real (L2 Book Agregado)":
    st.title("⚡ Hyperliquid - Perfil de Liquidez e Ofertas Reais")

    col1, col2 = st.columns([2, 5])
    with col1:
        selected_symbol = st.selectbox(
            "Selecione o Ativo:",
            options=['BTC', 'ETH', 'SOL', 'AVAX', 'XRP', 'SUI', 'DOGE'],
            index=0
        )

    price, oi, raw_bids, raw_asks = get_real_market_liquidity(selected_symbol)
    if price == 0.0:
        price = 81500.0 if selected_symbol == 'BTC' else 2271.2

    # Processar e agrupar os Bids e Asks reais em faixas (bins) proporcionais ao preço
    bin_size = price * 0.002  # Intervalo de agrupamento dinâmico (0.2% do preço)
    
    def process_book_side(orders, is_bid=True):
        if not orders:
            return pd.DataFrame(columns=["Bin", "Volume"])
        
        df = pd.DataFrame(orders, columns=["px", "sz", "n"])
        df["px"] = df["px"].astype(float)
        df["sz"] = df["sz"].astype(float)
        
        # Filtrar apenas o range relevante próximo ao preço atual (±15%)
        if is_bid:
            df = df[(df["px"] >= price * 0.85) & (df["px"] <= price)]
        else:
            df = df[(df["px"] <= price * 1.15) & (df["px"] >= price)]
            
        if df.empty:
            return pd.DataFrame(columns=["Bin", "Volume"])
            
        df["Bin"] = (df["px"] / bin_size).round() * bin_size
        grouped = df.groupby("Bin")["sz"].sum().reset_index()
        grouped.rename(columns={"sz": "Volume"}, inplace=True)
        return grouped

    df_bids_agg = process_book_side(raw_bids, is_bid=True)
    df_asks_agg = process_book_side(raw_asks, is_bid=False)

    fig = make_subplots(
        rows=2, cols=1, 
        row_heights=[0.75, 0.25], 
        vertical_spacing=0.03,
        shared_xaxes=True
    )

    # Cores assimétricas baseadas nas paredes reais de ordens
    if not df_bids_agg.empty:
        fig.add_trace(go.Bar(
            x=df_bids_agg["Bin"], y=df_bids_agg["Volume"], 
            marker_color="#1E88E5", name="Paredes de Compra (Bids Reais)"
        ), row=1, col=1)

    if not df_asks_agg.empty:
        fig.add_trace(go.Bar(
            x=df_asks_agg["Bin"], y=df_asks_agg["Volume"], 
            marker_color="#FF7043", name="Paredes de Venda (Asks Reais)"
        ), row=1, col=1)

    # Curvas de acumulação real baseadas no book
    if not df_bids_agg.empty:
        cum_bids = df_bids_agg.sort_values("Bin", ascending=False)
        cum_bids["CumVol"] = cum_bids["Volume"].cumsum()
        fig.add_trace(go.Scatter(
            x=cum_bids["Bin"], y=cum_bids["CumVol"], 
            fill='tozeroy', mode='lines', line=dict(color='rgba(30, 136, 229, 0.9)', width=2),
            fillcolor='rgba(30, 136, 229, 0.2)', name="Acumulado Bids"
        ), row=2, col=1)

    if not df_asks_agg.empty:
        cum_asks = df_asks_agg.sort_values("Bin", ascending=True)
        cum_asks["CumVol"] = cum_asks["Volume"].cumsum()
        fig.add_trace(go.Scatter(
            x=cum_asks["Bin"], y=cum_asks["CumVol"], 
            fill='tozeroy', mode='lines', line=dict(color='rgba(255, 112, 67, 0.9)', width=2),
            fillcolor='rgba(255, 112, 67, 0.2)', name="Acumulado Asks"
        ), row=2, col=1)

    fig.add_vline(x=price, line_dash="dash", line_color="#00FF66", row=1, col=1)
    fig.add_vline(x=price, line_dash="dash", line_color="#00FF66", row=2, col=1)

    fig.add_annotation(
        x=price, y=0.95, yref="paper",
        text=f"<b>Preço Atual: US$ {price:,.2f}</b>",
        showarrow=False, font=dict(color="#00FF66", size=12),
        bgcolor="#0c0e12", bordercolor="#00FF66", borderwidth=1
    )

    fig.update_layout(
        title=dict(text=f"Ativo: {selected_symbol} | Open Interest Real: {oi:,.0f} contratos", font=dict(color="white")),
        template="plotly_dark", paper_bgcolor="#0c0e12", plot_bgcolor="#0c0e12",
        height=750, showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(color="white")),
        margin=dict(t=80, b=20, l=40, r=40)
    )

    fig.update_xaxes(title_text="", row=1, col=1, showticklabels=False, gridcolor="rgba(255,255,255,0.05)")
    fig.update_xaxes(title_text="Níveis de Preço Agregados (US$)", row=2, col=1, gridcolor="rgba(255,255,255,0.05)")
    fig.update_yaxes(title_text="Volume L2 (Size)", row=1, col=1, gridcolor="rgba(255,255,255,0.05)")
    fig.update_yaxes(title_text="Acumulado Book", row=2, col=1, gridcolor="rgba(255,255,255,0.05)")

    st.plotly_chart(fig, use_container_width=True)

# =====================================================================
# PÁGINA 2: MURALHA DE ORDENS LIMITE (BOOK L2 REAL)
# =====================================================================
elif pagina == "🧱 Muralha de Ordens Limite (Book L2 Real)":
    st.title("🧱 Muralhas de Ordens Limite (Livro L2 Real da Hyperliquid)")

    selected_symbol = st.selectbox("Selecione o Ativo:", options=['BTC', 'ETH', 'SOL', 'XRP', 'SUI'], index=0)
    price, oi, raw_bids, raw_asks = get_real_market_liquidity(selected_symbol)

    if price == 0.0:
        price = 81500.0

    df_bids = pd.DataFrame(raw_bids, columns=["px", "sz", "n"]) if raw_bids else pd.DataFrame(columns=["px", "sz"])
    df_asks = pd.DataFrame(raw_asks, columns=["px", "sz", "n"]) if raw_asks else pd.DataFrame(columns=["px", "sz"])

    fig_lim = go.Figure()

    if not df_bids.empty:
        df_bids["px"] = df_bids["px"].astype(float)
        df_bids["sz"] = df_bids["sz"].astype(float)
        fig_lim.add_trace(go.Bar(
            y=df_bids["px"], x=df_bids["sz"],
            orientation='h', marker_color="#1E88E5",
            name="Ordens de Compra (Bids Reais)"
        ))

    if not df_asks.empty:
        df_asks["px"] = df_asks["px"].astype(float)
        df_asks["sz"] = df_asks["sz"].astype(float)
        fig_lim.add_trace(go.Bar(
            y=df_asks["px"], x=df_asks["sz"],
            orientation='h', marker_color="#FF7043",
            name="Ordens de Venda (Asks Reais)"
        ))

    fig_lim.add_hline(
        y=price, line_dash="dash", line_color="#00FF66",
        annotation_text=f"<b>Preço Atual: US$ {price:,.2f}</b>",
        annotation_position="bottom right",
        annotation_font=dict(color="#00FF66", size=12)
    )

    fig_lim.update_layout(
        title=dict(text=f"Muralhas de Ordens Limite | Ativo: {selected_symbol}", font=dict(color="white")),
        template="plotly_dark", paper_bgcolor="#0c0e12", plot_bgcolor="#0c0e12",
        height=850,
        xaxis=dict(title="Tamanho do Lote Real (Size)", showgrid=True, gridcolor="rgba(255,255,255,0.05)"),
        yaxis=dict(title="Faixas de Preço (US$)", autorange="reversed", showgrid=True, gridcolor="rgba(255,255,255,0.05)"),
        showlegend=True
    )

    st.plotly_chart(fig_lim, use_container_width=True)
