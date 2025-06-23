import pandas as pd
import os
import functools # Importa a biblioteca para cache

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
        filtros_df = pd.read_excel(filtros_path)
        return filtros_df
    except FileNotFoundError:
        print(f"ERRO: Arquivo de filtros não encontrado em: {filtros_path}")
        return pd.DataFrame(columns=['CD_MUN', 'ANO', 'NM_MUN'])

@functools.lru_cache(maxsize=None)
def load_variable_data(area, variable):
    """
    Carrega os dados de um arquivo de variável específico.
    O decorador @lru_cache garante que cada arquivo de variável seja lido do disco apenas uma vez.
    """
    file_path = os.path.join(DATA_PATH, area, f"{variable}.xlsx")
    try:
        df = pd.read_excel(file_path)
        return df
    except FileNotFoundError:
        print(f"ERRO: Arquivo de variável não encontrado em: {file_path}")
        return pd.DataFrame(columns=['CD_MUN', 'ANO', 'VALOR'])

# --- Funções de Combinação de Dados (Não precisam de cache direto) ---

def combine_data_with_filters(filtros_df, variable_df, years=None, municipios=None):
    """Combina os dados de uma variável com os filtros aplicados."""
    if filtros_df.empty or variable_df.empty:
        return pd.DataFrame()

    if years:
        filtros_df = filtros_df[filtros_df['ANO'].isin(years)]
    
    # Usar merge em vez de join/set_index para clareza e robustez
    merged_df = pd.merge(filtros_df, variable_df, on=['CD_MUN', 'ANO'], how='inner', suffixes=('_filtros', '_variavel'))
    
    if municipios:
        merged_df = merged_df[merged_df['NM_MUN'].isin(municipios)]
    
    # Renomear a coluna de nome do município para evitar confusão
    if 'NM_MUN_filtros' in merged_df.columns:
        merged_df = merged_df.rename(columns={'NM_MUN_filtros': 'NM_MUN'})

    return merged_df

def load_multiple_variables(section_variable_pairs, years=None, municipios=None):
    """Carrega e combina dados de múltiplas variáveis de diferentes seções."""
    filtros_df = load_filters()
    if filtros_df.empty:
        return pd.DataFrame()

    # Filtra os dados de filtros uma única vez
    if years:
        filtros_df = filtros_df[filtros_df['ANO'].isin(years)]
    if municipios:
        filtros_df = filtros_df[filtros_df['NM_MUN'].isin(municipios)]
    
    # Define o DataFrame inicial como a base de filtros
    result_df = filtros_df.copy()

    for section, variable in section_variable_pairs:
        variable_df = load_variable_data(section, variable)
        if not variable_df.empty:
            # Renomeia a coluna de valor antes do merge para evitar conflitos
            variable_df = variable_df.rename(columns={'VALOR': variable})
            # Junta cada variável ao DataFrame de resultado
            result_df = pd.merge(result_df, variable_df, on=['CD_MUN', 'ANO'], how='inner')

    return result_df
