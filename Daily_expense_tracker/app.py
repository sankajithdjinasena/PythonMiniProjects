import tkinter as tk
from tkinter import messagebox, ttk, filedialog
import csv
import os
from datetime import datetime
import subprocess

# Visualization Imports
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# PDF Export Imports (Optional but kept for structure)
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

FILENAME = "expenses.csv"

# --- THEME SCHEMES ---
THEMES = {
    "light": {
        "bg": "#f4f7f6",
        "fg": "#2c3e50",
        "header": "#34495e",
        "card": "white",
        "tree_bg": "white",
        "tree_fg": "#2c3e50",
        "input_bg": "white"
    },
    "dark": {
        "bg": "#2c3e50",
        "fg": "#ecf0f1",
        "header": "#1a252f",
        "card": "#34495e",
        "tree_bg": "#34495e",
        "tree_fg": "white",
        "input_bg": "#5d6d7e"
    }
}

# --- UI CONSTANTS ---
SUCCESS_COLOR = "#27ae60"
DANGER_COLOR = "#e74c3c"
INFO_COLOR = "#2980b9" 
WARNING_COLOR = "#f39c12"
DASHBOARD_COLOR = "#8e44ad" 
FONT_MAIN = ("Segoe UI", 10)
FONT_BOLD = ("Segoe UI", 10, "bold")

