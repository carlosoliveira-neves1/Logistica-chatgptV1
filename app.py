import streamlit as st
import pandas as pd
import plotly.express as px
import io

st.set_page_config(page_title="Sistema de Logística V2", layout="wide")

# CSS customizado para visual moderno
st.markdown("""
    <style>
    body {background: #f6f9fe;}
    .big-title {font-size:2.4rem; font-weight:800; color: #213d5b;}
    .subtitle {font-size:1.3rem; color: #556; margin-bottom:30px;}
    .kpi-card {background:#f7fafc; padding:1.5rem; border-radius:1.2rem; text-align:center; margin-bottom:1rem; box-shadow:0 0 14px #e3e5e9;}
    .kpi-number {font-size:2.1rem; color:#2b6cb0; font-weight:900;}
    .kpi-label {color:#666; font-size:1.1rem;}
    .sugestao-card {
        background: #fff; border-radius:1rem; box-shadow:0 0 10px #e3e6ed; 
        padding:1.1rem; margin-bottom:1.1rem;
        display:flex; flex-direction:row; align-items:center; gap:18px;
    }
    .cod {font-weight:700; background:#ebf8ff; border-radius:8px; padding:5px 10px; font-size:1.15rem;}
    .prod {font-size:1.12rem; font-weight:700;}
    .loja {color:#475; font-size:1rem; font-weight:700;}
    .destino {color:#2375e1; font-weight:700;}
    .transferir {font-size:1.15rem; color:#d97706; font-weight:900;}
    .mini {color:#999; font-size:.97rem;}
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="big-title">Sistema de Logística <span style="font-size:1.3rem;color:#4f91fc;">V2</span></div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Sugestões Inteligentes de Transferência de Produtos • Dashboard Visual</div>', unsafe_allow_html=True)

uploaded_file = st.file_uploader("📄 Upload da Planilha", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file, header=31)
    df = df[pd.to_numeric(df.iloc[:, 0], errors='coerce').notnull()]
    df.columns = [
        'Codigo', 'Descricao', 'Referencia', 'Saldo_Anterior', 'Total_Recebimento', 'Total_Vendas', 'Saldo_Atual',
        'Vendas_Mega_Loja', 'Saldo_Mega_Loja',
        'Vendas_Mascote', 'Saldo_Mascote',
        'Vendas_Tatuape', 'Saldo_Tatuape',
        'Vendas_Indianopolis', 'Saldo_Indianopolis',
        'Vendas_Praia_Grande', 'Saldo_Praia_Grande',
        'Vendas_Fabrica', 'Saldo_Fabrica',
        'Vendas_Osasco', 'Saldo_Osasco'
    ]
    lojas = ['Mega_Loja', 'Mascote', 'Tatuape', 'Indianopolis', 'Praia_Grande', 'Fabrica', 'Osasco']
    for col in df.columns:
        if 'Vendas' in col or 'Saldo' in col:
            df[col] = pd.to_numeric(df[col].replace('-', 0), errors='coerce').fillna(0).astype(int)

    # Função de sugestão (igual anterior)
    def sugerir_transferencias(df, lojas):
        sugestoes = []
        for _, row in df.iterrows():
            produto = row['Codigo']
            descricao = row['Descricao']
            referencia = row['Referencia']
            vendas_lojas = {loja: row[f'Vendas_{loja}'] for loja in lojas}
            saldo_lojas = {loja: row[f'Saldo_{loja}'] for loja in lojas}
            loja_maior_venda = max(vendas_lojas, key=lambda k: vendas_lojas[k])
            for loja in lojas:
                saldo = saldo_lojas[loja]
                vendas = vendas_lojas[loja]
                if saldo > vendas and saldo > 0:
                    qtd_transferir = saldo - vendas
                    if vendas_lojas[loja_maior_venda] > 0 and loja != loja_maior_venda:
                        sugestoes.append({
                            'Codigo': produto,
                            'Descricao': descricao,
                            'Referencia': referencia,
                            'Loja_Origem': loja,
                            'Estoque_Origem': saldo,
                            'Vendas_Origem': vendas,
                            'Loja_Destino': loja_maior_venda,
                            'Vendas_Destino': vendas_lojas[loja_maior_venda],
                            'Transferir_Qtd': qtd_transferir
                        })
        return pd.DataFrame(sugestoes)

    sugestoes = sugerir_transferencias(df, lojas)

    # KPIs
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f'<div class="kpi-card"><div class="kpi-number">{sugestoes.shape[0]}</div><div class="kpi-label">Sugestões de Transferência</div></div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="kpi-card"><div class="kpi-number">{df.shape[0]}</div><div class="kpi-label">Produtos Analisados</div></div>', unsafe_allow_html=True)
    with col3:
        st.markdown(f'<div class="kpi-card"><div class="kpi-number">{len(set(sugestoes["Loja_Origem"].tolist() + sugestoes["Loja_Destino"].tolist()))}</div><div class="kpi-label">Lojas Envolvidas</div></div>', unsafe_allow_html=True)

    # Gráfico de barras — produtos parados por loja de origem
    if not sugestoes.empty:
        grafico = px.bar(
            sugestoes.groupby('Loja_Origem')['Transferir_Qtd'].sum().reset_index(),
            x='Loja_Origem', y='Transferir_Qtd', color='Loja_Origem',
            title="Produtos parados por loja de origem", labels={"Transferir_Qtd": "Qtd. a Transferir"}
        )
        st.plotly_chart(grafico, use_container_width=True)

    # GRÁFICO DE PIZZA — Distribuição de Transferências por Loja de Destino
    if not sugestoes.empty:
        st.markdown("### Distribuição de Transferências por Loja de Destino")
        fig_pizza = px.pie(
            sugestoes, 
            names='Loja_Destino', 
            values='Transferir_Qtd',
            title="Percentual de produtos a transferir para cada loja",
            hole=0.45
        )
        st.plotly_chart(fig_pizza, use_container_width=True)

    # RANKING DE PRODUTOS — Top produtos sugeridos para transferência
    if not sugestoes.empty:
        st.markdown("### Ranking dos Produtos com Maior Transferência Sugerida")
        top_produtos = (
            sugestoes.groupby(['Codigo', 'Descricao'])['Transferir_Qtd']
            .sum()
            .reset_index()
            .sort_values('Transferir_Qtd', ascending=False)
            .head(10)
        )
        fig_ranking = px.bar(
            top_produtos, 
            x='Transferir_Qtd', y='Descricao', 
            orientation='h',
            title='Top 10 Produtos em Volume de Transferência Sugerida',
            labels={'Transferir_Qtd':'Qtd. a Transferir', 'Descricao':'Produto'}
        )
        st.plotly_chart(fig_ranking, use_container_width=True)

    # HEATMAP — Origem x Destino das Transferências
    if not sugestoes.empty:
        st.markdown("### Heatmap das Transferências (Origem x Destino)")
        matriz = (
            sugestoes.groupby(['Loja_Origem', 'Loja_Destino'])['Transferir_Qtd']
            .sum().reset_index()
        )
        heatmap_data = matriz.pivot(index='Loja_Origem', columns='Loja_Destino', values='Transferir_Qtd').fillna(0)
        fig_heat = px.imshow(
            heatmap_data,
            text_auto=True,
            aspect="auto",
            color_continuous_scale='Blues',
            title="Volume de Transferência por Origem e Destino"
        )
        st.plotly_chart(fig_heat, use_container_width=True)

    # Cards das sugestões
    st.markdown('<h4>Sugestões de Transferência</h4>', unsafe_allow_html=True)
    if not sugestoes.empty:
        for idx, row in sugestoes.iterrows():
            st.markdown(
                f"""
                <div class="sugestao-card">
                    <span class="cod">{row['Codigo']}</span>
                    <span class="prod">{row['Descricao']}</span>
                    <span class="mini">Estoque: <b>{row['Estoque_Origem']}</b> • Vendas: <b>{row['Vendas_Origem']}</b></span>
                    <span style="margin-left:1.5rem;"><span class="loja">{row['Loja_Origem']}</span> ➡️ <span class="destino">{row['Loja_Destino']}</span></span>
                    <span class="transferir">Transferir: {row['Transferir_Qtd']}</span>
                </div>
                """, unsafe_allow_html=True
            )
    else:
        st.info("Nenhuma sugestão de transferência encontrada para os dados desta planilha.")

    # Download do Excel
    excel_buffer = io.BytesIO()
    sugestoes.to_excel(excel_buffer, index=False)
    excel_buffer.seek(0)
    st.download_button(
        "📥 Baixar resultado em Excel",
        data=excel_buffer,
        file_name="sugestao_transferencias.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
else:
    st.info("Faça upload de uma planilha para iniciar.")
