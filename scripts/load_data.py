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
def combine_data_with_filters(filtros_df, variable_df, year=None, municipios=None):
    # Filtragem prévia por ano, se especificado
    if year is not None:
        filtros_df = filtros_df[filtros_df['ANO'] == year]
    
    # Criar índices para acelerar o merge
    filtros_df = filtros_df.set_index(['CD_MUN', 'ANO'])
    variable_df = variable_df.set_index(['CD_MUN', 'ANO'])
    
    # Join com sufixos para evitar conflito de colunas
    merged_df = filtros_df.join(variable_df, how='left', lsuffix='_filtros', rsuffix='_variavel').reset_index()
    
    # Filtrar por municípios, se especificado
    if municipios:
        merged_df = merged_df[merged_df['NM_MUN_filtros'].isin(municipios)]
    
    return merged_df