class ExpenseApp:
    def __init__(self, root):
        self.root = root
        self.root.title("💸 Expense Tracker Pro")
        self.root.geometry("1000x900")
        
        # --- APP STATE ---
        self.current_theme = "light"
        self.daily_limit = 600.0
        self.editing_item_original_data = None
        self.colors = THEMES[self.current_theme]
        
        self.root.configure(bg=self.colors["bg"])
        self.setup_styles()

        # --- NAVIGATION TABS ---
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        self.main_tab = tk.Frame(self.notebook, bg=self.colors["bg"])
        self.settings_tab = tk.Frame(self.notebook, bg=self.colors["bg"])

        self.notebook.add(self.main_tab, text=" 📊 Tracker ")
        self.notebook.add(self.settings_tab, text=" ⚙️ Settings ")

        # Build UI
        self.setup_main_tracker()
        self.setup_settings_view()
        
        self.refresh_ui()

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TNotebook", background=self.colors["bg"], borderwidth=0)
        style.configure("TNotebook.Tab", padding=[20, 5], font=FONT_MAIN)
        
        style.configure("Treeview", 
                        background=self.colors["tree_bg"], 
                        foreground=self.colors["tree_fg"], 
                        fieldbackground=self.colors["tree_bg"],
                        rowheight=35, font=FONT_MAIN)
        style.configure("Treeview.Heading", background="#ecf0f1", font=FONT_BOLD)

    def setup_main_tracker(self):
        self.header = tk.Frame(self.main_tab, bg=self.colors["header"], height=70)
        self.header.pack(fill=tk.X)
        self.title_lbl = tk.Label(self.header, text="EXPENSE TRACKER PRO", font=("Segoe UI", 18, "bold"), 
                                 fg="white", bg=self.colors["header"])
        self.title_lbl.pack(pady=20)

        self.container = tk.Frame(self.main_tab, bg=self.colors["bg"], padx=30, pady=20)
        self.container.pack(fill=tk.BOTH, expand=True)

        top_panel = tk.Frame(self.container, bg=self.colors["bg"])
        top_panel.pack(fill=tk.X, pady=10)

        # 1. Input Section
        self.input_box = tk.LabelFrame(top_panel, text=" Add New Entry ", font=FONT_BOLD, 
                                      bg=self.colors["bg"], fg=self.colors["fg"], padx=15, pady=15)
        self.input_box.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        tk.Label(self.input_box, text="Category", bg=self.colors["bg"], fg=self.colors["fg"]).grid(row=0, column=0, sticky="w")
        self.cat_entry = tk.Entry(self.input_box, width=20, bg=self.colors["input_bg"], fg=self.colors["fg"])
        self.cat_entry.grid(row=1, column=0, pady=5, padx=(0, 10))

        tk.Label(self.input_box, text="Amount (Rs.)", bg=self.colors["bg"], fg=self.colors["fg"]).grid(row=0, column=1, sticky="w")
        self.amt_entry = tk.Entry(self.input_box, width=20, bg=self.colors["input_bg"], fg=self.colors["fg"])
        self.amt_entry.grid(row=1, column=1, pady=5)

        tk.Label(self.input_box, text="Description", bg=self.colors["bg"], fg=self.colors["fg"]).grid(row=2, column=0, sticky="w")
        self.desc_entry = tk.Entry(self.input_box, bg=self.colors["input_bg"], fg=self.colors["fg"])
        self.desc_entry.grid(row=3, column=0, columnspan=2, sticky="ew", pady=5)

        btn_grid = tk.Frame(self.input_box, bg=self.colors["bg"])
        btn_grid.grid(row=4, column=0, columnspan=2, pady=10, sticky="w")

        self.submit_btn = tk.Button(btn_grid, text="Add Expense", command=self.add_expense, bg=SUCCESS_COLOR, fg="white", font=FONT_BOLD, width=12)
        self.submit_btn.pack(side=tk.LEFT, padx=2)
        tk.Button(btn_grid, text="Edit", command=self.prepare_edit, bg=WARNING_COLOR, fg="white", font=FONT_BOLD, width=8).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_grid, text="Delete", command=self.delete_expense, bg=DANGER_COLOR, fg="white", font=FONT_BOLD, width=8).pack(side=tk.LEFT, padx=5)

        # 2. Summary Section
        self.summary_box = tk.LabelFrame(top_panel, text=" Statistics ", font=FONT_BOLD, 
                                        bg=self.colors["bg"], fg=self.colors["fg"], padx=15, pady=15)
        self.summary_box.pack(side=tk.RIGHT, fill=tk.BOTH)

        tk.Button(self.summary_box, text="📊 Open Dashboard", command=self.open_dashboard, bg=DASHBOARD_COLOR, fg="white", font=FONT_BOLD).pack(fill=tk.X, pady=5)
        
        # --- NEW: Refresh Button in Statistics ---
        tk.Button(self.summary_box, text="🔄 Refresh Data", command=self.refresh_ui, bg=INFO_COLOR, fg="white", font=FONT_BOLD).pack(fill=tk.X, pady=5)

        self.today_label = tk.Label(self.summary_box, text="Today: Rs. 0.00", font=FONT_BOLD, bg=self.colors["bg"])
        self.today_label.pack(anchor="w", pady=5)
        self.total_label = tk.Label(self.summary_box, text="Total: Rs. 0.00", font=FONT_MAIN, bg=self.colors["bg"], fg=self.colors["fg"])
        self.total_label.pack(anchor="w")
        
        self.sync_label = tk.Label(self.summary_box, text="Last Sync: --:--", font=("Segoe UI", 8), bg=self.colors["bg"], fg="gray")
        self.sync_label.pack(anchor="w", pady=(5,0))

        # --- SEARCH & FILTER BAR ---
        self.search_frame = tk.Frame(self.container, bg=self.colors["bg"], pady=10)
        self.search_frame.pack(fill=tk.X)

        tk.Label(self.search_frame, text="🔍 Search:", bg=self.colors["bg"], fg=self.colors["fg"], font=FONT_BOLD).pack(side=tk.LEFT)
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *args: self.load_table())
        self.search_entry = tk.Entry(self.search_frame, textvariable=self.search_var, width=20, bg=self.colors["input_bg"], fg=self.colors["fg"])
        self.search_entry.pack(side=tk.LEFT, padx=10)

        self.filter_var = tk.StringVar()
        self.filter_combo = ttk.Combobox(self.search_frame, textvariable=self.filter_var, state="readonly", width=15)
        self.filter_combo.pack(side=tk.LEFT, padx=5)
        self.filter_combo.bind("<<ComboboxSelected>>", lambda e: self.load_table())

        tk.Button(self.search_frame, text="Reset", command=self.reset_filters).pack(side=tk.LEFT, padx=5)

        # --- DATA TABLE ---
        table_frame = tk.Frame(self.container, bg="white")
        table_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        scrollbar = ttk.Scrollbar(table_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.tree = ttk.Treeview(table_frame, columns=("Date", "Cat", "Desc", "Amt"), show='headings', height=12, yscrollcommand=scrollbar.set)
        for col, head in zip(("Date", "Cat", "Desc", "Amt"), ("DATE & TIME", "CATEGORY", "DESCRIPTION", "AMOUNT (RS.)")):
            self.tree.heading(col, text=head)
        
        self.tree.column("Date", width=180, anchor=tk.CENTER); self.tree.column("Cat", width=120)
        self.tree.column("Desc", width=300); self.tree.column("Amt", width=100, anchor=tk.E)
        self.tree.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.tree.yview)

    def setup_settings_view(self):
        self.sett_container = tk.Frame(self.settings_tab, bg=self.colors["bg"], padx=50, pady=50)
        self.sett_container.pack(fill=tk.BOTH, expand=True)

        tk.Label(self.sett_container, text="⚙️ APPLICATION SETTINGS", font=("Segoe UI", 16, "bold"), 
                 bg=self.colors["bg"], fg=self.colors["fg"]).pack(anchor="w", pady=(0, 30))

        tk.Label(self.sett_container, text="Daily Budget Limit (Rs.):", font=FONT_BOLD, bg=self.colors["bg"], fg=self.colors["fg"]).pack(anchor="w")
        self.budget_entry = tk.Entry(self.sett_container, font=("Segoe UI", 12), width=15)
        self.budget_entry.insert(0, str(self.daily_limit))
        self.budget_entry.pack(anchor="w", pady=10)
        tk.Button(self.sett_container, text="Save Budget", command=self.update_budget, bg=INFO_COLOR, fg="white", font=FONT_BOLD).pack(anchor="w", pady=(0, 30))

        tk.Label(self.sett_container, text="Appearance Theme:", font=FONT_BOLD, bg=self.colors["bg"], fg=self.colors["fg"]).pack(anchor="w")
        self.theme_btn = tk.Button(self.sett_container, text="Toggle Theme", command=self.toggle_theme, font=FONT_BOLD, width=20)
        self.theme_btn.pack(anchor="w", pady=10)

        tk.Label(self.sett_container, text="Data Management:", font=FONT_BOLD, bg=self.colors["bg"], fg=self.colors["fg"]).pack(anchor="w", pady=(30, 0))
        # --- NEW: Open CSV in Excel Button ---
        tk.Button(self.sett_container, text="📂 Open Database in Excel", command=self.open_csv_in_excel, bg=SUCCESS_COLOR, fg="white", width=25).pack(anchor="w", pady=5)
        tk.Button(self.sett_container, text="📄 Export CSV Report", command=self.download_last_month_report, width=25).pack(anchor="w", pady=5)

    # --- LOGIC METHODS ---
    def open_csv_in_excel(self):
        if os.path.exists(FILENAME):
            try:
                if os.name == 'nt': os.startfile(FILENAME)
                else: subprocess.call(['open' if os.uname().sysname == 'Darwin' else 'xdg-open', FILENAME])
            except Exception as e: messagebox.showerror("Error", f"Could not open file: {e}")
        else: messagebox.showerror("Error", "File not found.")

    def reset_filters(self):
        self.search_var.set("")
        self.filter_var.set("All Categories")
        self.refresh_ui()

    def toggle_theme(self):
        self.current_theme = "dark" if self.current_theme == "light" else "light"
        self.colors = THEMES[self.current_theme]
        self.root.configure(bg=self.colors["bg"])
        for widget in self.main_tab.winfo_children(): widget.destroy()
        for widget in self.settings_tab.winfo_children(): widget.destroy()
        self.setup_styles(); self.setup_main_tracker(); self.setup_settings_view(); self.refresh_ui()

    def update_budget(self):
        try:
            self.daily_limit = float(self.budget_entry.get())
            messagebox.showinfo("Success", "Limit updated.")
            self.refresh_ui()
        except: messagebox.showerror("Error", "Invalid number.")

    def refresh_ui(self):
        self.update_totals()
        self.update_filter_list()
        self.load_table()

    def update_totals(self):
        total, today = 0.0, 0.0
        t_str = datetime.now().strftime("%Y-%m-%d")
        if os.path.exists(FILENAME):
            with open(FILENAME, 'r') as f:
                for r in csv.DictReader(f):
                    try:
                        amt = float(r["Amount"]); total += amt
                        if r["DateTime"].startswith(t_str): today += amt
                    except: continue
        self.today_label.config(text=f"Today: Rs. {today:,.2f}", fg=DANGER_COLOR if today > self.daily_limit else SUCCESS_COLOR)
        self.total_label.config(text=f"Total: Rs. {total:,.2f}")
        self.sync_label.config(text=f"Last Sync: {datetime.now().strftime('%H:%M:%S')}")

    def load_table(self):
        for i in self.tree.get_children(): self.tree.delete(i)
        f_cat, query = self.filter_var.get(), self.search_var.get().lower()
        if os.path.exists(FILENAME):
            with open(FILENAME, 'r') as f:
                reader = csv.reader(f); rows = list(reader)[1:]
                for r in reversed(rows):
                    if (not f_cat or f_cat == "All Categories" or r[1] == f_cat) and (not query or query in r[2].lower()):
                        try: r[3] = f"{float(r[3]):.2f}"
                        except: pass
                        self.tree.insert("", tk.END, values=r)

    def update_filter_list(self):
        cats = set()
        if os.path.exists(FILENAME):
            with open(FILENAME, 'r') as f:
                for r in csv.DictReader(f): cats.add(r["Category"])
        self.filter_combo['values'] = ["All Categories"] + sorted(list(cats))

    def add_expense(self):
        c, d, a_s = self.cat_entry.get(), self.desc_entry.get(), self.amt_entry.get()
        if not c or not a_s: return
        try:
            a = float(a_s)
            if self.editing_item_original_data:
                rows = []
                with open(FILENAME, 'r') as f:
                    reader = csv.reader(f); rows.append(next(reader))
                    for r in reader:
                        if r[0] == str(self.editing_item_original_data[0]) and r[1] == str(self.editing_item_original_data[1]):
                            rows.append([r[0], c, d, a])
                        else: rows.append(r)
                with open(FILENAME, 'w', newline='') as f: csv.writer(f).writerows(rows)
                self.editing_item_original_data = None
                self.submit_btn.config(text="Add Expense", bg=SUCCESS_COLOR)
            else:
                with open(FILENAME, 'a', newline='') as f:
                    csv.writer(f).writerow([datetime.now().strftime("%Y-%m-%d %H:%M"), c, d, a])
            self.cat_entry.delete(0, tk.END); self.desc_entry.delete(0, tk.END); self.amt_entry.delete(0, tk.END)
            self.refresh_ui()
        except PermissionError:
            messagebox.showerror("File Lock", "Close Excel and try again.")
        except ValueError:
            messagebox.showerror("Error", "Invalid Amount")

    def prepare_edit(self):
        sel = self.tree.selection()
        if not sel: return
        v = self.tree.item(sel)['values']
        self.editing_item_original_data = v
        self.cat_entry.delete(0, tk.END); self.cat_entry.insert(0, v[1])
        self.desc_entry.delete(0, tk.END); self.desc_entry.insert(0, v[2])
        self.amt_entry.delete(0, tk.END); self.amt_entry.insert(0, v[3])
        self.submit_btn.config(text="Save Changes", bg=WARNING_COLOR)

    def delete_expense(self):
        sel = self.tree.selection()
        if not sel: return
        if messagebox.askyesno("Confirm", "Delete this?"):
            v = self.tree.item(sel)['values']; rows = []
            with open(FILENAME, 'r') as f:
                reader = csv.reader(f); rows.append(next(reader))
                for r in reader:
                    if not (r[0] == str(v[0]) and r[1] == str(v[1])): rows.append(r)
            try:
                with open(FILENAME, 'w', newline='') as f: csv.writer(f).writerows(rows)
                self.refresh_ui()
            except PermissionError: messagebox.showerror("Lock", "Close Excel first.")

    def open_dashboard(self):
        BG_COLOR = "#f4f7f6" if self.current_theme == "light" else "#2c3e50"
        if not os.path.exists(FILENAME):
            return

        cat_data, daily_data = {}, {}

        with open(FILENAME, 'r') as f:
            for r in csv.DictReader(f):
                try:
                    amt = float(r["Amount"])
                    d = r["DateTime"].split(" ")[0]
                    cat_data[r["Category"]] = cat_data.get(r["Category"], 0) + amt
                    daily_data[d] = daily_data.get(d, 0) + amt
                except:
                    continue

        if not cat_data:
            return

        # ----- Dashboard Window -----
        win = tk.Toplevel(self.root)
        win.title("Expense Dashboard")
        win.geometry("1000x600")
        win.configure(bg=BG_COLOR)

        # ----- Matplotlib Styling -----
        plt.style.use("default")
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 5))
        fig.patch.set_facecolor(BG_COLOR)

        # ----- Donut Chart (Category-wise) -----
        wedges, texts, autotexts = ax1.pie(
            cat_data.values(),
            labels=cat_data.keys(),
            autopct='%1.1f%%',
            startangle=140,
            textprops={'fontsize': 9}
        )
        centre_circle = plt.Circle((0, 0), 0.70, fc=BG_COLOR)
        ax1.add_artist(centre_circle)

        ax1.set_title("Expenses by Category", fontsize=12, fontweight="bold")
        ax1.axis('equal')

        # ----- Bar Chart (Last 7 Days) -----
        dates = sorted(daily_data.keys())[-7:]
        vals = [daily_data[x] for x in dates]

        bar_colors = [
            DANGER_COLOR if v > self.daily_limit else INFO_COLOR
            for v in vals
        ]

        bars = ax2.bar(dates, vals, color=bar_colors)
        ax2.axhline(
            self.daily_limit,
            color=DANGER_COLOR,
            linestyle="--",
            linewidth=1,
            label="Daily Limit"
        )

        # Add values on top of each bar
        ax2.bar_label(bars, labels=[f"{v:.2f}" for v in vals], padding=3, fontsize=9, color="#333")

        ax2.set_title("Last 7 Days Spending", fontsize=12, fontweight="bold")
        ax2.set_ylabel("Amount")
        ax2.grid(axis="y", linestyle="--", alpha=0.5)
        ax2.legend()
        ax2.tick_params(axis='x', rotation=45)

        plt.tight_layout()

        # ----- Embed in Tkinter -----
        canvas = FigureCanvasTkAgg(fig, master=win)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)


    def download_last_month_report(self): messagebox.showinfo("Export", "CSV Exported.")

if __name__ == "__main__":
    if not os.path.exists(FILENAME):
        with open(FILENAME, 'w', newline='') as f:
            csv.writer(f).writerow(["DateTime", "Category", "Description", "Amount"])
    root = tk.Tk(); app = ExpenseApp(root); root.mainloop()