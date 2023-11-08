# Bilbiotecas
# nterface gráfica
from tkinter import *  
from tkinter import ttk, filedialog, messagebox 
import tkinter as tk
import pywhatkit    # bibliotecas para envio de mensagens
import keyboard     # controle de teclado
import time # controle de tempo
from datetime import datetime   # data e hora
import re   # expressões regulares
import pdfplumber   # leitura de arquivos PDF
import pyautogui    # controle de mause 
import threading    # controle de threads


cancelar_envio = False  # Variável para controle do cancelamento do envio
thread_envio = None # Variável para controle da thread de envio

log_file = 'PyWhatKit_DB.txt'   # Arquivo de log criado automaticamente

#  monta a tela principal do programa
def montaTela():
    global root

    root = tk.Tk() 
    
    root.title("WhatsApp Automatizado")
    # Pega a resolução da tela do usuário
    screen_width = root.winfo_screenwidth() 
    screen_height = root.winfo_screenheight()

    # Calcula a posição da janela 
    x = (screen_width / 2) - (825 / 2)
    y = (screen_height / 2) - (600 / 2)
    
    root.geometry('%dx%d+%d+%d' % (825, 600, x, y)) # Define a posição da janela e seu tamanho para que fique centralizada
    
    # Cria o frame principal da janela 
    mainframe = ttk.Frame(root, padding="3 3 12 12")   
    mainframe.grid(column=0, row=0, sticky=(N, W, E, S))    
    root.columnconfigure(0, weight=1)   
    root.rowconfigure(0, weight=1)  
    
    # Cria um titulo para o frame principal
    ttk.Label(mainframe, font=("Arial", 14, "bold"),  text="Mandar WhatsApp\n", anchor="center").grid(column=1, row=1, sticky=tk.W)    
        
    # Cria os botões de ação
    ttk.Button(mainframe, text="Histórico",  command=telaHistorico).grid(column=1, row=4, columnspan=3, sticky=tk.EW) 
    ttk.Button(mainframe, text="Mandar mensagem",  command=enviarMensagem).grid(column=1, row=5, columnspan=3, sticky=tk.EW) 
    ttk.Button(mainframe, text="Cancelar", command=cancelar).grid(column=1, row=6, columnspan=5, sticky=tk.EW) 


    root.mainloop() 

def anexar_arquivo():   # função para anexar o arquivo PDF abre uma janela para selecionar o arquivo em pdf
    return filedialog.askopenfilename()

def cancelar():     # função para cancelar o envio de mensagens e para fechar o programa
    global cancelar_envio, thread_envio
    if thread_envio is not None and thread_envio.is_alive():
        cancelar_envio = True
        root.destroy()
    else:
        root.destroy()

# Tela de histórico de mensagens enviadas 
def telaHistorico():    
    global date_entry   
    global name_entry
    global text_widget

    # Configuração da interface gráfica
    root = tk.Tk()
    root.title('Visualizador de Logs')

    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    x = (screen_width / 2) - (825 / 2)
    y = (screen_height / 2) - (600 / 2)

    root.geometry('%dx%d+%d+%d' % (825, 600, x, y))
    

    # Campos de entrada para pesquisa
    ttk.Label(root, text='Data:').grid(row=0, column=0, columnspan=1, sticky=tk.W)
    date_entry = ttk.Entry(root)
    date_entry.grid(row=0, column=1, columnspan=4, sticky=tk.EW)

    ttk.Label(root, text='Número:').grid(row=1, column=0, columnspan=1, sticky=tk.W)
    name_entry = ttk.Entry(root)
    name_entry.grid(row=1, column=1, columnspan=4, sticky=tk.EW)


    # Botões de filtro e sair
    ttk.Button(root, text='Pesquisar', command=search_logs).grid(row=2, column=0, columnspan=5, sticky=tk.EW)
    ttk.Button(root, text='Sair', command=root.destroy).grid(row=3, column=0, columnspan=5, sticky=tk.EW)

    # Widget de texto para exibição dos logs
    text_widget = tk.Text(root, wrap='word')
    text_widget.grid(row=4, column=0, columnspan=5, sticky='nsew')

    # Barra de rolagem para o widget de texto
    scrollbar = ttk.Scrollbar(root, command=text_widget.yview)
    scrollbar.grid(row=4, column=5, sticky='ns')
    text_widget['yscrollcommand'] = scrollbar.set

    # Iniciar com todos os logs
    update_display(read_logs())

    root.mainloop()

