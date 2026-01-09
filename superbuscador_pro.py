#!/usr/bin/env python3
import os
import shutil
import threading
import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path
import re
import sys

# ================= CONFIG =================
EXCLUIR = {
    ".cache", ".local", "node_modules", ".git", "__pycache__",
    "Windows", "Program Files", "Program Files (x86)"
}

EXTENSIONES = {
    "Todo": [],
    "Imágenes": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".svg"],
    "Videos": [".mp4", ".mkv", ".avi", ".mov", ".webm"],
    "Música": [".mp3", ".wav", ".flac", ".ogg"],
    "Documentos": [".pdf", ".docx", ".txt", ".odt", ".xlsx", ".pptx"]
}

# ================= NORMALIZAR =================
def normalizar(texto):
    texto = texto.lower()
    texto = re.sub(r'[_\-.]+', ' ', texto)
    texto = re.sub(r'([a-z])([0-9])', r'\1 \2', texto)
    texto = re.sub(r'([0-9])([a-z])', r'\1 \2', texto)
    texto = re.sub(r'[^a-z0-9 ]+', '', texto)
    return texto.strip()

# ================= COINCIDENCIA INTELIGENTE =================
def coincide(termino, nombre):
    """
    Coincidencia tipo Google:
    - stilo        -> stilo1212
    - stilo1212    -> stilo-12, stilo_1212
    - sti 12       -> stilo_final_12
    """
    t = normalizar(termino)
    n = normalizar(nombre)

    # coincidencia directa rápida
    if t in n:
        return True

    t_tokens = t.split()
    n_tokens = n.split()

    for tt in t_tokens:
        if not any(tt in nt or nt in tt for nt in n_tokens):
            return False

    return True

# ================= COPIA SEGURA =================
def copiar_seguro(origen, destino):
    archivo = destino / origen.name
    i = 1
    while archivo.exists():
        archivo = destino / f"{origen.stem}_{i}{origen.suffix}"
        i += 1
    shutil.copy2(origen, archivo)

# ================= BUSCADOR =================
def buscar():
    termino = entry_busqueda.get().strip()
    tipo = combo_tipo.get()
    limite = int(spin_cantidad.get())

    if not termino:
        messagebox.showwarning("⚠️", "Escribe algo para buscar")
        return

    termino_norm = normalizar(termino)

    # Escritorio multiplataforma
    escritorio = (
        Path.home() / "Desktop"
        if sys.platform.startswith("win")
        else Path.home() / "Escritorio"
    )

    carpeta = escritorio / f"Busqueda_{termino_norm.replace(' ', '_')}"
    carpeta.mkdir(parents=True, exist_ok=True)

    encontrados = 0
    extensiones = EXTENSIONES[tipo]

    lbl_estado.config(text="🔥 Escaneando tu PC...")

    rutas = [Path.home()]
    if not sys.platform.startswith("win"):
        rutas += [Path("/media"), Path("/mnt")]

    for base in rutas:
        if not base.exists():
            continue

        for raiz, dirs, files in os.walk(base):
            dirs[:] = [d for d in dirs if d not in EXCLUIR]

            for nombre in files:
                if encontrados >= limite:
                    finalizar(carpeta)
                    return

                if coincide(termino, nombre):
                    ruta = Path(raiz) / nombre
                    if not extensiones or ruta.suffix.lower() in extensiones:
                        try:
                            copiar_seguro(ruta, carpeta)
                            encontrados += 1
                            lbl_estado.config(
                                text=f"⚡ Encontrados: {encontrados}"
                            )
                        except:
                            pass

    finalizar(carpeta)

# ================= FINAL =================
def finalizar(carpeta):
    lbl_estado.config(text="👑 BÚSQUEDA TERMINADA")

    try:
        if sys.platform.startswith("win"):
            os.startfile(carpeta)
        else:
            os.system(f'xdg-open "{carpeta}"')
    except:
        pass

    messagebox.showinfo(
        "✅ LISTO",
        f"Archivos guardados en:\n{carpeta}"
    )

def iniciar_busqueda():
    threading.Thread(target=buscar, daemon=True).start()

# ================= UI GOD =================
root = tk.Tk()
root.title("🔥 BUSCADOR GOD MODE 🔥")
root.geometry("460x520")
root.resizable(False, False)

style = ttk.Style(root)
style.theme_use("clam")

BG = "#0f0f14"
FG = "#eaeaff"
ACCENT = "#8a5cff"

root.configure(bg=BG)
style.configure(".", background=BG, foreground=FG, font=("Segoe UI", 10))
style.configure("Header.TLabel", font=("Segoe UI Black", 18), foreground=ACCENT)
style.configure("TEntry", fieldbackground="#1a1a25")
style.configure("TCombobox", fieldbackground="#1a1a25")
style.configure(
    "TButton",
    background=ACCENT,
    foreground="white",
    font=("Segoe UI Semibold", 11),
    padding=10
)

frame = ttk.Frame(root, padding=25)
frame.pack(fill="both", expand=True)

ttk.Label(
    frame,
    text="⚡ BUSCADOR LOCAL GOD ⚡",
    style="Header.TLabel"
).pack(pady=10)

entry_busqueda = ttk.Entry(frame, font=("Segoe UI", 12))
entry_busqueda.pack(fill="x", pady=12)

ttk.Label(frame, text="🎯 Tipo de archivo").pack(anchor="w")
combo_tipo = ttk.Combobox(
    frame,
    values=list(EXTENSIONES.keys()),
    state="readonly"
)
combo_tipo.current(0)
combo_tipo.pack(fill="x", pady=6)

ttk.Label(frame, text="📦 Máx resultados").pack(anchor="w")
spin_cantidad = ttk.Spinbox(frame, from_=1, to=1000, width=7)
spin_cantidad.set(20)
spin_cantidad.pack(pady=6)

ttk.Button(
    frame,
    text="🚀 BUSCAR AHORA",
    command=iniciar_busqueda
).pack(pady=20)

lbl_estado = ttk.Label(
    frame,
    text="😈 Listo para dominar tu disco..."
)
lbl_estado.pack(pady=15)

ttk.Label(
    frame,
    text="Local • Multiplataforma • Búsqueda Inteligente",
    foreground="#777"
).pack(side="bottom")

root.mainloop()