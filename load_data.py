import pandas as pd
import os
import functools

# --- Configuração de Caminhos Absolutos ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, 'data', 'dw')

# --- Funções de Carregamento com Cache ---

@functools.lru_cache(maxsize=None)
def load_filters():
    """
    Carrega os dados do arquivo de filtros.
    O decorador @lru_cache garante que o arquivo seja lido do disco apenas uma vez.
    """
    filtros_path = os.path.join(DATA_PATH, "Filtros.xlsx")
    try:
        return pd.read_excel(filtros_path)
    except FileNotFoundError:
        print(f"ERRO: Arquivo de filtros não encontrado em: {filtros_path}")
        return pd.DataFrame(columns=['CD_MUN', 'ANO', 'NM_MUN'])

@functools.lru_cache(maxsize=None)
def load_variable_data(area, variable):
    """
    Carrega os dados de um arquivo de variável específico.
    O decorador @lru_cache garante que cada arquivo seja lido apenas uma vez.
    """
    file_path = os.path.join(DATA_PATH, area, f"{variable}.xlsx")
    try:
        return pd.read_excel(file_path)
    except FileNotFoundError:
        print(f"ERRO: Arquivo de variável não encontrado em: {file_path}")
        return pd.DataFrame(columns=['CD_MUN', 'ANO', 'VALOR'])

# --- Funções de Combinação de Dados ---

def combine_data_with_filters(filtros_df, variable_df, years=None, municipios=None):
    """
    Combina os dados de uma variável com os filtros aplicados, tratando nomes de colunas de forma robusta.
    """
    if filtros_df.empty or variable_df.empty:
        return pd.DataFrame()

    if years:
        filtros_df = filtros_df[filtros_df['ANO'].isin(years)]
    
    # Realiza o merge. Se 'NM_MUN' existir em ambos, pandas adicionará sufixos.
    merged_df = pd.merge(filtros_df, variable_df, on=['CD_MUN', 'ANO'], how='inner', suffixes=('_filtros', '_variavel'))

    # Identifica o nome correto da coluna do município após o merge.
    municipio_col = 'NM_MUN_filtros' if 'NM_MUN_filtros' in merged_df.columns else 'NM_MUN'

    if municipios:
        # Verifica se a coluna de município realmente existe antes de filtrar.
        if municipio_col in merged_df.columns:
            merged_df = merged_df[merged_df[municipio_col].isin(municipios)]
        else:
            print(f"AVISO: Coluna de município '{municipio_col}' não encontrada para filtragem.")
            return pd.DataFrame()

    # Padroniza o nome da coluna para 'NM_MUN' para consistência no resto do app.
    if 'NM_MUN_filtros' in merged_df.columns:
        merged_df = merged_df.rename(columns={'NM_MUN_filtros': 'NM_MUN'})
    
    return merged_df

def load_multiple_variables(section_variable_pairs, years=None, municipios=None):
    """Carrega e combina dados de múltiplas variáveis de diferentes seções."""
    filtros_df = load_filters()
    if filtros_df.empty: return pd.DataFrame()

    # Aplica filtros de ano e município uma única vez na base de filtros.
    if years:
        filtros_df = filtros_df[filtros_df['ANO'].isin(years)]
    if municipios:
        filtros_df = filtros_df[filtros_df['NM_MUN'].isin(municipios)]
    
    # Começa com a base de filtros já filtrada.
    result_df = filtros_df.copy()

    for section, variable in section_variable_pairs:
        variable_df = load_variable_data(section, variable)
        if not variable_df.empty:
            # Renomeia a coluna VALOR para o nome da variável para evitar conflitos no merge.
            variable_df = variable_df.rename(columns={'VALOR': variable})
            # Junta cada variável ao DataFrame de resultado.
            result_df = pd.merge(result_df, variable_df, on=['CD_MUN', 'ANO'], how='inner')

    return result_df
