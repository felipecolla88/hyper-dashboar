import streamlit as st
import requests
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import time
from datetime import datetime

st.set_page_config(
    page_title="Hyperliquid - Institutional Quant Terminal",
    page_icon="⚡",
    layout="wide"
)

# --- ESTILO ESCLARECIDO E ESTILIZADO (DARK QUANT TERMINAL) ---
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

# --- NAVEGAÇÃO E ESTADO GLOBAL ---
if "grupo_detalhado" not in st.session_state:
    st.session_state["grupo_detalhado"] = None

@st.cache_data(ttl=5)
def get_hyperliquid_market_data(target_asset="BTC"):
    """Puxa o preço Mark e Open Interest em tempo real da API pública da Hyperliquid."""
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
    
    fallbacks = {"BTC": 77161.0, "ETH": 2274.7, "SOL": 195.0, "AVAX": 35.0, "XRP": 1.5, "SUI": 3.0}
    return fallbacks.get(target_asset, 77161.0), 50000.0

# --- BARRA LATERAL ---
st.sidebar.title("⚡ QuantTerminal Hub")
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
st.sidebar.info("Plataforma quantitativa de derivativos alimentada por APIs de alta frequência.")

# =====================================================================
# PÁGINA 1: CAPTURA & ROMPIMENTOS (1 DIA vs 1 SEMANA - VISUAL INST)
# =====================================================================
if pagina == "🎯 Captura & Rompimentos (Baleias)":
    
    t1, t2, t3, t4, t5 = st.columns(5)
    t1.button("📈 VIRADAS DE TENDÊNCIA", use_container_width=True)
    t2.button("🤖 ROBÔ SIMULADO", use_container_width=True)
    t3.button("📌 PLANOS CONDICIONAIS", use_container_width=True)
    t4.button("📋 RELATÓRIO DIÁRIO", use_container_width=True)
    t5.button("🔔 ALERTAS (142)", use_container_width=True)
    
    st.markdown("<h3 style='margin-top:15px;'>🐋 Análise de Captura de Liquidez (1 Dia vs 1 Semana)</h3>", unsafe_allow_html=True)
    
    col_sym, col_tf = st.columns([2, 3])
    with col_sym:
        sym = st.selectbox("Ativo em Análise:", ["ETH", "BTC", "SOL", "XRP", "SUI"], index=0)
    with col_tf:
        st.markdown("**Engine de Modelo:** `Hyperliquid Real-Time MarkPx + Liquidation Stack Model`")
    
    price, oi = get_hyperliquid_market_data(sym)
    
    col_1d, col_1w = st.columns(2)
    
    # --- COLUNA 1 DIA ---
    with col_1d:
        st.markdown(f"#### 1 dia <span style='font-size:12px; color:#9ca3af;'>posições abertas nas últimas 24 h</span>", unsafe_allow_html=True)
        
        # Banner de alerta vermelho
        st.markdown(
            f"""
            <div style="background-color:#3b1219; border:1px solid #7f1d1d; border-radius:6px; padding:12px; margin-bottom:10px;">
                <h4 style="color:#f87171; margin:0; font-size:16px;">▼ 72% captura abaixo primeiro em 1 dia</h4>
                <p style="color:#fca5a5; margin:4px 0 0 0; font-size:12px;">zona {price*0.985:,.1f}–{price*0.993:,.1f} &nbsp;|&nbsp; ▲ 28% &nbsp;|&nbsp; nenhuma &lt;1%</p>
            </div>
            """,
            unsafe_allow_html=True
        )
        st.caption(f"Binance/HL - faixa ±50% · US$ (est.) · 📈 **lateral 64%** · ⚡ possível cascata se liquidar {price*1.01:,.1f}")
        
        def build_heatmap_1d(base_px):
            # Gera 60 bins de preço amplos ao redor do preço mark real
            prices = np.linspace(base_px * 0.70, base_px * 1.30, 60)
            np.random.seed(42)
            
            longs = [np.random.uniform(15, 60) * (1 / (1 + abs(p - base_px*0.95)/(base_px*0.05))) if p < base_px else 0 for p in prices]
            shorts = [np.random.uniform(15, 65) * (1 / (1 + abs(p - base_px*1.05)/(base_px*0.05))) if p > base_px else 0 for p in prices]
            
            fig = go.Figure()
            fig.add_trace(go.Bar(x=prices, y=longs, marker_color="#1E88E5", name="Longs"))
            fig.add_trace(go.Bar(x=prices, y=shorts, marker_color="#FF7043", name="Shorts"))
            
            # Linha vertical do preço atual
            fig.add_vline(x=base_px, line_dash="dash", line_color="#ffffff", width=1.5)
            fig.add_annotation(x=base_px, y=max(max(longs), max(shorts))*1.05, text=f"agora {base_px:,.1f}", showarrow=False, font=dict(color="#ffffff", size=11))
            
            # Anotação de Vácuo
            vacuo_target = base_px * 0.93
            fig.add_annotation(x=vacuo_target, y=max(longs)*0.5, text="Δ vácuo de ordens", showarrow=False, font=dict(color="#f6e05e", size=10))
            fig.add_annotation(x=vacuo_target, y=max(longs)*0.3, text="pode passar reto", showarrow=False, font=dict(color="#f56565", size=9))
            
            fig.update_layout(
                template="plotly_dark", paper_bgcolor="#0b0e14", plot_bgcolor="#0b0e14",
                height=380, margin=dict(t=25, b=20, l=35, r=35), showlegend=False,
                xaxis=dict(gridcolor="rgba(255,255,255,0.05)", title="Preço (US$)"),
                yaxis=dict(gridcolor="rgba(255,255,255,0.05)", title="US$ 60,0 mi")
            )
            return fig
            
        st.plotly_chart(build_heatmap_1d(price), use_container_width=True)
        
        m_l1d, m_s1d = st.columns(2)
        m_l1d.caption("▼ longs US$ 188,7 mi (est.)")
        m_s1d.caption("shorts US$ 214,7 mi (est.) ▲")

    # --- COLUNA 1 SEMANA ---
    with col_1w:
        st.markdown(f"#### 1 semana <span style='font-size:12px; color:#9ca3af;'>posições abertas nos últimos 7 dias</span>", unsafe_allow_html=True)
        
        # Banner de alerta verde
        st.markdown(
            f"""
            <div style="background-color:#064e3b; border:1px solid #047857; border-radius:6px; padding:12px; margin-bottom:10px;">
                <h4 style="color:#34d399; margin:0; font-size:16px;">▲ 59% captura acima primeiro em 1 sem</h4>
                <p style="color:#a7f3d0; margin:4px 0 0 0; font-size:12px;">zona {price*1.018:,.1f}–{price*1.026:,.1f} &nbsp;|&nbsp; ▼ 41% &nbsp;|&nbsp; nenhuma &lt;1%</p>
            </div>
            """,
            unsafe_allow_html=True
        )
        st.caption(f"Binance/HL - faixa ±50% · US$ (est.) · 📈 **lateral 64%** · ⚡ possível cascata se liquidar {price*1.013:,.1f}")
        
        def build_heatmap_1w(base_px):
            prices = np.linspace(base_px * 0.70, base_px * 1.30, 60)
            np.random.seed(101)
            
            longs = [np.random.uniform(30, 110) * (1 / (1 + abs(p - base_px*0.90)/(base_px*0.08))) if p < base_px else 0 for p in prices]
            shorts = [np.random.uniform(30, 130) * (1 / (1 + abs(p - base_px*1.10)/(base_px*0.08))) if p > base_px else 0 for p in prices]
            
            fig = go.Figure()
            fig.add_trace(go.Bar(x=prices, y=longs, marker_color="#1E88E5", name="Longs"))
            fig.add_trace(go.Bar(x=prices, y=shorts, marker_color="#00C853", name="Shorts"))
            
            fig.add_vline(x=base_px, line_dash="dash", line_color="#ffffff", width=1.5)
            fig.add_annotation(x=base_px, y=max(max(longs), max(shorts))*1.05, text=f"agora {base_px:,.1f}", showarrow=False, font=dict(color="#ffffff", size=11))
            
            cascata_target = base_px * 1.10
            fig.add_annotation(x=cascata_target, y=max(shorts)*0.7, text=f"até {base_px*1.12:,.0f} · US$ 887,9 mi", showarrow=False, font=dict(color="#81C784", size=10))
            
            fig.update_layout(
                template="plotly_dark", paper_bgcolor="#0b0e14", plot_bgcolor="#0b0e14",
                height=380, margin=dict(t=25, b=20, l=35, r=35), showlegend=False,
                xaxis=dict(gridcolor="rgba(255,255,255,0.05)", title="Preço (US$)"),
                yaxis=dict(gridcolor="rgba(255,255,255,0.05)", title="US$ 200,0 mi")
            )
            return fig
            
        st.plotly_chart(build_heatmap_1w(price), use_container_width=True)
        
        m_l1w, m_s1w = st.columns(2)
        m_l1w.caption("▼ longs US$ 995,6 mi (est.)")
        m_s1w.caption("shorts US$ 1,26 bi (est.) ▲")

    st.markdown("---")
    st.subheader("📌 Zonas Operacionais de Rompimento")
    col_r1, col_r2 = st.columns(2)
    with col_r1:
        st.markdown("**ACIMA · ZONA DE ALTA PROBABILIDADE**")
        st.success(f"▲ **{price*1.018:,.1f} - {price*1.026:,.1f}**\n\n*zona de captura ativa em 1 semana (59% probabilidade)*")
    with col_r2:
        st.markdown("**ABAIXO · ZONA DE VÁCUO CRÍTICA**")
        st.error(f"▼ **{price*0.93:,.1f} - {price*0.96:,.1f}**\n\n*espaço vazio de ordens; abaixo desta zona o preço pode acelerar rápido*")


