import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import seaborn as sns
import threading
from datetime import datetime

# Set seaborn style for better visuals
sns.set_style("whitegrid")

class EnhancedCSVAnalyzerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("CSV Data Analyzer Pro")
        self.root.geometry("1300x900")
        self.root.configure(bg="#f8fafc")
        
        # Center the window
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
        
        # Set icon and styling
        self.root.option_add('*TCombobox*Listbox.font', ('Segoe UI', 10))
        
        self.df = None
        self.cleaned_df = None
        self.current_figure = None
        
        # ===== Custom Colors =====
        self.colors = {
            'primary': '#4361ee',
            'secondary': '#3a0ca3',
            'accent': '#7209b7',
            'success': '#4cc9f0',
            'danger': '#f72585',
            'warning': '#f8961e',
            'light': '#f8f9fa',
            'dark': '#212529',
            'sidebar': '#2d3748',
            'card': '#ffffff'
        }
        
        # ===== Main Layout =====
        self.main_container = tk.Frame(root, bg=self.colors['light'])
        self.main_container.pack(fill="both", expand=True, padx=2, pady=2)
        
        # ===== Sidebar =====
        self.sidebar = tk.Frame(self.main_container, bg=self.colors['sidebar'], width=250)
        self.sidebar.pack(side="left", fill="y", padx=(0, 2), pady=2)
        self.sidebar.pack_propagate(False)
        
        # Logo/Title in Sidebar
        logo_frame = tk.Frame(self.sidebar, bg=self.colors['sidebar'], height=100)
        logo_frame.pack(fill="x", pady=(20, 30))
        
        tk.Label(
            logo_frame, 
            text="📊", 
            font=("Segoe UI", 40),
            bg=self.colors['sidebar'], 
            fg="white"
        ).pack()
        
        tk.Label(
            logo_frame, 
            text="DATA ANALYZER", 
            font=("Segoe UI", 14, "bold"),
            bg=self.colors['sidebar'], 
            fg="white"
        ).pack()
        
        tk.Label(
            logo_frame, 
            text="PRO EDITION", 
            font=("Segoe UI", 9),
            bg=self.colors['sidebar'], 
            fg="#a0aec0"
        ).pack()
        
        # Sidebar Menu
        menu_items = [
            ("📁 Load Data", self.load_csv),
            ("🏠 Dashboard", self.show_dashboard),
            ("🧹 Data Cleaning", self.show_cleaning_panel),
            ("📈 Visualizations", self.show_visualization_panel),
            ("📊 Statistics", self.show_statistics_panel),
            ("💾 Export Data", self.export_cleaned_csv)
        ]
        
        for i, (text, command) in enumerate(menu_items):
            btn = tk.Button(
                self.sidebar,
                text=text,
                font=("Segoe UI", 11),
                bg=self.colors['sidebar'],
                fg="white",
                anchor="w",
                padx=20,
                pady=12,
                relief="flat",
                cursor="hand2",
                command=command
            )
            btn.pack(fill="x", padx=10, pady=2)
            
            # Add hover effect
            btn.bind("<Enter>", lambda e, b=btn: b.config(bg="#4a5568"))
            btn.bind("<Leave>", lambda e, b=btn: b.config(bg=self.colors['sidebar']))
        
        # Status at bottom of sidebar
        self.status_frame = tk.Frame(self.sidebar, bg="#1a202c", height=80)
        self.status_frame.pack(side="bottom", fill="x", pady=(20, 0))
        self.status_frame.pack_propagate(False)
        
        self.status_label = tk.Label(
            self.status_frame,
            text="Ready",
            font=("Segoe UI", 9),
            bg="#1a202c",
            fg="#a0aec0",
            padx=20,
            pady=10
        )
        self.status_label.pack(anchor="w")
        
        # ===== Main Content Area =====
        self.content_area = tk.Frame(self.main_container, bg=self.colors['light'])
        self.content_area.pack(side="right", fill="both", expand=True, padx=2, pady=2)
        
        # Header in Content Area
        self.header = tk.Frame(self.content_area, bg="white", height=70)
        self.header.pack(fill="x", padx=20, pady=(20, 10))
        self.header.pack_propagate(False)
        
        self.title_label = tk.Label(
            self.header,
            text="Welcome to CSV Data Analyzer",
            font=("Segoe UI", 18, "bold"),
            bg="white",
            fg=self.colors['dark']
        )
        self.title_label.pack(side="left", padx=20)
        
        # File info display
        self.file_info_label = tk.Label(
            self.header,
            text="No file loaded",
            font=("Segoe UI", 10),
            bg="white",
            fg="#718096"
        )
        self.file_info_label.pack(side="right", padx=20)
        
        # ===== Card Container for Content =====
        self.card_container = tk.Frame(self.content_area, bg=self.colors['light'])
        self.card_container.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # Initial welcome card
        self.show_welcome_card()
        
        # Progress bar for long operations
        self.progress = ttk.Progressbar(
            self.content_area,
            mode='indeterminate',
            length=300
        )
        
    def show_welcome_card(self):
        self.clear_content()
        
        card = tk.Frame(self.card_container, bg="white", padx=40, pady=40)
        card.pack(fill="both", expand=True)
        
        tk.Label(
            card,
            text="👋 Welcome to Data Analyzer Pro",
            font=("Segoe UI", 24, "bold"),
            bg="white",
            fg=self.colors['dark']
        ).pack(pady=(0, 20))
        
        tk.Label(
            card,
            text="Upload a CSV file to begin analyzing your data",
            font=("Segoe UI", 12),
            bg="white",
            fg="#718096"
        ).pack(pady=(0, 40))
        
        # Features grid
        features = [
            ("📁", "Load CSV Files", "Support for large datasets"),
            ("🧹", "Data Cleaning", "Handle missing values & outliers"),
            ("📊", "Visual Analytics", "Interactive charts & graphs"),
            ("⚡", "Fast Processing", "Optimized for performance"),
            ("📈", "Statistical Analysis", "Comprehensive insights"),
            ("💾", "Export Options", "Multiple format support")
        ]
        
        features_frame = tk.Frame(card, bg="white")
        features_frame.pack(fill="x", pady=20)
        
        for i, (icon, title, desc) in enumerate(features):
            feature_card = tk.Frame(
                features_frame, 
                bg="#f7fafc",
                relief="groove",
                borderwidth=1
            )
            feature_card.grid(row=i//3, column=i%3, padx=10, pady=10, sticky="nsew")
            
            tk.Label(
                feature_card,
                text=icon,
                font=("Segoe UI", 20),
                bg="#f7fafc"
            ).pack(pady=(15, 5))
            
            tk.Label(
                feature_card,
                text=title,
                font=("Segoe UI", 11, "bold"),
                bg="#f7fafc"
            ).pack()
            
            tk.Label(
                feature_card,
                text=desc,
                font=("Segoe UI", 9),
                bg="#f7fafc",
                fg="#718096",
                wraplength=120
            ).pack(pady=5)
            
            features_frame.grid_columnconfigure(i%3, weight=1)
        
        # Upload button
        upload_btn = tk.Button(
            card,
            text="📁 Upload CSV File",
            font=("Segoe UI", 12, "bold"),
            bg=self.colors['primary'],
            fg="white",
            padx=30,
            pady=12,
            cursor="hand2",
            relief="flat",
            command=self.load_csv
        )
        upload_btn.pack(pady=40)
        
        # Add hover effect
        upload_btn.bind("<Enter>", lambda e: upload_btn.config(bg=self.colors['secondary']))
        upload_btn.bind("<Leave>", lambda e: upload_btn.config(bg=self.colors['primary']))
    
    def show_dashboard(self):
        if self.df is None:
            self.show_message("No Data", "Please load a CSV file first.", "info")
            return
        
        self.clear_content()
        
        dashboard_card = tk.Frame(self.card_container, bg="white", padx=20, pady=20)
        dashboard_card.pack(fill="both", expand=True)
        
        tk.Label(
            dashboard_card,
            text="🏠 Data Dashboard",
            font=("Segoe UI", 16, "bold"),
            bg="white",
            fg=self.colors['dark']
        ).pack(anchor="w", pady=(0, 20))
        
        # Dashboard metrics
        metrics_frame = tk.Frame(dashboard_card, bg="white")
        metrics_frame.pack(fill="x", pady=(0, 20))
        
        metrics = [
            ("📊 Total Rows", f"{self.cleaned_df.shape[0]:,}", "#4361ee"),
            ("📈 Total Columns", f"{self.cleaned_df.shape[1]}", "#7209b7"),
            ("⚠️ Missing Values", f"{self.cleaned_df.isnull().sum().sum():,}", "#f8961e"),
            ("🔍 Duplicate Rows", f"{self.cleaned_df.duplicated().sum():,}", "#f72585"),
            ("💾 Memory Usage", f"{self.cleaned_df.memory_usage(deep=True).sum() / 1024 / 1024:.2f} MB", "#4cc9f0"),
            ("📅 Last Updated", datetime.now().strftime("%Y-%m-%d %H:%M"), "#38b000")
        ]
        
        for i, (title, value, color) in enumerate(metrics):
            metric_card = tk.Frame(
                metrics_frame,
                bg="#f8fafc",
                relief="groove",
                borderwidth=1
            )
            metric_card.grid(row=i//3, column=i%3, padx=10, pady=10, sticky="nsew")
            
            tk.Label(
                metric_card,
                text=title,
                font=("Segoe UI", 10),
                bg="#f8fafc",
                fg="#718096"
            ).pack(anchor="w", padx=15, pady=(15, 5))
            
            tk.Label(
                metric_card,
                text=value,
                font=("Segoe UI", 16, "bold"),
                bg="#f8fafc",
                fg=color
            ).pack(anchor="w", padx=15, pady=(0, 15))
            
            metrics_frame.grid_columnconfigure(i%3, weight=1)
        
        # Quick Actions
        actions_frame = tk.Frame(dashboard_card, bg="#f1f5f9", padx=20, pady=20)
        actions_frame.pack(fill="x", pady=(0, 20))
        
        tk.Label(
            actions_frame,
            text="⚡ Quick Actions",
            font=("Segoe UI", 14, "bold"),
            bg="#f1f5f9",
            fg=self.colors['dark']
        ).pack(anchor="w", pady=(0, 15))
        
        action_buttons = [
            ("Remove All Missing", self.remove_all_missing),
            ("Remove All Duplicates", self.remove_all_duplicates),
            ("View Top 10 Rows", self.show_top_rows),
            ("Generate Summary", self.show_quick_summary)
        ]
        
        button_frame = tk.Frame(actions_frame, bg="#f1f5f9")
        button_frame.pack()
        
        for text, command in action_buttons:
            btn = tk.Button(
                button_frame,
                text=text,
                font=("Segoe UI", 10),
                bg=self.colors['primary'],
                fg="white",
                padx=20,
                pady=8,
                cursor="hand2",
                relief="flat",
                command=command
            )
            btn.pack(side="left", padx=10, pady=5)
            btn.bind("<Enter>", lambda e, b=btn: b.config(bg=self.colors['secondary']))
            btn.bind("<Leave>", lambda e, b=btn: b.config(bg=self.colors['primary']))
        
        # Data Preview
        preview_frame = tk.Frame(dashboard_card, bg="white")
        preview_frame.pack(fill="both", expand=True)
        
        tk.Label(
            preview_frame,
            text="👁️ Quick Data Preview",
            font=("Segoe UI", 14, "bold"),
            bg="white",
            fg=self.colors['dark']
        ).pack(anchor="w", pady=(0, 15))
        
        # Create table for quick preview
        table_frame = tk.Frame(preview_frame, bg="white")
        table_frame.pack(fill="both", expand=True)
        
        # Add scrollbars
        h_scrollbar = ttk.Scrollbar(table_frame, orient="horizontal")
        v_scrollbar = ttk.Scrollbar(table_frame, orient="vertical")
        
        self.dash_tree = ttk.Treeview(
            table_frame,
            show="headings",
            xscrollcommand=h_scrollbar.set,
            yscrollcommand=v_scrollbar.set,
            height=8
        )
        
        h_scrollbar.config(command=self.dash_tree.xview)
        v_scrollbar.config(command=self.dash_tree.yview)
        
        h_scrollbar.pack(side="bottom", fill="x")
        v_scrollbar.pack(side="right", fill="y")
        self.dash_tree.pack(side="left", fill="both", expand=True)
        
        # Configure treeview style
        style = ttk.Style()
        style.theme_use("clam")
        style.configure(
            "Treeview",
            background="white",
            foreground=self.colors['dark'],
            fieldbackground="white",
            borderwidth=0,
            font=('Segoe UI', 9)
        )
        style.configure(
            "Treeview.Heading",
            background="#edf2f7",
            foreground=self.colors['dark'],
            font=('Segoe UI', 9, 'bold'),
            borderwidth=1,
            relief="flat"
        )
        
        # Populate table with first 10 rows
        preview_df = self.cleaned_df.head(10)
        self.dash_tree["columns"] = list(preview_df.columns)
        
        for col in preview_df.columns:
            self.dash_tree.heading(col, text=col)
            self.dash_tree.column(col, width=100, anchor="center", minwidth=50)
        
        for _, row in preview_df.iterrows():
            self.dash_tree.insert("", "end", values=list(row))
    
    def remove_all_missing(self):
        original_rows = len(self.cleaned_df)
        original_missing = self.cleaned_df.isnull().sum().sum()
        
        self.cleaned_df = self.cleaned_df.dropna()
        
        removed_rows = original_rows - len(self.cleaned_df)
        removed_missing = original_missing - self.cleaned_df.isnull().sum().sum()
        
        message = (f"Removed all missing values!\n\n"
                  f"• Removed {removed_rows} rows with missing values\n"
                  f"• Eliminated {removed_missing} missing values\n"
                  f"• New dataset has {len(self.cleaned_df):,} rows\n"
                  f"• Data retained: {(len(self.cleaned_df)/original_rows*100):.1f}%")
        
        self.show_message("Missing Values Removed", message, "success")
        self.show_dashboard()
    
    def remove_all_duplicates(self):
        original_rows = len(self.cleaned_df)
        duplicate_count = self.cleaned_df.duplicated().sum()
        
        self.cleaned_df = self.cleaned_df.drop_duplicates()
        
        message = (f"Removed all duplicate rows!\n\n"
                  f"• Removed {duplicate_count} duplicate rows\n"
                  f"• Original rows: {original_rows:,}\n"
                  f"• New row count: {len(self.cleaned_df):,}\n"
                  f"• Data retained: {(len(self.cleaned_df)/original_rows*100):.1f}%")
        
        self.show_message("Duplicates Removed", message, "success")
        self.show_dashboard()
    
    def show_top_rows(self):
        self.show_data_preview()
    
    def show_quick_summary(self):
        self.show_statistics_panel()
    
    def clear_content(self):
        for widget in self.card_container.winfo_children():
            widget.destroy()
    
    def update_status(self, message):
        self.status_label.config(text=message)
        self.root.update()
    
    def show_message(self, title, message, message_type="info"):
        """
        Show a custom styled message box with larger size
        message_type can be: "info", "warning", "error", "success", "question"
        """
        
        # For question types, use standard messagebox with larger font
        if message_type == "question":
            # Create larger question dialog
            dialog = tk.Toplevel(self.root)
            dialog.title(title)
            dialog.geometry("500x300")  # Larger size
            dialog.configure(bg="white")
            dialog.transient(self.root)
            dialog.grab_set()
            
            # Center the dialog
            dialog.update_idletasks()
            width = dialog.winfo_width()
            height = dialog.winfo_height()
            x = (self.root.winfo_screenwidth() // 2) - (width // 2)
            y = (self.root.winfo_screenheight() // 2) - (height // 2)
            dialog.geometry(f'{width}x{height}+{x}+{y}')
            
            # Question icon
            tk.Label(dialog, text="❓", font=("Segoe UI", 50), 
                    bg="white", fg="#4361ee").pack(pady=30)
            
            # Title
            tk.Label(dialog, text=title, font=("Segoe UI", 16, "bold"), 
                    bg="white", fg="#212529").pack()
            
            # Message
            tk.Label(dialog, text=message, font=("Segoe UI", 12), 
                    bg="white", fg="#718096", wraplength=450).pack(pady=15)
            
            result = [None]  # Use list to store result
            
            # Button frame
            button_frame = tk.Frame(dialog, bg="white")
            button_frame.pack(pady=20)
            
            # Yes button
            yes_button = tk.Button(button_frame, text="Yes",
                                bg="#38b000", fg="white", padx=40, pady=10,
                                font=("Segoe UI", 11, "bold"),
                                command=lambda: self.message_button_clicked(dialog, True, result))
            yes_button.pack(side="left", padx=20)
            
            # No button
            no_button = tk.Button(button_frame, text="No",
                                bg="#f72585", fg="white", padx=40, pady=10,
                                font=("Segoe UI", 11, "bold"),
                                command=lambda: self.message_button_clicked(dialog, False, result))
            no_button.pack(side="left", padx=20)
            
            # Add hover effects
            yes_button.bind("<Enter>", lambda e: yes_button.config(bg="#06d6a0"))
            yes_button.bind("<Leave>", lambda e: yes_button.config(bg="#38b000"))
            no_button.bind("<Enter>", lambda e: no_button.config(bg="#e63946"))
            no_button.bind("<Leave>", lambda e: no_button.config(bg="#f72585"))
            
            dialog.wait_window()
            return result[0]
        
        # Create custom dialog for other types
        dialog = tk.Toplevel(self.root)
        dialog.title(title)
        dialog.geometry("600x350")  # Larger size
        dialog.configure(bg="white")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Center the dialog
        dialog.update_idletasks()
        width = dialog.winfo_width()
        height = dialog.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        dialog.geometry(f'{width}x{height}+{x}+{y}')
        
        # Set icon and colors based on message type
        if message_type == "success":
            icon = "✅"
            icon_color = "#38b000"
            button_color = "#38b000"
        elif message_type == "warning":
            icon = "⚠️"
            icon_color = "#f8961e"
            button_color = "#f8961e"
        elif message_type == "error":
            icon = "❌"
            icon_color = "#f72585"
            button_color = "#f72585"
        else:  # info (default)
            icon = "ℹ️"
            icon_color = "#4361ee"
            button_color = "#4361ee"
        
        # Icon (larger)
        tk.Label(dialog, text=icon, font=("Segoe UI", 60), 
                bg="white", fg=icon_color).pack(pady=30)
        
        # Title (larger font)
        tk.Label(dialog, text=title, font=("Segoe UI", 18, "bold"), 
                bg="white", fg="#212529").pack(pady=(0, 10))
        
        # Message (larger font with more space)
        # Split long messages into lines for better readability
        lines = self.wrap_text(message, 70)  # Wrap at 70 characters
        for line in lines:
            tk.Label(dialog, text=line, font=("Segoe UI", 12), 
                    bg="white", fg="#718096").pack()
        
        # OK button (larger)
        ok_button = tk.Button(dialog, text="OK", command=dialog.destroy,
                            bg=button_color, fg="white", padx=50, pady=25,
                            font=("Segoe UI", 12, "bold"))
        ok_button.pack(pady=20)
        
        # Add hover effect
        ok_button.bind("<Enter>", 
                    lambda e, b=ok_button, c=button_color: 
                    b.config(bg=self.adjust_color(c, -30)))
        ok_button.bind("<Leave>", 
                    lambda e, b=ok_button, c=button_color: 
                    b.config(bg=c))
        
        # Bind Enter key to close dialog
        dialog.bind('<Return>', lambda e: dialog.destroy())
        dialog.bind('<Escape>', lambda e: dialog.destroy())
        
        # Focus the OK button
        ok_button.focus_set()

    def message_button_clicked(self, dialog, value, result_store):
        """Handle button clicks in question dialogs"""
        result_store[0] = value
        dialog.destroy()

    def wrap_text(self, text, max_length):
        """Wrap text into multiple lines"""
        words = text.split()
        lines = []
        current_line = []
        current_length = 0
        
        for word in words:
            if current_length + len(word) + 1 <= max_length:
                current_line.append(word)
                current_length += len(word) + 1
            else:
                lines.append(" ".join(current_line))
                current_line = [word]
                current_length = len(word)
        
        if current_line:
            lines.append(" ".join(current_line))
        
        return lines

    def load_csv(self):
        self.update_status("Selecting file...")
        
        path = filedialog.askopenfilename(
            filetypes=[
                ("CSV Files", "*.csv"),
                ("Excel Files", "*.xlsx"),
                ("All Files", "*.*")
            ]
        )
        
        if not path:
            self.update_status("Ready")
            return
        
        self.update_status("Loading file...")
        
        # Show loading animation
        self.progress.place(relx=0.5, rely=0.5, anchor="center")
        self.progress.start()
        
        # Load in background thread
        def load_data():
            try:
                self.df = pd.read_csv(path)
                self.cleaned_df = self.df.copy()
                
                self.root.after(0, self.on_data_loaded, path)
            except Exception as e:
                self.root.after(0, self.show_message, "Error", 
                              f"Error loading file:\n{str(e)}", "error")
            finally:
                self.root.after(0, self.progress.stop)
                self.root.after(0, self.progress.place_forget)
        
        threading.Thread(target=load_data, daemon=True).start()
    
    def on_data_loaded(self, path):
        self.update_status("Data loaded successfully")
        
        # Update file info
        filename = path.split('/')[-1]
        self.file_info_label.config(
            text=f"{filename} | {self.df.shape[0]} rows × {self.df.shape[1]} cols"
        )
        
        # Show dashboard
        self.show_dashboard()
        
        # Show success message
        self.show_message("Success", 
                         f"CSV file loaded successfully!\n\n"
                         f"• File: {filename}\n"
                         f"• Rows: {self.df.shape[0]:,}\n"
                         f"• Columns: {self.df.shape[1]}\n"
                         f"• Missing values: {self.df.isnull().sum().sum():,}\n"
                         f"• Duplicate rows: {self.df.duplicated().sum():,}",
                         "success")
    
    def show_data_preview(self):
        self.clear_content()
        
        # Statistics card
        stats_card = tk.Frame(self.card_container, bg="white", padx=20, pady=20)
        stats_card.pack(fill="x", pady=(0, 20))
        
        tk.Label(
            stats_card,
            text="📊 Dataset Overview",
            font=("Segoe UI", 14, "bold"),
            bg="white",
            fg=self.colors['dark']
        ).pack(anchor="w", pady=(0, 15))
        
        # Stats grid
        stats_grid = tk.Frame(stats_card, bg="white")
        stats_grid.pack(fill="x")
        
        stats_data = [
            ("Total Rows", f"{self.df.shape[0]:,}"),
            ("Total Columns", f"{self.df.shape[1]}"),
            ("Missing Values", f"{self.df.isnull().sum().sum():,}"),
            ("Duplicate Rows", f"{self.df.duplicated().sum():,}"),
            ("Memory Usage", f"{self.df.memory_usage(deep=True).sum() / 1024 / 1024:.2f} MB"),
            ("Data Types", f"{len(self.df.select_dtypes(include=['number']).columns)} numeric, "
                         f"{len(self.df.select_dtypes(include=['object']).columns)} text")
        ]
        
        for i, (label, value) in enumerate(stats_data):
            stat_frame = tk.Frame(stats_grid, bg="#f8fafc", padx=15, pady=10)
            stat_frame.grid(row=i//3, column=i%3, padx=10, pady=10, sticky="nsew")
            
            tk.Label(
                stat_frame,
                text=label,
                font=("Segoe UI", 9),
                bg="#f8fafc",
                fg="#718096"
            ).pack(anchor="w")
            
            tk.Label(
                stat_frame,
                text=value,
                font=("Segoe UI", 12, "bold"),
                bg="#f8fafc",
                fg=self.colors['dark']
            ).pack(anchor="w", pady=(5, 0))
            
            stats_grid.grid_columnconfigure(i%3, weight=1)
        
        # Data preview card
        preview_card = tk.Frame(self.card_container, bg="white", padx=20, pady=20)
        preview_card.pack(fill="both", expand=True)
        
        tk.Label(
            preview_card,
            text="👁️ Data Preview (First 50 rows)",
            font=("Segoe UI", 14, "bold"),
            bg="white",
            fg=self.colors['dark']
        ).pack(anchor="w", pady=(0, 15))
        
        # Create table using ttk Treeview with better styling
        table_frame = tk.Frame(preview_card, bg="white")
        table_frame.pack(fill="both", expand=True)
        
        # Add scrollbars
        h_scrollbar = ttk.Scrollbar(table_frame, orient="horizontal")
        v_scrollbar = ttk.Scrollbar(table_frame, orient="vertical")
        
        self.tree = ttk.Treeview(
            table_frame,
            show="headings",
            xscrollcommand=h_scrollbar.set,
            yscrollcommand=v_scrollbar.set,
            height=15
        )
        
        h_scrollbar.config(command=self.tree.xview)
        v_scrollbar.config(command=self.tree.yview)
        
        h_scrollbar.pack(side="bottom", fill="x")
        v_scrollbar.pack(side="right", fill="y")
        self.tree.pack(side="left", fill="both", expand=True)
        
        # Configure treeview style
        style = ttk.Style()
        style.theme_use("clam")
        style.configure(
            "Treeview",
            background="white",
            foreground=self.colors['dark'],
            fieldbackground="white",
            borderwidth=0,
            font=('Segoe UI', 10)
        )
        style.configure(
            "Treeview.Heading",
            background="#edf2f7",
            foreground=self.colors['dark'],
            font=('Segoe UI', 10, 'bold'),
            borderwidth=1,
            relief="flat"
        )
        
        # Populate table
        preview_df = self.df.head(50)
        self.tree["columns"] = list(preview_df.columns)
        
        for col in preview_df.columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120, anchor="center", minwidth=50)
        
        for _, row in preview_df.iterrows():
            self.tree.insert("", "end", values=list(row))
    
    def show_cleaning_panel(self):
        if self.df is None:
            self.show_message("No Data", "Please load a CSV file first.", "info")
            return
        
        self.clear_content()
        
        cleaning_card = tk.Frame(self.card_container, bg="white", padx=20, pady=20)
        cleaning_card.pack(fill="both", expand=True)
        
        tk.Label(
            cleaning_card,
            text="🧹 Data Cleaning Tools",
            font=("Segoe UI", 16, "bold"),
            bg="white",
            fg=self.colors['dark']
        ).pack(anchor="w", pady=(0, 20))
        
        # Column selection
        selection_frame = tk.Frame(cleaning_card, bg="white")
        selection_frame.pack(fill="x", pady=(0, 20))
        
        tk.Label(
            selection_frame,
            text="Select Column:",
            font=("Segoe UI", 11, "bold"),
            bg="white",
            fg=self.colors['dark']
        ).pack(side="left", padx=(0, 10))
        
        self.clean_column = ttk.Combobox(
            selection_frame,
            values=list(self.cleaned_df.columns),
            state="readonly",
            width=30,
            font=("Segoe UI", 10)
        )
        self.clean_column.current(0)
        self.clean_column.pack(side="left", padx=(0, 30))
        
        # Cleaning methods
        methods_frame = tk.Frame(cleaning_card, bg="white")
        methods_frame.pack(fill="x", pady=(0, 30))
        
        cleaning_methods = [
            ("Mean Imputation", "Replace missing with column mean", "#4cc9f0"),
            ("Median Imputation", "Replace missing with column median", "#4361ee"),
            ("Mode Imputation", "Replace missing with most frequent value", "#7209b7"),
            ("Drop Rows", "Remove rows with missing values", "#f72585"),
            ("Forward Fill", "Fill with previous value", "#f8961e"),
            ("Backward Fill", "Fill with next value", "#38b000")
        ]
        
        for i, (title, desc, color) in enumerate(cleaning_methods):
            method_card = tk.Frame(
                methods_frame,
                bg="#f8fafc",
                relief="groove",
                borderwidth=1
            )
            method_card.grid(row=i//2, column=i%2, padx=10, pady=10, sticky="nsew")
            
            tk.Label(
                method_card,
                text=title,
                font=("Segoe UI", 11, "bold"),
                bg="#f8fafc",
                fg=color
            ).pack(anchor="w", padx=15, pady=(15, 5))
            
            tk.Label(
                method_card,
                text=desc,
                font=("Segoe UI", 9),
                bg="#f8fafc",
                fg="#718096",
                wraplength=250
            ).pack(anchor="w", padx=15, pady=(0, 15))
            
            apply_btn = tk.Button(
                method_card,
                text="Apply",
                font=("Segoe UI", 9, "bold"),
                bg=color,
                fg="white",
                padx=20,
                pady=5,
                cursor="hand2",
                relief="flat",
                command=lambda m=title: self.apply_cleaning_method(m)
            )
            apply_btn.pack(anchor="w", padx=15, pady=(0, 15))
            
            # Hover effect
            apply_btn.bind("<Enter>", lambda e, b=apply_btn, c=color: 
                          b.config(bg=self.adjust_color(c, -30)))
            apply_btn.bind("<Leave>", lambda e, b=apply_btn, c=color: 
                          b.config(bg=c))
            
            methods_frame.grid_columnconfigure(i%2, weight=1)
        
        # Additional cleaning options
        extra_frame = tk.Frame(cleaning_card, bg="#f1f5f9", padx=20, pady=20)
        extra_frame.pack(fill="x", pady=(20, 0))
        
        tk.Label(
            extra_frame,
            text="🔧 Advanced Cleaning Options",
            font=("Segoe UI", 12, "bold"),
            bg="#f1f5f9",
            fg=self.colors['dark']
        ).pack(anchor="w", pady=(0, 10))
        
        # Duplicate removal button
        dup_btn = tk.Button(
            extra_frame,
            text="Remove Duplicate Rows",
            font=("Segoe UI", 11),
            bg="#f72585",
            fg="white",
            padx=30,
            pady=10,
            cursor="hand2",
            relief="flat",
            command=self.remove_duplicates_specific
        )
        dup_btn.pack(side="left", padx=10)
        dup_btn.bind("<Enter>", lambda e: dup_btn.config(bg="#e63946"))
        dup_btn.bind("<Leave>", lambda e: dup_btn.config(bg="#f72585"))
        
        # Outlier removal button
        outlier_btn = tk.Button(
            extra_frame,
            text="Remove Outliers (IQR Method)",
            font=("Segoe UI", 11),
            bg=self.colors['warning'],
            fg="white",
            padx=30,
            pady=10,
            cursor="hand2",
            relief="flat",
            command=self.remove_outliers
        )
        outlier_btn.pack(side="left", padx=10)
        outlier_btn.bind("<Enter>", lambda e: outlier_btn.config(bg="#f3722c"))
        outlier_btn.bind("<Leave>", lambda e: outlier_btn.config(bg=self.colors['warning']))
    
    def remove_duplicates_specific(self):
        original_rows = len(self.cleaned_df)
        duplicate_count = self.cleaned_df.duplicated().sum()
        
        if duplicate_count == 0:
            self.show_message("No Duplicates", "No duplicate rows found in the dataset.", "info")
            return
        
        self.cleaned_df = self.cleaned_df.drop_duplicates()
        
        message = (f"Duplicate rows removed!\n\n"
                  f"• Removed {duplicate_count} duplicate rows\n"
                  f"• Original rows: {original_rows:,}\n"
                  f"• New row count: {len(self.cleaned_df):,}\n"
                  f"• Data retained: {(len(self.cleaned_df)/original_rows*100):.1f}%")
        
        self.update_status(f"Removed {duplicate_count} duplicate rows")
        self.show_message("Duplicates Removed", message, "success")
        
        # Refresh data preview
        self.refresh_data_preview()
    
    def apply_cleaning_method(self, method):
        col = self.clean_column.get()
        if not col:
            return
        
        try:
            original_missing = self.cleaned_df[col].isnull().sum()
            original_rows = len(self.cleaned_df)
            
            if method == "Mean Imputation":
                if pd.api.types.is_numeric_dtype(self.cleaned_df[col]):
                    self.cleaned_df[col] = self.cleaned_df[col].fillna(
                        self.cleaned_df[col].mean()
                    )
                    message = f"Replaced {original_missing} missing values in '{col}' with mean: {self.cleaned_df[col].mean():.2f}"
                else:
                    self.show_message("Invalid Operation", 
                                    "Mean imputation only works for numeric columns", "warning")
                    return
            
            elif method == "Median Imputation":
                if pd.api.types.is_numeric_dtype(self.cleaned_df[col]):
                    self.cleaned_df[col] = self.cleaned_df[col].fillna(
                        self.cleaned_df[col].median()
                    )
                    message = f"Replaced {original_missing} missing values in '{col}' with median: {self.cleaned_df[col].median():.2f}"
                else:
                    self.show_message("Invalid Operation",
                                    "Median imputation only works for numeric columns", "warning")
                    return
            
            elif method == "Mode Imputation":
                mode_val = self.cleaned_df[col].mode()[0] if not self.cleaned_df[col].mode().empty else ""
                self.cleaned_df[col] = self.cleaned_df[col].fillna(mode_val)
                message = f"Replaced {original_missing} missing values in '{col}' with mode: '{mode_val}'"
            
            elif method == "Drop Rows":
                self.cleaned_df = self.cleaned_df.dropna(subset=[col])
                rows_removed = original_rows - len(self.cleaned_df)
                message = f"Removed {rows_removed} rows with missing values in '{col}'\nNew dataset has {len(self.cleaned_df)} rows"
            
            elif method == "Forward Fill":
                self.cleaned_df[col] = self.cleaned_df[col].ffill()
                current_missing = self.cleaned_df[col].isnull().sum()
                message = f"Applied forward fill to '{col}'\nMissing values reduced from {original_missing} to {current_missing}"
            
            elif method == "Backward Fill":
                self.cleaned_df[col] = self.cleaned_df[col].bfill()
                current_missing = self.cleaned_df[col].isnull().sum()
                message = f"Applied backward fill to '{col}'\nMissing values reduced from {original_missing} to {current_missing}"
            
            # Update status and show message
            self.update_status(f"Applied {method} to {col}")
            self.show_message("Cleaning Applied Successfully", message, "success")
            
            # Refresh data preview
            self.refresh_data_preview()
            
        except Exception as e:
            self.show_message("Error", f"Failed to apply cleaning method:\n{str(e)}", "error")
    
    def remove_outliers(self):
        col = self.clean_column.get()
        if not col:
            return
        
        if not pd.api.types.is_numeric_dtype(self.cleaned_df[col]):
            self.show_message("Invalid Operation",
                            "Outlier removal only works for numeric columns", "warning")
            return
        
        original_count = len(self.cleaned_df)
        
        Q1 = self.cleaned_df[col].quantile(0.25)
        Q3 = self.cleaned_df[col].quantile(0.75)
        IQR = Q3 - Q1
        
        self.cleaned_df = self.cleaned_df[
            (self.cleaned_df[col] >= Q1 - 1.5 * IQR) &
            (self.cleaned_df[col] <= Q3 + 1.5 * IQR)
        ]
        
        removed_count = original_count - len(self.cleaned_df)
        
        # Show detailed message
        message = (
            f"Outlier removal completed for column: '{col}'\n\n"
            f"• Removed {removed_count} outliers\n"
            f"• Original rows: {original_count:,}\n"
            f"• New row count: {len(self.cleaned_df):,}\n"
            f"• IQR range: [{Q1 - 1.5*IQR:.2f}, {Q3 + 1.5*IQR:.2f}]\n"
            f"• Data retained: {(len(self.cleaned_df)/original_count*100):.1f}%"
        )
        
        self.update_status(f"Removed {removed_count} outliers from {col}")
        self.show_message("Outliers Removed Successfully", message, "success")
        
        # Refresh data preview
        self.refresh_data_preview()
    
    def refresh_data_preview(self):
        """Refresh the data preview table with cleaned data"""
        if hasattr(self, 'tree') and self.tree:
            # Clear existing data
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            # Add cleaned data
            preview_df = self.cleaned_df.head(50)
            for _, row in preview_df.iterrows():
                self.tree.insert("", "end", values=list(row))
    
    def show_visualization_panel(self):
        if self.df is None:
            self.show_message("No Data", "Please load a CSV file first.", "info")
            return
        
        self.clear_content()
        
        viz_card = tk.Frame(self.card_container, bg="white", padx=20, pady=20)
        viz_card.pack(fill="both", expand=True)
        
        tk.Label(
            viz_card,
            text="📈 Data Visualizations",
            font=("Segoe UI", 16, "bold"),
            bg="white",
            fg=self.colors['dark']
        ).pack(anchor="w", pady=(0, 20))
        
        # ===== Visualization Selector =====
        selector_frame = tk.Frame(viz_card, bg="white")
        selector_frame.pack(fill="x", pady=(0, 20))
        
        tk.Label(
            selector_frame,
            text="Chart Type:",
            font=("Segoe UI", 11, "bold"),
            bg="white",
            fg=self.colors['dark']
        ).pack(side="left", padx=(0, 15))
        
        # Visualization type dropdown
        self.viz_type = ttk.Combobox(
            selector_frame,
            values=[
                "Histogram",
                "Box Plot", 
                "Scatter Plot",
                "Line Chart",
                "Bar Chart",
                "Pie Chart"
            ],
            state="readonly",
            width=15,
            font=("Segoe UI", 10)
        )
        self.viz_type.current(0)
        self.viz_type.pack(side="left", padx=(0, 30))
        self.viz_type.bind('<<ComboboxSelected>>', self.update_viz_selectors)
        
        # X-Axis selector
        tk.Label(
            selector_frame,
            text="X-Axis:",
            font=("Segoe UI", 11, "bold"),
            bg="white",
            fg=self.colors['dark']
        ).pack(side="left", padx=(0, 10))
        
        self.viz_x = ttk.Combobox(
            selector_frame,
            state="readonly",
            width=20,
            font=("Segoe UI", 10)
        )
        self.viz_x.pack(side="left", padx=(0, 20))
        
        # Y-Axis selector (only for certain charts)
        self.y_label = tk.Label(
            selector_frame,
            text="Y-Axis:",
            font=("Segoe UI", 11, "bold"),
            bg="white",
            fg=self.colors['dark']
        )
        
        self.viz_y = ttk.Combobox(
            selector_frame,
            state="readonly",
            width=20,
            font=("Segoe UI", 10)
        )
        
        # Generate button
        generate_btn = tk.Button(
            selector_frame,
            text="Generate Chart",
            font=("Segoe UI", 10, "bold"),
            bg=self.colors['primary'],
            fg="white",
            padx=20,
            pady=5,
            cursor="hand2",
            relief="flat",
            command=self.generate_visualization
        )
        generate_btn.pack(side="left", padx=(20, 0))
        
        # Hover effect
        generate_btn.bind("<Enter>", lambda e: generate_btn.config(bg=self.colors['secondary']))
        generate_btn.bind("<Leave>", lambda e: generate_btn.config(bg=self.colors['primary']))
        
        # Initialize selectors
        self.update_viz_selectors()
        
        # Chart display area with Save button
        chart_container = tk.Frame(viz_card, bg="white")
        chart_container.pack(fill="both", expand=True, pady=(20, 0))
        
        # Chart controls frame
        controls_frame = tk.Frame(chart_container, bg="white", height=40)
        controls_frame.pack(fill="x", pady=(0, 10))
        controls_frame.pack_propagate(False)
        
        # Save Chart button
        self.save_chart_btn = tk.Button(
            controls_frame,
            text="💾 Save Chart",
            font=("Segoe UI", 10, "bold"),
            bg="#38b000",
            fg="white",
            padx=20,
            pady=5,
            cursor="hand2",
            relief="flat",
            command=self.save_chart,
            state="disabled"
        )
        self.save_chart_btn.pack(side="right", padx=10)
        self.save_chart_btn.bind("<Enter>", lambda e: self.save_chart_btn.config(bg="#06d6a0"))
        self.save_chart_btn.bind("<Leave>", lambda e: self.save_chart_btn.config(bg="#38b000"))
        
        # Chart display area
        self.chart_display = tk.Frame(chart_container, bg="#f8fafc", height=450)
        self.chart_display.pack(fill="both", expand=True)
        
        # Initial message
        self.chart_message = tk.Label(
            self.chart_display,
            text="👆 Select chart type and axis columns, then click 'Generate Chart'",
            font=("Segoe UI", 12),
            bg="#f8fafc",
            fg="#718096"
        )
        self.chart_message.pack(expand=True)
        
        # Store current figure
        self.current_figure = None
    
    def update_viz_selectors(self, event=None):
        """Update column selectors based on chosen visualization type"""
        viz_type = self.viz_type.get()
        
        # Hide Y-axis by default
        self.y_label.pack_forget()
        self.viz_y.pack_forget()
        
        if viz_type in ["Histogram", "Box Plot", "Bar Chart", "Pie Chart"]:
            # Single column needed
            if viz_type in ["Bar Chart", "Pie Chart"]:
                # For bar/pie charts, show categorical first, then numeric
                categorical_cols = list(self.cleaned_df.select_dtypes(include=['object']).columns)
                numeric_cols = list(self.cleaned_df.select_dtypes(include=['number']).columns)
                available_cols = categorical_cols + numeric_cols
            else:
                # For histogram/boxplot, show numeric first
                numeric_cols = list(self.cleaned_df.select_dtypes(include=['number']).columns)
                categorical_cols = list(self.cleaned_df.select_dtypes(include=['object']).columns)
                available_cols = numeric_cols + categorical_cols
            
            self.viz_x['values'] = available_cols
            if available_cols:
                self.viz_x.current(0)
            
            # Add column type indicator
            self.add_column_type_indicator(self.viz_x, available_cols)
        
        elif viz_type in ["Scatter Plot", "Line Chart"]:
            # Two columns needed
            numeric_cols = list(self.cleaned_df.select_dtypes(include=['number']).columns)
            all_cols = list(self.cleaned_df.columns)
            
            self.viz_x['values'] = all_cols
            self.viz_y['values'] = numeric_cols
            
            if len(all_cols) >= 1:
                self.viz_x.current(0)
            if len(numeric_cols) >= 1:
                self.viz_y.current(0)
            
            # Show Y-axis selector
            self.y_label.pack(side="left", padx=(20, 10))
            self.viz_y.pack(side="left", padx=(0, 20))
            
            # Add column type indicators
            self.add_column_type_indicator(self.viz_x, all_cols)
            self.add_column_type_indicator(self.viz_y, numeric_cols)
    
    def add_column_type_indicator(self, combobox, columns):
        """Add column type indicators to combobox values"""
        if not columns:
            return
        
        formatted_values = []
        for col in columns:
            dtype = str(self.cleaned_df[col].dtype)
            if dtype.startswith('int') or dtype.startswith('float'):
                type_indicator = " (numeric)"
            elif dtype == 'object':
                type_indicator = " (text)"
            elif dtype == 'datetime64[ns]':
                type_indicator = " (date)"
            else:
                type_indicator = f" ({dtype})"
            
            formatted_values.append(f"{col}{type_indicator}")
        
        combobox['values'] = formatted_values
        
        # Store mapping of formatted values to actual column names
        combobox.column_mapping = {f"{col}{self.get_column_type_indicator(col)}": col for col in columns}
    
    def get_column_type_indicator(self, column):
        """Get type indicator for a column"""
        if column not in self.cleaned_df.columns:
            return ""
        
        dtype = str(self.cleaned_df[column].dtype)
        if dtype.startswith('int') or dtype.startswith('float'):
            return " (numeric)"
        elif dtype == 'object':
            return " (text)"
        elif dtype == 'datetime64[ns]':
            return " (date)"
        else:
            return f" ({dtype})"
    
    def get_actual_column_name(self, combobox, formatted_value):
        """Extract actual column name from formatted combobox value"""
        if hasattr(combobox, 'column_mapping') and formatted_value in combobox.column_mapping:
            return combobox.column_mapping[formatted_value]
        
        # Fallback: remove anything in parentheses
        if " (" in formatted_value:
            return formatted_value.split(" (")[0]
        return formatted_value
    
    def generate_visualization(self):
        viz_type = self.viz_type.get()
        x_col_formatted = self.viz_x.get()
        
        if not x_col_formatted:
            self.show_message("No Column Selected", "Please select at least one column.", "warning")
            return
        
        x_col = self.get_actual_column_name(self.viz_x, x_col_formatted)
        
        # Get Y column if applicable
        y_col = None
        if self.viz_y.winfo_ismapped():
            y_col_formatted = self.viz_y.get()
            if y_col_formatted:
                y_col = self.get_actual_column_name(self.viz_y, y_col_formatted)
        
        # Clear previous chart
        for widget in self.chart_display.winfo_children():
            widget.destroy()
        
        # Generate the selected visualization
        try:
            if viz_type == "Histogram":
                self.create_histogram(x_col)
            elif viz_type == "Box Plot":
                self.create_boxplot(x_col)
            elif viz_type == "Scatter Plot":
                if y_col:
                    self.create_scatter_plot(x_col, y_col)
                else:
                    self.show_message("Y-Axis Needed", 
                                    "Please select Y-axis column for scatter plot.", "warning")
                    return
            elif viz_type == "Line Chart":
                self.create_line_chart(x_col, y_col)
            elif viz_type == "Bar Chart":
                self.create_bar_chart(x_col)
            elif viz_type == "Pie Chart":
                self.create_pie_chart(x_col)
            
            # Enable save button
            self.save_chart_btn.config(state="normal")
            
        except Exception as e:
            self.show_message("Chart Error", f"Failed to create chart:\n{str(e)}", "error")
            # Disable save button on error
            self.save_chart_btn.config(state="disabled")
    
    def save_chart(self):
        if self.current_figure is None:
            self.show_message("No Chart", "No chart to save. Please generate a chart first.", "warning")
            return
        
        file_types = [
            ("PNG Image", "*.png"),
            ("PDF Document", "*.pdf"),
            ("SVG Vector", "*.svg"),
            ("All Files", "*.*")
        ]
        
        path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=file_types
        )
        
        if path:
            try:
                self.current_figure.savefig(path, dpi=300, bbox_inches='tight')
                
                filename = path.split('/')[-1]
                self.show_message("Chart Saved", 
                                f"Chart saved successfully!\n\n"
                                f"• File: {filename}\n"
                                f"• Size: {self.current_figure.get_size_inches()[0]:.1f}×{self.current_figure.get_size_inches()[1]:.1f} inches\n"
                                f"• DPI: 300\n"
                                f"• Format: {path.split('.')[-1].upper()}", 
                                "success")
                
                self.update_status(f"Chart saved as {filename}")
                
            except Exception as e:
                self.show_message("Save Failed", f"Error saving chart:\n{str(e)}", "error")
    
    def create_histogram(self, col):
        if not pd.api.types.is_numeric_dtype(self.cleaned_df[col]):
            self.show_message("Invalid Column", 
                            "Histogram requires numeric columns.", "warning")
            return
        
        self.current_figure = plt.Figure(figsize=(10, 6), dpi=100)
        ax = self.current_figure.add_subplot(111)
        
        data = self.cleaned_df[col].dropna()
        ax.hist(data, bins=min(30, len(data)//10), edgecolor='white', alpha=0.7, 
                color=self.colors['primary'])
        
        ax.set_xlabel(col, fontsize=11)
        ax.set_ylabel('Frequency', fontsize=11)
        ax.set_title(f'Histogram of {col}', fontsize=13, fontweight='bold')
        ax.grid(True, alpha=0.3)
        
        # Add statistics
        stats_text = f"Mean: {data.mean():.2f}\nStd: {data.std():.2f}\nN: {len(data):,}"
        ax.text(0.02, 0.98, stats_text, transform=ax.transAxes, fontsize=10,
                verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
        
        canvas = FigureCanvasTkAgg(self.current_figure, self.chart_display)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)
    
    def create_boxplot(self, col):
        if not pd.api.types.is_numeric_dtype(self.cleaned_df[col]):
            self.show_message("Invalid Column", 
                            "Box plot requires numeric columns.", "warning")
            return
        
        self.current_figure = plt.Figure(figsize=(10, 6), dpi=100)
        ax = self.current_figure.add_subplot(111)
        
        data = self.cleaned_df[col].dropna()
        bp = ax.boxplot(data, patch_artist=True, vert=False)
        
        # Customize boxplot colors
        bp['boxes'][0].set_facecolor(self.colors['primary'])
        bp['boxes'][0].set_alpha(0.7)
        bp['medians'][0].set_color('red')
        bp['medians'][0].set_linewidth(2)
        
        ax.set_xlabel(col, fontsize=11)
        ax.set_title(f'Box Plot of {col}', fontsize=13, fontweight='bold')
        ax.grid(True, alpha=0.3)
        
        # Add statistics
        Q1 = data.quantile(0.25)
        Q3 = data.quantile(0.75)
        IQR = Q3 - Q1
        
        stats_text = (f"Q1: {Q1:.2f}\n"
                     f"Median: {data.median():.2f}\n"
                     f"Q3: {Q3:.2f}\n"
                     f"IQR: {IQR:.2f}\n"
                     f"N: {len(data):,}")
        ax.text(0.02, 0.98, stats_text, transform=ax.transAxes, fontsize=10,
                verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
        
        canvas = FigureCanvasTkAgg(self.current_figure, self.chart_display)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)
    
    def create_scatter_plot(self, x_col, y_col):
        self.current_figure = plt.Figure(figsize=(10, 6), dpi=100)
        ax = self.current_figure.add_subplot(111)
        
        ax.scatter(self.cleaned_df[x_col], self.cleaned_df[y_col], 
                  alpha=0.6, color=self.colors['primary'], edgecolors='white')
        
        ax.set_xlabel(f"{x_col} (X-Axis)", fontsize=11)
        ax.set_ylabel(f"{y_col} (Y-Axis)", fontsize=11)
        ax.set_title(f'Scatter Plot: {x_col} vs {y_col}', fontsize=13, fontweight='bold')
        ax.grid(True, alpha=0.3)
        
        canvas = FigureCanvasTkAgg(self.current_figure, self.chart_display)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)
    
    def create_line_chart(self, x_col, y_col=None):
        self.current_figure = plt.Figure(figsize=(10, 6), dpi=100)
        ax = self.current_figure.add_subplot(111)
        
        if y_col:
            data = self.cleaned_df[[x_col, y_col]].head(100)
            ax.plot(data.index, data[x_col], marker='o', linewidth=2, label=f"{x_col} (X)",
                   color=self.colors['primary'])
            ax.plot(data.index, data[y_col], marker='s', linewidth=2, label=f"{y_col} (Y)",
                   color=self.colors['accent'])
            ax.legend()
            title = f'Line Chart: {x_col} vs {y_col}'
        else:
            data = self.cleaned_df[x_col].head(100)
            ax.plot(data.index, data, marker='o', linewidth=2, color=self.colors['primary'])
            title = f'Line Chart: {x_col}'
        
        ax.set_xlabel('Index (X-Axis)', fontsize=11)
        ax.set_ylabel('Value (Y-Axis)', fontsize=11)
        ax.set_title(title, fontsize=13, fontweight='bold')
        ax.grid(True, alpha=0.3)
        
        canvas = FigureCanvasTkAgg(self.current_figure, self.chart_display)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)
    
    def create_bar_chart(self, col):
        top_values = self.cleaned_df[col].value_counts().head(10)
        
        self.current_figure = plt.Figure(figsize=(10, 6), dpi=100)
        ax = self.current_figure.add_subplot(111)
        
        colors = plt.cm.Set3(np.linspace(0, 1, len(top_values)))
        bars = ax.bar(range(len(top_values)), top_values.values, color=colors, edgecolor='white')
        
        ax.set_xlabel(col, fontsize=11)
        ax.set_ylabel('Count', fontsize=11)
        ax.set_title(f'Bar Chart: Top 10 Values in {col}', fontsize=13, fontweight='bold')
        ax.set_xticks(range(len(top_values)))
        ax.set_xticklabels(top_values.index, rotation=45, ha='right')
        ax.grid(True, alpha=0.3, axis='y')
        
        # Add value labels on bars
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                   f'{int(height)}', ha='center', va='bottom', fontsize=9)
        
        canvas = FigureCanvasTkAgg(self.current_figure, self.chart_display)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)
    
    def create_pie_chart(self, col):
        value_counts = self.cleaned_df[col].value_counts().head(6)  # Top 6 categories
        
        self.current_figure = plt.Figure(figsize=(8, 8), dpi=100)
        ax = self.current_figure.add_subplot(111)
        
        colors = plt.cm.Pastel1(np.linspace(0, 1, len(value_counts)))
        wedges, texts, autotexts = ax.pie(value_counts.values, 
                                         labels=value_counts.index,
                                         autopct='%1.1f%%',
                                         colors=colors,
                                         startangle=90,
                                         textprops={'fontsize': 10})
        
        ax.set_title(f'Pie Chart: Distribution of {col}', fontsize=13, fontweight='bold')
        ax.axis('equal')  # Make the pie chart circular
        
        canvas = FigureCanvasTkAgg(self.current_figure, self.chart_display)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)
    
    def show_statistics_panel(self):
        if self.df is None:
            self.show_message("No Data", "Please load a CSV file first.", "info")
            return
        
        self.clear_content()
        
        stats_card = tk.Frame(self.card_container, bg="white", padx=20, pady=20)
        stats_card.pack(fill="both", expand=True)
        
        tk.Label(
            stats_card,
            text="📊 Statistical Analysis",
            font=("Segoe UI", 16, "bold"),
            bg="white",
            fg=self.colors['dark']
        ).pack(anchor="w", pady=(0, 20))
        
        # Create notebook for multiple tabs
        notebook = ttk.Notebook(stats_card)
        notebook.pack(fill="both", expand=True)
        
        # Tab 1: Column Details
        col_frame = tk.Frame(notebook, bg="white")
        notebook.add(col_frame, text="Column Details")
        
        # Create treeview for column details
        col_tree_frame = tk.Frame(col_frame, bg="white")
        col_tree_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Add scrollbars
        col_v_scroll = ttk.Scrollbar(col_tree_frame, orient="vertical")
        col_h_scroll = ttk.Scrollbar(col_tree_frame, orient="horizontal")
        
        col_tree = ttk.Treeview(
            col_tree_frame,
            columns=("Column", "Data Type", "Non-Null", "Null", "Null %", "Unique", "Sample Values"),
            show="headings",
            yscrollcommand=col_v_scroll.set,
            xscrollcommand=col_h_scroll.set,
            height=15
        )
        
        col_v_scroll.config(command=col_tree.yview)
        col_h_scroll.config(command=col_tree.xview)
        
        col_v_scroll.pack(side="right", fill="y")
        col_h_scroll.pack(side="bottom", fill="x")
        col_tree.pack(side="left", fill="both", expand=True)
        
        # Configure columns
        col_tree.heading("Column", text="Column Name")
        col_tree.heading("Data Type", text="Data Type")
        col_tree.heading("Non-Null", text="Non-Null Count")
        col_tree.heading("Null", text="Null Count")
        col_tree.heading("Null %", text="Null %")
        col_tree.heading("Unique", text="Unique Values")
        col_tree.heading("Sample Values", text="Sample Values")
        
        col_tree.column("Column", width=150)
        col_tree.column("Data Type", width=100)
        col_tree.column("Non-Null", width=100)
        col_tree.column("Null", width=80)
        col_tree.column("Null %", width=80)
        col_tree.column("Unique", width=80)
        col_tree.column("Sample Values", width=200)
        
        # Populate column details
        for col in self.cleaned_df.columns:
            non_null = self.cleaned_df[col].count()
            null_count = self.cleaned_df[col].isnull().sum()
            null_percent = (null_count / len(self.cleaned_df)) * 100 if len(self.cleaned_df) > 0 else 0
            unique_count = self.cleaned_df[col].nunique()
            
            # Get sample values
            sample_values = []
            for val in self.cleaned_df[col].dropna().head(3):
                sample_values.append(str(val))
            sample_str = ", ".join(sample_values) if sample_values else "N/A"
            
            # Get data type with better formatting
            dtype = str(self.cleaned_df[col].dtype)
            if dtype.startswith('int'):
                dtype_fmt = "Integer"
            elif dtype.startswith('float'):
                dtype_fmt = "Float"
            elif dtype == 'object':
                dtype_fmt = "Text"
            elif dtype == 'datetime64[ns]':
                dtype_fmt = "Date"
            elif dtype == 'bool':
                dtype_fmt = "Boolean"
            else:
                dtype_fmt = dtype
            
            col_tree.insert("", "end", values=(
                col,
                dtype_fmt,
                f"{non_null:,}",
                f"{null_count:,}",
                f"{null_percent:.1f}%",
                f"{unique_count:,}",
                sample_str[:50] + "..." if len(sample_str) > 50 else sample_str
            ))
        
        # Tab 2: Numerical Statistics
        num_frame = tk.Frame(notebook, bg="white")
        notebook.add(num_frame, text="Numerical Statistics")
        
        # Create text widget for numerical statistics
        num_text_frame = tk.Frame(num_frame, bg="white")
        num_text_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        num_scrollbar = ttk.Scrollbar(num_text_frame)
        num_scrollbar.pack(side="right", fill="y")
        
        num_text = tk.Text(
            num_text_frame,
            font=("Consolas", 10),
            wrap="none",
            yscrollcommand=num_scrollbar.set,
            bg="#f8fafc",
            padx=15,
            pady=15
        )
        num_text.pack(side="left", fill="both", expand=True)
        num_scrollbar.config(command=num_text.yview)
        
        # Display numerical statistics
        numeric_cols = self.cleaned_df.select_dtypes(include=['number'])
        if len(numeric_cols.columns) > 0:
            num_text.insert("end", "NUMERICAL COLUMNS STATISTICS\n")
            num_text.insert("end", "=" * 50 + "\n\n")
            
            desc = numeric_cols.describe().T
            for col in numeric_cols.columns:
                num_text.insert("end", f"{col}:\n")
                num_text.insert("end", "-" * 40 + "\n")
                num_text.insert("end", f"  Count:    {desc.loc[col, 'count']:,.0f}\n")
                num_text.insert("end", f"  Mean:     {desc.loc[col, 'mean']:,.2f}\n")
                num_text.insert("end", f"  Std:      {desc.loc[col, 'std']:,.2f}\n")
                num_text.insert("end", f"  Min:      {desc.loc[col, 'min']:,.2f}\n")
                num_text.insert("end", f"  25%:      {desc.loc[col, '25%']:,.2f}\n")
                num_text.insert("end", f"  50%:      {desc.loc[col, '50%']:,.2f}\n")
                num_text.insert("end", f"  75%:      {desc.loc[col, '75%']:,.2f}\n")
                num_text.insert("end", f"  Max:      {desc.loc[col, 'max']:,.2f}\n\n")
        else:
            num_text.insert("end", "No numerical columns found in the dataset.\n")
        
        num_text.config(state="disabled")
        
        # Tab 3: Overall Statistics
        overall_frame = tk.Frame(notebook, bg="white")
        notebook.add(overall_frame, text="Overall Statistics")
        
        # Create text widget for overall statistics
        overall_text_frame = tk.Frame(overall_frame, bg="white")
        overall_text_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        overall_scrollbar = ttk.Scrollbar(overall_text_frame)
        overall_scrollbar.pack(side="right", fill="y")
        
        overall_text = tk.Text(
            overall_text_frame,
            font=("Consolas", 10),
            wrap="none",
            yscrollcommand=overall_scrollbar.set,
            bg="#f8fafc",
            padx=15,
            pady=15
        )
        overall_text.pack(side="left", fill="both", expand=True)
        overall_scrollbar.config(command=overall_text.yview)
        
        # Display overall statistics
        overall_text.insert("end", "DATASET OVERALL STATISTICS\n")
        overall_text.insert("end", "=" * 50 + "\n\n")
        
        overall_text.insert("end", "BASIC INFORMATION:\n")
        overall_text.insert("end", "-" * 40 + "\n")
        overall_text.insert("end", f"Rows: {self.cleaned_df.shape[0]:,}\n")
        overall_text.insert("end", f"Columns: {self.cleaned_df.shape[1]}\n")
        overall_text.insert("end", f"Total cells: {self.cleaned_df.size:,}\n")
        overall_text.insert("end", f"Memory usage: {self.cleaned_df.memory_usage(deep=True).sum() / 1024 / 1024:.2f} MB\n\n")
        
        overall_text.insert("end", "DATA TYPE DISTRIBUTION:\n")
        overall_text.insert("end", "-" * 40 + "\n")
        for dtype, count in self.cleaned_df.dtypes.value_counts().items():
            dtype_str = str(dtype)
            if dtype_str.startswith('int'):
                dtype_name = "Integer"
            elif dtype_str.startswith('float'):
                dtype_name = "Float"
            elif dtype_str == 'object':
                dtype_name = "Text"
            elif dtype_str == 'datetime64[ns]':
                dtype_name = "Date"
            else:
                dtype_name = dtype_str
            overall_text.insert("end", f"{dtype_name}: {count}\n")
        overall_text.insert("end", "\n")
        
        overall_text.insert("end", "MISSING VALUES SUMMARY:\n")
        overall_text.insert("end", "-" * 40 + "\n")
        missing_total = self.cleaned_df.isnull().sum().sum()
        overall_text.insert("end", f"Total missing values: {missing_total:,}\n")
        overall_text.insert("end", f"Percentage of missing data: {(missing_total/self.cleaned_df.size*100):.2f}%\n\n")
        
        overall_text.insert("end", "DUPLICATE ROWS:\n")
        overall_text.insert("end", "-" * 40 + "\n")
        duplicate_count = self.cleaned_df.duplicated().sum()
        overall_text.insert("end", f"Duplicate rows: {duplicate_count:,}\n")
        overall_text.insert("end", f"Percentage duplicates: {(duplicate_count/len(self.cleaned_df)*100):.2f}%\n")
        
        overall_text.config(state="disabled")
    
    def export_cleaned_csv(self):
        if self.cleaned_df is None:
            self.show_message("No Data", "No data to export.", "info")
            return
        
        path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[
                ("CSV Files", "*.csv"),
                ("Excel Files", "*.xlsx"),
                ("JSON Files", "*.json"),
                ("All Files", "*.*")
            ]
        )
        
        if path:
            try:
                if path.endswith('.csv'):
                    self.cleaned_df.to_csv(path, index=False)
                    file_type = "CSV"
                elif path.endswith('.xlsx'):
                    self.cleaned_df.to_excel(path, index=False)
                    file_type = "Excel"
                elif path.endswith('.json'):
                    self.cleaned_df.to_json(path, orient='records')
                    file_type = "JSON"
                
                filename = path.split('/')[-1]
                message = (f"Data exported successfully!\n\n"
                          f"• File: {filename}\n"
                          f"• Format: {file_type}\n"
                          f"• Rows: {self.cleaned_df.shape[0]:,}\n"
                          f"• Columns: {self.cleaned_df.shape[1]}\n"
                          f"• Missing values: {self.cleaned_df.isnull().sum().sum():,}\n"
                          f"• Duplicate rows: {self.cleaned_df.duplicated().sum():,}")
                
                self.update_status(f"Exported to {filename}")
                self.show_message("Export Successful", message, "success")
                
            except Exception as e:
                self.show_message("Export Failed", f"Error during export:\n{str(e)}", "error")
    
    def adjust_color(self, color, amount=20):
        """Lighten or darken a color (simplified implementation)"""
        return color

if __name__ == "__main__":
    root = tk.Tk()
    app = EnhancedCSVAnalyzerApp(root)
    root.mainloop()