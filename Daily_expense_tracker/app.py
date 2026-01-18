import tkinter as tk
from tkinter import messagebox, ttk
import csv
import os
from datetime import datetime, timedelta

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
INFO_COLOR = "#2980b9"  # New color for weekly
TEXT_COLOR = "#2c3e50"
FONT_MAIN = ("Segoe UI", 10)
FONT_BOLD = ("Segoe UI", 10, "bold")

class ExpenseApp:
    def __init__(self, root):
        self.root = root
        self.root.title("💸 Expense Tracker Pro")
        self.root.geometry("900x750") # Slightly wider/taller for new UI
        self.root.configure(bg=BG_COLOR)

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
        input_box = tk.LabelFrame(top_frame, text=" Add New Entry ", font=FONT_BOLD, 
                                  bg=BG_COLOR, fg=TEXT_COLOR, padx=15, pady=15)
        input_box.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        tk.Label(input_box, text="Category", bg=BG_COLOR, font=FONT_MAIN).grid(row=0, column=0, sticky="w")
        self.cat_entry = tk.Entry(input_box, font=FONT_MAIN, width=20)
        self.cat_entry.grid(row=1, column=0, pady=(0, 10), padx=(0, 10))

        tk.Label(input_box, text="Amount (Rs.)", bg=BG_COLOR, font=FONT_MAIN).grid(row=0, column=1, sticky="w")
        self.amt_entry = tk.Entry(input_box, font=FONT_MAIN, width=20)
        self.amt_entry.grid(row=1, column=1, pady=(0, 10))

        tk.Label(input_box, text="Description", bg=BG_COLOR, font=FONT_MAIN).grid(row=2, column=0, sticky="w")
        self.desc_entry = tk.Entry(input_box, font=FONT_MAIN)
        self.desc_entry.grid(row=3, column=0, columnspan=2, sticky="ew", pady=(0, 10))

        btn_frame = tk.Frame(input_box, bg=BG_COLOR)
        btn_frame.grid(row=4, column=0, columnspan=2, sticky="ew")
        
        tk.Button(btn_frame, text="Add Expense", command=self.add_expense, bg=SUCCESS_COLOR, 
                  fg="white", font=FONT_BOLD, relief="flat", width=15, cursor="hand2").pack(side=tk.LEFT, padx=2)
        tk.Button(btn_frame, text="Delete Selected", command=self.delete_expense, bg=DANGER_COLOR, 
                  fg="white", font=FONT_BOLD, relief="flat", width=15, cursor="hand2").pack(side=tk.LEFT, padx=10)

        # Summary Box (Modified to include Weekly)
        summary_box = tk.LabelFrame(top_frame, text=" Spending Summary ", font=FONT_BOLD, 
                                    bg=BG_COLOR, fg=TEXT_COLOR, padx=15, pady=15)
        tk.Button(
            summary_box,
            text="Download Last Month Report",
            command=self.download_last_month_report,
            bg=INFO_COLOR,
            fg="white",
            font=FONT_BOLD,
            relief="flat",
            cursor="hand2"
            ).pack(anchor="w", pady=10)

        tk.Label(summary_box, text="Select Month", bg=BG_COLOR, font=FONT_MAIN).pack(anchor="w")

        self.month_var = tk.StringVar()
        months = [
            "January","February","March","April","May","June",
            "July","August","September","October","November","December"
        ]
        self.month_combo = ttk.Combobox(
            summary_box,
            textvariable=self.month_var,
            values=months,
            state="readonly",
            width=18
        )
        self.month_combo.current(datetime.now().month - 1)
        self.month_combo.pack(anchor="w", pady=5)

        tk.Button(
            summary_box,
            text="Download PDF Report",
            command=self.download_selected_month_pdf,
            bg=INFO_COLOR,
            fg="white",
            font=FONT_BOLD,
            relief="flat",
            cursor="hand2"
        ).pack(anchor="w", pady=10)


        summary_box.pack(side=tk.RIGHT, fill=tk.BOTH)

        self.today_label = tk.Label(summary_box, text="Today: Rs. 0.00", font=FONT_BOLD, 
                                    fg=SUCCESS_COLOR, bg=BG_COLOR)
        self.today_label.pack(anchor="w", pady=2)

        self.weekly_label = tk.Label(summary_box, text="This Week: Rs. 0.00", font=FONT_BOLD, 
                                     fg=INFO_COLOR, bg=BG_COLOR)
        self.weekly_label.pack(anchor="w", pady=2)
        
        self.total_label = tk.Label(summary_box, text="Total: Rs. 0.00", font=FONT_MAIN, 
                                    fg=TEXT_COLOR, bg=BG_COLOR)
        self.total_label.pack(anchor="w", pady=2)

        # --- BOTTOM SECTION: TABLE ---
        table_frame = tk.Frame(main_container, bg="white")
        table_frame.pack(fill=tk.BOTH, expand=True, pady=20)

        scrollbar = ttk.Scrollbar(table_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.tree = ttk.Treeview(table_frame, columns=("Date", "Cat", "Desc", "Amt"), 
                                  show='headings', height=15, yscrollcommand=scrollbar.set)
        
        self.tree.heading("Date", text="DATE & TIME")
        self.tree.heading("Cat", text="CATEGORY")
        self.tree.heading("Desc", text="DESCRIPTION")
        self.tree.heading("Amt", text="AMOUNT (RS.)")
        
        self.tree.column("Date", width=180, anchor=tk.CENTER)
        self.tree.column("Cat", width=120, anchor=tk.W)
        self.tree.column("Desc", width=300, anchor=tk.W)
        self.tree.column("Amt", width=100, anchor=tk.E)
        
        self.tree.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.tree.yview)

        self.refresh_ui()

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background="white", foreground=TEXT_COLOR, rowheight=35, fieldbackground="white", font=FONT_MAIN)
        style.configure("Treeview.Heading", background="#ecf0f1", foreground=TEXT_COLOR, font=FONT_BOLD, relief="flat")
        style.map("Treeview", background=[('selected', '#d5dbdb')])

    def add_expense(self):
        category = self.cat_entry.get()
        description = self.desc_entry.get()
        amount_str = self.amt_entry.get()

        if not category or not amount_str:
            messagebox.showwarning("Input Error", "Please fill in Category and Amount")
            return

        try:
            amount = float(amount_str)
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")

            with open(FILENAME, mode='a', newline='') as file:
                writer = csv.writer(file)
                writer.writerow([timestamp, category, description, amount])

            self.cat_entry.delete(0, tk.END)
            self.desc_entry.delete(0, tk.END)
            self.amt_entry.delete(0, tk.END)
            self.refresh_ui()

        except ValueError:
            messagebox.showerror("Error", "Amount must be a number")

    def delete_expense(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Selection Error", "Please select an item to delete.")
            return

        if messagebox.askyesno("Confirm", "Delete this expense?"):
            item_data = self.tree.item(selected_item)['values']
            updated_rows = []
            deleted = False
            
            with open(FILENAME, mode='r') as file:
                reader = csv.reader(file)
                header = next(reader)
                updated_rows.append(header)
                for row in reader:
                    if not deleted and row[0] == str(item_data[0]) and float(row[3]) == float(item_data[3]):
                        deleted = True
                        continue
                    updated_rows.append(row)

            with open(FILENAME, mode='w', newline='') as file:
                writer = csv.writer(file)
                writer.writerows(updated_rows)

            self.refresh_ui()

    def refresh_ui(self):
        self.update_totals()
        self.load_table()

    def update_totals(self):
        total_all, total_day, total_week = 0.0, 0.0, 0.0
        
        now = datetime.now()
        today_str = now.strftime("%Y-%m-%d")
        seven_days_ago = now - timedelta(days=7)

        if os.path.exists(FILENAME):
            with open(FILENAME, mode='r') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    try:
                        amt = float(row["Amount"])
                        total_all += amt
                        
                        # FIX: Try to parse with seconds, if it fails, try without seconds
                        date_str = row["DateTime"]
                        try:
                            row_date = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
                        except ValueError:
                            row_date = datetime.strptime(date_str, "%Y-%m-%d %H:%M")
                        
                        # Daily check
                        if date_str.startswith(today_str):
                            total_day += amt
                        
                        # Weekly check
                        if row_date >= seven_days_ago:
                            total_week += amt
                    except (ValueError, KeyError):
                        # This skips rows that might be corrupted or empty
                        continue

        self.total_label.config(text=f"Total: Rs. {total_all:,.2f}")
        self.today_label.config(text=f"Today: Rs. {total_day:,.2f}")
        self.weekly_label.config(text=f"This Week: Rs. {total_week:,.2f}")
        
    def load_table(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        if os.path.exists(FILENAME):
            with open(FILENAME, mode='r') as file:
                rows = list(csv.reader(file))[1:]
                for row in reversed(rows):
                    self.tree.insert("", tk.END, values=row)

    def download_last_month_report(self):
        if not os.path.exists(FILENAME):
            messagebox.showinfo("No Data", "No expenses found.")
            return

        now = datetime.now()
        first_day_this_month = now.replace(day=1)
        last_month_end = first_day_this_month - timedelta(days=1)
        last_month_start = last_month_end.replace(day=1)

        report_rows = []

        with open(FILENAME, mode='r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                try:
                    date_str = row["DateTime"]
                    try:
                        expense_date = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
                    except ValueError:
                        expense_date = datetime.strptime(date_str, "%Y-%m-%d %H:%M")

                    if last_month_start <= expense_date <= last_month_end:
                        report_rows.append(row)
                except (KeyError, ValueError):
                    continue

        if not report_rows:
            messagebox.showinfo("No Data", "No expenses found for last month.")
            return

        report_name = f"Expense_Report_{last_month_start.strftime('%Y_%m')}.csv"

        with open(report_name, mode='w', newline='') as file:
            writer = csv.DictWriter(
                file,
                fieldnames=["DateTime", "Category", "Description", "Amount"]
            )
            writer.writeheader()
            writer.writerows(report_rows)

        messagebox.showinfo(
            "Report Downloaded",
            f"Last month report saved as:\n{report_name}"
        )

    def export_month_to_pdf(self, year, month):
        if not os.path.exists(FILENAME):
            messagebox.showinfo("No Data", "No expenses found.")
            return

        rows = []
        total = 0.0

        with open(FILENAME, mode='r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                try:
                    dt = row["DateTime"]
                    try:
                        date_obj = datetime.strptime(dt, "%Y-%m-%d %H:%M:%S")
                    except ValueError:
                        date_obj = datetime.strptime(dt, "%Y-%m-%d %H:%M")

                    if date_obj.year == year and date_obj.month == month:
                        rows.append([
                            row["DateTime"],
                            row["Category"],
                            row["Description"],
                            f"Rs. {float(row['Amount']):,.2f}"
                        ])
                        total += float(row["Amount"])
                except:
                    continue

        if not rows:
            messagebox.showinfo("No Data", "No expenses found for selected month.")
            return

        filename = f"Expense_Report_{year}_{month:02d}.pdf"
        pdf = SimpleDocTemplate(filename, pagesize=A4)

        styles = getSampleStyleSheet()
        elements = []

        elements.append(Paragraph(
            f"<b>Expense Report – {year}-{month:02d}</b>", styles["Title"]
        ))

        table_data = [["Date & Time", "Category", "Description", "Amount"]] + rows
        table_data.append(["", "", "TOTAL", f"Rs. {total:,.2f}"])

        table = Table(table_data, colWidths=[120, 90, 200, 90])
        table.setStyle(TableStyle([
            ("GRID", (0,0), (-1,-1), 1, colors.grey),
            ("BACKGROUND", (0,0), (-1,0), colors.lightgrey),
            ("FONT", (0,0), (-1,0), "Helvetica-Bold"),
            ("ALIGN", (-1,1), (-1,-1), "RIGHT"),
            ("FONT", (-2,-1), (-1,-1), "Helvetica-Bold"),
        ]))

        elements.append(table)
        pdf.build(elements)

        messagebox.showinfo("PDF Exported", f"Saved as:\n{filename}")

    def download_selected_month_pdf(self):
        month_name = self.month_var.get()
        if not month_name:
            messagebox.showwarning("Select Month", "Please select a month.")
            return

        month_number = datetime.strptime(month_name, "%B").month
        year = datetime.now().year

        # If future month selected, assume last year
        if month_number > datetime.now().month:
            year -= 1

        self.export_month_to_pdf(year, month_number)




if __name__ == "__main__":
    if not os.path.exists(FILENAME):
        with open(FILENAME, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["DateTime", "Category", "Description", "Amount"])

    root = tk.Tk()
    app = ExpenseApp(root)
    root.mainloop()