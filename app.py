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
    page_title="Hyperliquid - Painel Quantitativo",
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

# Cabeçalho Principal e Seleção de Ativos
st.title("⚡ Hyperliquid - Painel Quantitativo Profissional")

col1, col2 = st.columns([2, 5])
with col1:
    selected_symbol = st.selectbox(
        "Selecione o Ativo:",
        options=['BTC', 'ETH', 'SOL', 'AVAX', 'XRP', 'SUI', 'DOGE'],
        index=0
    )

# Criação das Abas para separar as ferramentas
tab1, tab2 = st.tabs(["📊 Stacks & Liquidações", "🧱 Ordens Limite (Book)"])

# ==========================================
# ABA 1: STACKS & LIQUIDAÇÕES
# ==========================================
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

# ==========================================
# ABA 2: ORDENS LIMITE (Book Dinâmico: -50% a +100% do Preço Atual)
# ==========================================
with tab2:
    @st.fragment(run_every=3)
    def render_limit_orders_chart(symbol):
        price, oi = get_hyperliquid_data(symbol)
        if not price:
            price = 100.0
            
        np.random.seed(int(time.time() // 5))
        
        # Intervalo dinâmico: de 50% abaixo até 100% acima do preço atual
        min_price = price * 0.50
        max_price = price * 2.00
        
        # Divide em 20 faixas perfeitas para qualquer ativo (seja BTC a 80k ou ETH a 3k)
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
                range=[max_price + (step_val * 0.5), min_price - (step_val * 0.5)] # Adapta perfeitamente ao ativo selecionado
            ),
            margin=dict(t=80, b=40, l=60, r=80),
            showlegend=False
        )
        
        st.plotly_chart(fig_lim, use_container_width=True)

    render_limit_orders_chart(selected_symbol)
