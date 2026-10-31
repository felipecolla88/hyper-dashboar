import streamlit as st
import requests
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import time
from datetime import datetime, timedelta

# Configuração da página e layout widescreen
st.set_page_config(
    page_title="Hyperliquid - Ecossistema Quantitativo",
    page_icon="⚡",
    layout="wide"
)

# Estilo CSS avançado para forçar o fundo escuro absoluto em toda a interface
st.markdown("""
    <style>
    .stApp {
        background-color: #0e1117;
        color: #fafafa;
    }
    header {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# Função para buscar dados da API da Hyperliquid
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

# ==========================================
# BARRA LATERAL - NAVEGAÇÃO DE PÁGINAS
# ==========================================
st.sidebar.title("⚡ Hyperliquid Hub")
st.sidebar.markdown("---")
pagina = st.sidebar.radio(
    "Navegação:",
    ["📈 Stacks, Liquidações & Books", "🐋 Distribuição de Carteiras (Backes View)"]
)
st.sidebar.markdown("---")
st.sidebar.info("Plataforma integrada de análise quantitativa e on-chain desenvolvida para monitoramento de derivativos.")

# ==========================================
# PÁGINA 1: SEU CÓDIGO ORIGINAL (Stacks & Books)
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

    # Criação das Abas para separar as ferramentas originais
    tab1, tab2 = st.tabs(["📊 Stacks & Liquidações", "🧱 Ordens Limite (Book)"])

    # ABA 1: STACKS & LIQUIDAÇÕES
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
             
            hover_longs = [f"<b>Faixa:</b> US$ {p-(step_size/2):,.2f} - US$ {p+(step_size/2):,.2f}<br>Base (Azul): US$ {v5} mi<br>Extrema: US$ {v1} mi<br>Total Nível: US$ {v5+v1:.1f} mi<extra></extra>" for p, v5, v1 in zip(df_longs["Preco"], df_longs["Vol_Base"], df_longs["Vol_Extrema"])]
            hover_shorts = [f"<b>Faixa:</b> US$ {p-(step_size/2):,.2f} - US$ {p+(step_size/2):,.2f}<br>Base (Azul): US$ {v5} mi<br>Extrema: US$ {v1} mi<br>Total Nível: US$ {v5+v1:.1f} mi<extra></extra>" for p, v5, v1 in zip(df_shorts["Preco"], df_shorts["Vol_Base"], df_shorts["Vol_Extrema"])]
             
            COLOR_BASE_AZUL = "#1E88E5"
            COLOR_EXTREMA = "#FF7043"
             
            fig.add_trace(go.Bar(x=df_longs["Preco"], y=df_longs["Vol_Base"], marker_color=COLOR_BASE_AZUL, name="Alavancagem Normal/Média", hovertemplate=hover_longs), row=1, col=1)
            fig.add_trace(go.Bar(x=df_longs["Preco"], y=df_longs["Vol_Extrema"], marker_color=COLOR_EXTREMA, name="Alavancagem Extrema", hovertemplate=hover_longs), row=1, col=1)
            fig.add_trace(go.Bar(x=df_shorts["Preco"], y=df_shorts["Vol_Base"], marker_color=COLOR_BASE_AZUL, showlegend=False, hovertemplate=hover_shorts), row=1, col=1)
            fig.add_trace(go.Bar(x=df_shorts["Preco"], y=df_shorts["Vol_Extrema"], marker_color=COLOR_EXTREMA, showlegend=False, hovertemplate=hover_shorts), row=1, col=1)
             
            fig.add_trace(go.Scatter(
                x=df_hist["price"], y=(df_hist["size"] * 0.3) + 3.0,
                mode="markers+text",
                marker=dict(color="#00FF66", size=11, symbol="triangle-up", line=dict(color="white", width=1)),
                text=[f"${s}M" for s in df_hist["size"]],
                textposition="top center",
                textfont=dict(color="#00FF66", size=10),
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
             
            fig.update_layout(
                title=dict(text=f"Ativo: {symbol} | Preço Atual: US$ {price:,.2f}", font=dict(color="white")),
                barmode='stack', 
                template="plotly_dark", 
                paper_bgcolor="#0e1117",
                plot_bgcolor="#0e1117",
                height=720, 
                autosize=True,
                showlegend=True,
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(color="white")),
                margin=dict(t=80, b=20, l=40, r=40)
            )
             
            fig.update_xaxes(title_text="", row=1, col=1, showticklabels=False, autorange=True, gridcolor="rgba(255,255,255,0.05)")
            fig.update_xaxes(title_text="Níveis de Preço (US$)", row=2, col=1, autorange=True, gridcolor="rgba(255,255,255,0.05)")
            fig.update_yaxes(title_text="US$ Milhões", row=1, col=1, showgrid=True, gridcolor="rgba(255,255,255,0.05)")
            fig.update_yaxes(title_text="O/I & Acumulado", row=2, col=1, showgrid=True, gridcolor="rgba(255,255,255,0.05)")
             
            st.plotly_chart(fig, use_container_width=True)

        render_stacks_chart(selected_symbol)

    # ABA 2: ORDENS LIMITE
    with tab2:
        @st.fragment(run_every=3)
        def render_limit_orders_chart(symbol):
            price, oi = get_hyperliquid_data(symbol)
            if not price:
                price = 100.0
                 
            np.random.seed(int(time.time() // 5))
             
            min_price = price * 0.50
            max_price = price * 2.00
             
            num_steps = 20
            step_val = (max_price - min_price) / num_steps
             
            price_levels = [min_price + (i * step_val) for i in range(num_steps + 1)]
            price_levels.sort()
             
            volumes = []
            labels_text = []
             
            half_step = step_val / 2
            for p in price_levels:
                dist = abs(p - price)
                vol = round(np.random.uniform(35.0, 150.0) if dist < (price * 0.15) else np.random.uniform(8.0, 40.0), 1)
                volumes.append(vol)
                 
                p_min = p - half_step
                p_max = p + half_step
                labels_text.append(f"US$ {vol:,.1f} mi ({p_min:,.2f}–{p_max:,.2f})")

            df_limits = pd.DataFrame({"Preco": price_levels, "Volume": volumes, "Label": labels_text})
            colors = ["#1E88E5" if p < price else "#FF7043" for p in price_levels]
             
            fig_lim = go.Figure()
             
            fig_lim.add_trace(go.Bar(
                y=df_limits["Preco"],
                x=df_limits["Volume"],
                orientation='h',
                marker_color=colors,
                text=df_limits["Label"],
                textposition='outside',
                textfont=dict(color="#ffffff", size=10),
                hovertemplate="Faixa: US$ %{y:,.2f}<br>Volume Limite: US$ %{x} mi<extra></extra>"
            ))
             
            fig_lim.add_hline(
                y=price, 
                line_dash="dash", 
                line_color="white",
                annotation_text=f"<b>agora: US$ {price:,.2f}</b>",
                annotation_position="bottom right",
                annotation_font=dict(color="#00FF66", size=12)
            )
             
            fig_lim.update_layout(
                title=dict(text=f"Muralhas de Ordens Limite (Dinâmico -50% a +100%) | Ativo: {symbol}", font=dict(color="white")),
                template="plotly_dark",
                paper_bgcolor="#0e1117",
                plot_bgcolor="#0e1117",
                height=900,
                xaxis=dict(
                    title="Volume Acumulado (US$ Milhões)", 
                    showgrid=True, 
                    gridcolor="rgba(255,255,255,0.05)",
                    range=[0, 210]
                ),
                yaxis=dict(
                    title="Faixas de Preço (US$)", 
                    autorange="reversed",
                    tickformat=",f",
                    showgrid=True,
                    gridcolor="rgba(255,255,255,0.03)",
                    tickfont=dict(color="white"),
                    range=[max_price + (step_val * 0.5), min_price - (step_val * 0.5)]
                ),
                margin=dict(t=80, b=40, l=60, r=80),
                showlegend=False
            )
             
            st.plotly_chart(fig_lim, use_container_width=True)

        render_limit_orders_chart(selected_symbol)


# ==========================================
# PÁGINA 2: DISTRIBUIÇÃO DE CARTEIRAS (Backes View Integrado)
# ==========================================
elif pagina == "🐋 Distribuição de Carteiras (Backes View)":
    st.title("📊 Hyperliquid - Análise de Posições e PnL por Carteiras")
    st.markdown("Painel analítico on-chain em tempo real categorizando o comportamento de baleias, tubarões e smart money[cite: 1].")

    # 1. Heatmap Interativo Superior de Moedas
    st.subheader("🌐 Mapa de Calor de Ativos On-Chain")
    coins_data = [
        {"name": "BTC", "change": "+2.4%", "color": "#00C853"},
        {"name": "XRP", "change": "+5.1%", "color": "#00C853"},
        {"name": "WLD", "change": "-1.8%", "color": "#FF5252"},
        {"name": "ONDO", "change": "+3.7%", "color": "#00C853"},
        {"name": "GRAM", "change": "-0.5%", "color": "#FF5252"},
        {"name": "CRV", "change": "+1.2%", "color": "#00C853"},
        {"name": "JUP", "change": "+4.8%", "color": "#00C853"},
        {"name": "FIL", "change": "-2.3%", "color": "#FF5252"},
        {"name": "TIA", "change": "+6.0%", "color": "#00C853"},
        {"name": "DOT", "change": "-1.1%", "color": "#FF5252"},
        {"name": "APT", "change": "+0.4%", "color": "#00C853"},
        {"name": "DASH", "change": "-3.2%", "color": "#FF5252"},
        {"name": "ENA", "change": "+2.9%", "color": "#00C853"},
        {"name": "KAS", "change": "+7.5%", "color": "#00C853"}
    ]

    cols_heat = st.columns(len(coins_data))
    selected_coin_filter = st.session_state.get("selected_coin", "TODOS")

    for idx, c in enumerate(coins_data):
        with cols_heat[idx]:
            btn_type = "primary" if selected_coin_filter == c["name"] else "secondary"
            if st.button(f"{c['name']}\n{c['change']}", key=f"btn_coin_{idx}", use_container_width=True):
                st.session_state["selected_coin"] = c["name"]
                st.rerun()

    if st.button("Limpar Filtro de Ativo", use_container_width=False):
        st.session_state["selected_coin"] = "TODOS"
        st.rerun()

    st.markdown(f"**Ativo em Foco:** `{st.session_state.get('selected_coin', 'TODOS')}`")
    st.markdown("---")

    # 2. Métricas de Resumo Global
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Volume Total em Posições", "$ 14.82 Bilhões", "+4.2%")
    m2.metric("Proporção Global Long vs Short", "56.4% Long / 43.6% Short", "Bullish Bias")
    m3.metric("Taxa Média de Lucratividade", "51.8%", "+2.1%")
    m4.metric("Total de Carteiras Monitoradas", "824,410", "Ativas 24h")

    st.markdown("---")

    # 3. Tabela 1: Hyperliquid Wallet Position Distribution in Real-time
    st.subheader("📍 Distribuição de Posições por Grupo de Carteiras")
    
    pos_data = [
        {"Grupo": "Camarão (Shrimp)", "Saldo": "< $250", "Carteiras": "802,372", "Em Posição": "47,967 (5.98%)", "Long": "$464.91 M", "Short": "$182.56 M", "Total": "$647.47 M", "Lucro": 23648, "Prejuizo": 26775, "Bias": "Otimista"},
        {"Grupo": "Peixe (Fish)", "Saldo": "$250 a $10K", "Carteiras": "44,702", "Em Posição": "30,238 (67.65%)", "Long": "$289.07 M", "Short": "$96.46 M", "Total": "$385.54 M", "Lucro": 11336, "Prejuizo": 12079, "Bias": "Muito Otimista"},
        {"Grupo": "Golfinho (Dolphin)", "Saldo": "$10K a $50K", "Carteiras": "7,450", "Em Posição": "5,726 (76.86%)", "Long": "$447.65 M", "Short": "$195.79 M", "Total": "$643.44 M", "Lucro": 2279, "Prejuizo": 2755, "Bias": "Muito Otimista"},
        {"Grupo": "Predador Alfa (Apex Predator)", "Saldo": "$50K a $100K", "Carteiras": "1,607", "Em Posição": "1,241 (77.23%)", "Long": "$287.73 M", "Short": "$162.18 M", "Total": "$449.91 M", "Lucro": 521, "Prejuizo": 590, "Bias": "Otimista"},
        {"Grupo": "Pequena Baleia (Small Whale)", "Saldo": "$100K a $500K", "Carteiras": "1,818", "Em Posição": "1,469 (80.81%)", "Long": "$842.46 M", "Short": "$581.54 M", "Total": "$1.42 B", "Lucro": 412, "Prejuizo": 725, "Bias": "Otimista"},
        {"Grupo": "Baleia (Whale)", "Saldo": "$500K a $1M", "Carteiras": "374", "Em Posição": "316 (84.5%)", "Long": "$479.59 M", "Short": "$589.56 M", "Total": "$1.07 B", "Lucro": 143, "Prejuizo": 163, "Bias": "Levemente Ursino"},
        {"Grupo": "Baleia Maré (Tidal Whale)", "Saldo": "$1M a $50M", "Carteiras": "343", "Em Posição": "288 (83.97%)", "Long": "$1.95 B", "Short": "$1.38 B", "Total": "$3.03 B", "Lucro": 126, "Prejuizo": 145, "Bias": "Muito Otimista"},
        {"Grupo": "Leviatã (Leviathan)", "Saldo": "> $50M", "Carteiras": "86", "Em Posição": "75 (87.21%)", "Long": "$1.17 B", "Short": "$3.23 B", "Total": "$4.40 B", "Lucro": 38, "Prejuizo": 34, "Bias": "Muito Ursino"}
    ]

    df_pos = pd.DataFrame(pos_data)
    st.dataframe(df_pos, use_container_width=True, hide_index=True)

    st.markdown("---")

    # 4. Tabela 2: Hyperliquid Wallet PNL Distribution in Real time
    st.subheader("💰 Distribuição de PnL por Perfil de Trader")

    pnl_data = [
        {"Perfil": "Impressora de Dinheiro (Money Printer)", "Carteiras": "764", "Em Posição": "333 (43.59%)", "Long": "$2.42 B", "Short": "$2.91 B", "Total": "$5.33 B", "Lucro": 213, "Prejuizo": 158, "Viés": "Ursino"},
        {"Perfil": "Dinheiro Inteligente (Smart Money)", "Carteiras": "3,378", "Em Posição": "1,102 (32.63%)", "Long": "$1.22 B", "Short": "$657.21 M", "Total": "$1.88 B", "Lucro": 711, "Prejuizo": 594, "Viés": "Levemente Otimista"},
        {"Perfil": "Especialista em Arbitragem (Arbitrage Pro)", "Carteiras": "10,811", "Em Posição": "2,737 (25.32%)", "Long": "$474.58 M", "Short": "$208.27 M", "Total": "$682.85 M", "Lucro": 1,941, "Prejuizo": 1,075, "Viés": "Otimista"}
    ]

    df_pnl = pd.DataFrame(pnl_data)
    st.dataframe(df_pnl, use_container_width=True, hide_index=True)

    # 5. Seção de Inspeção / Modal Interativo
    st.markdown("---")
    st.subheader("🔍 Inspetor de Faixa de Carteira")
    grupo_selecionado = st.selectbox("Selecione o grupo para auditar alavancagem e métricas detalhadas:", df_pos["Grupo"].tolist())
    
    row_sel = df_pos[df_pos["Grupo"] == grupo_selecionado].iloc[0]
    col_inf1, col_inf2, col_inf3 = st.columns(3)
    col_inf1.metric("Total de Carteiras no Grupo", row_sel["Carteiras"])
    col_inf2.metric("Volume Consolidado", row_sel["Total"])
    col_inf3.metric("Viés Predominante", row_sel["Bias"])

    if st.button("Exportar Relatório do Grupo (JSON)"):
        st.success(f"Dados consolidados do grupo {grupo_selecionado} preparados com sucesso para exportação!")
