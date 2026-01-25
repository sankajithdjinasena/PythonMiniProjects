import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class CSVAnalyzerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("CSV Data Analyzer")
        self.root.geometry("1100x750")
        self.root.configure(bg="#f4f6f7")

        self.df = None
        self.cleaned_df = None

        # ===== Header =====
        header = tk.Frame(root, bg="#2c3e50", height=60)
        header.pack(fill="x")

        tk.Label(
            header, text="CSV Data Analyzer",
            bg="#2c3e50", fg="white",
            font=("Segoe UI", 18, "bold")
        ).pack(pady=15)

        # ===== Controls =====
        controls = tk.Frame(root, bg="#ecf0f1")
        controls.pack(fill="x", padx=10, pady=10)

        tk.Button(controls, text="Upload CSV", width=15, command=self.load_csv).pack(side="left", padx=10)

        self.export_btn = tk.Button(
            controls, text="Export Cleaned CSV",
            width=18, state="disabled", command=self.export_cleaned_csv
        )
        self.export_btn.pack(side="left", padx=10)

        # ===== Output Area =====
        output_frame = tk.Frame(root)
        output_frame.pack(fill="x", padx=10)

        scroll = tk.Scrollbar(output_frame)
        scroll.pack(side="right", fill="y")

        self.output = tk.Text(
            output_frame, height=10,
            font=("Consolas", 11),
            yscrollcommand=scroll.set
        )
        self.output.pack(fill="x")
        scroll.config(command=self.output.yview)

        # ===== Table =====
        table_frame = tk.Frame(root)
        table_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.tree = ttk.Treeview(table_frame, show="headings")
        self.tree.pack(side="left", fill="both", expand=True)

        vsb = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        vsb.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=vsb.set)

        # ===== Cleaning Controls =====
        clean_frame = tk.Frame(root, bg="#ecf0f1")
        clean_frame.pack(fill="x", padx=10, pady=5)

        tk.Label(clean_frame, text="Column:", bg="#ecf0f1").pack(side="left", padx=5)

        self.clean_column = ttk.Combobox(clean_frame, state="readonly", width=20)
        self.clean_column.pack(side="left", padx=5)

        tk.Label(clean_frame, text="Missing Value:", bg="#ecf0f1").pack(side="left", padx=5)

        self.missing_method = ttk.Combobox(
            clean_frame, state="readonly",
            values=["Mean", "Median", "Mode", "Drop Rows"],
            width=15
        )
        self.missing_method.current(0)
        self.missing_method.pack(side="left", padx=5)

        tk.Button(
            clean_frame, text="Apply Missing",
            command=self.handle_missing_values
        ).pack(side="left", padx=10)

        tk.Button(
            clean_frame, text="Remove Outliers",
            command=self.remove_outliers
        ).pack(side="left", padx=10)

        # ===== Chart Buttons =====
        chart_controls = tk.Frame(root, bg="#ecf0f1")
        chart_controls.pack(fill="x", padx=10, pady=5)

        tk.Button(chart_controls, text="Histogram", command=self.show_histogram).pack(side="left", padx=10)
        tk.Button(chart_controls, text="Boxplot", command=self.show_boxplot).pack(side="left", padx=10)

        # ===== Plot Area =====
        self.plot_frame = tk.Frame(root, bg="#f4f6f7")
        self.plot_frame.pack(fill="both", padx=10, pady=10)

    # ================= FUNCTIONS =================

    def load_csv(self):
        path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        if not path:
            return

        try:
            self.df = pd.read_csv(path)
            self.cleaned_df = self.df.copy()
        except Exception as e:
            messagebox.showerror("Error", str(e))
            return

        self.output.delete(1.0, tk.END)
        self.output.insert(tk.END, f"Rows: {self.df.shape[0]}\n")
        self.output.insert(tk.END, f"Columns: {self.df.shape[1]}\n\n")
        self.output.insert(tk.END, "Missing Values:\n")
        self.output.insert(tk.END, f"{self.df.isnull().sum()}\n\n")
        self.output.insert(tk.END, "Duplicate Rows:\n")
        self.output.insert(tk.END, f"{self.df.duplicated().sum()}\n\n")
        self.output.insert(tk.END, "Statistical Summary:\n")
        self.output.insert(tk.END, f"{self.df.describe()}\n")

        self.show_table(self.df.head(10))

        self.clean_column["values"] = list(self.df.columns)
        self.clean_column.current(0)

        self.export_btn.config(state="normal")

    def show_table(self, df):
        self.tree.delete(*self.tree.get_children())
        self.tree["columns"] = list(df.columns)

        for col in df.columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120, anchor="center")

        for _, row in df.iterrows():
            self.tree.insert("", "end", values=list(row))

    def handle_missing_values(self):
        col = self.clean_column.get()
        method = self.missing_method.get()

        if col == "":
            return

        if method == "Mean":
            if pd.api.types.is_numeric_dtype(self.cleaned_df[col]):
                self.cleaned_df[col] = self.cleaned_df[col].fillna(
                    self.cleaned_df[col].mean()
                )
            else:
                messagebox.showwarning("Warning", "Mean only for numeric columns")
                return

        elif method == "Median":
            if pd.api.types.is_numeric_dtype(self.cleaned_df[col]):
                self.cleaned_df[col] = self.cleaned_df[col].fillna(
                    self.cleaned_df[col].median()
                )
            else:
                messagebox.showwarning("Warning", "Median only for numeric columns")
                return

        elif method == "Mode":
            self.cleaned_df[col] = self.cleaned_df[col].fillna(
                self.cleaned_df[col].mode()[0]
            )

        elif method == "Drop Rows":
            self.cleaned_df = self.cleaned_df.dropna(subset=[col])

        self.show_table(self.cleaned_df.head(10))


    def remove_outliers(self):
        col = self.clean_column.get()
        if not pd.api.types.is_numeric_dtype(self.cleaned_df[col]):
            messagebox.showwarning("Warning", "Numeric columns only")
            return

        Q1 = self.cleaned_df[col].quantile(0.25)
        Q3 = self.cleaned_df[col].quantile(0.75)
        IQR = Q3 - Q1

        self.cleaned_df = self.cleaned_df[
            (self.cleaned_df[col] >= Q1 - 1.5 * IQR) &
            (self.cleaned_df[col] <= Q3 + 1.5 * IQR)
        ]

        self.show_table(self.cleaned_df.head(10))

    def clear_plot(self):
        for widget in self.plot_frame.winfo_children():
            widget.destroy()

    def show_histogram(self):
        col = self.clean_column.get()
        if not pd.api.types.is_numeric_dtype(self.cleaned_df[col]):
            return

        self.clear_plot()
        fig = plt.Figure(figsize=(5, 4))
        ax = fig.add_subplot(111)
        ax.hist(self.cleaned_df[col].dropna(), bins=20)
        ax.set_title(f"Histogram of {col}")

        FigureCanvasTkAgg(fig, self.plot_frame).get_tk_widget().pack()

    def show_boxplot(self):
        col = self.clean_column.get()
        if not pd.api.types.is_numeric_dtype(self.cleaned_df[col]):
            return

        self.clear_plot()
        fig = plt.Figure(figsize=(5, 4))
        ax = fig.add_subplot(111)
        ax.boxplot(self.cleaned_df[col].dropna())
        ax.set_title(f"Boxplot of {col}")

        FigureCanvasTkAgg(fig, self.plot_frame).get_tk_widget().pack()

    def export_cleaned_csv(self):
        path = filedialog.asksaveasfilename(defaultextension=".csv")
        if path:
            self.cleaned_df.to_csv(path, index=False)
            messagebox.showinfo("Success", "CSV Exported Successfully")


if __name__ == "__main__":
    root = tk.Tk()
    app = CSVAnalyzerApp(root)
    root.mainloop()
