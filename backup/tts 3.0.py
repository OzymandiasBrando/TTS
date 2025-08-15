import tkinter as tk
import tkinter.ttk as ttk
from tkinter import filedialog
import threading, datetime, queue, random, string, time, os, json
from gtts import gTTS # pyright: ignore[reportMissingImports]
from pygame import mixer # pyright: ignore[reportMissingImports]
import keyboard  # type: ignore

# Mixer no Cable Input
mixer.init(devicename="CABLE Input (VB-Audio Virtual Cable)")

CONFIG_FILE = "tts_slots_config.json"

def generate_random_string(length=8):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

# Configurações
tts_volume = 0.5
slots_volume = 0.05
selected_language = "la"
audio_slots = [None] * 40
slot_names = [""] * 40

# Idiomas
from languages2 import languages_map

# === Funções TTS ===
def speak_text(text, lang):
    if text.strip() and text != placeholder_text:
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

tts_queue = queue.Queue()
def tts_worker():
    while True:
        item = tts_queue.get()
        if item is None:
            break
        text, lang = item
        speak_text(text, lang)
        tts_queue.task_done()

def on_enter(event=None, from_popup=False, popup_entry=None, popup=None):
    if from_popup:
        text = popup_entry.get()
    else:
        text = entry.get()

    if text.strip().lower() in ("sair", "exit", "quit"):
        tts_queue.put(None)
        root.destroy()
    elif text.strip() and text != placeholder_text:
        now = datetime.datetime.now().strftime("%H:%M:%S")
        history_text.config(state=tk.NORMAL)
        history_text.insert(tk.END, f"[{now}] {text}\n")
        history_text.insert(tk.END, "─" * 20 + "\n")
        history_text.see(tk.END)
        history_text.config(state=tk.DISABLED)

        if from_popup:
            popup.destroy()
        else:
            entry.delete(0, tk.END)
            entry.focus_set()

        tts_queue.put((text, selected_language))
        update_message_count()

def on_language_change(event=None):
    global selected_language
    selected_language = languages_map[language_combo.get()]

def set_volume(val):
    global tts_volume
    tts_volume = float(val)

def set_slots_volume(val):
    global slots_volume
    slots_volume = float(val)

def update_message_count():
    message_count.set(message_count.get() + 1)
    history_label.config(text=f"Histórico: {message_count.get()} Mensagens")

def clear_history():
    history_text.config(state=tk.NORMAL)
    history_text.delete(1.0, tk.END)
    history_text.config(state=tk.DISABLED)
    message_count.set(0)
    history_label.config(text="Histórico: 0 Mensagens")

def repeat_last():
    history_text.config(state=tk.NORMAL)
    lines = history_text.get(1.0, tk.END).strip().split("\n")
    history_text.config(state=tk.DISABLED)
    last = [l for l in lines if l.startswith("[")]
    if last:
        msg = last[-1].split("]", 1)[-1].strip()
        tts_queue.put((msg, selected_language))

# === Funções Slots ===
slot_buttons = []

def update_slot_button(slot_index):
    file = audio_slots[slot_index]
    name = slot_names[slot_index]
    display_name = name if name else f"Slot {slot_index+1}"
    slot_buttons[slot_index].config(text=display_name)

def select_file(slot_index):
    file_path = filedialog.askopenfilename(filetypes=[("MP3 Files", "*.mp3")])
    if file_path:
        audio_slots[slot_index] = file_path
        if not slot_names[slot_index]:
            slot_names[slot_index] = os.path.splitext(os.path.basename(file_path))[0]
        update_slot_button(slot_index)
        save_slots_config()

def play_slot(slot_index):
    path = audio_slots[slot_index]
    if path:
        mixer.music.load(path)
        mixer.music.set_volume(slots_volume)
        mixer.music.play()

def rename_slot(slot_index):
    def save_name():
        new_name = name_entry.get().strip()
        if new_name:
            slot_names[slot_index] = new_name
            update_slot_button(slot_index)
            rename_win.destroy()
            save_slots_config()
    
    rename_win = tk.Toplevel(root)
    rename_win.title("Renomear Slot")
    rename_win.geometry("300x100")
    rename_win.configure(bg="#181a20")
    
    ttk.Label(rename_win, text="Novo nome:").pack(pady=(10, 0))
    name_entry = ttk.Entry(rename_win, font=("Segoe UI", 12))
    name_entry.pack(pady=5, padx=10, fill=tk.X)
    name_entry.insert(0, slot_names[slot_index])
    ttk.Button(rename_win, text="Salvar", command=save_name).pack(pady=5)

