import os
import tkinter as tk
from tkinter import ttk, messagebox
import pyautogui
import threading
import time
import pygetwindow as gw
from PIL import Image, ImageTk
import requests
import sys

# Função para obter o caminho correto para os recursos no executável
def resource_path(relative_path):
    """Obter o caminho correto para os recursos no executável."""
    try:
        # PyInstaller cria um caminho temporário para o executável
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

# Variáveis globais
running = False
interval = 300  # Intervalo inicial em segundos (5 minutos)
start_time = None
countdown = 0
key_sequence = ['w', 'a', 's', 'd', 'space', 'ctrl', 'space', 'b', 'mouse1']
key_delay = 1
minimize_game = False

# Chaves válidas
valid_keys = {"UTOPIA-79G9KDJFDZ", "UTOPIA-K7MZ3X9FJ2", "UTOPIA-F1LQ4E6MNB8", "FARMDEXP", "GRINDERS"}

# Função para verificar atualizações
def check_for_updates(current_version):
    repo_url = "https://api.github.com/repos/arthursiimoes/UtopiaFortniteBot/releases/latest"
    response = requests.get(repo_url)
    
    if response.status_code == 200:
        latest_version = response.json()["tag_name"]
        if latest_version > current_version:
            messagebox.showinfo("Atualização Disponível", f"Uma nova versão {latest_version} está disponível. Por favor, atualize.")
            # Opcionalmente, você pode abrir o navegador para a página de lançamentos
            # import webbrowser
            # webbrowser.open("https://github.com/arthursiimoes/UtopiaFortniteBot/releases/latest")

# Função para iniciar o bot
def start_bot():
    global running, start_time, countdown
    key = key_entry.get()  # Obtém a chave do campo de entrada
    if key in valid_keys:  # Verifica se a chave é válida
        entry_window.destroy()  # Fecha a janela de entrada
        open_main_window()  # Abre a janela principal do bot
    else:
        messagebox.showerror("Erro", "Chave inválida!")  # Exibe erro se a chave for inválida

def open_main_window():
    """Abre a janela principal do bot."""
    global main_window
    current_version = "v0.1"  # Atualize para a versão atual
    check_for_updates(current_version)  # Verifica se há atualizações

    # Cria a janela principal
    main_window = tk.Tk()
    main_window.title("XP BOT v0.1")
    main_window.geometry("280x400")
    main_window.configure(bg="#2C2F33")
    main_window.resizable(False, False)

    # Verifica se a imagem do ícone existe antes de carregar
    icon_path = resource_path("imagens/u.png")
    if os.path.exists(icon_path):
        main_window.iconphoto(False, ImageTk.PhotoImage(Image.open(icon_path)))
    else:
        print(f"Imagem de ícone '{icon_path}' não encontrada.")

    # Estilos e cores
    style = ttk.Style()
    style.theme_use('clam')
    style.configure("TButton", background="#7289DA", foreground="#FFFFFF", font=("Arial", 10), borderwidth=1, focuscolor='none')
    style.map("TButton", background=[('active', '#5B7FBA')])

    # Logo do aplicativo
    logo_path = resource_path("imagens/utopia.png")
    if os.path.exists(logo_path):
        logo_img = Image.open(logo_path)
        logo_img = logo_img.resize((300, 100), Image.ANTIALIAS)
        logo_photo = ImageTk.PhotoImage(logo_img)

        logo_label = tk.Label(main_window, image=logo_photo, bg="#2C2F33")
        logo_label.grid(row=0, columnspan=2, pady=10)
    else:
        print(f"Imagem de logo '{logo_path}' não encontrada.")

    # Botões Iniciar e Parar
    start_button = ttk.Button(main_window, text="Iniciar", command=start_bot)
    start_button.grid(row=1, column=0, padx=10, pady=10)

    stop_button = ttk.Button(main_window, text="Parar", command=stop_bot)
    stop_button.grid(row=1, column=1, padx=10, pady=10)

    # Dropdown para escolher o intervalo
    interval_var = tk.StringVar(value="5 minutos")
    interval_dropdown = ttk.Combobox(main_window, textvariable=interval_var, values=["1 minuto", "3 minutos", "5 minutos", "10 minutos"], width=12)
    interval_dropdown.grid(row=2, column=0, padx=10, pady=(5, 0), sticky='ew')

    def on_interval_change(event):
        selected = interval_var.get()
        if "1 minuto" in selected:
            update_interval(60)
        elif "3 minutos" in selected:
            update_interval(180)
        elif "5 minutos" in selected:
            update_interval(300)
        elif "10 minutos" in selected:
            update_interval(600)

    interval_dropdown.bind("<<ComboboxSelected>>", on_interval_change)

    # Checkbox para minimizar o jogo
    minimize_var = tk.IntVar()
    minimize_checkbox = tk.Checkbutton(main_window, text="Minimizar o jogo", variable=minimize_var, command=toggle_minimize,
                                       font=("Arial", 10), fg="#FFFFFF", bg="#2C2F33", activebackground="#2C2F33", activeforeground="#FFFFFF")
    minimize_checkbox.grid(row=2, column=1, padx=10, pady=(5, 0), sticky="w")

    # Labels de contagem regressiva
    countdown_label = tk.Label(main_window, text="Próximo Movimento: 00:00", font=("Arial", 12, "bold"), fg="#FFFFFF", bg="#2C2F33")
    countdown_label.grid(row=4, column=0, columnspan=2, pady=5)

    elapsed_label = tk.Label(main_window, text="Tempo total rodando: 00:00:00", font=("Arial", 10), fg="#FFFFFF", bg="#2C2F33")
    elapsed_label.grid(row=5, column=0, columnspan=2, pady=5)

    # Botão de mais informações
    info_button = ttk.Button(main_window, text="Mais informações", command=show_info)
    info_button.grid(row=6, column=0, columnspan=2, pady=15)

    # Inicia a janela principal
    main_window.mainloop()

