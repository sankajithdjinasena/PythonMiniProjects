@echo off
cd /d E:\Project\Python_Mini_Project\Daily_expense_tracker

:: Install reportlab if it's missing
"C:\Users\user\AppData\Local\Programs\Python\Python312\python.exe" -m pip install reportlab

:: Run the application
"C:\Users\user\AppData\Local\Programs\Python\Python312\python.exe" app.py

pause