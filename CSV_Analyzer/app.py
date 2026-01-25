import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import pandas as pd

class CSVAnalyzerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("CSV Data Analyzer")
        self.root.geometry("1100x700")
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
            controls, text="Upload CSV", width=15, command=self.load_csv
        )
        upload_btn.pack(side="left", padx=10)

        self.clean_btn = tk.Button(
            controls, text="Clean Data", width=15, state="disabled"
        )
        self.clean_btn.pack(side="left", padx=10)

        self.export_btn = tk.Button(
            controls, text="Export Cleaned CSV", width=18, state="disabled"
        )
        self.export_btn.pack(side="left", padx=10)

        # ===== Output Area (Scrollable) =====
        output_frame = tk.Frame(root)
        output_frame.pack(fill="x", padx=10, pady=5)

        output_scroll = tk.Scrollbar(output_frame)
        output_scroll.pack(side="right", fill="y")

        self.output = tk.Text(
            output_frame,
            height=10,
            wrap="word",
            font=("Consolas", 11),
            yscrollcommand=output_scroll.set
        )
        self.output.pack(side="left", fill="x", expand=True)

        output_scroll.config(command=self.output.yview)

        # ===== Table Frame =====
        table_frame = tk.Frame(root)
        table_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.tree = ttk.Treeview(table_frame, show="headings")
        self.tree.pack(side="left", fill="both", expand=True)

        v_scroll = ttk.Scrollbar(
            table_frame, orient="vertical", command=self.tree.yview
        )
        v_scroll.pack(side="right", fill="y")

        h_scroll = ttk.Scrollbar(
            root, orient="horizontal", command=self.tree.xview
        )
        h_scroll.pack(fill="x")

        self.tree.configure(
            yscrollcommand=v_scroll.set,
            xscrollcommand=h_scroll.set
        )

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
        self.output.insert(
            tk.END, f"Rows: {self.df.shape[0]} | Columns: {self.df.shape[1]}\n\n"
        )

        self.output.insert(tk.END, "Columns:\n")
        for col in self.df.columns:
            self.output.insert(tk.END, f"  {col}\n")

        self.output.insert(tk.END, "\nMissing Values:\n")
        self.output.insert(tk.END, f"{self.df.isnull().sum()}\n\n")

        self.output.insert(tk.END, "Duplicate Rows:\n")
        self.output.insert(tk.END, f"{self.df.duplicated().sum()}\n\n")

        self.output.insert(tk.END, "Statistical Summary:\n")
        self.output.insert(tk.END, f"{self.df.describe()}\n")

        # Show first 10 rows in table
        self.show_table(self.df.head(10))

        self.clean_btn.config(state="normal")

    def show_table(self, dataframe):
        # Clear existing table
        self.tree.delete(*self.tree.get_children())

        # Set columns
        self.tree["columns"] = list(dataframe.columns)

        for col in dataframe.columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120, anchor="center")

        # Insert rows
        for _, row in dataframe.iterrows():
            self.tree.insert("", "end", values=list(row))

if __name__ == "__main__":
    root = tk.Tk()
    app = CSVAnalyzerApp(root)
    root.mainloop()
