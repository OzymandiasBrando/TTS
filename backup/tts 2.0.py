import tkinter as tk
import tkinter.ttk as ttk
import threading
import datetime
import queue
import random
import string
import time
import os
from gtts import gTTS  # pyright: ignore[reportMissingImports]
from pygame import mixer  # pyright: ignore[reportMissingImports]

# === CONFIGURAR O MIXER PARA SAÍDA NO CABLE INPUT ===
mixer.init(devicename="CABLE Input (VB-Audio Virtual Cable)")

# --- FUNÇÃO PARA GERAR NOMES DE ARQUIVOS TEMPORÁRIOS ---
def generate_random_string(length=8):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

# Configurações iniciais
tts_volume = 0.5
selected_language = "pt-br"  # idioma padrão

# --- TODOS OS IDIOMAS SUPORTADOS PELO gTTS ---
languages_map = {
    "Afrikaans": "af",
    "Albanês": "sq",
    "Amárico": "am",
    "Árabe": "ar",
    "Basco": "eu",
    "Bengali": "bn",
    "Bósnio": "bs",
    "Catalão": "ca",
    "Cebuano": "ceb",
    "Chichewa": "ny",
    "Chinês (Mandarim)": "zh-CN",
    "Chinês (Taiwan)": "zh-TW",
    "Croata": "hr",
    "Tcheco": "cs",
    "Dinamarquês": "da",
    "Holandês": "nl",
    "Inglês": "en",
    "Esperanto": "eo",
    "Estoniano": "et",
    "Filipino": "tl",
    "Finlandês": "fi",
    "Francês": "fr",
    "Frísio": "fy",
    "Galego": "gl",
    "Georgiano": "ka",
    "Alemão": "de",
    "Grego": "el",
    "Guarani": "gn",
    "Gujarati": "gu",
    "Haitiano": "ht",
    "Hausa": "ha",
    "Havaiano": "haw",
    "Hebraico": "he",
    "Hindi": "hi",
    "Hmong": "hmn",
    "Húngaro": "hu",
    "Islandês": "is",
    "Igbo": "ig",
    "Indonésio": "id",
    "Irlandês": "ga",
    "Italiano": "it",
    "Japonês": "ja",
    "Javanês": "jv",
    "Canarês": "kn",
    "Cazaque": "kk",
    "Khmer": "km",
    "Coreano": "ko",
    "Curdí (Kurmanji)": "ku",
    "Quirguiz": "ky",
    "Lao": "lo",
    "Latim": "la",
    "Letão": "lv",
    "Lituano": "lt",
    "Luxemburguês": "lb",
    "Macedônio": "mk",
    "Malgaxe": "mg",
    "Malaio": "ms",
    "Malaiala": "ml",
    "Maori": "mi",
    "Marathi": "mr",
    "Mongol": "mn",
    "Myanmar (Burmês)": "my",
    "Nepali": "ne",
    "Norueguês": "no",
    "Nyanja": "ny",
    "Odia (Oriya)": "or",
    "Pashto": "ps",
    "Persa": "fa",
    "Polonês": "pl",
    "Português (Brasil)": "pt-br",
    "Português (Portugal)": "pt-pt",
    "Punjabi": "pa",
    "Romeno": "ro",
    "Russo": "ru",
    "Sérvio": "sr",
    "Sesotho": "st",
    "Shona": "sn",
    "Sindhi": "sd",
    "Sinhala": "si",
    "Eslovaco": "sk",
    "Esloveno": "sl",
    "Somali": "so",
    "Espanhol": "es",
    "Sundanês": "su",
    "Suaíli": "sw",
    "Sueco": "sv",
    "Tajique": "tg",
    "Tamil": "ta",
    "Tártaro": "tt",
    "Telugu": "te",
    "Tailandês": "th",
    "Turco": "tr",
    "Turcomeno": "tk",
    "Ucraniano": "uk",
    "Urdu": "ur",
    "Uigur": "ug",
    "Uzbeque": "uz",
    "Vietnamita": "vi",
    "Galês": "cy",
    "Xhosa": "xh",
    "Iídiche": "yi",
}

# --- FUNÇÃO PARA FALAR ---
def speak_text(text, lang):
    if text.strip():
        tts = gTTS(text=text, lang=lang)
        filename = f"{generate_random_string()}.mp3"
        tts.save(filename)
        mixer.music.load(filename)
        mixer.music.set_volume(tts_volume)
        mixer.music.play()
        while mixer.music.get_busy():
            time.sleep(0.1)
        mixer.music.unload()
        os.remove(filename)

# --- FILA E THREAD DO TTS ---
tts_queue = queue.Queue()
def tts_worker():
    while True:
        item = tts_queue.get()
        if item is None:
            break
        text, lang = item
        speak_text(text, lang)
        tts_queue.task_done()