# === Configuração ===
def save_slots_config():
    data = {
        "slots": audio_slots,
        "slot_names": slot_names,
        "tts_volume": tts_volume,
        "slots_volume": slots_volume,
        "language": selected_language
    }
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def load_slots_config():
    global tts_volume, slots_volume, selected_language, audio_slots, slot_names
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            audio_slots = data.get("slots", [None] * 40)
            slot_names = data.get("slot_names", [""] * 40)
            tts_volume = data.get("tts_volume", 0.5)
            slots_volume = data.get("slots_volume", 0.5)
            selected_language = data.get("language", "pt-br")

# === GUI ===
root = tk.Tk()
root.title("TTS Interface")

def center_window(width=1200, height=600):
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = (screen_width // 2) - (width // 2)
    y = (screen_height // 2) - (height // 2)
    root.geometry(f"{width}x{height}+{x}+{y}")

center_window(1200, 600)

root.configure(bg="#181a20")
style = ttk.Style()
style.theme_use("clam")
style.configure("TFrame", background="#181a20")
style.configure("TLabel", background="#181a20", foreground="#fff", font=("Segoe UI", 11, "bold"))
style.configure("TButton", background="#23272f", foreground="#fff", font=("Segoe UI", 10, "bold"), padding=6)
style.configure("TEntry", fieldbackground="#23272f", foreground="#fff", font=("Segoe UI", 11))
style.configure("TCombobox", fieldbackground="#23272f", background="#23272f", foreground="#fff", font=("Segoe UI", 11, "bold"))
style.configure("TScale", background="#181a20", troughcolor="#23272f")

# Notebook
notebook = ttk.Notebook(root)
notebook.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

# === Aba TTS ===
tts_frame = ttk.Frame(notebook, style="TFrame")
notebook.add(tts_frame, text="TTS")

top_frame = ttk.Frame(tts_frame, style="TFrame")
top_frame.pack(fill=tk.X, pady=(5, 5))
entry = ttk.Entry(top_frame, font=("Segoe UI", 11))
entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=5)

# Placeholder
placeholder_text = "Digite o texto para falar..."
def restore_placeholder():
    entry.delete(0, tk.END)
    entry.insert(0, placeholder_text)
    entry.config(foreground="gray")

def on_entry_click(event):
    if entry.get() == placeholder_text:
        entry.delete(0, tk.END)
        entry.config(foreground="white")

def on_focus_out(event):
    if entry.get().strip() == "":
        restore_placeholder()

restore_placeholder()
entry.bind("<FocusIn>", on_entry_click)
entry.bind("<FocusOut>", on_focus_out)

entry.bind("<Return>", on_enter)
ttk.Button(top_frame, text="Falar", command=on_enter, width=8).pack(side=tk.LEFT, padx=(5, 0))

control_frame = ttk.Frame(tts_frame, style="TFrame")
control_frame.pack(fill=tk.X, pady=(0, 5))
ttk.Label(control_frame, text="Volume").pack(side=tk.LEFT, padx=(0, 5))
volume_slider = ttk.Scale(control_frame, from_=0, to=1, orient=tk.HORIZONTAL, command=set_volume, length=120)
volume_slider.set(tts_volume)
volume_slider.pack(side=tk.LEFT, padx=(0, 15))
ttk.Label(control_frame, text="Idioma").pack(side=tk.LEFT)
language_combo = ttk.Combobox(control_frame, values=list(languages_map.keys()), state="readonly", width=15)
language_combo.pack(side=tk.LEFT, padx=(5, 15))
language_combo.set(list(languages_map.keys())[list(languages_map.values()).index(selected_language)])
language_combo.bind("<<ComboboxSelected>>", on_language_change)
ttk.Button(control_frame, text="Repetir", command=repeat_last, width=8).pack(side=tk.RIGHT, padx=(5, 0))
ttk.Button(control_frame, text="Limpar Histórico", command=clear_history, width=15).pack(side=tk.RIGHT)

message_count = tk.IntVar(value=0)
history_label = ttk.Label(tts_frame, text="Histórico: 0 Mensagens")
history_label.pack(anchor="w", padx=5)
history_text = tk.Text(tts_frame, width=50, height=10, font=("Segoe UI", 10, "bold"),
                       bg="#23272f", fg="#00ffae", borderwidth=0, highlightthickness=1, relief="solid", wrap=tk.WORD)
history_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=(0, 5))
history_text.config(state=tk.DISABLED)

