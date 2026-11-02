# ==========================================
# PÁGINA 1: CAPTURA & ROMPIMENTOS (DINÂMICO POR ATIVO)
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
        sym = st.selectbox("Ativo em Análise:", ["BTC", "ETH", "SOL", "XRP", "SUI"], index=0)
    with col_tf:
        st.markdown("**Modo de Janela:** `1 Dia / 1 Semana`")
    
    # Busca o preço real da API para o ativo selecionado
    price, _ = get_hyperliquid_data(sym)
    
    col_1d, col_1w = st.columns(2)
    
    with col_1d:
        st.markdown("#### 1 dia <span style='font-size:12px; color:#9ca3af;'>posições abertas nas últimas 24 h</span>", unsafe_allow_html=True)
        st.error("▼ **72% captura abaixo primeiro em 1 dia**\nzona 2.250–2.264 | ▲ 28% | nenhuma <1%")
        st.caption(f"Binance - faixa ±50% · US$ (est.) · 📈 **lateral 64%** · Ativo: {sym}")
        
        def make_chart_1d(base_price):
            np.random.seed(24)
            # Cria a escala de preços dinamicamente centrada no preço real do ativo (-30% a +30%)
            prices = np.linspace(base_price * 0.70, base_price * 1.30, 50)
            longs = [np.random.uniform(5, 45) if p < base_price else 0 for p in prices]
            shorts = [np.random.uniform(5, 50) if p > base_price else 0 for p in prices]
            
            fig = go.Figure()
            fig.add_trace(go.Bar(x=prices, y=longs, marker_color="#1E88E5", name="Longs"))
            fig.add_trace(go.Bar(x=prices, y=shorts, marker_color="#FF7043", name="Shorts"))
            fig.add_vline(x=base_price, line_dash="dash", line_color="white")
            fig.add_annotation(x=base_price, y=55, text=f"agora {base_price:,.1f}", showarrow=False, font=dict(color="white"))
            
            fig.update_layout(
                template="plotly_dark", paper_bgcolor="#0c0e12", plot_bgcolor="#0c0e12",
                height=360, margin=dict(t=20, b=20, l=30, r=30), showlegend=False,
                xaxis=dict(gridcolor="rgba(255,255,255,0.05)", tickformat=",.0f"),
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
        st.caption(f"Binance - faixa ±50% · US$ (est.) · 📈 **lateral 64%** · Ativo: {sym}")
        
        def make_chart_1w(base_price):
            np.random.seed(168)
            # Cria a escala dinâmica para 1 semana
            prices = np.linspace(base_price * 0.70, base_price * 1.30, 50)
            longs = [np.random.uniform(10, 80) if p < base_price else 0 for p in prices]
            shorts = [np.random.uniform(10, 95) if p > base_price else 0 for p in prices]
            
            fig = go.Figure()
            fig.add_trace(go.Bar(x=prices, y=longs, marker_color="#1E88E5", name="Longs"))
            fig.add_trace(go.Bar(x=prices, y=shorts, marker_color="#00C853", name="Shorts"))
            fig.add_vline(x=base_price, line_dash="dash", line_color="white")
            fig.add_annotation(x=base_price, y=100, text=f"agora {base_price:,.1f}", showarrow=False, font=dict(color="white"))
            
            fig.update_layout(
                template="plotly_dark", paper_bgcolor="#0c0e12", plot_bgcolor="#0c0e12",
                height=360, margin=dict(t=20, b=20, l=30, r=30), showlegend=False,
                xaxis=dict(gridcolor="rgba(255,255,255,0.05)", tickformat=",.0f"),
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
        st.success(f"▲ **Resistência Principal**\n\n*Zona mapeada acima de {price * 1.03:,.1f} para o ativo {sym}*")
    with col_r2:
        st.markdown("**ABAIXO · ZONA DE VÁCUO CRÍTICA**")
        st.error(f"▼ **Suporte / Vácuo**\n\n*Abaixo de {price * 0.97:,.1f} o preço pode acelerar no ativo {sym}*")
