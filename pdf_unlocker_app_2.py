import os
import tkinter as tk
from tkinter import filedialog, messagebox

# Try to enable cross-platform drag & drop via tkinterdnd2 (nice-to-have).
# If unavailable, the app still works with the Browse button.
_HAS_DND = True
try:
    from tkinterdnd2 import DND_FILES, TkinterDnD
except Exception:
    _HAS_DND = False

import pikepdf


APP_TITLE = "PDF Password Remover"
DEFAULT_WIDTH = 520
DEFAULT_HEIGHT = 300


def suggest_output_path(input_pdf: str) -> str:
    """Return '<same_dir>/<name>_unlocked.pdf' for an input path."""
    if not input_pdf or not input_pdf.lower().endswith(".pdf"):
        return ""
    folder, filename = os.path.split(input_pdf)
    stem = os.path.splitext(filename)[0]
    return os.path.join(folder, f"{stem}_unlocked.pdf")


def set_input_path(path: str):
    entry_input.delete(0, tk.END)
    entry_input.insert(0, path)
    # If output empty, auto-fill with same folder suggestion
    if not entry_output.get().strip():
        out = suggest_output_path(path)
        if out:
            entry_output.delete(0, tk.END)
            entry_output.insert(0, out)


def browse_file():
    file_path = filedialog.askopenfilename(
        title="Select Locked PDF",
        filetypes=[("PDF Files", "*.pdf")],
    )
    if file_path:
        set_input_path(file_path)


def save_file():
    # Offer a default suggestion near the input if known
    initial = suggest_output_path(entry_input.get().strip()) or "unlocked.pdf"
    folder = os.path.dirname(initial) or os.getcwd()
    default_name = os.path.basename(initial) or "unlocked.pdf"

    file_path = filedialog.asksaveasfilename(
        title="Save Unlocked PDF As",
        initialdir=folder,
        initialfile=default_name,
        defaultextension=".pdf",
        filetypes=[("PDF Files", "*.pdf")],
    )
    if file_path:
        entry_output.delete(0, tk.END)
        entry_output.insert(0, file_path)


def unlock_pdf():
    input_pdf = entry_input.get().strip()
    output_pdf = entry_output.get().strip()
    password = entry_password.get()

    if not input_pdf:
        messagebox.showerror("Error", "Please select a locked PDF.")
        return
    if not os.path.exists(input_pdf):
        messagebox.showerror("Error", "Input PDF file does not exist.")
        return
    if not password:
        messagebox.showerror("Error", "Please enter the password.")
        return

    # If user didn't choose output, auto-save next to the input
    if not output_pdf:
        output_pdf = suggest_output_path(input_pdf)

    # Guard against accidental overwrite
    if os.path.exists(output_pdf):
        if not messagebox.askyesno("Overwrite?",
                                   f"'{output_pdf}' already exists.\nOverwrite?"):
            return

    try:
        with pikepdf.open(input_pdf, password=password) as pdf:
            pdf.save(output_pdf)
        messagebox.showinfo("Success", f"Password removed!\nSaved as:\n{output_pdf}")
    except pikepdf._qpdf.PasswordError:
        messagebox.showerror("Error", "Incorrect password.")
    except Exception as e:
        messagebox.showerror("Error", f"{e}")


def on_drop(event):
    # tkinterdnd2 sends a string that may contain braces for spaced paths
    data = event.data.strip()
    # It can also deliver multiple files; take the first
    if data.startswith("{") and data.endswith("}"):
        data = data[1:-1]
    # Split on spaces only if multiple paths present without braces
    # (tkdnd delivers quoted/braced when needed)
    first = data.split()[-1] if " " in data and not data.startswith("/") else data
    if first.lower().endswith(".pdf"):
        set_input_path(first)
    else:
        messagebox.showerror("Error", "Please drop a valid PDF file.")


# --- GUI Setup ---
RootClass = TkinterDnD.Tk if _HAS_DND else tk.Tk
root = RootClass()
root.title(APP_TITLE)
root.geometry(f"{DEFAULT_WIDTH}x{DEFAULT_HEIGHT}")
root.resizable(False, False)

# Title
title_lbl = tk.Label(root, text=APP_TITLE, font=("Segoe UI", 14, "bold"))
title_lbl.pack(pady=(10, 0))

# Input file
tk.Label(root, text="Locked PDF (drag & drop or Browse):").pack(
    anchor="w", padx=12, pady=(12, 2)
)
frame_input = tk.Frame(root)
frame_input.pack(fill="x", padx=12)

entry_input = tk.Entry(frame_input)
entry_input.pack(side="left", fill="x", expand=True)
btn_browse = tk.Button(frame_input, text="Browse", command=browse_file)
btn_browse.pack(side="left", padx=6)

# Enable drag & drop onto the entry if tkinterdnd2 is available
if _HAS_DND:
    entry_input.drop_target_register(DND_FILES)
    entry_input.dnd_bind("<<Drop>>", on_drop)

# Output file
tk.Label(root, text="Unlocked PDF (optional):").pack(
    anchor="w", padx=12, pady=(10, 2)
)
frame_output = tk.Frame(root)
frame_output.pack(fill="x", padx=12)

entry_output = tk.Entry(frame_output)
entry_output.pack(side="left", fill="x", expand=True)
btn_saveas = tk.Button(frame_output, text="Save As", command=save_file)
btn_saveas.pack(side="left", padx=6)

# Password
tk.Label(root, text="Password:").pack(anchor="w", padx=12, pady=(10, 2))
entry_password = tk.Entry(root, show="*")
entry_password.pack(fill="x", padx=12)

# Unlock button
btn_unlock = tk.Button(
    root, text="Unlock PDF", command=unlock_pdf, bg="#4CAF50", fg="white"
)
btn_unlock.pack(pady=16)

# Footer hint
hint = ("Tip: If you don't pick an output file, the app will save next to the "
        "original as *_unlocked.pdf*.")
tk.Label(root, text=hint, fg="#666").pack(padx=12)

root.mainloop()