# Mensagem fixa no canto inferior direito do histórico
shortcut_label = ttk.Label(
    tts_frame,
    text="💡 Dica: Use Ctrl+Enter para abrir o TTS rápido",
    font=("Segoe UI", 9),
    foreground="#aaaaaa",
    background="#181a20"
)
shortcut_label.place(relx=1.0, rely=1.0, anchor="se", x=-5, y=-5)

# === Aba Sons ===
# === Aba Sons ===
sons_frame = ttk.Frame(notebook, style="TFrame")
notebook.add(sons_frame, text="Sons")

# Frame centralizado para os slots
slots_container = ttk.Frame(sons_frame, style="TFrame")
slots_container.pack(expand=True)  # ocupa o centro da aba

slot_buttons.clear()
for i in range(40):
    row = i // 4
    col = (i % 4) * 3
    btn_file = ttk.Button(slots_container, text=f"Slot {i+1}", width=14, command=lambda i=i: select_file(i))
    btn_file.grid(row=row, column=col, padx=2, pady=2)
    slot_buttons.append(btn_file)
    ttk.Button(slots_container, text="Nomear", width=10, command=lambda i=i: rename_slot(i)).grid(row=row, column=col+1, padx=2)
    ttk.Button(slots_container, text="▶", width=3, command=lambda i=i: play_slot(i)).grid(row=row, column=col+2, padx=2)

# Volume dos slots
slots_vol_frame = ttk.Frame(sons_frame, style="TFrame")
slots_vol_frame.pack(side=tk.BOTTOM, pady=10)
ttk.Label(slots_vol_frame, text="Volume").pack(side=tk.LEFT, padx=(0, 5))
slots_volume_slider = ttk.Scale(slots_vol_frame, from_=0, to=1, orient=tk.HORIZONTAL, command=set_slots_volume, length=150)
slots_volume_slider.set(slots_volume)
slots_volume_slider.pack(side=tk.LEFT)


# === Pop-up com Ctrl+Enter ===
def open_quick_popup():
    popup = tk.Toplevel(root)
    popup.title("TTS Rápido")
    popup.configure(bg="#181a20")
    popup.geometry("400x120")

    # Sempre no topo até fechar
    popup.attributes("-topmost", True)

    popup.grab_set()
    popup.lift()
    popup.focus_force()

    entry_popup = ttk.Entry(popup, font=("Segoe UI", 11))
    entry_popup.pack(pady=15, padx=10, fill=tk.X, ipady=5)

    def restore_ph():
        if entry_popup.get().strip() == "":
            entry_popup.delete(0, tk.END)
            entry_popup.insert(0, placeholder_text)
            entry_popup.config(foreground="gray")

    def click_in(e):
        if entry_popup.get() == placeholder_text:
            entry_popup.delete(0, tk.END)
            entry_popup.config(foreground="white")

    entry_popup.bind("<FocusIn>", click_in)
    entry_popup.bind("<FocusOut>", lambda e: restore_ph())
    restore_ph()

    entry_popup.bind("<Return>", lambda e: on_enter(from_popup=True, popup_entry=entry_popup, popup=popup))
    ttk.Button(popup, text="Falar", command=lambda: on_enter(from_popup=True, popup_entry=entry_popup, popup=popup)).pack(pady=5)

    # Garante foco total
    popup.after(50, lambda: [
        popup.lift(),
        popup.focus_force(),
        entry_popup.focus_set()
    ])

# Atalho global
def hotkey_listener():
    keyboard.add_hotkey("ctrl+enter", open_quick_popup)
    keyboard.wait()

threading.Thread(target=hotkey_listener, daemon=True).start()

# === Inicia ===
threading.Thread(target=tts_worker, daemon=True).start()
load_slots_config()
for i in range(40):
    update_slot_button(i)
root.mainloop()
