import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import pandas as pd
import os
import time
import re

def centralizar_janela(janela, largura, altura):
    largura_tela = janela.winfo_screenwidth()
    altura_tela = janela.winfo_screenheight()

    pos_x = (largura_tela // 2) - (largura // 2)
    pos_y = (altura_tela // 2) - (largura // 2)

    janela.geometry(f'{largura}x{altura}+{pos_x}+{pos_y}')

def selecionar_arquivo():
    arquivo = filedialog.askopenfilename(title="Selecione o arquivo Excel", filetypes=[("Arquivo Excel", "*.xlsx")])
    if arquivo:
        print(f"Arquivo selecionado: {arquivo}")
        entrada_var.set(arquivo)

def selecionar_diretorio():
    diretorio = filedialog.askdirectory(title="Selecione o diretório de saída")
    if diretorio:
        print(f"Diretório selecionado: {diretorio}")
        saida_var.set(diretorio)

def transformar_dados():
    try:
        arquivo = entrada_var.get()
        diretorio_saida = saida_var.get()

        if not arquivo or not diretorio_saida:
            messagebox.showerror("Erro", "Por favor, selecione o arquivo e o diretório de saída.")
            print("Erro: Arquivo ou diretório de saída não selecionado.")
            return

        # Atualizar barra de progresso para iniciar
        barra_progresso.start()
        print("Iniciando transformação de dados...")

        # Leitura do arquivo Excel
        time.sleep(1)  # Simulando atraso para mostrar progresso
        df = pd.read_excel(arquivo)
        print(f"Arquivo Excel lido com sucesso. Colunas encontradas: {df.columns.tolist()}")

        # Atualizar a barra de progresso
        barra_progresso.step(25)

        # Converter os nomes das colunas para string
        df.columns = df.columns.map(str)
        print("Nomes das colunas convertidos para string.")

        # Identificar colunas que possuem anos
        padrao_ano = re.compile(r'(\d{4})')  # Busca por um ano de quatro dígitos (ex.: 1999, 2000, 2021)
        colunas_ano = [col for col in df.columns if padrao_ano.search(col)]
        print(f"Colunas identificadas como anos: {colunas_ano}")

        if not colunas_ano:
            barra_progresso.stop()
            messagebox.showerror("Erro", "Não foram encontradas colunas com anos no formato esperado.")
            print("Erro: Nenhuma coluna com anos no formato esperado foi encontrada.")
            return

        # Criar lista para armazenar DataFrames
        dfs = []

        # Iterar sobre as colunas e derreter (melt) os dados
        for coluna in colunas_ano:
            ano_encontrado = coluna  # Mantém o ano encontrado como está, pois agora consideramos apenas anos de quatro dígitos
            print(f"Processando coluna: {coluna}, Ano encontrado: {ano_encontrado}")
            df_temp = df[['CD_MUN', 'NM_MUN', coluna]].copy()
            df_temp = df_temp.rename(columns={coluna: 'VALOR'})
            df_temp['ANO'] = ano_encontrado
            dfs.append(df_temp)

        # Concatenar todos os DataFrames
        df_resultante = pd.concat(dfs, ignore_index=True)
        print("DataFrames concatenados com sucesso.")

        # Atualizar a barra de progresso
        barra_progresso.step(50)

        # Salvar o nome do arquivo com o nome da pasta de nível superior ao destino
        nome_pasta = os.path.basename(os.path.dirname(diretorio_saida))
        nome_arquivo = os.path.basename(arquivo).replace('.xlsx', f'_{nome_pasta}.xlsx')
        caminho_saida = os.path.join(diretorio_saida, nome_arquivo)
        df_resultante.to_excel(caminho_saida, index=False)
        print(f"Arquivo transformado salvo em: {caminho_saida}")

        # Atualizar a barra de progresso
        barra_progresso.step(25)

        # Completar e parar a barra de progresso
        barra_progresso.stop()
        messagebox.showinfo("Sucesso", f"Dados transformados e salvos em: {caminho_saida}")
        print("Transformação de dados concluída com sucesso.")
    
    except Exception as e:
        barra_progresso.stop()
        messagebox.showerror("Erro", f"Ocorreu um erro: {str(e)}")
        print(f"Erro ocorrido: {str(e)}")

def mostrar_mensagem():
    messagebox.showinfo("Bem-vindo", "Este aplicativo transforma seus dados de Excel separando o ano e permitindo filtragem.")
    print("Mensagem de boas-vindas exibida.")

# Criação da janela principal
janela = tk.Tk()
janela.title("Transformador de Dados Excel")

# Definir as dimensões da janela e centralizá-la
largura_janela = 400
altura_janela = 300
centralizar_janela(janela, largura_janela, altura_janela)

entrada_var = tk.StringVar()
saida_var = tk.StringVar()

# Botões e entradas
tk.Label(janela, text="Arquivo de entrada:").pack(pady=5)
tk.Entry(janela, textvariable=entrada_var, width=50).pack(pady=5)
tk.Button(janela, text="Selecionar Arquivo", command=selecionar_arquivo).pack(pady=5)

tk.Label(janela, text="Diretório de saída:").pack(pady=5)
tk.Entry(janela, textvariable=saida_var, width=50).pack(pady=5)
tk.Button(janela, text="Selecionar Diretório", command=selecionar_diretorio).pack(pady=5)

# Barra de progresso
barra_progresso = ttk.Progressbar(janela, orient="horizontal", length=300, mode="determinate")
barra_progresso.pack(pady=10)

tk.Button(janela, text="Transformar", command=transformar_dados, bg="green", fg="white").pack(pady=20)

# Mensagem inicial
mostrar_mensagem()

# Executar a janela
janela.mainloop()