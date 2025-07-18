import streamlit as st
import pandas as pd
import math
from io import BytesIO

st.set_page_config(page_title="Painel de Montagem", layout="wide")
st.title("🔧 Painel de Montagens com Estoque e Pedidos")

# Links atualizados dos arquivos no GitHub (novo repositório)
URL_ESTRUTURA = "https://github.com/CamilaG288/Turbos_montaveis/raw/main/ESTRUTURAS.xlsx"
URL_CURVA = "https://github.com/CamilaG288/Turbos_montaveis/raw/main/CURVA%20ABC.xlsx"
URL_ESTOQUE = "https://github.com/CamilaG288/Turbos_montaveis/raw/main/ALMOX102.xlsx"
URL_PEDIDOS = "https://github.com/CamilaG288/Turbos_montaveis/raw/main/PEDIDOS.xlsx"

# Exclusões fixas por descrição (itens fáceis de repor)
EXCLUIR_DESCRICOES = ["CINTA PLASTICA", "PLAQUETA", "SACO PLASTICO", "ETIQUETA", "REBITE", "CAIXA", "CERTIFICADO"]

@st.cache_data
def carregar_dados():
    estrutura = pd.read_excel(URL_ESTRUTURA, skiprows=1)  # ajustado para pular apenas a primeira linha
    curva = pd.read_excel(URL_CURVA)
    estoque = pd.read_excel(URL_ESTOQUE)
    pedidos = pd.read_excel(URL_PEDIDOS)
    return estrutura, curva, estoque, pedidos

# Processamento
estrutura, curva, estoque, pedidos = carregar_dados()

# Renomear colunas para nomes amigáveis
estrutura.columns.values[15] = "Componente"
estrutura = estrutura.rename(columns={
    "Produto": "Pai_Final",
    "Qtde. Líquida": "Qtde_Liquida",
    "Setup/Perda": "Setup",
    "Descrição do Produto": "Descricao",
    "Nível": "Nivel"
})

# Padronizar textos e remover espaços
estrutura['Pai_Final'] = estrutura['Pai_Final'].astype(str).str.strip()
estrutura['Componente'] = estrutura['Componente'].astype(str).str.strip()
estrutura['Fantasma'] = estrutura['Fantasma'].astype(str).str.strip()
estrutura['Nivel'] = estrutura['Nivel'].astype(str).str.strip()

# Limpeza e filtros da estrutura
estrutura = estrutura[estrutura['Nivel'].isin(["1", "2"])]
estrutura = estrutura[~estrutura['Componente'].str.endswith("P")]
estrutura = estrutura[estrutura['Fantasma'].str.upper() != 'S']

# Reorganização dos níveis considerando também produtos presentes na curva ou pedidos
estrutura_n1 = estrutura[estrutura['Nivel'] == "1"]
potenciais_pais = set(curva[curva.columns[0]].astype(str).str.strip()).union(
    set(pedidos['Produto'].astype(str).str.strip())
)
estrutura_n2 = estrutura[
    (estrutura['Nivel'] == "2") &
    (estrutura['Pai_Final'].isin(potenciais_pais))
]
estrutura = pd.concat([estrutura_n1, estrutura_n2])

# Curva ABC ordenada
coluna_prioridade = curva.columns[7]
curva = curva.rename(columns={curva.columns[0]: "Produto"})
curva['Produto'] = curva['Produto'].astype(str).str.strip()
curva_sorted = curva.sort_values(by=coluna_prioridade, ascending=True)

# Preparar estoque
estoque = estoque.rename(columns={"Produto": "Componente", "Qtde Atual": "Quantidade"})
estoque['Componente'] = estoque['Componente'].astype(str).str.strip()
estoque_dict = estoque.groupby("Componente")["Quantidade"].sum().to_dict()

