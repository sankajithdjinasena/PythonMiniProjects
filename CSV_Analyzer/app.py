import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import pandas as pd

class CSVAnalyzerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("CSV Data Analyzer")
        self.root.geometry("800x600")

        title = tk.Label(root, text="CSV Data Analyzer", font=("Arial", 18, "bold"))
        title.pack(pady=10)

        btn_upload = tk.Button(root, text="Upload CSV File", command=self.load_csv)
        btn_upload.pack(pady=5)

        self.output = scrolledtext.ScrolledText(root, width=100, height=30)
        self.output.pack(padx=10, pady=10)

    def load_csv(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("CSV Files", "*.csv")]
        )

        if not file_path:
            return

        try:
            df = pd.read_csv(file_path)
        except Exception as e:
            messagebox.showerror("Error", str(e))
            return

        self.output.delete(1.0, tk.END)

        self.output.insert(tk.END, "=== Dataset Shape ===\n")
        self.output.insert(tk.END, f"Rows: {df.shape[0]}\n")
        self.output.insert(tk.END, f"Columns: {df.shape[1]}\n\n")

        self.output.insert(tk.END, "=== Missing Values ===\n")
        self.output.insert(tk.END, f"{df.isnull().sum()}\n\n")

        self.output.insert(tk.END, "=== Duplicate Rows ===\n")
        self.output.insert(tk.END, f"{df.duplicated().sum()}\n\n")

        self.output.insert(tk.END, "=== Summary Statistics ===\n")
        self.output.insert(tk.END, f"{df.describe(include='all')}\n")

if __name__ == "__main__":
    root = tk.Tk()
    app = CSVAnalyzerApp(root)
    root.mainloop()
