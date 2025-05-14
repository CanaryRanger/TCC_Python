import pandas as pd

# Função para carregar os dados de filtros
def load_filters():
    filtros_path = "../data/dw/Filtros.xlsx"
    filtros_df = pd.read_excel(filtros_path)
    return filtros_df

# Função para carregar os dados de uma variável
def load_variable_data(area, variable):
    file_path = f"../data/dw/{area}/{variable}.xlsx"
    df = pd.read_excel(file_path)
    return df

# Função para combinar os dados de filtros com os dados da variável
def combine_data_with_filters(filtros_df, variable_df, years=None, municipios=None):
    # Filtragem prévia por anos, se especificado
    if years is not None and years:
        filtros_df = filtros_df[filtros_df['ANO'].isin(years)]
    
    # Criar índices para acelerar o merge
    filtros_df = filtros_df.set_index(['CD_MUN', 'ANO'])
    variable_df = variable_df.set_index(['CD_MUN', 'ANO'])
    
    # Join com sufixos para evitar conflito de colunas
    merged_df = filtros_df.join(variable_df, how='left', lsuffix='_filtros', rsuffix='_variavel').reset_index()
    
    # Filtrar por municípios, se especificado
    if municipios:
        merged_df = merged_df[merged_df['NM_MUN_filtros'].isin(municipios)]
    
    return merged_df

# Função para combinar dados de múltiplas variáveis, permitindo diferentes seções
def load_multiple_variables(section_variable_pairs, years=None, municipios=None):
    filtros_df = load_filters()
    combined_dfs = []
    
    for section, variable in section_variable_pairs:
        variable_df = load_variable_data(section, variable)
        merged_df = combine_data_with_filters(filtros_df, variable_df, years=years, municipios=municipios)
        # Renomear a coluna VALOR para o nome da variável
        merged_df = merged_df.rename(columns={'VALOR': variable})
        # Selecionar apenas as colunas necessárias
        merged_df = merged_df[['CD_MUN', 'ANO', 'NM_MUN_filtros', variable]]
        combined_dfs.append(merged_df)
    
    # Combinar todos os DataFrames
    result_df = combined_dfs[0]
    for df in combined_dfs[1:]:
        result_df = result_df.merge(
            df[['CD_MUN', 'ANO', df.columns[-1]]], 
            on=['CD_MUN', 'ANO'], 
            how='inner'  # Usar inner para garantir dados comuns
        )
    
    return result_df