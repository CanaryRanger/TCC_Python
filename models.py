import pandas as pd
from scipy import stats
import os
import unicodedata
from load_data import load_filters, load_variable_data, combine_data_with_filters, load_multiple_variables, DATA_PATH

# Função para normalizar texto (remover acentos)
def normalize_text(text):
    """Remove acentos e converte para minúsculas para comparação."""
    if not text:
        return ""
    # Normalizar para decompor caracteres acentuados (ex.: 'ã' -> 'a' + '~')
    normalized = unicodedata.normalize('NFKD', str(text))
    # Remover diacríticos (acentos) e converter para minúsculas
    return ''.join(c for c in normalized if not unicodedata.combining(c)).lower()

# # Função para carregar arquivos da seção
# def load_section_files(area):
#     section_path = f"../data/dw/{area}/"
#     files = [f for f in os.listdir(section_path) if f.endswith('.xlsx')]
#     return files


def load_section_files(area):
    """Carrega os nomes dos arquivos de uma determinada seção."""
    section_path = os.path.join(DATA_PATH, area) # Caminho agora é absoluto
    if not os.path.exists(section_path):
        print(f"Aviso: O diretório não foi encontrado: {section_path}")
        return []
    return [f for f in os.listdir(section_path) if f.endswith('.xlsx')]

# Função para calcular estatísticas
def calculate_statistics(df, variavel, iqr_multiplier=1.5):
### --- Código para validação das bibliotecas e do join no load_data.py ---- ###

    # stats_result = {}
    # test_data = [0.1683943758618205, 0.1620977241191381, 0.163068919876716, 0.1681304393463355, 
    #              0.1801848566900228, 0.1861701572810068, 0.1911233408523403, 0.1960505982627124, 
    #              0.1873534914332561, 0.174532931273655, 0.1898552894342499, 0.1813390463457654, 
    #              0.1733742477811903, 0.1704589930843963, 0.1944022019148184, 0.07300360441573536, 
    #              0.1828029737904217, 0.0388038347042544, 0.09990405093895749, 0.0978581013179412, 
    #              0.08955969834464803, 0.09480092461753206, 0.1002783035770839]
    # df_clean = pd.Series(test_data)
    # print(f"Valores de teste: {df_clean.tolist()}")
    # print(f"Média: {df_clean.mean():.4f}, Desvio Padrão: {df_clean.std():.4f}")
    # stats_result['mean'] = df_clean.mean()
    # stats_result['median'] = df_clean.median()
    # stats_result['std_dev'] = df_clean.std()
    # kurtosis_scipy_pearson = stats.kurtosis(df_clean, nan_policy='omit', fisher=False)
    # kurtosis_scipy_fisher = stats.kurtosis(df_clean, nan_policy='omit', fisher=True)
    # kurtosis_pandas = df_clean.kurtosis()
    # print(f"Curtose (Scipy Pearson): {kurtosis_scipy_pearson:.2f}")
    # print(f"Curtose (Scipy Fisher): {kurtosis_scipy_fisher:.2f}")
    # print(f"Curtose (Pandas Fisher): {kurtosis_pandas:.2f}")
    # stats_result['kurtosis'] = kurtosis_scipy_pearson
    # q1 = df_clean.quantile(0.25)
    # q3 = df_clean.quantile(0.75)
    # iqr = q3 - q1
    # stats_result['lower_fence'] = q1 - iqr_multiplier * iqr
    # stats_result['upper_fence'] = q3 + iqr_multiplier * iqr
    # return stats_result

### ----                               FIM DOS TESTES                   ---- ###

    ## Definição para as variáveis para calcular estatisticas
    stats_result = {}
    if variavel in df.columns:
        df[variavel] = pd.to_numeric(df[variavel], errors='coerce')
        df_clean = df[variavel].dropna()
        if not df_clean.empty:
            stats_result['mean'] = df_clean.mean()
            stats_result['median'] = df_clean.median()
            stats_result['std_dev'] = df_clean.std()
            stats_result['kurtosis'] = stats.kurtosis(df_clean, nan_policy='omit', fisher=False)
            # Calcular cercas
            q1 = df_clean.quantile(0.25)
            q3 = df_clean.quantile(0.75)
            iqr = q3 - q1
            stats_result['lower_fence'] = q1 - iqr_multiplier * iqr
            stats_result['upper_fence'] = q3 + iqr_multiplier * iqr
        else:
            stats_result = {key: None for key in ['mean', 'median', 'std_dev', 'kurtosis', 'lower_fence', 'upper_fence']}
    else:
        stats_result = {key: None for key in ['mean', 'median', 'std_dev', 'kurtosis', 'lower_fence', 'upper_fence']}
    return stats_result