# Atualiza o widget de texto com os logs filtrados
def update_display(logs):
    text_widget.delete('1.0', tk.END)   # Limpa o widget de texto
    # Inserir os logs filtrados no widget de texto
    for log in logs:
        text_widget.insert(tk.END, log + '\n--------------------\n')

# Lê os logs do arquivo de texto
def read_logs():
    with open(log_file, 'r') as file:
        return file.read().split('--------------------\n')

# Pesquisa os logs com base nos campos de entrada   
def search_logs():
    date_query = date_entry.get().strip()
    phone_query = name_entry.get().strip()
    all_logs = read_logs()
    filtered_logs = []

    for log in all_logs:
        if date_query and phone_query:  # Se ambos os campos forem preenchidos
            if date_query in log and phone_query in log:
                filtered_logs.append(log)
        elif date_query or phone_query :  # Se apenas um campo for preenchido
            if (date_query in log) or (phone_query in log):
                filtered_logs.append(log)
        else:  # Se não for nada encontrado
            messagebox.showinfo("Erro", f"Não foi possivel encontrar o registro")

    update_display(filtered_logs)

# Extrai os números de telefone de um arquivo PDF
def estrairTelefonePDF():
    # Padrão para encontrar números de telefone no formato (XX) XXXX-XXXX
    pattern = re.compile(r'\(\d{2}\)\s\d{4}-\d{4}') 

    all_phones = []

    with pdfplumber.open(anexar_arquivo()) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            # Encontra todas as ocorrências do padrão no texto
            phones = pattern.findall(text)
            # Adiciona os números de telefone encontrados à lista
            all_phones.extend(phones)

   # Processa os números de telefone para remover caracteres indesejados e adicionar o prefixo +55
    phones = ['+55' + re.sub(r'[()\s-]', '', phone) for phone in all_phones]
    return phones     

# Envia as mensagens para os contatos
def enviarMensagem():
    contatos = estrairTelefonePDF()

    # Inicia a thread de envio de mensagens
    thread_envio = threading.Thread(target=enviarMensagensThread, args=(contatos,))
    thread_envio.start()

# Envia as mensagens para os contatos
def enviarMensagensThread(contatos):
    try:  # Tenta enviar as mensagens
        for i in range(len(contatos)):
            time.sleep(10)
            if cancelar_envio:
                break  # Interrompe o envio se o botão de cancelar foi clicado
            pywhatkit.sendwhatmsg(contatos[i], 'rtdyutdfyut', datetime.now().hour, datetime.now().minute + 1)
            time.sleep(20)  # Espera o navegador abrir e a mensagem ser enviada
            if cancelar_envio:
                break  # Interrompe o envio se o botão de cancelar foi clicado
            if not cancelar_envio:
                pyautogui.click(650, 800)   # Clica em uma posição no navegador para que ele fique em primeiro plano
                time.sleep(2)
                keyboard.press_and_release('enter') # Preciona a tecla para que seja feito o envio 
                time.sleep(5)
                keyboard.press_and_release('ctrl + w') # Preciona as teclas para fechar a aba do navegador  
    except Exception as e:  # Exibe uma mensagem de erro caso ocorra algum problema
        messagebox.showinfo("Erro", f"Não foi possivel enviar a mensagem. Tente novamente mais tarde.\nErro: {e}")



montaTela()     # Chama a execução do programa 