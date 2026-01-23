import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd

class CSVAnalyzerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("CSV Data Analyzer")
        self.root.geometry("1000x650")
        self.root.configure(bg="#f4f6f7")

        self.df = None
        self.cleaned_df = None

        # ===== Header =====
        header = tk.Frame(root, bg="#2c3e50", height=60)
        header.pack(fill="x")

        title = tk.Label(
            header,
            text="CSV Data Analyzer",
            bg="#2c3e50",
            fg="white",
            font=("Segoe UI", 18, "bold")
        )
        title.pack(pady=15)

        # ===== Control Panel =====
        controls = tk.Frame(root, bg="#ecf0f1", height=80)
        controls.pack(fill="x", padx=10, pady=10)

        upload_btn = tk.Button(
            controls,
            text="Upload CSV",
            width=15,
            command=self.load_csv
        )
        upload_btn.pack(side="left", padx=10)

        self.clean_btn = tk.Button(
            controls,
            text="Clean Data",
            width=15,
            state="disabled"
        )
        self.clean_btn.pack(side="left", padx=10)

        self.export_btn = tk.Button(
            controls,
            text="Export Cleaned CSV",
            width=18,
            state="disabled"
        )
        self.export_btn.pack(side="left", padx=10)

        # ===== Output Area =====
        self.output = tk.Text(
            root,
            wrap="word",
            font=("Consolas", 11)
        )
        self.output.pack(fill="both", expand=True, padx=10, pady=10)

    def load_csv(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("CSV Files", "*.csv")]
        )
        if not file_path:
            return

        try:
            self.df = pd.read_csv(file_path)
        except Exception as e:
            messagebox.showerror("Error", str(e))
            return

        self.output.delete(1.0, tk.END)
        self.output.insert(tk.END, "CSV loaded successfully!\n\n")

        self.output.insert(tk.END, f"Rows: {self.df.shape[0]}\n")
        self.output.insert(tk.END, f"Columns: {self.df.shape[1]}\n\n")

        self.output.insert(tk.END, "Columns:\n")
        for col in self.df.columns:
            self.output.insert(tk.END, f"  {col}\n")

        self.output.insert(tk.END, "\nMissing Values:\n")
        self.output.insert(tk.END, f"{self.df.isnull().sum()}\n\n")

        self.output.insert(tk.END, "Duplicate Rows:\n")
        self.output.insert(tk.END, f"{self.df.duplicated().sum()}\n\n")

        self.output.insert(tk.END, "Statistical summary:\n")
        self.output.insert(tk.END, f"{self.df.describe()}\n\n")

        self.clean_btn.config(state="normal")

if __name__ == "__main__":
    root = tk.Tk()
    app = CSVAnalyzerApp(root)
    root.mainloop()
