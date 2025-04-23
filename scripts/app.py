import dash
from dash import dcc, html, Input, Output
import plotly.express as px
import pandas as pd
from scipy import stats
import os
from load_data import load_filters, load_variable_data, combine_data_with_filters  # Funções de carregamento de dados

# Inicializando o app Dash
app = dash.Dash(__name__, suppress_callback_exceptions=True)

# Função para carregar arquivos da seção
def load_section_files(area):
    section_path = f"../data/dw/{area}/"
    files = [f for f in os.listdir(section_path) if f.endswith('.xlsx')]
    return files

# Layout do app
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    
    html.Div([
        # Menu de navegação lateral
        html.H2("Menu"),
        dcc.Link("Ambiental", href="/ambiental", className="menu-item"),
        dcc.Link("Saúde", href="/saude", className="menu-item"),
        dcc.Link("Geografia", href="/geografia", className="menu-item"),
        dcc.Link("Predição", href="/predicao", className="menu-item"),
    ], className="sidebar"),

    html.Div([
        html.H1("Dashboard Interativo"),
        html.Div([
            dcc.Dropdown(id="ano-dropdown"),# options=[{'label': str(i), 'value': i} for i in range(1999, 2023)], value=2023),
            dcc.Dropdown(id="variavel-dropdown"),
            dcc.Dropdown(id="municipio-dropdown", multi=True, placeholder="Selecione o município"), # Filtro de municípios
            dcc.Graph(id="grafico"),
            html.Div(id='estatisticas')
        ], className="content"),
    ], className="main-content")
])



# Callback para atualizar as variáveis no dropdown com base na seção
@app.callback(
    Output('municipio-dropdown', 'options'),  # Corrigido para 'municipio-dropdown'
    [Input('url', 'pathname'),
     Input('ano-dropdown', 'value')]
)
def update_cidade_dropdown(pathname, year):
    section = pathname.strip('/')
    
    if not section or not year:
        return []
    
    # Carregar filtros para a seção selecionada e filtrar por ano
    filtros_df = load_filters()
    filtros_df = filtros_df[filtros_df['ANO'] == year]  # Filtrar pelo ano
    
    # Obter as cidades únicas para o ano selecionado
    city_options = [{'label': city, 'value': city} for city in filtros_df['NM_MUN'].unique()]
    
    return city_options

@app.callback(
    Output('ano-dropdown', 'options'),
    [Input('url', 'pathname')]
)
def update_ano_dropdown(pathname):
    section = pathname.strip('/')
    
    if not section:
        return []
    
    # Carregar os filtros para a seção selecionada
    filtros_df = load_filters()
    
    # Obter os anos únicos para a seção
    anos = filtros_df['ANO'].unique()
    ano_options = [{'label': str(ano), 'value': ano} for ano in sorted(anos)]  # Organizar os anos em ordem crescente
    
    return ano_options

@app.callback(
    Output('variavel-dropdown', 'options'),
    [Input('url', 'pathname')]
)
def update_variable_dropdown(pathname):
    section = pathname.strip('/')
    if section:
        files = load_section_files(section)
        variable_options = [{'label': file.split('.')[0], 'value': file.split('.')[0]} for file in files]
        return variable_options
    return []


# Função para calcular estatísticas
def calculate_statistics(df, variavel):
    stats_result = {}  # Renomeando para evitar conflito com o nome da biblioteca
    
    if variavel in df.columns:
        # Garantir que a coluna 'VALOR' é numérica e tratar valores inválidos
        df[variavel] = pd.to_numeric(df[variavel], errors='coerce')  # Converte para numérico, 'coerce' converte erros para NaN
        
        # Remover valores NaN antes de calcular as estatísticas
        df_clean = df[variavel].dropna()  # Removendo NaNs para as estatísticas

        # Calcular as estatísticas
        if not df_clean.empty:
            stats_result['mean'] = df_clean.mean()
            stats_result['median'] = df_clean.median()
            stats_result['std_dev'] = df_clean.std()
            stats_result['kurtosis'] = stats.kurtosis(df_clean, nan_policy='omit')  # Usando scipy.stats.kurtosis
        else:
            stats_result = {key: None for key in ['mean', 'median', 'std_dev', 'kurtosis']}
    else:
        stats_result = {key: None for key in ['mean', 'median', 'std_dev', 'kurtosis']}

    # Verifique os tipos de dados após a conversão
    print(df[variavel].dtype)  # Deve mostrar 'float64' ou 'int64'
       
    return stats_result

# Callback para atualizar o gráfico e as estatísticas
@app.callback(
    [Output('grafico', 'figure'),
     Output('estatisticas', 'children')],
    [Input('url', 'pathname'), 
     Input('ano-dropdown', 'value'), 
     Input('variavel-dropdown', 'value'),
     Input('municipio-dropdown', 'value')]  # Novo filtro de município
)
def update_graph_and_statistics(pathname, year, variavel, municipios):
    section = pathname.strip('/')
    
    if not section or not variavel:
        return {}, ""

    # Carregar filtros e dados da variável
    filtros_df = load_filters()
    variable_df = load_variable_data(section, variavel)
    
    # Filtrar pelos anos
    if year:
        filtros_df = filtros_df[filtros_df['ANO'] == year]  # Filtrar pelo ano
    
    # Combinar dados de filtros com a variável
    combined_df = combine_data_with_filters(filtros_df, variable_df)
    
    # Filtrar dados de acordo com os municípios selecionados
    if municipios:
        combined_df = combined_df[combined_df['NM_MUN_x'].isin(municipios)]  # Filtra pelos municípios selecionados
    
    # Verificar se os dados estão sendo carregados corretamente
    if combined_df.empty:
        return {}, "Nenhum dado encontrado para a combinação de filtros"

    # Calcular estatísticas com base no campo 'VALOR'
    stats = calculate_statistics(combined_df, 'VALOR')
    
    # Criar o gráfico
    fig = px.bar(combined_df, x='NM_MUN_x', y='VALOR', title=f'{variavel} - {section} ({year})')

    # Exibir estatísticas
    stats_text = [
        html.Div(f"Média: {stats['mean']:.2f}" if stats['mean'] is not None else "Média: Dados insuficientes"),
        html.Div(f"Mediana: {stats['median']:.2f}" if stats['median'] is not None else "Mediana: Dados insuficientes"),
        html.Div(f"Desvio Padrão: {stats['std_dev']:.2f}" if stats['std_dev'] is not None else "Desvio Padrão: Dados insuficientes"),
        html.Div(f"Curtose: {stats['kurtosis']:.2f}" if stats['kurtosis'] is not None else "Curtose: Dados insuficientes")
    ]

    return fig, stats_text


# Rodar o servidor
if __name__ == '__main__':
    app.run_server(debug=True)
