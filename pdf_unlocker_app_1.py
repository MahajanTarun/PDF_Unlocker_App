import tkinter as tk
from tkinter import filedialog, messagebox
import pikepdf
import os

def browse_file():
    file_path = filedialog.askopenfilename(
        title="Select Locked PDF",
        filetypes=[("PDF Files", "*.pdf")]
    )
    if file_path:
        entry_input.delete(0, tk.END)
        entry_input.insert(0, file_path)

def save_file():
    file_path = filedialog.asksaveasfilename(
        title="Save Unlocked PDF As",
        defaultextension=".pdf",
        filetypes=[("PDF Files", "*.pdf")]
    )
    if file_path:
        entry_output.delete(0, tk.END)
        entry_output.insert(0, file_path)

def unlock_pdf():
    input_pdf = entry_input.get()
    output_pdf = entry_output.get()
    password = entry_password.get()

    if not os.path.exists(input_pdf):
        messagebox.showerror("Error", "Input PDF file does not exist.")
        return
    if not password:
        messagebox.showerror("Error", "Please enter the password.")
        return
    if not output_pdf:
        messagebox.showerror("Error", "Please choose where to save the unlocked PDF.")
        return

    try:
        with pikepdf.open(input_pdf, password=password) as pdf:
            pdf.save(output_pdf)
        messagebox.showinfo("Success", f"Password removed!\nSaved as:\n{output_pdf}")
    except pikepdf._qpdf.PasswordError:
        messagebox.showerror("Error", "Incorrect password.")
    except Exception as e:
        messagebox.showerror("Error", str(e))

# --- GUI Setup ---
root = tk.Tk()
root.title("PDF Password Remover")
root.geometry("450x250")
root.resizable(False, False)

# Input file
tk.Label(root, text="Locked PDF:").pack(anchor="w", padx=10, pady=(10, 0))
frame_input = tk.Frame(root)
frame_input.pack(fill="x", padx=10)
entry_input = tk.Entry(frame_input, width=40)
entry_input.pack(side="left", fill="x", expand=True)
tk.Button(frame_input, text="Browse", command=browse_file).pack(side="left", padx=5)

# Output file
tk.Label(root, text="Unlocked PDF:").pack(anchor="w", padx=10, pady=(10, 0))
frame_output = tk.Frame(root)
frame_output.pack(fill="x", padx=10)
entry_output = tk.Entry(frame_output, width=40)
entry_output.pack(side="left", fill="x", expand=True)
tk.Button(frame_output, text="Save As", command=save_file).pack(side="left", padx=5)

# Password
tk.Label(root, text="Password:").pack(anchor="w", padx=10, pady=(10, 0))
entry_password = tk.Entry(root, show="*", width=30)
entry_password.pack(fill="x", padx=10)

# Unlock button
tk.Button(root, text="Unlock PDF", command=unlock_pdf, bg="#4CAF50", fg="white").pack(pady=15)

root.mainloop()
