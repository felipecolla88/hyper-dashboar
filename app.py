import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# --- GERENCIAMENTO DE ESTADO ---
if "grupo_detalhado" not in st.session_state:
    st.session_state["grupo_detalhado"] = None

# --- MODO 1: VISÃO GERAL (TABELA PRINCIPAL COM BOTÕES DE DRILL-DOWN) ---
if st.session_state["grupo_detalhado"] is None:
    st.title("🐋 Distribuição de Carteiras")
    st.write("Clique em um grupo para abrir o detalhamento completo:")
    
    # Exemplo de seleção de grupo simulando o clique na linha da tabela
    col_sel, _ = st.columns([3, 7])
    with col_sel:
        grupo_clicado = st.selectbox(
            "Selecionar Grupo de Carteira:",
            ["Shrimp", "Fish", "Dolphin", "Apex Predator", "Small Whale", "Whale", "Tidal Whale", "Leviathan"],
            index=7 # Padrão: Leviathan
        )
        if st.button(f"🔍 Inspecionar {grupo_clicado}", use_container_width=True):
            st.session_state["grupo_detalhado"] = grupo_clicado
            st.rerun()

# --- MODO 2: JANELA DE DETALHAMENTO DO GRUPO (ESTILO DASHBOARD LEVIATHAN) ---
else:
    grupo = st.session_state["grupo_detalhado"]
    
    # Botão de voltar no topo
    if st.button("← Voltar para Distribuição de Carteiras"):
        st.session_state["grupo_detalhado"] = None
        st.rerun()
        
    st.caption(f"Distribuição de posição da carteira Hyperliquid em tempo real / {grupo}")
    
    # Header Principal
    st.header(f"{grupo} <span style='font-size: 16px; color: #9ca3af;'>( $50M Para ∞ )</span>", anchor=False)
    st.markdown("**Wallets:** 86 &nbsp;&nbsp;|&nbsp;&nbsp; **Posição total:** $3.92B", unsafe_allow_html=True)
    
    # Barra de Traders Em Posição (73 Traders - 84.89%)
    st.progress(0.8489, text="73 Traders em Posição (84.89%)")
    
    # Métricas Long / Short / Lucro / Prejuízo em Colunas
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Posição Long", "$1.23B", delta="31.3%", delta_color="normal")
    m2.metric("Posição Short", "$2.69B", delta="-68.7%", delta_color="inverse")
    m3.metric("Lucro (Winners)", "44 Carteiras", delta="54.3%", delta_color="normal")
    m4.metric("Prejuízo (Losers)", "28 Carteiras", delta="-45.7%", delta_color="inverse")
    
    st.markdown("---")
    
    # 3 Painéis Lado a Lado
    col_rank, col_risco, col_ultimas = st.columns([1, 1, 1])
    
    with col_rank:
        st.subheader("Ranking de posição por ativo")
        df_rank = pd.DataFrame({
            "Ativo": ["BTC", "ETH", "HYPE", "ZEC", "SOL", "XRP"],
            "Long": ["$407.54M", "$247.93M", "$237.64M", "$45.57M", "$21.08M", "$47.18M"],
            "Short": ["$905.88M", "$552.32M", "$352.81M", "$193.10M", "$172.73M", "$61.63M"],
            "Total": ["$1.31B", "$800.25M", "$590.45M", "$238.67M", "$193.81M", "$108.81M"]
        })
        st.dataframe(df_rank, use_container_width=True, hide_index=True)
        
    with col_risco:
        st.subheader("Risco de liquidação por ativo")
        df_risco = pd.DataFrame({
            "Ativo": ["VVV", "BTC", "HYPE", "ETH", "SKY", "APT"],
            "% Risco": ["19.48%", "14.72%", "11.79%", "8.64%", "0.00%", "0.00%"],
            "Volume": ["$32.92M", "$1.31B", "$590.05M", "$800.26M", "$437.43K", "$1.15M"]
        })
        st.dataframe(df_risco, use_container_width=True, hide_index=True)
        
    with col_ultimas:
        st.subheader("Últimas posições")
        df_ultimas = pd.DataFrame({
            "Endereço": ["0x5b...c060", "0x5b...c060", "0xb8...6e36", "0xfc...9d9d", "0x08...ca88"],
            "Ativo": ["ETH", "BTC", "BTC", "BTC", "HYPE"],
            "PnL Atual": ["-$219.74M", "-$180.07M", "-$141.28M", "-$129.39M", "+$121.45M"]
        })
        st.dataframe(df_ultimas, use_container_width=True, hide_index=True)
        
    st.markdown("---")
    st.subheader(f"Endereço da carteira {grupo}")
    
    # Tabela detalhada de endereços individuais
    df_wallets = pd.DataFrame({
        "Endereço": ["0x5b8a...c060", "0xb8e3...6e36", "0xfc71...9d9d", "0x08a1...ca88"],
        "Margem": ["$136.01M", "$110.03M", "$98.45M", "$85.12M"],
        "Bias da Wallet": ["Muito bearish", "Muito bearish", "Bearish", "Muito bullish"],
        "Em posição": ["$610.72M", "$437.42M", "$380.15M", "$290.00M"],
        "UPNL": ["+$12.82M", "+$10.22M", "-$5.14M", "+$18.40M"],
        "Risco Liq": ["HYPE (6%)", "HYPE (11%)", "BTC (14%)", "ETH (3%)"],
        "Grupo PnL": ["Impressora de dinheiro", "Impressora de dinheiro", "Smart Money", "Impressora de dinheiro"]
    })
    st.dataframe(df_wallets, use_container_width=True, hide_index=True)
