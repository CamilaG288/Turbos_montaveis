import streamlit as st
import pandas as pd
from io import BytesIO

st.set_page_config(page_title="Análise de Pedidos", layout="wide")
st.title("📦 Análise de Pedidos - Qtde. Produzir + Componentes Necessários")

# Função auxiliar para exportar Excel
def converter_para_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Resultado")
    output.seek(0)
    return output

# --- ETAPA 1: Análise dos Pedidos ---

# Leitura da planilha de pedidos
URL_PEDIDOS = "https://github.com/CamilaG288/Turbos_montaveis/raw/main/PEDIDOS.xlsx"
df_pedidos = pd.read_excel(URL_PEDIDOS)

# Cálculo da quantidade real: Qtde. Abe - (Qtde. Separ - Qtde. Ate)
df_pedidos["Quantidade_Produzir"] = df_pedidos.iloc[:, 15] - (df_pedidos.iloc[:, 16] - df_pedidos.iloc[:, 13])

# Filtrar pedidos com quantidade a produzir > 0
df_pedidos_filtrados = df_pedidos[df_pedidos["Quantidade_Produzir"] > 0].copy()

# Reorganizar colunas para exibição
colunas_exibir = [
    "Cliente", "Nome", "Tp.Doc", "Pedido", "Produto", "Descricao", "Qtde. Abe", "Quantidade_Produzir"
]
df_exibir = df_pedidos_filtrados[colunas_exibir]

# Exibir pedidos válidos
st.subheader("📌 Pedidos com Quantidade a Produzir > 0")
st.dataframe(df_exibir)

# Botão para baixar pedidos filtrados
st.download_button(
    label="📥 Baixar Pedidos com Qtde. Produzir > 0",
    data=converter_para_excel(df_exibir),
    file_name="pedidos_quantidade_produzir.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

# --- ETAPA 2: Componentes por Estrutura ---

# Leitura da estrutura de produtos
URL_ESTRUTURA = "https://github.com/CamilaG288/Turbos_montaveis/raw/main/ESTRUTURAS.xlsx"
df_estrutura = pd.read_excel(URL_ESTRUTURA)

# Conversão e limpeza das colunas importantes
df_estrutura.iloc[:, 1] = df_estrutura.iloc[:, 1].astype(str).str.strip()    # Coluna B - pai
df_estrutura.iloc[:, 15] = df_estrutura.iloc[:, 15].astype(str).str.strip() # Coluna P - filho

# Conversão da coluna W (índice 22) para float, tratando vírgulas e espaços
df_estrutura.iloc[:, 22] = (
    df_estrutura.iloc[:, 22]
    .astype(str)
    .str.replace(",", ".", regex=False)
    .str.strip()
    .astype(float)
)

# Filtro: remove fantasmas e pais que terminam com "P"
df_estrutura_filtrada = df_estrutura[
    (df_estrutura.iloc[:, 19] != "S") & (df_estrutura.iloc[:, 15].notna())
]
df_estrutura_filtrada = df_estrutura_filtrada[~df_estrutura_filtrada.iloc[:, 1].str.endswith("P")]

# Montar lista de componentes
componentes_lista = []

for _, pedido in df_pedidos_filtrados.iterrows():
    produto_final = str(pedido["Produto"]).strip()
    quantidade_produzir = pedido["Quantidade_Produzir"]

    filhos = df_estrutura_filtrada[df_estrutura_filtrada.iloc[:, 1] == produto_final]

    for _, filho in filhos.iterrows():
        cod_componente = filho.iloc[15]      # Coluna P (componente)
        qtd_por_unidade = filho.iloc[22]     # Coluna W

        if pd.notna(qtd_por_unidade) and qtd_por_unidade > 0:
            componentes_lista.append({
                "Produto Final": produto_final,
                "Componente": cod_componente,
                "Quantidade por Unidade": qtd_por_unidade,
                "Quantidade a Produzir": quantidade_produzir,
                "Qtde Necessária do Componente": quantidade_produzir * qtd_por_unidade,
                "Cliente": pedido["Cliente"],
                "Pedido": pedido["Pedido"]
            })

# Exibir resultado final
df_componentes = pd.DataFrame(componentes_lista)

st.subheader("🧮 Componentes Necessários por Estrutura")
st.dataframe(df_componentes)

# Botão para baixar componentes
st.download_button(
    label="📥 Baixar Componentes Necessários",
    data=converter_para_excel(df_componentes),
    file_name="componentes_necessarios.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)