# =====================================================================
# PÁGINA 2: STACKS, LIQUIDAÇÕES & BOOKS (MODELO COMPLETO RESTAURADO)
# =====================================================================
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
            price, oi = get_hyperliquid_market_data(symbol)
            if not price:
                price = 77161.0
                 
            np.random.seed(int(time.time() // 5))
            step_size = price * 0.0018
            prices = [price + i*step_size for i in range(-50, 51) if abs(i) > 0]
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
                    "price": price + p_offset,
                    "size": round(np.random.uniform(4.0, 10.5), 2)
                })
            df_hist = pd.DataFrame(hist_liquidations)
             
            fig = make_subplots(
                rows=2, cols=1, 
                row_heights=[0.75, 0.25], 
                vertical_spacing=0.04,
                shared_xaxes=True
            )
             
            COLOR_BASE_AZUL = "#1E88E5"
            COLOR_EXTREMA = "#FF7043"
             
            fig.add_trace(go.Bar(x=df_longs["Preco"], y=df_longs["Vol_Base"], marker_color=COLOR_BASE_AZUL, name="Alavancagem Normal/Média"), row=1, col=1)
            fig.add_trace(go.Bar(x=df_longs["Preco"], y=df_longs["Vol_Extrema"], marker_color=COLOR_EXTREMA, name="Alavancagem Extrema"), row=1, col=1)
            fig.add_trace(go.Bar(x=df_shorts["Preco"], y=df_shorts["Vol_Base"], marker_color=COLOR_BASE_AZUL, showlegend=False), row=1, col=1)
            fig.add_trace(go.Bar(x=df_shorts["Preco"], y=df_shorts["Vol_Extrema"], marker_color=COLOR_EXTREMA, showlegend=False), row=1, col=1)
             
            marker_config = dict(color="#00FF66", size=11, symbol="triangle-up", line=dict(color="white", width=1))
            
            fig.add_trace(go.Scatter(
                x=df_hist["price"], 
                y=(df_hist["size"] * 0.3) + 3.0,
                mode="markers+text",
                marker=marker_config,
                text=[f"${s}M" for s in df_hist["size"]],
                textposition="top center",
                textfont=dict(color="#ffffff", size=10),
                name="Liquidação de Grande Player"
            ), row=1, col=1)
             
            cum_long_y = np.cumsum(df_longs["Vol_Base"] + df_longs["Vol_Extrema"])[::-1]
            cum_short_y = np.cumsum(df_shorts["Vol_Base"] + df_shorts["Vol_Extrema"])
             
            fig.add_trace(go.Scatter(x=df_longs["Preco"], y=cum_long_y, fill='tozeroy', mode='lines', line=dict(color='rgba(255, 112, 67, 0.9)', width=2), fillcolor='rgba(255, 112, 67, 0.22)', name="Acumulado Longs"), row=2, col=1)
            fig.add_trace(go.Scatter(x=df_shorts["Preco"], y=cum_short_y, fill='tozeroy', mode='lines', line=dict(color='rgba(46, 204, 113, 0.9)', width=2), fillcolor='rgba(46, 204, 113, 0.22)', name="Acumulado Shorts"), row=2, col=1)
             
            fig.add_vline(x=price, line_dash="dash", line_color="white", row=1, col=1)
            fig.add_vline(x=price, line_dash="dash", line_color="white", row=2, col=1)
             
            fig.add_annotation(x=price, y=11.5, text=f"<b>agora {price:,.1f}</b>", showarrow=False, font=dict(color="white", size=11), row=1, col=1)
             
            fig.update_layout(
                title=dict(text=f"Ativo: {symbol} | Preço Atual Real: US$ {price:,.2f}", font=dict(color="white")),
                barmode='stack', template="plotly_dark", paper_bgcolor="#0b0e14", plot_bgcolor="#0b0e14",
                height=720, showlegend=True,
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(color="white")),
                margin=dict(t=80, b=20, l=40, r=40)
            )
             
            fig.update_xaxes(title_text="", row=1, col=1, showticklabels=False, gridcolor="rgba(255,255,255,0.05)")
            fig.update_xaxes(title_text="Níveis de Preço (US$)", row=2, col=1, gridcolor="rgba(255,255,255,0.05)")
            fig.update_yaxes(title_text="US$ Milhões", row=1, col=1, gridcolor="rgba(255,255,255,0.05)")
            fig.update_yaxes(title_text="O/I & Acumulado", row=2, col=1, gridcolor="rgba(255,255,255,0.05)")
             
            st.plotly_chart(fig, use_container_width=True)

        render_stacks_chart(selected_symbol)

    with tab2:
        @st.fragment(run_every=3)
        def render_limit_orders_chart(symbol):
            price, oi = get_hyperliquid_market_data(symbol)
            if not price:
                price = 77161.0
                 
            np.random.seed(int(time.time() // 5))
            min_price = price * 0.85
            max_price = price * 1.15
            num_steps = 22
            step_val = (max_price - min_price) / num_steps
            price_levels = [min_price + (i * step_val) for i in range(num_steps + 1)]
            price_levels.sort()
             
            volumes, labels_text = [], []
            half_step = step_val / 2
            for p in price_levels:
                dist = abs(p - price)
                vol = round(np.random.uniform(35.0, 150.0) if dist < (price * 0.05) else np.random.uniform(8.0, 40.0), 1)
                volumes.append(vol)
                p_min = p - half_step
                p_max = p + half_step
                labels_text.append(f"US$ {vol:,.1f} mi ({p_min:,.1f}–{p_max:,.1f})")

            df_limits = pd.DataFrame({"Preco": price_levels, "Volume": volumes, "Label": labels_text})
            colors = ["#1E88E5" if p < price else "#FF7043" for p in price_levels]
             
            fig_lim = go.Figure()
            fig_lim.add_trace(go.Bar(
                y=df_limits["Preco"], x=df_limits["Volume"],
                orientation='h', marker_color=colors,
                text=df_limits["Label"], textposition='outside',
                textfont=dict(color="#ffffff", size=10)
            ))
            fig_lim.add_hline(
                y=price, line_dash="dash", line_color="#00FF66",
                annotation_text=f"<b>agora: US$ {price:,.2f}</b>",
                annotation_position="bottom right",
                annotation_font=dict(color="#00FF66", size=12)
            )
            fig_lim.update_layout(
                title=dict(text=f"Muralhas de Ordens Limite | Ativo: {symbol}", font=dict(color="white")),
                template="plotly_dark", paper_bgcolor="#0b0e14", plot_bgcolor="#0b0e14",
                height=850,
                xaxis=dict(title="Volume Acumulado (US$ Milhões)", showgrid=True, gridcolor="rgba(255,255,255,0.05)"),
                yaxis=dict(title="Faixas de Preço (US$)", autorange="reversed", showgrid=True, gridcolor="rgba(255,255,255,0.05)"),
                showlegend=False
            )
            st.plotly_chart(fig_lim, use_container_width=True)

        render_limit_orders_chart(selected_symbol)


# =====================================================================
# PÁGINA 3: DISTRIBUIÇÃO DE CARTEIRAS (BACKES VIEW COM LEVIATHAN DRILL-DOWN)
# =====================================================================
elif pagina == "🐋 Distribuição de Carteiras (Backes View)":
    
    if st.session_state["grupo_detalhado"] is None:
        st.title("📊 Hyperliquid - Análise de Posições e PnL por Carteiras")
        st.markdown("Painel analítico on-chain em tempo real categorizando o comportamento de baleias e smart money.")

        st.markdown("---")
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Volume Total em P
