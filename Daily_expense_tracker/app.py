import csv
from datetime import datetime
import os

# Get today's date for filename
today = datetime.now().date().isoformat()
filename = f"expenses_{today}.csv"

# Create file with headers if not exists
if not os.path.exists(filename):
    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["DateTime", "Category", "Description", "Amount"])

print("💰 Daily Expense Tracker")
print(f"📅 File: {filename}")

while True:
    print("\n1. Add Expense")
    print("2. Exit")

    choice = input("Choose an option: ")

    if choice == "1":
        category = input("Category (Food, Travel, etc.): ")
        description = input("Description: ")
        amount = input("Amount: ")

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        with open(filename, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([timestamp, category, description, amount])

        print("✅ Expense added at", timestamp)

    elif choice == "2":
        print("📁 All expenses saved. See you!")
        break

    else:
        print("❌ Invalid option. Try again.")
