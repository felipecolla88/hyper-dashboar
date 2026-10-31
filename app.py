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
        {"Grupo": "Camarão (Shrimp)", "Saldo": "< $250", "Carteiras": "802,372", "Em Posição": "47,967 (5.98%)", "Long": "$464.91 M", "Short": "$182.56 M", "Total": "$647.47 M", "Lucro": "23,648", "Prejuizo": "26,775", "Bias": "Otimista"},
        {"Grupo": "Peixe (Fish)", "Saldo": "$250 a $10K", "Carteiras": "44,702", "Em Posição": "30,238 (67.65%)", "Long": "$289.07 M", "Short": "$96.46 M", "Total": "$385.54 M", "Lucro": "11,336", "Prejuizo": "12,079", "Bias": "Muito Otimista"},
        {"Grupo": "Golfinho (Dolphin)", "Saldo": "$10K a $50K", "Carteiras": "7,450", "Em Posição": "5,726 (76.86%)", "Long": "$447.65 M", "Short": "$195.79 M", "Total": "$643.44 M", "Lucro": "2,279", "Prejuizo": "2,755", "Bias": "Muito Otimista"},
        {"Grupo": "Predador Alfa (Apex Predator)", "Saldo": "$50K a $100K", "Carteiras": "1,607", "Em Posição": "1,241 (77.23%)", "Long": "$287.73 M", "Short": "$162.18 M", "Total": "$449.91 M", "Lucro": "521", "Prejuizo": "590", "Bias": "Otimista"},
        {"Grupo": "Pequena Baleia (Small Whale)", "Saldo": "$100K a $500K", "Carteiras": "1,818", "Em Posição": "1,469 (80.81%)", "Long": "$842.46 M", "Short": "$581.54 M", "Total": "$1.42 B", "Lucro": "412", "Prejuizo": "725", "Bias": "Otimista"},
        {"Grupo": "Baleia (Whale)", "Saldo": "$500K a $1M", "Carteiras": "374", "Em Posição": "316 (84.5%)", "Long": "$479.59 M", "Short": "$589.56 M", "Total": "$1.07 B", "Lucro": "143",
