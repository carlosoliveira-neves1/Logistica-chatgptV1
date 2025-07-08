import streamlit as st
import pandas as pd
import io

st.set_page_config(page_title="Sugestão de Transferências", layout="wide")
st.title("Análise de Transferências de Estoque entre Lojas")

uploaded_file = st.file_uploader("Faça upload da planilha .xlsx do relatório", type=["xlsx"])

if uploaded_file:
    # Ler planilha a partir da linha correta do relatório
    df = pd.read_excel(uploaded_file, header=31)
    # Mantém só linhas com código numérico
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

    # Função de sugestão (mesma lógica anterior)
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
    st.dataframe(sugestoes)

    # Exporta para Excel em memória
    excel_buffer = io.BytesIO()
    sugestoes.to_excel(excel_buffer, index=False)
    excel_buffer.seek(0)

    st.download_button(
        "Baixar resultado em Excel",
        data=excel_buffer,
        file_name="sugestao_transferencias.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
else:
    st.info("Faça upload de uma planilha para iniciar.")

