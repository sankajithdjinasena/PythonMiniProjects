import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import pandas as pd
import matplotlib.pyplot as plt


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

        # ===== Outlier Controls =====
        outlier_frame = tk.Frame(root, bg="#ecf0f1")
        outlier_frame.pack(fill="x", padx=10, pady=5)

        tk.Label(
            outlier_frame,
            text="Select Column for Outlier Detection:",
            bg="#ecf0f1",
            font=("Segoe UI", 10)
        ).pack(side="left", padx=5)

        self.column_select = ttk.Combobox(
            outlier_frame,
            state="readonly",
            width=30
        )
        self.column_select.pack(side="left", padx=5)

        outlier_btn = tk.Button(
            outlier_frame,
            text="Show Outliers (Boxplot)",
            command=self.show_outliers
        )
        outlier_btn.pack(side="left", padx=10)

        # ===== Data Cleaning Controls =====
        clean_frame = tk.Frame(self.root, bg="#ecf0f1")
        clean_frame.pack(fill="x", padx=10, pady=5)

        tk.Label(
            clean_frame,
            text="Select Column:",
            bg="#ecf0f1"
        ).pack(side="left", padx=5)

        self.clean_column = ttk.Combobox(
            clean_frame,
            state="readonly",
            width=25
        )
        self.clean_column.pack(side="left", padx=5)

        tk.Label(
            clean_frame,
            text="Missing Value Method:",
            bg="#ecf0f1"
        ).pack(side="left", padx=5)

        self.missing_method = ttk.Combobox(
            clean_frame,
            state="readonly",
            width=15,
            values=["Mean", "Median", "Mode", "Drop Rows"]
        )
        self.missing_method.pack(side="left", padx=5)
        self.missing_method.current(0)

        tk.Button(
            clean_frame,
            text="Apply Missing Value Handling",
            command=self.handle_missing_values
        ).pack(side="left", padx=10)

        tk.Button(
            clean_frame,
            text="Remove Outliers",
            command=self.remove_outliers
        ).pack(side="left", padx=10)



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

        # Populate numeric columns only
        numeric_cols = self.df.select_dtypes(include="number").columns.tolist()
        self.column_select["values"] = numeric_cols

        if numeric_cols:
            self.column_select.current(0)

        # Initialize cleaned dataframe
        self.cleaned_df = self.df.copy()

        # Populate column selectors
        all_columns = self.df.columns.tolist()
        self.clean_column["values"] = all_columns
        self.clean_column.current(0)



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

    def show_outliers(self):
        if self.df is None:
            messagebox.showwarning("Warning", "Please load a CSV file first.")
            return

        col = self.column_select.get()
        if not col:
            messagebox.showwarning("Warning", "Please select a column.")
            return

        data = self.df[col].dropna()

        # IQR method
        Q1 = data.quantile(0.25)
        Q3 = data.quantile(0.75)
        IQR = Q3 - Q1

        lower = Q1 - 1.5 * IQR
        upper = Q3 + 1.5 * IQR

        outliers = data[(data < lower) | (data > upper)]

        # Boxplot
        plt.figure()
        plt.boxplot(data, vert=True)
        plt.title(f"Boxplot for {col}")
        plt.ylabel(col)
        plt.show()

        messagebox.showinfo(
            "Outlier Result",
            f"Column: {col}\nOutliers detected: {len(outliers)}"
        )

    def handle_missing_values(self):
        if self.cleaned_df is None:
            return

        col = self.clean_column.get()
        method = self.missing_method.get()

        if col == "":
            return

        if method == "Mean":
            if pd.api.types.is_numeric_dtype(self.cleaned_df[col]):
                self.cleaned_df[col].fillna(self.cleaned_df[col].mean(), inplace=True)
            else:
                messagebox.showwarning("Warning", "Mean can be applied only to numeric columns.")
                return

        elif method == "Median":
            if pd.api.types.is_numeric_dtype(self.cleaned_df[col]):
                self.cleaned_df[col].fillna(self.cleaned_df[col].median(), inplace=True)
            else:
                messagebox.showwarning("Warning", "Median can be applied only to numeric columns.")
                return

        elif method == "Mode":
            self.cleaned_df[col].fillna(self.cleaned_df[col].mode()[0], inplace=True)

        elif method == "Drop Rows":
            self.cleaned_df.dropna(subset=[col], inplace=True)

        self.refresh_after_cleaning(f"Missing values handled for column: {col}")

    def remove_outliers(self):
        if self.cleaned_df is None:
            return

        col = self.clean_column.get()

        if not pd.api.types.is_numeric_dtype(self.cleaned_df[col]):
            messagebox.showwarning("Warning", "Outlier removal works only for numeric columns.")
            return

        data = self.cleaned_df[col].dropna()

        Q1 = data.quantile(0.25)
        Q3 = data.quantile(0.75)
        IQR = Q3 - Q1

        lower = Q1 - 1.5 * IQR
        upper = Q3 + 1.5 * IQR

        before = len(self.cleaned_df)
        self.cleaned_df = self.cleaned_df[
            (self.cleaned_df[col] >= lower) & (self.cleaned_df[col] <= upper)
        ]
        after = len(self.cleaned_df)

        self.refresh_after_cleaning(
            f"Outliers removed from {col}. Rows removed: {before - after}"
        )

    def refresh_after_cleaning(self, message):
        self.output.insert(tk.END, f"\n{message}\n")
        self.show_table(self.cleaned_df.head(10))
        self.export_btn.config(state="normal")



if __name__ == "__main__":
    root = tk.Tk()
    app = CSVAnalyzerApp(root)
    root.mainloop()
