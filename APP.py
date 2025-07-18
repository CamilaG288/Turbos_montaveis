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
    estrutura = pd.read_excel(URL_ESTRUTURA)
    curva = pd.read_excel(URL_CURVA)
    estoque = pd.read_excel(URL_ESTOQUE)
    pedidos = pd.read_excel(URL_PEDIDOS)
    return estrutura, curva, estoque, pedidos

# Processamento
estrutura, curva, estoque, pedidos = carregar_dados()

# Mostrar colunas da estrutura para depuração
temp_colunas = estrutura.columns.tolist()
st.write("Colunas disponíveis na planilha de estrutura:", temp_colunas)

# Atribuir nomes de colunas corretos (evita erro com colunas inexistentes)
estrutura.columns.values[6] = 'Pai_Final'
estrutura.columns.values[15] = 'Componente'
estrutura.columns.values[16] = 'Nivel'
estrutura.columns.values[17] = 'Descricao'
estrutura.columns.values[18] = 'Fantasma'
estrutura.columns.values[19] = 'UM'
estrutura.columns.values[20] = 'GRP'

# Limpeza e filtros da estrutura
estrutura = estrutura[estrutura['Nivel'].isin([1, 2])]
estrutura = estrutura[~estrutura['Componente'].astype(str).str.endswith("P")]
estrutura = estrutura[estrutura['Fantasma'] != 'S']
estrutura['Pai_Final'] = estrutura['Pai_Final'].astype(str).str.strip()
estrutura['Componente'] = estrutura['Componente'].astype(str).str.strip()
estrutura_nivel2 = estrutura[estrutura['Nivel'] == 2]
estrutura_nivel2 = estrutura_nivel2[estrutura_nivel2['Pai_Final'] == estrutura_nivel2['Pai_Final']]
estrutura = pd.concat([
    estrutura[estrutura['Nivel'] == 1],
    estrutura_nivel2
])

# Curva ABC ordenada
curva_sorted = curva.sort_values(by='H', ascending=True)

# Preparar estoque
estoque = estoque.rename(columns={"Produto": "Componente", "Qtde Atual": "Quantidade"})
estoque['Componente'] = estoque['Componente'].astype(str).str.strip()
estoque_dict = estoque.groupby("Componente")['Quantidade'].sum().to_dict()

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
            'Qtde_Reservada': qtde
        })
df_reservas = pd.DataFrame(reservas)
df_reservas = df_reservas.groupby('Componente', as_index=False)['Qtde_Reservada'].sum()

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
        if any(comp.startswith(desc) for desc in EXCLUIR_DESCRICOES):
            continue
        qtd = estoque_pos.get(comp, 0)
        min_possivel = min(min_possivel, math.floor(qtd))
    if min_possivel >= 1 and min_possivel != math.inf:
        montagem[produto] = min_possivel
        for _, linha in estrutura_pai.iterrows():
            comp = linha['Componente']
            if any(comp.startswith(desc) for desc in EXCLUIR_DESCRICOES):
                continue
            estoque_pos[comp] -= min_possivel

# Mostrar resultados
st.subheader("📊 Produtos que Podemos Montar com Estoque Disponível")
df_montagem = pd.DataFrame(montagem.items(), columns=['Produto', 'Quantidade Possível'])
st.dataframe(df_montagem, use_container_width=True)

# Download do resultado
buffer = BytesIO()
df_montagem.to_excel(buffer, index=False)
st.download_button("📅 Baixar Resultado em Excel", buffer.getvalue(), file_name="montagem_resultado.xlsx")
