import pandas as pd
import os
import functools

# --- Configuração de Caminhos Absolutos ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, 'data', 'dw')

# --- Funções de Carregamento com Cache e Conversão de Tipo ---

def set_key_types(df):
    """
    Converte as colunas chave ('CD_MUN', 'ANO') para tipos numéricos inteiros.
    Isso previne erros de junção (merge) devido a tipos de dados inconsistentes.
    Usa 'errors="ignore"' para não quebrar se a coluna não existir.
    """
    if df.empty:
        return df
    
    # Usamos um loop para converter as colunas individualmente e de forma segura.
    for col in ['CD_MUN', 'ANO']:
        if col in df.columns:
            # Converte para numérico, transformando erros em NaN, e depois para Int64 que suporta NaN.
            df[col] = pd.to_numeric(df[col], errors='coerce')
            df = df.dropna(subset=[col]) # Remove linhas onde a chave é inválida/nula
            df[col] = df[col].astype('Int64')
    return df

@functools.lru_cache(maxsize=None)
def load_filters():
    """
    Carrega o arquivo de filtros e garante a consistência dos tipos de dado.
    """
    filtros_path = os.path.join(DATA_PATH, "Filtros.xlsx")
    try:
        df = pd.read_excel(filtros_path)
        return set_key_types(df) # <-- APLICA A CORREÇÃO
    except FileNotFoundError:
        print(f"ERRO: Arquivo de filtros não encontrado em: {filtros_path}")
        return pd.DataFrame(columns=['CD_MUN', 'ANO', 'NM_MUN'])

@functools.lru_cache(maxsize=None)
def load_variable_data(area, variable):
    """
    Carrega um arquivo de variável e garante a consistência dos tipos de dado.
    """
    file_path = os.path.join(DATA_PATH, area, f"{variable}.xlsx")
    try:
        df = pd.read_excel(file_path)
        return set_key_types(df) # <-- APLICA A CORREÇÃO
    except FileNotFoundError:
        print(f"ERRO: Arquivo de variável não encontrado em: {file_path}")
        return pd.DataFrame(columns=['CD_MUN', 'ANO', 'VALOR'])

# --- Funções de Combinação de Dados (Agora mais seguras) ---

def combine_data_with_filters(filtros_df, variable_df, years=None, municipios=None):
    """
    Combina os dados de uma variável com os filtros aplicados.
    """
    if filtros_df.empty or variable_df.empty:
        return pd.DataFrame()

    if years:
        filtros_df = filtros_df[filtros_df['ANO'].isin(years)]
    
    merged_df = pd.merge(filtros_df, variable_df, on=['CD_MUN', 'ANO'], how='inner', suffixes=('_filtros', '_variavel'))

    municipio_col = 'NM_MUN_filtros' if 'NM_MUN_filtros' in merged_df.columns else 'NM_MUN'
    if municipios:
        if municipio_col in merged_df.columns:
            merged_df = merged_df[merged_df[municipio_col].isin(municipios)]
        else:
            return pd.DataFrame()

    if 'NM_MUN_filtros' in merged_df.columns:
        merged_df = merged_df.rename(columns={'NM_MUN_filtros': 'NM_MUN'})
    
    return merged_df

def load_multiple_variables(section_variable_pairs, years=None, municipios=None):
    """Carrega e combina dados de múltiplas variáveis de diferentes seções."""
    filtros_df = load_filters()
    if filtros_df.empty: return pd.DataFrame()

    if years:
        filtros_df = filtros_df[filtros_df['ANO'].isin(years)]
    if municipios:
        filtros_df = filtros_df[filtros_df['NM_MUN'].isin(municipios)]
    
    result_df = filtros_df.copy()

    for section, variable in section_variable_pairs:
        variable_df = load_variable_data(section, variable)
        if not variable_df.empty:
            variable_df = variable_df.rename(columns={'VALOR': variable})
            result_df = pd.merge(result_df, variable_df, on=['CD_MUN', 'ANO'], how='inner')

    return result_df
