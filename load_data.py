import pandas as pd
import os

# --- Configuração de Caminhos Absolutos ---
# Pega o caminho absoluto do diretório onde este script (load_data.py) está localizado.
# Isso garante que o caminho para os dados funcione tanto localmente quanto no servidor.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Constrói o caminho para a pasta 'dw' dentro da pasta 'data'.
DATA_PATH = os.path.join(BASE_DIR, 'data', 'dw')

# Função para carregar os dados de filtros
def load_filters():
    """Carrega os dados do arquivo de filtros."""
    filtros_path = os.path.join(DATA_PATH, "Filtros.xlsx")
    try:
        filtros_df = pd.read_excel(filtros_path)
        return filtros_df
    except FileNotFoundError:
        print(f"ERRO: Arquivo de filtros não encontrado em: {filtros_path}")
        # Retorna um DataFrame vazio com as colunas esperadas para evitar erros posteriores.
        return pd.DataFrame(columns=['CD_MUN', 'ANO', 'NM_MUN'])

# Função para carregar os dados de uma variável
def load_variable_data(area, variable):
    """Carrega os dados de um arquivo de variável específico."""
    file_path = os.path.join(DATA_PATH, area, f"{variable}.xlsx")
    try:
        df = pd.read_excel(file_path)
        return df
    except FileNotFoundError:
        print(f"ERRO: Arquivo de variável não encontrado em: {file_path}")
        # Retorna um DataFrame vazio com as colunas esperadas.
        return pd.DataFrame(columns=['CD_MUN', 'ANO', 'VALOR'])

# Função para combinar os dados de filtros com os dados da variável
def combine_data_with_filters(filtros_df, variable_df, years=None, municipios=None):
    """Combina os dados de uma variável com os filtros aplicados."""
    # Garante que os DataFrames não estejam vazios antes de continuar
    if filtros_df.empty or variable_df.empty:
        return pd.DataFrame()

    # Filtragem prévia por anos, se especificado
    if years is not None and years:
        filtros_df = filtros_df[filtros_df['ANO'].isin(years)]
    
    # Criar índices para acelerar o merge
    filtros_df = filtros_df.set_index(['CD_MUN', 'ANO'])
    variable_df = variable_df.set_index(['CD_MUN', 'ANO'])
    
    # Join com sufixos para evitar conflito de colunas
    merged_df = filtros_df.join(variable_df, how='inner', lsuffix='_filtros', rsuffix='_variavel').reset_index()
    
    # Filtrar por municípios, se especificado
    if municipios:
        merged_df = merged_df[merged_df['NM_MUN_filtros'].isin(municipios)]
    
    return merged_df

# Função para combinar dados de múltiplas variáveis, permitindo diferentes seções
def load_multiple_variables(section_variable_pairs, years=None, municipios=None):
    """Carrega e combina dados de múltiplas variáveis de diferentes seções."""
    filtros_df = load_filters()
    combined_dfs = []
    
    # Garante que temos um DataFrame de filtros válido
    if filtros_df.empty:
        return pd.DataFrame()

    for section, variable in section_variable_pairs:
        variable_df = load_variable_data(section, variable)
        if not variable_df.empty:
            merged_df = combine_data_with_filters(filtros_df.copy(), variable_df, years=years, municipios=municipios)
            # Renomear a coluna VALOR para o nome da variável
            merged_df = merged_df.rename(columns={'VALOR': variable})
            # Selecionar apenas as colunas necessárias para o merge final
            if not merged_df.empty:
                 combined_dfs.append(merged_df[['CD_MUN', 'ANO', 'NM_MUN_filtros', variable]])

    if not combined_dfs:
        return pd.DataFrame()

    # Combinar todos os DataFrames das variáveis em um só
    result_df = combined_dfs[0]
    for df in combined_dfs[1:]:
        # Garante que a coluna de variável existe antes do merge
        if df.columns[-1] in df.columns:
            result_df = pd.merge(
                result_df,
                df[['CD_MUN', 'ANO', df.columns[-1]]], 
                on=['CD_MUN', 'ANO'], 
                how='inner' # Usar 'inner' para garantir que temos dados para todas as variáveis em um dado ano/município
            )
    
    return result_df
