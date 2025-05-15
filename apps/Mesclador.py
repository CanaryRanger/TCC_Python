import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import pandas as pd
import os
import time

def centralizar_janela(janela, largura, altura):
    largura_tela = janela.winfo_screenwidth()
    altura_tela = janela.winfo_screenheight()

    pos_x = (largura_tela // 2) - (largura // 2)
    pos_y = (altura_tela // 2) - (largura // 2)

    janela.geometry(f'{largura}x{altura}+{pos_x}+{pos_y}')

def selecionar_arquivo_base():
    arquivo = filedialog.askopenfilename(title="Selecione o arquivo base", filetypes=[("Arquivo Excel", "*.xlsx")])
    if arquivo:
        base_var.set(arquivo)

def selecionar_arquivo_informacoes():
    arquivo = filedialog.askopenfilename(title="Selecione o arquivo de informações", filetypes=[("Arquivo Excel", "*.xlsx")])
    if arquivo:
        info_var.set(arquivo)

def selecionar_diretorio():
    diretorio = filedialog.askdirectory(title="Selecione o diretório de saída")
    if diretorio:
        saida_var.set(diretorio)

def realizar_juncao():
    try:
        arquivo_base = base_var.get()
        arquivo_info = info_var.get()
        diretorio_saida = saida_var.get()

        if not arquivo_base or not arquivo_info or not diretorio_saida:
            messagebox.showerror("Erro", "Por favor, selecione os arquivos e o diretório de saída.")
            return

        # Atualizar barra de progresso para iniciar
        barra_progresso.start()

        # Carregar arquivos
        time.sleep(1)  # Simulando atraso para mostrar progresso
        df_base = pd.read_excel(arquivo_base)
        df_info = pd.read_excel(arquivo_info)

        # Atualizar a barra de progresso
        barra_progresso.step(25)

        # Verificar qual coluna existe na tabela base e complementar a informação
        if 'CD_MUN' in df_base.columns and 'NM_MUN' not in df_base.columns:
            if 'NM_MUN' in df_info.columns:
                # Complementar com NM_MUN a partir do df_info
                df_resultante = pd.merge(df_base, df_info[['CD_MUN', 'NM_MUN']], how='left', on='CD_MUN')
                # Reorganizar colunas: CD_MUN, NM_MUN, ...
                colunas_ordenadas = ['CD_MUN', 'NM_MUN'] + [col for col in df_resultante.columns if col not in ['CD_MUN', 'NM_MUN']]
                df_resultante = df_resultante[colunas_ordenadas]
            else:
                barra_progresso.stop()
                messagebox.showerror("Erro", "A tabela de informações não contém a coluna NM_MUN necessária para complementar a tabela base.")
                return
        elif 'NM_MUN' in df_base.columns and 'CD_MUN' not in df_base.columns:
            if 'CD_MUN' in df_info.columns:
                # Complementar com CD_MUN a partir do df_info
                df_resultante = pd.merge(df_base, df_info[['CD_MUN', 'NM_MUN']], how='left', on='NM_MUN')
                # Reorganizar colunas: CD_MUN, NM_MUN, ...
                colunas_ordenadas = ['CD_MUN', 'NM_MUN'] + [col for col in df_resultante.columns if col not in ['CD_MUN', 'NM_MUN']]
                df_resultante = df_resultante[colunas_ordenadas]
            else:
                barra_progresso.stop()
                messagebox.showerror("Erro", "A tabela de informações não contém a coluna CD_MUN necessária para complementar a tabela base.")
                return
        else:
            barra_progresso.stop()
            messagebox.showerror("Erro", "A tabela base deve conter apenas uma das colunas: CD_MUN ou NM_MUN.")
            return

        # Atualizar a barra de progresso
        barra_progresso.step(50)

        # Salvar o nome do arquivo com o nome da pasta de nível superior ao destino
        nome_pasta = os.path.basename(os.path.dirname(diretorio_saida))
        nome_arquivo = os.path.basename(arquivo_base).replace('.xlsx', f'_{nome_pasta}.xlsx')
        caminho_saida = os.path.join(diretorio_saida, nome_arquivo)
        df_resultante.to_excel(caminho_saida, index=False)

        # Atualizar a barra de progresso
        barra_progresso.step(25)

        # Completar e parar a barra de progresso
        barra_progresso.stop()
        messagebox.showinfo("Sucesso", f"Juncao realizada com sucesso! Dados salvos em: {caminho_saida}")
    
    except Exception as e:
        barra_progresso.stop()
        messagebox.showerror("Erro", f"Ocorreu um erro: {str(e)}")

def mostrar_mensagem():
    messagebox.showinfo("Bem-vindo", "Este aplicativo realiza um complemento de dados entre duas tabelas Excel, trazendo o nome ou o código do município que estiver ausente.")

# Criação da janela principal
janela = tk.Tk()
janela.title("Aplicativo de Junção de Dados")

# Definir as dimensões da janela e centralizá-la
largura_janela = 400
altura_janela = 400
centralizar_janela(janela, largura_janela, altura_janela)

base_var = tk.StringVar()
info_var = tk.StringVar()
saida_var = tk.StringVar()

# Botões e entradas
tk.Label(janela, text="Arquivo base:").pack(pady=5)
tk.Entry(janela, textvariable=base_var, width=50).pack(pady=5)
tk.Button(janela, text="Selecionar Arquivo Base", command=selecionar_arquivo_base).pack(pady=5)

tk.Label(janela, text="Arquivo de informações:").pack(pady=5)
tk.Entry(janela, textvariable=info_var, width=50).pack(pady=5)
tk.Button(janela, text="Selecionar Arquivo de Informações", command=selecionar_arquivo_informacoes).pack(pady=5)

tk.Label(janela, text="Diretório de saída:").pack(pady=5)
tk.Entry(janela, textvariable=saida_var, width=50).pack(pady=5)
tk.Button(janela, text="Selecionar Diretório", command=selecionar_diretorio).pack(pady=5)

# Barra de progresso
barra_progresso = ttk.Progressbar(janela, orient="horizontal", length=300, mode="determinate")
barra_progresso.pack(pady=10)

tk.Button(janela, text="Realizar Junção", command=realizar_juncao, bg="green", fg="white").pack(pady=20)

# Mensagem inicial
mostrar_mensagem()

# Executar a janela
janela.mainloop()