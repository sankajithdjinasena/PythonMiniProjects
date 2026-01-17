import tkinter as tk
from tkinter import messagebox, ttk
import csv
import os
from datetime import datetime

FILENAME = "expenses.csv"

class ExpenseApp:
    def __init__(self, root):
        self.root = root
        self.root.title("💸 Expense Tracker Pro")
        self.root.geometry("800x800")

        # --- UI Header ---
        tk.Label(root, text="Expense Tracker", font=("Arial", 18, "bold")).pack(pady=10)

        # --- Input Frame ---
        input_frame = tk.Frame(root)
        input_frame.pack(pady=10)

        tk.Label(input_frame, text="Category:").grid(row=0, column=0, padx=5, pady=5)
        self.cat_entry = tk.Entry(input_frame)
        self.cat_entry.grid(row=0, column=1)

        tk.Label(input_frame, text="Description:").grid(row=1, column=0, padx=5, pady=5)
        self.desc_entry = tk.Entry(input_frame)
        self.desc_entry.grid(row=1, column=1)

        tk.Label(input_frame, text="Amount:").grid(row=2, column=0, padx=5, pady=5)
        self.amt_entry = tk.Entry(input_frame)
        self.amt_entry.grid(row=2, column=1)

        # --- Buttons ---
        btn_frame = tk.Frame(root)
        btn_frame.pack(pady=10)

        tk.Button(btn_frame, text="Add Expense", command=self.add_expense, bg="#4CAF50", fg="white", width=15).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Delete Selected", command=self.delete_expense, bg="#f44336", fg="white", width=15).pack(side=tk.LEFT, padx=5)

        # --- Totals Display ---
        self.total_label = tk.Label(root, text="Total (All Time): Rs. 0.00", font=("Arial", 10, "bold"))
        self.total_label.pack()
        self.today_label = tk.Label(root, text="Total (Today): Rs. 0.00", font=("Arial", 10, "bold"))
        self.today_label.pack()

        # --- Table (Treeview) ---
        tk.Label(root, text="\nRecent Expenses:").pack()
        self.tree = ttk.Treeview(root, columns=("Date", "Cat", "Desc", "Amt"), show='headings', height=10)
        self.tree.heading("Date", text="Date/Time")
        self.tree.heading("Cat", text="Category")
        self.tree.heading("Desc", text="Description")
        self.tree.heading("Amt", text="Amount (Rs.)")
        
        # Adjusting column widths
        self.tree.column("Date", width=150)
        self.tree.column("Cat", width=100)
        self.tree.column("Desc", width=250)
        # Add 'anchor=tk.E' to align the text to the right (East)
        self.tree.column("Amt", width=80, anchor=tk.E)
        self.tree.pack(pady=10, padx=20)

        # Initial Load
        self.refresh_ui()

    def add_expense(self):
        category = self.cat_entry.get()
        description = self.desc_entry.get()
        amount_str = self.amt_entry.get()

        if not category or not amount_str:
            messagebox.showwarning("Input Error", "Please fill in Category and Amount")
            return

        try:
            amount = float(amount_str)
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

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

        # Confirm deletion
        confirm = messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this entry?")
        if not confirm:
            return

        # Get values of the selected row
        item_data = self.tree.item(selected_item)['values']
        # item_data is a list: [Date, Category, Description, Amount]
        # Since we display strings, we convert Amount back to float for matching
        item_data[3] = f"{float(item_data[3]):.1f}" # Normalizing for comparison

        # Read all data and filter out the one to delete
        updated_rows = []
        deleted = False
        with open(FILENAME, mode='r') as file:
            reader = csv.reader(file)
            header = next(reader)
            updated_rows.append(header)
            
            for row in reader:
                # Simple check: match exact timestamp and amount to identify the row
                # (In a real app, an ID column is better, but this works for simple CSVs)
                if not deleted and row[0] == str(item_data[0]) and f"{float(row[3]):.1f}" == item_data[3]:
                    deleted = True # Skip this row (delete it)
                    continue
                updated_rows.append(row)

        # Write the updated data back to CSV
        with open(FILENAME, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerows(updated_rows)

        self.refresh_ui()
        messagebox.showinfo("Deleted", "Expense removed successfully.")

    def refresh_ui(self):
        """Helper to update both the totals and the table display"""
        self.update_totals()
        self.load_table()

    def update_totals(self):
        total_all = 0.0
        total_day = 0.0
        today = datetime.now().strftime("%Y-%m-%d")

        if os.path.exists(FILENAME):
            with open(FILENAME, mode='r') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    amt = float(row["Amount"])
                    total_all += amt
                    if row["DateTime"].startswith(today):
                        total_day += amt

        self.total_label.config(text=f"Total (All Time): Rs.{total_all:.2f}")
        self.today_label.config(text=f"Total (Today): Rs.{total_day:.2f}")

    def load_table(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        if os.path.exists(FILENAME):
            with open(FILENAME, mode='r') as file:
                rows = list(csv.reader(file))[1:]
                for row in rows:
                    self.tree.insert("", tk.END, values=row)

if __name__ == "__main__":
    if not os.path.exists(FILENAME):
        with open(FILENAME, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["DateTime", "Category", "Description", "Amount"])

    root = tk.Tk()
    app = ExpenseApp(root)
    root.mainloop()