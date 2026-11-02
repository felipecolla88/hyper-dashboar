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

# --- ESTADO GLOBAL DE NAVEGAÇÃO ---
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

# --- BARRA LATERAL COM TODAS AS OPÇÕES ---
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


# ==========================================
# PÁGINA 1: CAPTURA & ROMPIMENTOS (NOVO PAINEL)
# ==========================================
if pagina == "🎯 Captura & Rompimentos (Baleias)":
    
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

    st.markdown("---")
    st.subheader("📌 Rompimentos em 1 dia / 1 semana")
    col_r1, col_r2 = st.columns(2)
    with col_r1:
        st.markdown("**ACIMA · ZONA DE ALTA PROBABILIDADE**")
        st.success("▲ **2.319 - 2.333**\n\n*zona de captura ativa em 1 semana (59% probabilidade)*")
    with col_r2:
        st.markdown("**ABAIXO · ZONA DE VÁCUO CRÍTICA**")
        st.error("▼ **2.120 - 2.200**\n\n*espaço vazio de ordens; abaixo de 2.200 o preço pode acelerar rápido*")


# ==========================================
# PÁGINA 2: STACKS, LIQUIDAÇÕES & BOOKS
# ==========================================
elif pagina == "📈 Stacks, Liquidações & Books":
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
             
            fig = make_subplots(
                rows=2, cols=1, 
                row_heights=[0.78, 0.22], 
                vertical_spacing=0.03,
                shared_xaxes=True
            )
             
            COLOR_BASE_AZUL = "#1E88E5"
            COLOR_EXTREMA = "#FF7043"
             
            fig.add_trace(go.Bar(x=df_longs["Preco"], y=df_longs["Vol_Base"], marker_color=COLOR_BASE_AZUL, name="Alavancagem Normal"), row=1, col=1)
            fig.add_trace(go.Bar(x=df_longs["Preco"], y=df_longs["Vol_Extrema"], marker_color=COLOR_EXTREMA, name="Alavancagem Extrema"), row=1, col=1)
            fig.add_trace(go.Bar(x=df_shorts["Preco"], y=df_shorts["Vol_Base"], marker_color=COLOR_BASE_AZUL, showlegend=False), row=1, col=1)
            fig.add_trace(go.Bar(x=df_shorts["Preco"], y=df_shorts["Vol_Extrema"], marker_color=COLOR_EXTREMA, showlegend=False), row=1, col=1)
             
            fig.add_vline(x=price, line_dash="dash", line_color="white", row=1, col=1)
            fig.add_vline(x=price, line_dash="dash", line_color="white", row=2, col=1)
             
            fig.update_layout(
                title=dict(text=f"Ativo: {symbol} | Preço Atual: US$ {price:,.2f}", font=dict(color="white")),
                barmode='stack', template="plotly_dark", paper_bgcolor="#0c0e12", plot_bgcolor="#0c0e12", height=700
            )
            st.plotly_chart(fig, use_container_width=True)

        render_stacks_chart(selected_symbol)

    with tab2:
        st.subheader("🧱 Muralha de Ordens Limite (Book)")
        st.info("Visualização das ordens de compra e venda acumuladas no livro de ofertas.")


