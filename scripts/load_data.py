import pandas as pd

# Função para carregar os dados de filtros
def load_filters():
    filtros_path = "../data/dw/Filtros.xlsx"
    filtros_df = pd.read_excel(filtros_path)
    return filtros_df

# Função para carregar os dados de uma variável (por exemplo, CH4, CO2)
def load_variable_data(area, variable):
    file_path = f"../data/dw/{area}/{variable}.xlsx"  # Ajuste conforme necessário
    df = pd.read_excel(file_path)
    return df

# Função para combinar os dados de filtros com os dados da variável
def combine_data_with_filters(filtros_df, variable_df):
    # Join entre os filtros e os dados da variável com base nas colunas de município e ano
    merged_df = pd.merge(filtros_df, variable_df, how="left", on=["CD_MUN", "ANO"])
    return merged_df
