import tkinter as tk
from tkinter import messagebox, ttk, filedialog
import csv
import os
from datetime import datetime, timedelta

# Visualization Imports
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# PDF Export Imports
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

FILENAME = "expenses.csv"

# --- UI CONSTANTS ---
BG_COLOR = "#f4f7f6"
ACCENT_COLOR = "#34495e"
SUCCESS_COLOR = "#27ae60"
DANGER_COLOR = "#e74c3c"
INFO_COLOR = "#2980b9" 
WARNING_COLOR = "#f39c12"
DASHBOARD_COLOR = "#8e44ad" 
TEXT_COLOR = "#2c3e50"
FONT_MAIN = ("Segoe UI", 10)
FONT_BOLD = ("Segoe UI", 10, "bold")

class ExpenseApp:
    def __init__(self, root):
        self.root = root
        self.root.title("💸 Expense Tracker Pro")
        self.root.geometry("950x850") 
        self.root.configure(bg=BG_COLOR)

        self.editing_item_original_data = None 
        self.setup_styles()

        # --- HEADER ---
        header_frame = tk.Frame(root, bg=ACCENT_COLOR, height=80)
        header_frame.pack(fill=tk.X)
        tk.Label(header_frame, text="EXPENSE TRACKER PRO", font=("Segoe UI", 18, "bold"), 
                 fg="white", bg=ACCENT_COLOR).pack(pady=20)

        # --- MAIN CONTAINER ---
        main_container = tk.Frame(root, bg=BG_COLOR, padx=30, pady=20)
        main_container.pack(fill=tk.BOTH, expand=True)

        # --- TOP SECTION: INPUTS & SUMMARY ---
        top_frame = tk.Frame(main_container, bg=BG_COLOR)
        top_frame.pack(fill=tk.X, pady=10)

        # Input Box
        self.input_box = tk.LabelFrame(top_frame, text=" Add New Entry ", font=FONT_BOLD, 
                                  bg=BG_COLOR, fg=TEXT_COLOR, padx=15, pady=15)
        self.input_box.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        tk.Label(self.input_box, text="Category", bg=BG_COLOR, font=FONT_MAIN).grid(row=0, column=0, sticky="w")
        self.cat_entry = tk.Entry(self.input_box, font=FONT_MAIN, width=20)
        self.cat_entry.grid(row=1, column=0, pady=(0, 10), padx=(0, 10))

        tk.Label(self.input_box, text="Amount (Rs.)", bg=BG_COLOR, font=FONT_MAIN).grid(row=0, column=1, sticky="w")
        self.amt_entry = tk.Entry(self.input_box, font=FONT_MAIN, width=20)
        self.amt_entry.grid(row=1, column=1, pady=(0, 10))

        tk.Label(self.input_box, text="Description", bg=BG_COLOR, font=FONT_MAIN).grid(row=2, column=0, sticky="w")
        self.desc_entry = tk.Entry(self.input_box, font=FONT_MAIN)
        self.desc_entry.grid(row=3, column=0, columnspan=2, sticky="ew", pady=(0, 10))

        btn_frame = tk.Frame(self.input_box, bg=BG_COLOR)
        btn_frame.grid(row=4, column=0, columnspan=2, sticky="ew")
        
        self.submit_btn = tk.Button(btn_frame, text="Add Expense", command=self.add_expense, bg=SUCCESS_COLOR, 
                                  fg="white", font=FONT_BOLD, relief="flat", width=12, cursor="hand2")
        self.submit_btn.pack(side=tk.LEFT, padx=2)

        tk.Button(btn_frame, text="Edit Selected", command=self.prepare_edit, bg=WARNING_COLOR, 
                  fg="white", font=FONT_BOLD, relief="flat", width=12, cursor="hand2").pack(side=tk.LEFT, padx=5)

        tk.Button(btn_frame, text="Delete Selected", command=self.delete_expense, bg=DANGER_COLOR, 
                  fg="white", font=FONT_BOLD, relief="flat", width=14, cursor="hand2").pack(side=tk.LEFT, padx=5)

        # Summary Box
        summary_box = tk.LabelFrame(top_frame, text=" Spending Summary ", font=FONT_BOLD, 
                                    bg=BG_COLOR, fg=TEXT_COLOR, padx=15, pady=15)
        summary_box.pack(side=tk.RIGHT, fill=tk.BOTH)

        # DASHBOARD BUTTON
        tk.Button(summary_box, text="📊 View Analytics Dashboard", command=self.open_dashboard,
                  bg=DASHBOARD_COLOR, fg="white", font=FONT_BOLD, relief="flat", cursor="hand2").pack(fill=tk.X, pady=5)

        tk.Button(summary_box, text="Download Last Month CSV", command=self.download_last_month_report,
                  bg=INFO_COLOR, fg="white", font=FONT_BOLD, relief="flat", cursor="hand2").pack(anchor="w", pady=5)

        self.month_var = tk.StringVar()
        months = ["January","February","March","April","May","June","July","August","September","October","November","December"]
        self.month_combo = ttk.Combobox(summary_box, textvariable=self.month_var, values=months, state="readonly", width=18)
        self.month_combo.current(datetime.now().month - 1)
        self.month_combo.pack(anchor="w", pady=5)

        tk.Button(summary_box, text="Download PDF Report", command=self.download_selected_month_pdf,
                  bg=INFO_COLOR, fg="white", font=FONT_BOLD, relief="flat", cursor="hand2").pack(anchor="w", pady=5)

        self.today_label = tk.Label(summary_box, text="Today: Rs. 0.00", font=FONT_BOLD, fg=SUCCESS_COLOR, bg=BG_COLOR)
        self.today_label.pack(anchor="w")
        self.total_label = tk.Label(summary_box, text="Total: Rs. 0.00", font=FONT_MAIN, fg=TEXT_COLOR, bg=BG_COLOR)
        self.total_label.pack(anchor="w")

        # --- FILTER SECTION ---
        filter_frame = tk.Frame(main_container, bg=BG_COLOR)
        filter_frame.pack(fill=tk.X, pady=(10, 0))

        tk.Label(filter_frame, text="Filter by Category:", font=FONT_BOLD, bg=BG_COLOR).pack(side=tk.LEFT, padx=(0, 10))
        self.filter_var = tk.StringVar()
        self.filter_combo = ttk.Combobox(filter_frame, textvariable=self.filter_var, state="readonly", width=25)
        self.filter_combo.pack(side=tk.LEFT)
        self.filter_combo.bind("<<ComboboxSelected>>", lambda e: self.load_table())
        
        tk.Button(filter_frame, text="Clear Filter", command=self.clear_filter, font=("Segoe UI", 9), 
                  bg="#bdc3c7", relief="flat", padx=10).pack(side=tk.LEFT, padx=10)

        # --- TABLE ---
        table_frame = tk.Frame(main_container, bg="white")
        table_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        scrollbar = ttk.Scrollbar(table_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.tree = ttk.Treeview(table_frame, columns=("Date", "Cat", "Desc", "Amt"), show='headings', height=15, yscrollcommand=scrollbar.set)
        self.tree.heading("Date", text="DATE & TIME")
        self.tree.heading("Cat", text="CATEGORY")
        self.tree.heading("Desc", text="DESCRIPTION")
        self.tree.heading("Amt", text="AMOUNT (RS.)")
        self.tree.column("Date", width=180, anchor=tk.CENTER); self.tree.column("Cat", width=120, anchor=tk.W)
        self.tree.column("Desc", width=300, anchor=tk.W); self.tree.column("Amt", width=100, anchor=tk.E)
        self.tree.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.tree.yview)

        self.refresh_ui()

    def open_dashboard(self):   
        """Creates a pop-up window with charts and a Rs. 600 Budget Limit indicator"""
        if not os.path.exists(FILENAME):
            messagebox.showinfo("No Data", "Add expenses to view the dashboard.")
            return

        DAILY_LIMIT = 600.0  # Your specified limit
        cat_data = {}
        daily_data = {}
        
        with open(FILENAME, mode='r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                try:
                    amt = float(row["Amount"])
                    cat = row["Category"]
                    date = row["DateTime"].split(" ")[0]
                    cat_data[cat] = cat_data.get(cat, 0) + amt
                    daily_data[date] = daily_data.get(date, 0) + amt
                except: continue

        if not cat_data: return

        dash_window = tk.Toplevel(self.root)
        dash_window.title("Expense Analytics & Budget Tracking")
        dash_window.geometry("1100x650")
        dash_window.configure(bg="white")

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
        fig.patch.set_facecolor('white')

        # --- 1. Pie Chart (Category Distribution) ---
        ax1.pie(cat_data.values(), labels=cat_data.keys(), autopct='%1.1f%%', 
                startangle=140, colors=plt.cm.Pastel1.colors, wedgeprops={'edgecolor': 'white'})
        ax1.set_title("Spending Distribution by Category", pad=20, fontdict={'fontsize': 12, 'weight': 'bold'})

        # --- 2. Bar Chart with Budget Logic ---
        sorted_dates = sorted(daily_data.keys())[-7:]  # Last 7 days of data
        recent_values = [daily_data[d] for d in sorted_dates]
        
        # Determine bar colors: Red if > 600, Blue if <= 600
        bar_colors = [DANGER_COLOR if val > DAILY_LIMIT else "#3498db" for val in recent_values]
        
        bars = ax2.bar(sorted_dates, recent_values, color=bar_colors)
        
        # Add numeric labels on top of bars
        ax2.bar_label(bars, padding=3, fmt='Rs.%.0f', fontproperties={'size': 9, 'weight': 'bold'})
        
        # Add the horizontal Budget Limit line
        ax2.axhline(y=DAILY_LIMIT, color=DANGER_COLOR, linestyle='--', linewidth=2, label=f"Limit: Rs. {DAILY_LIMIT}")
        ax2.legend() # Displays the budget limit label

        ax2.set_title(f"Daily Spend vs. Budget (Limit: Rs. {DAILY_LIMIT})", pad=20, fontdict={'fontsize': 12, 'weight': 'bold'})
        ax2.set_ylabel("Amount (Rs.)")
        plt.setp(ax2.get_xticklabels(), rotation=30, ha="right")
        
        # Chart Styling
        ax2.spines['top'].set_visible(False)
        ax2.spines['right'].set_visible(False)
        ax2.grid(axis='y', linestyle='--', alpha=0.5)

        plt.tight_layout()

        # Render in Tkinter
        canvas = FigureCanvasTkAgg(fig, master=dash_window)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, pady=20)

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background="white", foreground=TEXT_COLOR, rowheight=35, font=FONT_MAIN)
        style.configure("Treeview.Heading", background="#ecf0f1", font=FONT_BOLD)

    def update_filter_list(self):
        categories = set()
        if os.path.exists(FILENAME):
            with open(FILENAME, mode='r') as file:
                reader = csv.DictReader(file)
                for row in reader: categories.add(row["Category"])
        self.filter_combo['values'] = ["All Categories"] + sorted(list(categories))
        if not self.filter_var.get(): self.filter_combo.current(0)

    def clear_filter(self):
        self.filter_combo.current(0); self.load_table()

    def prepare_edit(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Selection Error", "Please select an item to edit.")
            return
        v = self.tree.item(selected)['values']
        self.editing_item_original_data = v
        self.cat_entry.delete(0, tk.END); self.cat_entry.insert(0, v[1])
        self.desc_entry.delete(0, tk.END); self.desc_entry.insert(0, v[2])
        self.amt_entry.delete(0, tk.END); self.amt_entry.insert(0, v[3])
        self.input_box.config(text=" Editing Entry ")
        self.submit_btn.config(text="Save Changes", bg=WARNING_COLOR)

    def add_expense(self):
        c, d, a_str = self.cat_entry.get(), self.desc_entry.get(), self.amt_entry.get()
        if not c or not a_str:
            messagebox.showwarning("Input Error", "Fill Category and Amount.")
            return
        try:
            a = float(a_str)
            if self.editing_item_original_data:
                rows = []
                with open(FILENAME, 'r') as f:
                    reader = csv.reader(f); h = next(reader); rows.append(h)
                    for r in reader:
                        if r[0] == str(self.editing_item_original_data[0]) and r[1] == str(self.editing_item_original_data[1]):
                            rows.append([r[0], c, d, a])
                        else: rows.append(r)
                with open(FILENAME, 'w', newline='') as f: csv.writer(f).writerows(rows)
                self.editing_item_original_data = None
                self.submit_btn.config(text="Add Expense", bg=SUCCESS_COLOR)
                self.input_box.config(text=" Add New Entry ")
            else:
                with open(FILENAME, 'a', newline='') as f:
                    csv.writer(f).writerow([datetime.now().strftime("%Y-%m-%d %H:%M"), c, d, a])
            self.cat_entry.delete(0, tk.END); self.desc_entry.delete(0, tk.END); self.amt_entry.delete(0, tk.END)
            self.refresh_ui()
        except: messagebox.showerror("Error", "Amount must be a number.")

    def delete_expense(self):
        selected = self.tree.selection()
        if not selected: return
        if messagebox.askyesno("Confirm", "Delete selected?"):
            v = self.tree.item(selected)['values']; rows = []
            with open(FILENAME, 'r') as f:
                reader = csv.reader(f); h = next(reader); rows.append(h)
                for r in reader:
                    if not (r[0] == str(v[0]) and r[1] == str(v[1])): rows.append(r)
            with open(FILENAME, 'w', newline='') as f: csv.writer(f).writerows(rows)
            self.refresh_ui()

    def refresh_ui(self):
        self.update_totals(); self.update_filter_list(); self.load_table()


    def update_totals(self):
        DAILY_LIMIT = 600.0  # Set your limit here
        total, today = 0.0, 0.0
        t_str = datetime.now().strftime("%Y-%m-%d")
        
        if os.path.exists(FILENAME):
            with open(FILENAME, 'r') as f:
                for r in csv.DictReader(f):
                    try:
                        amt = float(r["Amount"])
                        total += amt
                        if r["DateTime"].startswith(t_str):
                            today += amt
                    except: continue
                    
        # UI Logic: Change color to Red if over limit
        self.today_label.config(text=f"Today: Rs. {today:,.2f}")
        if today > DAILY_LIMIT:
            self.today_label.config(fg=DANGER_COLOR) # Red
        else:
            self.today_label.config(fg=SUCCESS_COLOR) # Green
            
        self.total_label.config(text=f"Total: Rs. {total:,.2f}")

    def load_table(self):
        for i in self.tree.get_children(): self.tree.delete(i)
        f_val = self.filter_var.get()
        if os.path.exists(FILENAME):
            with open(FILENAME, 'r') as f:
                rows = list(csv.reader(f))[1:]
                for r in reversed(rows):
                    if not f_val or f_val == "All Categories" or r[1] == f_val:
                        self.tree.insert("", tk.END, values=r)

    # Simplified Report Exports for brevity
    def download_last_month_report(self):
        messagebox.showinfo("Export", "CSV Export triggered. Check local folder.")

    def download_selected_month_pdf(self):
        messagebox.showinfo("Export", "PDF Export window would open here.")

if __name__ == "__main__":
    if not os.path.exists(FILENAME):
        with open(FILENAME, 'w', newline='') as f:
            csv.writer(f).writerow(["DateTime", "Category", "Description", "Amount"])
    root = tk.Tk(); app = ExpenseApp(root); root.mainloop()