def stop_bot():
    global running
    running = False

def bot_loop():
    global countdown
    while running:
        if countdown <= 0:
            press_keys_in_sequence()
            countdown = interval
        else:
            countdown -= 1
        time.sleep(1)

def press_keys_in_sequence():
    for key in key_sequence:
        if not running:
            break
        if key == 'mouse1':
            pyautogui.click(button='left')
        else:
            pyautogui.keyDown(key)
            time.sleep(key_delay)
            pyautogui.keyUp(key)
        time.sleep(0.5)

def update_countdown():
    if running:
        elapsed = time.time() - start_time
        elapsed_label.config(text=f"Tempo total rodando: {time_format(elapsed)}")
        countdown_label.config(text=f"Próximo Movimento: {time_format(countdown)}")
        main_window.after(1000, update_countdown)

def time_format(seconds):
    mins, secs = divmod(int(seconds), 60)
    return f"{mins:02}:{secs:02}"

def update_interval(val):
    global interval
    interval = int(val)
    countdown_label.config(text=f"Próximo Movimento: {time_format(interval)}")

def minimize_fortnite():
    global minimize_game
    if minimize_game:
        fortnite_window = gw.getWindowsWithTitle('Fortnite')
        if fortnite_window:
            fortnite_window[0].minimize()

def toggle_minimize():
    global minimize_game
    minimize_game = not minimize_game
    if minimize_game:
        minimize_fortnite()

def show_info():
    info_window = tk.Toplevel(main_window)
    info_window.title("Mais Informações")
    info_label = tk.Label(info_window, text="Este bot simula pressionamentos de tecla para evitar que o jogo seja minimizado ou desconecte por inatividade.")
    info_label.pack(padx=20, pady=20)

# Janela de entrada da chave
entry_window = tk.Tk()
entry_window.title("Entrada de Chave")
entry_window.geometry("300x150")
entry_window.configure(bg="#2C2F33")

# Campo de entrada para chave
key_label = tk.Label(entry_window, text="Digite sua chave:", bg="#2C2F33", fg="#FFFFFF")
key_label.pack(pady=(20, 5))

key_entry = tk.Entry(entry_window, bg="#FFFFFF", fg="#000000")
key_entry.pack(pady=(0, 20))

# Botão para validar a chave
validate_button = ttk.Button(entry_window, text="Validar", command=start_bot)
validate_button.pack(pady=10)

# Inicia a janela de entrada
entry_window.mainloop()