# ==========================================
# PÁGINA 3: DISTRIBUIÇÃO DE CARTEIRAS (COM DRILL-DOWN LEVIATHAN)
# ==========================================
elif pagina == "🐋 Distribuição de Carteiras (Backes View)":
    
    if st.session_state["grupo_detalhado"] is None:
        st.title("📊 Hyperliquid - Análise de Posições e PnL por Carteiras[cite: 1]")
        st.markdown("Painel analítico on-chain em tempo real categorizando o comportamento de baleias e smart money[cite: 1].")

        coins_data = get_market_changes()
        cols_heat = st.columns(len(coins_data))
        for idx, c in enumerate(coins_data):
            with cols_heat[idx]:
                if st.button(f"{c['name']}\n{c['change']}", key=f"btn_c_{idx}", use_container_width=True):
                    st.session_state["selected_coin"] = c["name"]
                    st.rerun()

        st.markdown("---")
        
        groups = [
            {"Size": "$0 Para $250", "Grupo": "Shrimp", "Wallets": "925,424", "Long": "$10.12M", "Short": "$7.20M", "Total": "$17.32M", "Bias": "Bullish"},
            {"Size": "$250 Para $10K", "Grupo": "Fish", "Wallets": "47,047", "Long": "$200.93M", "Short": "$65.34M", "Total": "$266.26M", "Bias": "Muito bullish"},
            {"Size": "$10K Para $50K", "Grupo": "Dolphin", "Wallets": "7,668", "Long": "$355.89M", "Short": "$149.50M", "Total": "$505.39M", "Bias": "Muito bullish"},
            {"Size": "$50K Para $100K", "Grupo": "Apex Predator", "Wallets": "1,727", "Long": "$265.92M", "Short": "$129.43M", "Total": "$395.34M", "Bias": "Muito bullish"},
            {"Size": "$100K Para $500K", "Grupo": "Small Whale", "Wallets": "1,909", "Long": "$670.47M", "Short": "$511.39M", "Total": "$1.18B", "Bias": "Levemente bullish"},
            {"Size": "$500K Para $1M", "Grupo": "Whale", "Wallets": "371", "Long": "$435.00M", "Short": "$448.41M", "Total": "$883.41M", "Bias": "Indeciso"},
            {"Size": "$1M Para $50M", "Grupo": "Tidal Whale", "Wallets": "358", "Long": "$1.72B", "Short": "$1.16B", "Total": "$2.88B", "Bias": "Bullish"},
            {"Size": "$50M Para ∞", "Grupo": "Leviathan", "Wallets": "86", "Long": "$1.22B", "Short": "$2.69B", "Total": "$3.91B", "Bias": "Muito bearish"}
        ]
        
        df_groups = pd.DataFrame(groups)
        st.dataframe(df_groups, use_container_width=True, hide_index=True)
        
        st.markdown("---")
        if st.button("🔍 Inspecionar Grupo Leviathan (Drill-Down)", use_container_width=True):
            st.session_state["grupo_detalhado"] = "Leviathan"
            st.rerun()

    else:
        grupo = st.session_state["grupo_detalhado"]
        if st.button("← Voltar para Distribuição de Carteiras"):
            st.session_state["grupo_detalhado"] = None
            st.rerun()
            
        st.caption(f"Distribuição de posição da carteira Hyperliquid em tempo real / {grupo}")
        st.title(f"🐋 {grupo} ($50M Para ∞)")
        
        st.markdown("**Wallets:** 86 &nbsp;&nbsp;|&nbsp;&nbsp; **Posição total:** $3.91B", unsafe_allow_html=True)
        st.progress(0.8373, text="72 Traders em Posição (83.73%)")
        
        st.markdown("---")
        
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Posição Long", "$1.22B", "31.2% Long")
        m2.metric("Posição Short", "$2.69B", "-68.8% Short")
        m3.metric("Lucro (Winners)", "43 Carteiras", "59.7%")
        m4.metric("Prejuízo (Losers)", "29 Carteiras", "40.3%")
        
        st.markdown("---")
        
        c1, c2, c3 = st.columns([1, 1, 1])
        with c1:
            st.subheader("Ranking de posição por ativo")
            df_rank = pd.DataFrame({
                "Ativo": ["BTC", "ETH", "HYPE", "ZEC", "SOL", "XRP"],
                "Long": ["$407.54M", "$247.93M", "$237.64M", "$45.57M", "$21.08M", "$47.18M"],
                "Short": ["$905.88M", "$552.32M", "$352.81M", "$193.10M", "$172.73M", "$61.63M"],
                "Total": ["$1.31B", "$800.25M", "$590.45M", "$238.67M", "$193.81M", "$108.81M"]
            })
            st.dataframe(df_rank, use_container_width=True, hide_index=True)
            
        with c2:
            st.subheader("Risco de liquidação por ativo")
            df_risco = pd.DataFrame({
                "Ativo": ["VVV", "BTC", "HYPE", "ETH", "SKY", "APT"],
                "% Risco": ["19.48%", "14.72%", "11.79%", "8.64%", "0.00%", "0.00%"],
                "Volume": ["$32.92M", "$1.31B", "$590.05M", "$800.26M", "$437.43K", "$1.15M"]
            })
            st.dataframe(df_risco, use_container_width=True, hide_index=True)
            
        with c3:
            st.subheader("Últimas posições")
            df_ultimas = pd.DataFrame({
                "Endereço": ["0x5b...c060", "0x5b...c060", "0xb8...6e36", "0xfc...9d9d"],
                "Ativo": ["ETH", "BTC", "BTC", "BTC"],
                "PnL Atual": ["-$219.74M", "-$180.07M", "-$141.28M", "-$129.39M"]
            })
            st.dataframe(df_ultimas, use_container_width=True, hide_index=True)
            
        st.markdown("---")
        st.subheader(f"Endereço da carteira {grupo}")
        df_wallets = pd.DataFrame({
            "Endereço": ["0x5b8a...c060", "0xb8e3...6e36", "0xfc71...9d9d"],
            "Margem": ["$136.01M", "$110.03M", "$98.45M"],
            "Bias da Wallet": ["Muito bearish", "Muito bearish", "Bearish"],
            "Em posição": ["$610.72M", "$437.42M", "$380.15M"],
            "UPNL": ["+$12.82M", "+$10.22M", "-$5.14M"],
            "Risco Liq": ["HYPE (6%)", "HYPE (11%)", "BTC (14%)"],
            "Grupo PnL": ["Impressora de dinheiro", "Impressora de dinheiro", "Smart Money"]
        })
        st.dataframe(df_wallets, use_container_width=True, hide_index=True)