# Limpar pedidos
pedidos['Produto'] = pedidos['Produto'].astype(str).str.strip()
pedidos['Qtde_Pronta'] = pedidos['Qtde. Separ'] - pedidos['Qtde.Ate']
pedidos['Qtde_Pronta'] = pedidos['Qtde_Pronta'].apply(lambda x: max(x, 0))
pedidos['Qtde_Produzir'] = pedidos['Qtde. Abe'] - pedidos['Qtde_Pronta']
pedidos['Qtde_Produzir'] = pedidos['Qtde_Produzir'].apply(lambda x: max(x, 0))
pedidos_resumo = pedidos.groupby('Produto', as_index=False)['Qtde_Produzir'].sum()

# Reservar componentes para carteira
reservas = []
for _, row in pedidos_resumo.iterrows():
    pai = row['Produto']
    qtde = row['Qtde_Produzir']
    estrutura_pai = estrutura[estrutura['Pai_Final'] == pai]
    for _, comp in estrutura_pai.iterrows():
        reservas.append({
            'Componente': comp['Componente'],
            'Produto_Pai': pai,
            'Qtde_Reservada': qtde * comp['Qtde_Liquida']
        })
df_reservas = pd.DataFrame(reservas)
if not df_reservas.empty:
    df_reservas = df_reservas.groupby('Componente', as_index=False)['Qtde_Reservada'].sum()
else:
    df_reservas = pd.DataFrame(columns=['Componente', 'Qtde_Reservada'])

# Atualizar estoque com reservas
estoque_pos = estoque_dict.copy()
for _, row in df_reservas.iterrows():
    comp = row['Componente']
    estoque_pos[comp] = max(0, estoque_pos.get(comp, 0) - row['Qtde_Reservada'])

# Aplicar algoritmo greedy com curva ABC
montagem = {}
for produto in curva_sorted['Produto']:
    estrutura_pai = estrutura[estrutura['Pai_Final'] == produto]
    if estrutura_pai.empty:
        continue
    min_possivel = math.inf
    for _, linha in estrutura_pai.iterrows():
        comp = linha['Componente']
        descricao = str(linha['Descricao']).upper()
        if any(excl in descricao for excl in EXCLUIR_DESCRICOES):
            continue
        qtd_necessaria = linha['Qtde_Liquida']
        qtd_estoque = estoque_pos.get(comp, 0)
        if qtd_necessaria > 0:
            min_possivel = min(min_possivel, math.floor(qtd_estoque / qtd_necessaria))
    if min_possivel >= 1 and min_possivel != math.inf:
        montagem[produto] = min_possivel
        for _, linha in estrutura_pai.iterrows():
            comp = linha['Componente']
            descricao = str(linha['Descricao']).upper()
            if any(excl in descricao for excl in EXCLUIR_DESCRICOES):
                continue
            estoque_pos[comp] -= min_possivel * linha['Qtde_Liquida']

# Mostrar resultados
st.subheader("📊 Produtos que Podemos Montar com Estoque Disponível")
df_montagem = pd.DataFrame(montagem.items(), columns=['Produto', 'Quantidade Possível'])
st.dataframe(df_montagem, use_container_width=True)

# Verificações adicionais para o produto exemplo
produto_exemplo = "802925-01"
st.subheader(f"🔍 Verificação do Produto {produto_exemplo}")

if produto_exemplo in estrutura['Pai_Final'].values:
    estrutura_exemplo = estrutura[estrutura['Pai_Final'] == produto_exemplo]
    st.write("Estrutura do Produto:")
    st.dataframe(estrutura_exemplo)

    st.write("Estoque Atual dos Componentes (pós-reserva):")
    st.dataframe(pd.DataFrame.from_dict({
        comp: estoque_pos.get(comp, 0)
        for comp in estrutura_exemplo['Componente'].unique()
    }, orient='index', columns=['Estoque Disponível']).reset_index().rename(columns={'index': 'Componente'}))

    st.write("Quantidade que Deveria Aparecer se Possível Montar:")
    st.write(montagem.get(produto_exemplo, "Produto não foi considerado montável"))
else:
    st.warning("Produto não está presente na estrutura!")

# Download do resultado
buffer = BytesIO()
df_montagem.to_excel(buffer, index=False)
st.download_button("🗅️ Baixar Resultado em Excel", buffer.getvalue(), file_name="montagem_resultado.xlsx")