# --- FUNÇÕES DE INTERFACE ---
def on_enter(event=None):
    text = entry.get()
    if text.strip().lower() in ("sair", "exit", "quit"):
        tts_queue.put(None)
        root.destroy()
    elif text.strip():
        now = datetime.datetime.now().strftime("%H:%M:%S")
        history_text.config(state=tk.NORMAL)
        history_text.insert(tk.END, f"[{now}] {text}\n")
        history_text.insert(tk.END, "─" * 20 + "\n")
        history_text.config(state=tk.DISABLED)
        entry.delete(0, tk.END)
        tts_queue.put((text, selected_language))
        update_message_count()

def on_language_change(event=None):
    global selected_language
    selected_language = languages_map[language_combo.get()]

def set_volume(val):
    global tts_volume
    tts_volume = float(val)

def update_message_count():
    message_count.set(message_count.get() + 1)
    count_label.config(text=f"Mensagens: {message_count.get()}")

def clear_history():
    history_text.config(state=tk.NORMAL)
    history_text.delete(1.0, tk.END)
    history_text.config(state=tk.DISABLED)

def repeat_last():
    history_text.config(state=tk.NORMAL)
    lines = history_text.get(1.0, tk.END).strip().split("\n")
    history_text.config(state=tk.DISABLED)
    last = [l for l in lines if l.startswith("[")]
    if last:
        msg = last[-1].split("]", 1)[-1].strip()
        tts_queue.put((msg, selected_language))

# --- INTERFACE TKINTER ---
root = tk.Tk()
root.title("TTS Interface")
root.configure(bg="#181a20")

style = ttk.Style()
style.theme_use("clam")
style.configure("TLabel", background="#181a20", foreground="#ffffff", font=("Segoe UI", 13, "bold"))
style.configure("TButton", background="#23272f", foreground="#ffffff", font=("Segoe UI", 12, "bold"), padding=8)
style.configure("TEntry", fieldbackground="#23272f", foreground="#ffffff", font=("Segoe UI", 12))
style.configure("TCombobox", fieldbackground="#23272f", background="#23272f", foreground="#ffffff", font=("Segoe UI", 12, "bold"))
style.configure("TScale", background="#181a20", troughcolor="#23272f")

# Entrada de texto
frame = ttk.Frame(root, padding=15, style="TFrame")
frame.pack(padx=10, pady=10, fill=tk.X)
entry = ttk.Entry(frame, font=("Segoe UI", 12))
entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=8, padx=(0, 10))
entry.bind("<Return>", on_enter)
button = ttk.Button(frame, text="Falar", command=on_enter)
button.pack(side=tk.LEFT, padx=(0, 10), ipadx=12, ipady=8)

# Slider de volume
slider_frame = ttk.Frame(root, padding=10, style="TFrame")
slider_frame.pack(padx=10, pady=(0,10), fill=tk.X)
volume_label = ttk.Label(slider_frame, text="Volume", style="TLabel")
volume_label.pack(side=tk.LEFT, padx=(0,10))
volume_slider = ttk.Scale(slider_frame, from_=0, to=1, orient=tk.HORIZONTAL, command=set_volume, length=250)
volume_slider.set(tts_volume)
volume_slider.pack(side=tk.LEFT, padx=(0,20))

# Combobox de idioma
language_frame = ttk.Frame(root, padding=10, style="TFrame")
language_frame.pack(padx=10, pady=(0,10), fill=tk.X)
ttk.Label(language_frame, text="Escolha o idioma:", style="TLabel").pack(side=tk.LEFT, padx=(0,10))
language_combo = ttk.Combobox(language_frame, values=list(languages_map.keys()), state="readonly", width=30, font=("Segoe UI", 12, "bold"))
language_combo.pack(side=tk.LEFT, padx=(0,10))
language_combo.current(list(languages_map.values()).index("pt-br"))
language_combo.bind("<<ComboboxSelected>>", on_language_change)

# Histórico de mensagens
history_frame = ttk.Frame(root, padding=10, style="TFrame")
history_frame.pack(padx=10, pady=(0,10), fill=tk.BOTH, expand=True)
history_label = ttk.Label(history_frame, text="Histórico de mensagens:", style="TLabel")
history_label.pack(anchor="w")
history_text = tk.Text(history_frame, width=50, height=10, font=("Segoe UI", 12, "bold"), bg="#23272f", fg="#00ffae", borderwidth=0, highlightthickness=1, relief="solid", wrap=tk.WORD)
history_text.pack(fill=tk.BOTH, expand=True, pady=(5,0))
history_text.config(state=tk.DISABLED)

message_count = tk.IntVar(value=0)
count_label = ttk.Label(history_frame, text="Mensagens: 0", style="TLabel")
count_label.pack(anchor="w", pady=(0,5))
clear_button = ttk.Button(history_frame, text="Limpar histórico", command=clear_history, style="TButton")
clear_button.pack(anchor="e", pady=(5,0))
repeat_button = ttk.Button(history_frame, text="Repetir última", command=repeat_last, style="TButton")
repeat_button.pack(anchor="e", pady=(5,0))

info_label = ttk.Label(root, text="Certifique-se que o 'Cable Input' está como saída de áudio do programa!", style="TLabel")
info_label.pack(pady=(0,10))

# Inicia a thread do TTS
threading.Thread(target=tts_worker, daemon=True).start()
root.mainloop()
