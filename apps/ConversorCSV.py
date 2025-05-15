import os
import pandas as pd
import tkinter as tk
from tkinter import filedialog, messagebox

# Função para selecionar diretório de entrada (onde estão os arquivos Excel)
def selecionar_diretorio_entrada():
    diretorio = filedialog.askdirectory()
    if diretorio:
        entrada_path.set(diretorio)

# Função para selecionar diretório de saída (onde os arquivos CSV serão salvos)
def selecionar_diretorio_saida():
    diretorio = filedialog.askdirectory()
    if diretorio:
        saida_path.set(diretorio)

# Função para converter os arquivos Excel para CSV
def converter_excel_para_csv():
    diretorio_entrada = entrada_path.get()
    diretorio_saida = saida_path.get()

    if not diretorio_entrada or not diretorio_saida:
        messagebox.showwarning("Erro", "Por favor, selecione os diretórios de entrada e saída.")
        return

    try:
        for arquivo in os.listdir(diretorio_entrada):
            if arquivo.endswith('.xlsx') or arquivo.endswith('.xls'):
                # Caminho completo do arquivo Excel
                caminho_excel = os.path.join(diretorio_entrada, arquivo)
                # Lê o arquivo Excel
                df = pd.read_excel(caminho_excel)
                
                # Gera o nome do arquivo CSV baseado no nome do Excel
                nome_csv = os.path.splitext(arquivo)[0] + '.csv'
                caminho_csv = os.path.join(diretorio_saida, nome_csv)
                
                # Salva o DataFrame como CSV
                df.to_csv(caminho_csv, index=False)
                print(f'Convertido: {arquivo} -> {nome_csv}')
        
        messagebox.showinfo("Sucesso", "Todos os arquivos foram convertidos com sucesso!")
    except Exception as e:
        messagebox.showerror("Erro", f"Ocorreu um erro: {str(e)}")

# Interface gráfica com tkinter
app = tk.Tk()
app.title("Conversor de Excel para CSV")

# Variáveis para armazenar os caminhos dos diretórios
entrada_path = tk.StringVar()
saida_path = tk.StringVar()

# Configuração da interface
tk.Label(app, text="Diretório de Entrada (Excel):").grid(row=0, column=0, padx=10, pady=10)
tk.Entry(app, textvariable=entrada_path, width=50).grid(row=0, column=1, padx=10, pady=10)
tk.Button(app, text="Selecionar", command=selecionar_diretorio_entrada).grid(row=0, column=2, padx=10, pady=10)

tk.Label(app, text="Diretório de Saída (CSV):").grid(row=1, column=0, padx=10, pady=10)
tk.Entry(app, textvariable=saida_path, width=50).grid(row=1, column=1, padx=10, pady=10)
tk.Button(app, text="Selecionar", command=selecionar_diretorio_saida).grid(row=1, column=2, padx=10, pady=10)

tk.Button(app, text="Converter Excel para CSV", command=converter_excel_para_csv, bg="green", fg="white").grid(row=2, column=1, pady=20)

# Inicializar a aplicação
app.mainloop()
