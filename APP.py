import streamlit as st
import pandas as pd
from io import BytesIO

st.set_page_config(page_title="Análise de Pedidos", layout="wide")
st.title("📦 Análise de Pedidos - Qtde. Produzir + Estrutura Nível 2")

def converter_para_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Resultado")
    output.seek(0)
    return output

# --- ETAPA 1: PEDIDOS ---

URL_PEDIDOS = "https://github.com/CamilaG288/Turbos_montaveis/raw/main/PEDIDOS.xlsx"
df_pedidos = pd.read_excel(URL_PEDIDOS)

df_pedidos["Quantidade_Produzir"] = df_pedidos.iloc[:, 15] - (df_pedidos.iloc[:, 16] - df_pedidos.iloc[:, 13])
df_pedidos_filtrados = df_pedidos[df_pedidos["Quantidade_Produzir"] > 0].copy()

colunas_exibir = [
    "Cliente", "Nome", "Tp.Doc", "Pedido", "Produto", "Descricao", "Qtde. Abe", "Quantidade_Produzir"
]
df_exibir = df_pedidos_filtrados[colunas_exibir]

st.subheader("📌 Pedidos com Quantidade a Produzir > 0")
st.dataframe(df_exibir)

st.download_button(
    label="📥 Baixar Pedidos com Qtde. Produzir > 0",
    data=converter_para_excel(df_exibir),
    file_name="pedidos_quantidade_produzir.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

# --- ETAPA 2: ESTRUTURA NÍVEL 2 ---

URL_ESTRUTURA = "https://github.com/CamilaG288/Turbos_montaveis/raw/main/ESTRUTURAS.xlsx"
df_estrutura = pd.read_excel(URL_ESTRUTURA)

# Limpeza
df_estrutura.iloc[:, 1] = df_estrutura.iloc[:, 1].astype(str).str.strip()    # Pai (B)
df_estrutura.iloc[:, 15] = df_estrutura.iloc[:, 15].astype(str).str.strip() # Filho (P)
df_estrutura.iloc[:, 22] = (
    df_estrutura.iloc[:, 22]
    .astype(str)
    .str.replace(",", ".", regex=False)
    .str.strip()
    .astype(float)
)

# Filtro: não fantasma e com filho válido
df_estrutura_limpa = df_estrutura[
    (df_estrutura.iloc[:, 19] != "S") & (df_estrutura.iloc[:, 15].notna())
].copy()

# Mapear estrutura: pai → [(filho, qtd)]
estrutura_dict = {}
for _, row in df_estrutura_limpa.iterrows():
    pai = row.iloc[1]
    filho = row.iloc[15]
    qtd = row.iloc[22]
    if pd.notna(pai) and pd.notna(filho) and pd.notna(qtd):
        estrutura_dict.setdefault(pai, []).append((filho, qtd))

# Palavras-chave para exclusão via descrição (coluna R = índice 17)
palavras_excluir = [
    "SACO PLASTICO", "CAIXA", "PLAQUETA", "REBITE", "ETIQUETA", "CERTIFICADO", "CINTA PLASTICA"
]

estrutura_expandidas = []

for _, pedido in df_pedidos_filtrados.iterrows():
    pai_final = str(pedido["Produto"]).strip()
    qtd_produzir = pedido["Quantidade_Produzir"]
    filhos_n1 = estrutura_dict.get(pai_final, [])

    for filho1, qtd1 in filhos_n1:
        desc1 = df_estrutura_limpa[df_estrutura_limpa.iloc[:, 15] == filho1].iloc[0, 17].upper()

        if any(p in desc1 for p in palavras_excluir):
            continue

        if filho1.endswith("P"):
            filhos_do_P = estrutura_dict.get(filho1, [])
            for filho2, qtd2 in filhos_do_P:
                desc2 = df_estrutura_limpa[df_estrutura_limpa.iloc[:, 15] == filho2].iloc[0, 17].upper()
                if any(p in desc2 for p in palavras_excluir):
                    continue
                estrutura_expandidas.append({
                    "Pai Final": pai_final,
                    "Componente": filho2,
                    "Nível": 2,
                    "Qtd por Unidade": qtd1 * qtd2,
                    "Qtd Produzir": qtd_produzir,
                    "Qtd Necessária": qtd_produzir * qtd1 * qtd2,
                    "Cliente": pedido["Cliente"],
                    "Pedido": pedido["Pedido"]
                })
        else:
            estrutura_expandidas.append({
                "Pai Final": pai_final,
                "Componente": filho1,
                "Nível": 1,
                "Qtd por Unidade": qtd1,
                "Qtd Produzir": qtd_produzir,
                "Qtd Necessária": qtd_produzir * qtd1,
                "Cliente": pedido["Cliente"],
                "Pedido": pedido["Pedido"]
            })

# Resultado final
df_estrutura_nivel2 = pd.DataFrame(estrutura_expandidas)

st.subheader("🧬 Estrutura Explodida até Nível 2 (ajustada)")
st.dataframe(df_estrutura_nivel2)

st.download_button(
    label="📥 Baixar Estrutura Nível 2",
    data=converter_para_excel(df_estrutura_nivel2),
    file_name="estrutura_nivel2.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)
