import pyttsx3
import tkinter as tk
import tkinter.ttk as ttk
import threading
import datetime
import queue
import random
import string
import time
import os
# Configurações iniciais

selected_voice_id = None
tts_rate = 160
tts_volume = 1.0


def get_voices():
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')
    return voices

voices = get_voices()

voice_names = []
for v in voices:
    lang = ""
    if hasattr(v, "languages") and v.languages:
        lang = v.languages[0].decode("utf-8") if isinstance(v.languages[0], bytes) else str(v.languages[0])
    voice_names.append(f"{v.name} ({lang})")

def set_rate(val):
    global tts_rate
    tts_rate = int(float(val))

def set_volume(val):
    global tts_volume
    tts_volume = float(val)

def speak_text(text, device_idx=None):
    if text.strip():
        engine = pyttsx3.init()
        engine.setProperty('rate', tts_rate)
        engine.setProperty('volume', tts_volume)
        if selected_voice_id:
            engine.setProperty('voice', selected_voice_id)
        engine.say(text)
        engine.runAndWait()

tts_queue = queue.Queue()

def tts_worker():
    while True:
        item = tts_queue.get()
        if item is None:
            break
        text, _ = item  # device_idx não é mais usado
        speak_text(text)
        tts_queue.task_done()

def on_enter(event=None):
    text = entry.get()
    if text.strip().lower() in ("sair", "exit", "quit"):
        tts_queue.put(None)
        root.destroy()
    elif text.strip():
        now = datetime.datetime.now().strftime("%H:%M:%S")
        history_text.config(state=tk.NORMAL)
        history_text.insert(tk.END, f"[{now}] {text}\n")
        history_text.insert(tk.END, "─" * 40 + "\n")
        history_text.config(state=tk.DISABLED)
        entry.delete(0, tk.END)
        tts_queue.put((text, None))  # device_idx não é mais usado
        update_message_count()

def on_voice_change(event=None):
    global selected_voice_id
    idx = voice_combo.current()
    selected_voice_id = voices[idx].id

root = tk.Tk()
root.title("TTS Interface")
root.configure(bg="#181a20")

style = ttk.Style()
style.theme_use("clam")
style.configure("TLabel", background="#181a20", foreground="#ffffff", font=("Segoe UI", 13, "bold"))
style.configure("TButton", background="#23272f", foreground="#ffffff", font=("Segoe UI", 12, "bold"), padding=8)
style.configure("TEntry", fieldbackground="#23272f", foreground="#ffffff", font=("Segoe UI", 12))
style.configure(
    "TCombobox",
    fieldbackground="#23272f",
    background="#23272f",
    foreground="#ffffff",
    font=("Segoe UI", 12, "bold")
)
style.configure("TScale", background="#181a20", troughcolor="#23272f")

frame = ttk.Frame(root, padding=15, style="TFrame")
frame.pack(padx=10, pady=10, fill=tk.X)

entry = ttk.Entry(frame, font=("Segoe UI", 12))
entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=8, padx=(0, 10))
entry.bind("<Return>", on_enter)

button = ttk.Button(frame, text="Falar", command=on_enter)
button.pack(side=tk.LEFT, padx=(0, 10), ipadx=12, ipady=8)

slider_frame = ttk.Frame(root, padding=10, style="TFrame")
slider_frame.pack(padx=10, pady=(0,10), fill=tk.X)

rate_label = ttk.Label(slider_frame, text="Velocidade", style="TLabel")
rate_label.pack(side=tk.LEFT, padx=(0,10))
rate_slider = ttk.Scale(slider_frame, from_=80, to=400, orient=tk.HORIZONTAL, command=set_rate, length=250)
rate_slider.set(tts_rate)
rate_slider.pack(side=tk.LEFT, padx=(0,20))

volume_label = ttk.Label(slider_frame, text="Volume", style="TLabel")
volume_label.pack(side=tk.LEFT, padx=(0,10))
volume_slider = ttk.Scale(slider_frame, from_=0, to=1, orient=tk.HORIZONTAL, command=set_volume, length=250)
volume_slider.set(tts_volume)
volume_slider.pack(side=tk.LEFT, padx=(0,20))

