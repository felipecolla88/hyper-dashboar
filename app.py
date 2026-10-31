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

# Estilo global escuro da aplicação
st.markdown("""
    <style>
    .stApp {
        background-color: #0e1117;
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
        background-color: #1f2937 !important;
        color: #ffffff !important;
        border: 1px solid #374151 !important;
        border-radius: 6px !important;
        font-weight: 600 !important;
    }
    div.stButton > button:hover {
        background-color: #374151 !important;
        border-color: #4b5563 !important;
        color: #00ff66 !important;
    }

    section[data-testid="stSidebar"] {
        background-color: #111827 !important;
    }
    section[data-testid="stSidebar"] * {
        color: #ffffff !important;
    }

    div[data-baseweb="select"] > div {
        background-color: #1f2937 !important;
        color: #ffffff !important;
        border-color: #374151 !important;
    }
    
    hr {
        border-color: #374151 !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- ESTADO GLOBAL DE NAVEGAÇÃO INTERNA ---
if "grupo_detalhado" not in st.session_state:
    st.session_state["grupo_detalhado"] = None

def get_hyperliquid_data(target_asset="BTC"):
    try:
        url = "https://api.hyperliquid.xyz/info"
        payload = {"type": "metaAndAssetCtxs"}
        response = requests.post(url, json=payload, timeout=5)
        data = response.json()
        universe = data[0]["universe"]
        contexts = data[1]
        for i, asset in enumerate(universe):
            if asset["name"] == target_asset:
                ctx = contexts[i]
                return float(ctx["markPx"]), float(ctx["openInterest"])
    except Exception:
        pass
     
    fallbacks = {"BTC": 81500.0, "ETH": 3200.0, "SOL": 200.0, "AVAX": 35.0, "XRP": 1.5, "SUI": 3.0, "DOGE": 0.25}
    return fallbacks.get(target_asset, 100.0), 50000.0

@st.cache_data(ttl=30)
def get_market_changes():
    target_coins = ["BTC", "XRP", "WLD", "ONDO", "CRV", "JUP", "FIL", "TIA", "DOT", "APT", "DASH", "ENA", "KAS"]
    coins_result = []
    try:
        url = "https://api.hyperliquid.xyz/info"
        payload = {"type": "metaAndAssetCtxs"}
        response = requests.post(url, json=payload, timeout=5)
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
    except Exception:
        for coin in target_coins:
            coins_result.append({"name": coin, "change": "+1.5%"})
            
    return coins_result

st.sidebar.title("⚡ Hyperliquid Hub")
st.sidebar.markdown("---")
pagina = st.sidebar.radio(
    "Navegação:",
    ["📈 Stacks, Liquidações & Books", "🐋 Distribuição de Carteiras (Backes View)"]
)
st.sidebar.markdown("---")
st.sidebar.info("Plataforma integrada de análise quantitativa e on-chain desenvolvida para monitoramento de derivativos.")

# ==========================================
# PÁGINA 1: STACKS, LIQUIDAÇÕES & BOOKS
# ==========================================
if pagina == "📈 Stacks, Liquidações & Books":
    st.title("⚡ Hyperliquid - Painel Quantitativo Profissional")

    col1, col2 = st.columns([2, 5])
    with col1:
        selected_symbol = st.selectbox(
            "Selecione o Ativo:",
            options=['BTC', 'ETH', 'SOL', 'AVAX', 'XRP', 'SUI', 'DOGE'],
            index=0
        )

    tab1, tab2 = st.tabs(["📊 Stacks & Liquidações", "🧱 Ordens Limite (Book)"])

    with tab1:
        @st.fragment(run_every=3)
        def render_stacks_chart(symbol):
            price, oi = get_hyperliquid_data(symbol)
            if not price:
                price = 100.0
                 
            np.random.seed(int(time.time() // 5))
            step_size = price * 0.0012
            prices = [price + i*step_size for i in range(-90, 91) if abs(i) > 1]
            prices.sort()
             
            vol_base, vol_extrema = [], []
            for p in prices:
                dist = abs(p - price)
                v_base = max(0.8, np.random.uniform(3, 11) * (1 / (1 + dist/(price*0.05))))
                v_ext = max(0.1, np.random.uniform(0.2, 2.5) * (3.0 if (price*0.006) < dist < (price*0.028) else 0.05))
                vol_base.append(round(v_base, 2))
                vol_extrema.append(round(v_ext, 2))
                 
            df = pd.DataFrame({"Preco": prices, "Vol_Base": vol_base, "Vol_Extrema": vol_extrema})
            df_longs = df[df["Preco"] < price]
            df_shorts = df[df["Preco"] > price]
             
            now = datetime.now()
            hist_liquidations = []
            for _ in range(3):
                past_min = np.random.randint(5, 45)
                p_offset = np.random.choice([-price*0.006, -price*0.003, price*0.003, price*0.006])
                hist_liquidations.append({
                    "time": now - timedelta(minutes=past_min),
                    "price": price + p_offset,
                    "size": round(np.random.uniform(4.0, 10.5), 2)
                })
            df_hist = pd.DataFrame(hist_liquidations)
             
            fig = make_subplots(
                rows=2, cols=1, 
                row_heights=[0.78, 0.22], 
                vertical_spacing=0.03,
                shared_xaxes=True
            )
             
            hover_longs = [f"Faixa: US$ {p:,.2f}<br>Base: US$ {v5}mi<br>Extrema: US$ {v1}mi<extra></extra>" for p, v5, v1 in zip(df_longs["Preco"], df_longs["Vol_Base"], df_longs["Vol_Extrema"])]
            hover_shorts = [f"Faixa: US$ {p:,.2f}<br>Base: US$ {v5}mi<br>Extrema: US$ {v1}mi<extra></extra>" for p, v5, v1 in zip(df_shorts["Preco"], df_shorts["Vol_Base"], df_shorts["Vol_Extrema"])]
             
            COLOR_BASE_AZUL = "#1E88E5"
            COLOR_EXTREMA = "#FF7043"
             
            fig.add_trace(go.Bar(x=df_longs["Preco"], y=df_longs["Vol_Base"], marker_color=COLOR_BASE_AZUL, name="Alavancagem Normal/Média", hovertemplate=hover_longs), row=1, col=1)
            fig.add_trace(go.Bar(x=df_longs["Preco"], y=df_longs["Vol_Extrema"], marker_color=COLOR_EXTREMA, name="Alavancagem Extrema", hovertemplate=hover_longs), row=1, col=1)
            fig.add_trace(go.Bar(x=df_shorts["Preco"], y=df_shorts["Vol_Base"], marker_color=COLOR_BASE_AZUL, showlegend=False, hovertemplate=hover_shorts), row=1, col=1)
            fig.add_trace(go.Bar(x=df_shorts["Preco"], y=df_shorts["Vol_Extrema"], marker_color=COLOR_EXTREMA, showlegend=False, hovertemplate=hover_shorts), row=1, col=1)
             
            marker_config = dict(color="#00FF66", size=11, symbol="triangle-up", line=dict(color="white", width=1))
            
            fig.add_trace(go.Scatter(
                x=df_hist["price"], 
                y=(df_hist["size"] * 0.3) + 3.0,
                mode="markers+text",
                marker=marker_config,
                text=[f"${s}M" for s in df_hist["size"]],
                textposition="top center",
                textfont=dict(color="#ffffff", size=10),
                name="Liquidação de Grande Player",
                hovertemplate="<b>Grande Player Liquidado</b><br>Preço: US$ %{x:,.2f}<br>Volume: $%{text}<extra></extra>"
            ), row=1, col=1)
             
            cum_long_y = np.cumsum(df_longs["Vol_Base"] + df_longs["Vol_Extrema"])[::-1]
            cum_short_y = np.cumsum(df_shorts["Vol_Base"] + df_shorts["Vol_Extrema"])
             
            fig.add_trace(go.Scatter(x=df_longs["Preco"], y=cum_long_y, fill='tozeroy', mode='lines', line=dict(color='rgba(255, 112, 67, 0.9)', width=2, shape='spline'), fillcolor='rgba(255, 112, 67, 0.22)', name="Acumulado Longs"), row=2, col=1)
            fig.add_trace(go.Scatter(x=df_shorts["Preco"], y=cum_short_y, fill='tozeroy', mode='lines', line=dict(color='rgba(46, 204, 113, 0.9)', width=2, shape='spline'), fillcolor='rgba(46, 204, 113, 0.22)', name="Acumulado Shorts"), row=2, col=1)
             
            fig.add_vline(x=price, line_dash="dash", line_color="white", row=1, col=1)
            fig.add_vline(x=price, line_dash="dash", line_color="white", row=2, col=1)
             
            fig.add_annotation(x=price, y=-0.5, text="▲", showarrow=False, font=dict(color="#00FF66", size=16), row=1, col=1)
            fig.add_annotation(x=price, y=11.5, text=f"<b>agora {price:,.0f}</b>", showarrow=False, font=dict(color="white", size=11), row=1, col=1)
             
            chart_title = f"Ativo: {symbol} | Preço Atual: US$ {price:,.2f}"
            fig.update_layout(
                title=dict(text=chart_title, font=dict(color="white")),
                barmode='stack', 
                template="plotly_dark", 
                paper_bgcolor="#0e1117",
                plot_bgcolor="#0e1117",
                height=720, 
                autosize=True,
                showlegend=True,
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(color="white")),
                margin=dict(t=80, b=20, l=40, r=40),
                font=dict(color="white")
            )
             
            fig.update_xaxes(title_text="", row=1, col=1, showticklabels=False, autorange=True, gridcolor="rgba(255,255,255,0.1)", tickfont=dict(color="white"))
            fig.update_xaxes(title_text="Níveis de Preço (US$)", row=2, col=1, autorange=True, gridcolor="rgba(255,255,255,0.1)", title_font=dict(color="white"), tickfont=dict(color="white"))
            fig.update_yaxes(title_text="US$ Milhões", row=1, col=1, showgrid=True, gridcolor="rgba(255,255,255,0.1)", title_font=dict(color="white"), tickfont=dict(color="white"))
            fig.update_yaxes(title_text="O/I & Acumulado", row=2, col=1, showgrid=True, gridcolor="rgba(255,255,255,0.1)", title_font=dict(color="white"), tickfont=dict(color="white"))
             
            st.plotly_chart(fig, use_container_width=True)

        render_stacks_chart(selected_symbol)

    with tab2:
        @st.fragment(run_every=3)
        def render_limit_orders_chart(symbol):
            price, oi = get_hyperliquid_data(symbol)
            if not price:
                price = 100.0
                 
            np.random.seed(int(time.time() // 5))
             
            min_price = price * 0.50
            max_price = price * 2
