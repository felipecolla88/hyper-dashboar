import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

st.set_page_config(
    page_title="Hyperliquid - Institutional Real-Data Terminal",
    page_icon="⚡",
    layout="wide"
)

# Estilo global escuro estilo Terminal Quant
st.markdown("""
    <style>
    .stApp {
        background-color: #0b0e14;
        color: #e5e7eb;
    }
    header[data-testid="stHeader"] {
        background-color: transparent !important;
        visibility: visible !important;
    }
    button[kind="header"], button[kind="header"] svg, [data-testid="stSidebarNav"] svg {
        color: #ffffff !important;
        fill: #ffffff !important;
    }
    div.stButton > button {
        background-color: #161b22 !important;
        color: #f3f4f6 !important;
        border: 1px solid #30363d !important;
        border-radius: 6px !important;
        font-weight: 600 !important;
        font-size: 13px !important;
    }
    div.stButton > button:hover {
        background-color: #21262d !important;
        border-color: #58a6ff !important;
        color: #58a6ff !important;
    }
    section[data-testid="stSidebar"] {
        background-color: #161b22 !important;
        border-right: 1px solid #30363d !important;
    }
    section[data-testid="stSidebar"] * {
        color: #e5e7eb !important;
    }
    div[data-baseweb="select"] > div {
        background-color: #161b22 !important;
        color: #ffffff !important;
        border-color: #30363d !important;
    }
    hr {
        border-color: #30363d !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- FUNÇÃO DE DADOS 100% REAIS DA API HYPERLIQUID ---
@st.cache_data(ttl=5)
def get_hyperliquid_live_data(target_asset="BTC"):
    """Consulta dados reais e oficiais diretamente da API da Hyperliquid."""
    try:
        url = "https://api.hyperliquid.xyz/info"
        
        # Contextos de mercado (Preço Mark e Open Interest)
        payload_ctx = {"type": "metaAndAssetCtxs"}
        resp_ctx = requests.post(url, json=payload_ctx, timeout=3)
        mark_px, open_int, prev_day_px = 0.0, 0.0, 0.0
        
        if resp_ctx.status_code == 200:
            data = resp_ctx.json()
            universe = data[0]["universe"]
            contexts = data[1]
            for i, asset in enumerate(universe):
                if asset["name"] == target_asset:
                    ctx = contexts[i]
                    mark_px = float(ctx["markPx"])
                    open_int = float(ctx["openInterest"])
                    prev_day_px = float(ctx.get("prevDayPx", mark_px))
                    break

        # Livro de Ofertas L2 Real
        payload_book = {"type": "l2Book", "coin": target_asset}
        resp_book = requests.post(url, json=payload_book, timeout=3)
        bids, asks = [], []
        if resp_book.status_code == 200:
            book_data = resp_book.json()
            levels = book_data.get("levels", [[], []])
            bids = levels[0]
            asks = levels[1]

        return mark_px, open_int, prev_day_px, bids, asks
    except Exception:
        pass
    return 0.0, 0.0, 0.0, [], []

# --- BARRA LATERAL ---
st.sidebar.title("⚡ Real Data Terminal")
st.sidebar.markdown("---")
pagina = st.sidebar.radio(
    "Navegação:",
    [
        "📖 Livro de Ofertas L2 (Dados Reais)",
        "🌐 Monitor de Ativos & Open Interest"
    ]
)
st.sidebar.markdown("---")
st.sidebar.info("Modo estrito: Apenas dados obtidos diretamente das APIs públicas oficiais das exchanges.")

# =====================================================================
# PÁGINA 1: LIVRO DE OFERTAS L2 (DADOS REAIS EM DEGRAUS)
# =====================================================================
if pagina == "📖 Livro de Ofertas L2 (Dados Reais)":
    st.title("⚡ Livro de Ofertas L2 (Dados Reais da Hyperliquid)")
    st.markdown("Visualização direta da profundidade de mercado passiva (ordens limites reais no book).")

    col1, col2 = st.columns([2, 5])
    with col1:
        selected_symbol = st.selectbox(
            "Selecione o Ativo:",
            options=['BTC', 'ETH', 'SOL', 'AVAX', 'XRP', 'SUI', 'DOGE'],
            index=0
        )

    price, oi, prev_px, raw_bids, raw_asks = get_hyperliquid_live_data(selected_symbol)
    
    if price == 0.0:
        st.error("Não foi possível conectar à API da Hyperliquid no momento. Tente novamente em instantes.")
    else:
        change_24h = ((price - prev_px) / prev_px) * 100 if prev_px > 0 else 0.0

        # Métricas Reais do Ativo
        m1, m2, m3 = st.columns(3)
        m1.metric("Preço Mark Atual (Real)", f"US$ {price:,.2f}")
        m2.metric("Open Interest Global (Contratos)", f"{oi:,.2f}")
        m3.metric("Variação 24h", f"{change_24h:+.2f}%")

        st.markdown("---")

        df_bids = pd.DataFrame(raw_bids, columns=["px", "sz", "n"]) if raw_bids else pd.DataFrame(columns=["px", "sz"])
        df_asks = pd.DataFrame(raw_asks, columns=["px", "sz", "n"]) if raw_asks else pd.DataFrame(columns=["px", "sz"])

        if not df_bids.empty:
            df_bids["px"] = df_bids["px"].astype(float)
            df_bids["sz"] = df_bids["sz"].astype(float)
        if not df_asks.empty:
            df_asks["px"] = df_asks["px"].astype(float)
            df_asks["sz"] = df_asks["sz"].astype(float)

        # Gráfico institucional em degraus (Depth Chart Real)
        fig = go.Figure()

        if not df_bids.empty:
            df_bids = df_bids.sort_values("px", ascending=False)
            df_bids["cum_sz"] = df_bids["sz"].cumsum()
            fig.add_trace(go.Scatter(
                x=df_bids["px"], y=df_bids["cum_sz"],
                mode='lines', name='Bids (Compra)',
                line=dict(color='#00C853', width=2),
                fill='tozeroy', fillcolor='rgba(0, 200, 83, 0.15)'
            ))

        if not df_asks.empty:
            df_asks = df_asks.sort_values("px", ascending=True)
            df_asks["cum_sz"] = df_asks["sz"].cumsum()
            fig.add_trace(go.Scatter(
                x=df_asks["px"], y=df_asks["cum_sz"],
                mode='lines', name='Asks (Venda)',
                line=dict(color='#FF5252', width=2),
                fill='tozeroy', fillcolor='rgba(255, 82, 82, 0.15)'
            ))

        fig.add_vline(
            x=price, line_dash="dash", line_color="#ffffff",
            annotation_text=f"<b>Preço Atual: US$ {price:,.2f}</b>",
            annotation_position="top right",
            annotation_font=dict(color="#ffffff", size=12)
        )

        fig.update_layout(
            title=dict(text=f"Profundidade do Book L2 (Real) — {selected_symbol}", font=dict(color="white")),
            template="plotly_dark", paper_bgcolor="#0b0e14", plot_bgcolor="#0b0e14",
            height=700,
            xaxis=dict(title="Preço (US$)", gridcolor="rgba(255,255,255,0.05)"),
            yaxis=dict(title="Volume Acumulado (Size)", gridcolor="rgba(255,255,255,0.05)"),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )

        st.plotly_chart(fig, use_container_width=True)

# =====================================================================
# PÁGINA 2: MONITOR DE ATIVOS & OPEN INTEREST
# =====================================================================
elif pagina == "🌐 Monitor de Ativos & Open Interest":
    st.title("🌐 Monitor de Mercado Multiativos (Dados Oficiais)")
    st.markdown("Consulta em tempo real de preços e interesse em aberto diretamente na API da Hyperliquid[cite: 1].")

    ativos = ["BTC", "ETH", "SOL", "XRP", "SUI", "AVAX", "DOGE", "NEAR"]
    
    tabela_dados = []
    for a in ativos:
        p, o, prev, _, _ = get_hyperliquid_live_data(a)
        chg = ((p - prev) / prev) * 100 if prev > 0 else 0.0
        
        tabela_dados.append({
            "Ativo": a,
            "Preço Mark (US$)": f"${p:,.2f}" if p > 0 else "Indisponível",
            "Variação 24h": f"{chg:+.2f}%" if p > 0 else "N/A",
            "Open Interest (Contratos)": f"{o:,.2f}" if o > 0 else "N/A"
        })

    df_monitor = pd.DataFrame(tabela_dados)
    st.dataframe(df_monitor, use_container_width=True, hide_index=True)