voice_frame = ttk.Frame(root, padding=10, style="TFrame")
voice_frame.pack(padx=10, pady=(0,10), fill=tk.X)

ttk.Label(voice_frame, text="Escolha a voz:", style="TLabel").pack(side=tk.LEFT, padx=(0,10))
voice_combo = ttk.Combobox(
    voice_frame,
    values=voice_names,
    state="readonly",
    width=40,
    font=("Segoe UI", 12, "bold")
)
voice_combo.pack(side=tk.LEFT, padx=(0,10))
voice_combo.current(0)
selected_voice_id = voices[0].id
voice_combo.bind("<<ComboboxSelected>>", on_voice_change)

history_frame = ttk.Frame(root, padding=10, style="TFrame")
history_frame.pack(padx=10, pady=(0,10), fill=tk.BOTH, expand=True)

history_label = ttk.Label(history_frame, text="Histórico de mensagens:", style="TLabel")
history_label.pack(anchor="w")

history_text = tk.Text(
    history_frame,
    width=50,
    height=10,
    font=("Segoe UI", 12, "bold"),
    bg="#23272f",
    fg="#00ffae",
    borderwidth=0,
    highlightthickness=1,
    relief="solid",
    wrap=tk.WORD
)
history_text.pack(fill=tk.BOTH, expand=True, pady=(5,0))
history_text.config(state=tk.DISABLED)

message_count = tk.IntVar(value=0)

def update_message_count():
    message_count.set(message_count.get() + 1)
    count_label.config(text=f"Mensagens: {message_count.get()}")

count_label = ttk.Label(history_frame, text="Mensagens: 0", style="TLabel")
count_label.pack(anchor="w", pady=(0,5))

def clear_history():
    history_text.config(state=tk.NORMAL)
    history_text.delete(1.0, tk.END)
    history_text.config(state=tk.DISABLED)

clear_button = ttk.Button(history_frame, text="Limpar histórico", command=clear_history, style="TButton")
clear_button.pack(anchor="e", pady=(5,0))

def repeat_last():
    history_text.config(state=tk.NORMAL)
    lines = history_text.get(1.0, tk.END).strip().split("\n")
    history_text.config(state=tk.DISABLED)
    # Busca a última linha que começa com [
    last = [l for l in lines if l.startswith("[")]
    if last:
        msg = last[-1].split("]", 1)[-1].strip()
        tts_queue.put((msg, None))

repeat_button = ttk.Button(history_frame, text="Repetir última", command=repeat_last, style="TButton")
repeat_button.pack(anchor="e", pady=(5,0))

def toggle_theme():
    if root["bg"] == "#181a20":
        root.configure(bg="#f0f0f0")
        style.configure("TLabel", background="#f0f0f0", foreground="#23272f")
        style.configure("TButton", background="#e0e0e0", foreground="#23272f")
        style.configure("TEntry", fieldbackground="#e0e0e0", foreground="#23272f")
        style.configure("TCombobox", fieldbackground="#e0e0e0", background="#f0f0f0", foreground="#23272f")
        style.configure("TScale", background="#f0f0f0", troughcolor="#e0e0e0")
        history_text.config(bg="#e0e0e0", fg="#23272f")
    else:
        root.configure(bg="#181a20")
        style.configure("TLabel", background="#181a20", foreground="#ffffff")
        style.configure("TButton", background="#23272f", foreground="#ffffff")
        style.configure("TEntry", fieldbackground="#23272f", foreground="#ffffff")
        style.configure("TCombobox", fieldbackground="#23272f", background="#181a20", foreground="#ffffff")
        style.configure("TScale", background="#181a20", troughcolor="#23272f")
        history_text.config(bg="#23272f", fg="#00ffae")

theme_button = ttk.Button(history_frame, text="Alternar tema", command=toggle_theme, style="TButton")
theme_button.pack(anchor="e", pady=(5,0))

info_label = ttk.Label(root, text="Certifique-se que o 'Cable Input' está como saída padrão do Windows!", style="TLabel")
info_label.pack(pady=(0,10))

threading.Thread(target=tts_worker, daemon=True).start()

root.mainloop()