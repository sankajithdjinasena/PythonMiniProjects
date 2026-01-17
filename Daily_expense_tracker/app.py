import csv
from datetime import datetime
import os

FILENAME = "expenses.csv"

# Create CSV file with header if not exists
if not os.path.exists(FILENAME):
    with open(FILENAME, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["DateTime", "Category", "Description", "Amount"])

def add_expense():
    category = input("Category: ")
    description = input("Description: ")
    amount = float(input("Amount: "))

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open(FILENAME, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([timestamp, category, description, amount])

    print("✅ Expense added at", timestamp)

def total_all_time():
    total = 0.0
    with open(FILENAME, mode='r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            total += float(row["Amount"])

    print(f"💰 Total Spend (All Time): {total:.2f}")

def total_today():
    today = datetime.now().strftime("%Y-%m-%d")
    total = 0.0

    with open(FILENAME, mode='r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row["DateTime"].startswith(today):
                total += float(row["Amount"])

    print(f"📅 Total Spend Today: {total:.2f}")

# -------- MAIN LOOP --------
print("💸 Expense Tracker")

while True:
    print("\n1. Add Expense")
    print("2. View Total Spend (All Time)")
    print("3. View Total Spend (Today)")
    print("4. Exit")

    choice = input("Choose an option: ")

    if choice == "1":
        add_expense()
    elif choice == "2":
        total_all_time()
    elif choice == "3":
        total_today()
    elif choice == "4":
        print("👋 Goodbye!")
        break
    else:
        print("❌ Invalid choice, try again.")
