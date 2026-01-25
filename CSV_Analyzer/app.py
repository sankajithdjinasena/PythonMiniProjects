import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import seaborn as sns
from pandastable import Table
import threading

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
            ("🧹 Data Cleaning", self.show_cleaning_panel),
            ("📈 Visualizations", self.show_visualization_panel),
            ("📊 Statistics", self.show_statistics_panel),
            ("⚙️ Settings", self.show_settings_panel),
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
    
    def clear_content(self):
        for widget in self.card_container.winfo_children():
            widget.destroy()
    
    def update_status(self, message):
        self.status_label.config(text=message)
        self.root.update()
    
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
                self.root.after(0, self.show_error, f"Error loading file:\n{str(e)}")
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
        
        # Show data preview
        self.show_data_preview()
    
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
        style.map('Treeview.Heading', background=[('active', '#cbd5e0')])
        
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
            messagebox.showinfo("No Data", "Please load a CSV file first.")
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
        
        # Outlier removal section
        outlier_frame = tk.Frame(cleaning_card, bg="#f1f5f9", padx=20, pady=20)
        outlier_frame.pack(fill="x", pady=(20, 0))
        
        tk.Label(
            outlier_frame,
            text="🔍 Outlier Detection & Removal",
            font=("Segoe UI", 12, "bold"),
            bg="#f1f5f9",
            fg=self.colors['dark']
        ).pack(anchor="w", pady=(0, 10))
        
        outlier_btn = tk.Button(
            outlier_frame,
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
        outlier_btn.pack()
        
        # Hover effect
        outlier_btn.bind("<Enter>", lambda e: outlier_btn.config(bg="#f3722c"))
        outlier_btn.bind("<Leave>", lambda e: outlier_btn.config(bg=self.colors['warning']))
    
    def apply_cleaning_method(self, method):
        col = self.clean_column.get()
        if not col:
            return
        
        try:
            if method == "Mean Imputation":
                if pd.api.types.is_numeric_dtype(self.cleaned_df[col]):
                    self.cleaned_df[col] = self.cleaned_df[col].fillna(
                        self.cleaned_df[col].mean()
                    )
                else:
                    messagebox.showwarning("Invalid Operation", 
                                         "Mean imputation only works for numeric columns")
                    return
            
            elif method == "Median Imputation":
                if pd.api.types.is_numeric_dtype(self.cleaned_df[col]):
                    self.cleaned_df[col] = self.cleaned_df[col].fillna(
                        self.cleaned_df[col].median()
                    )
                else:
                    messagebox.showwarning("Invalid Operation",
                                         "Median imputation only works for numeric columns")
                    return
            
            elif method == "Mode Imputation":
                self.cleaned_df[col] = self.cleaned_df[col].fillna(
                    self.cleaned_df[col].mode()[0] if not self.cleaned_df[col].mode().empty else ""
                )
            
            elif method == "Drop Rows":
                self.cleaned_df = self.cleaned_df.dropna(subset=[col])
            
            elif method == "Forward Fill":
                self.cleaned_df[col] = self.cleaned_df[col].ffill()
            
            elif method == "Backward Fill":
                self.cleaned_df[col] = self.cleaned_df[col].bfill()
            
            self.update_status(f"Applied {method} to {col}")
            messagebox.showinfo("Success", 
                              f"{method} applied successfully!\n"
                              f"Remaining missing values in {col}: "
                              f"{self.cleaned_df[col].isnull().sum()}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to apply cleaning method:\n{str(e)}")
    
    def remove_outliers(self):
        col = self.clean_column.get()
        if not col:
            return
        
        if not pd.api.types.is_numeric_dtype(self.cleaned_df[col]):
            messagebox.showwarning("Invalid Operation",
                                 "Outlier removal only works for numeric columns")
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
        
        self.update_status(f"Removed {removed_count} outliers from {col}")
        messagebox.showinfo("Outliers Removed",
                          f"Removed {removed_count} outliers from '{col}'\n"
                          f"New dataset has {len(self.cleaned_df)} rows")
    
    def show_visualization_panel(self):
        if self.df is None:
            messagebox.showinfo("No Data", "Please load a CSV file first.")
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
        
        # Chart type selection
        chart_frame = tk.Frame(viz_card, bg="white")
        chart_frame.pack(fill="x", pady=(0, 20))
        
        chart_types = [
            ("📊 Histogram", "Distribution of a single variable", self.show_histogram),
            ("📦 Box Plot", "Distribution and outliers", self.show_boxplot),
            ("📈 Line Chart", "Trends over time/sequence", self.show_line_chart),
            ("• Scatter Plot", "Relationship between two variables", self.show_scatter_plot),
            ("📊 Bar Chart", "Categorical data comparison", self.show_bar_chart),
            ("🫓 Pie Chart", "Proportional composition", self.show_pie_chart)
        ]
        
        for i, (title, desc, command) in enumerate(chart_types):
            chart_card = tk.Frame(
                chart_frame,
                bg="#f8fafc",
                relief="groove",
                borderwidth=1,
                cursor="hand2"
            )
            chart_card.grid(row=i//3, column=i%3, padx=10, pady=10, sticky="nsew")
            chart_card.bind("<Button-1>", lambda e, cmd=command: cmd())
            
            tk.Label(
                chart_card,
                text=title,
                font=("Segoe UI", 11, "bold"),
                bg="#f8fafc",
                fg=self.colors['primary']
            ).pack(anchor="w", padx=15, pady=(15, 5))
            
            tk.Label(
                chart_card,
                text=desc,
                font=("Segoe UI", 9),
                bg="#f8fafc",
                fg="#718096",
                wraplength=150
            ).pack(anchor="w", padx=15, pady=(0, 15))
            
            chart_frame.grid_columnconfigure(i%3, weight=1)
        
        # Chart display area
        self.chart_display = tk.Frame(viz_card, bg="white", height=400)
        self.chart_display.pack(fill="both", expand=True, pady=(20, 0))
    
    def create_chart_frame(self, title):
        # Clear previous chart
        for widget in self.chart_display.winfo_children():
            widget.destroy()
        
        # Create new chart container
        chart_container = tk.Frame(self.chart_display, bg="white")
        chart_container.pack(fill="both", expand=True)
        
        tk.Label(
            chart_container,
            text=title,
            font=("Segoe UI", 14, "bold"),
            bg="white",
            fg=self.colors['dark']
        ).pack(anchor="w", pady=(0, 10))
        
        return chart_container
    
    def show_histogram(self):
        col = self.get_numeric_column("Select column for histogram:")
        if not col:
            return
        
        chart_container = self.create_chart_frame(f"Histogram of {col}")
        
        fig = plt.Figure(figsize=(10, 6), dpi=100)
        ax = fig.add_subplot(111)
        
        data = self.cleaned_df[col].dropna()
        ax.hist(data, bins=min(30, len(data)//10), edgecolor='white', alpha=0.7, 
                color=self.colors['primary'])
        
        ax.set_xlabel(col, fontsize=11)
        ax.set_ylabel('Frequency', fontsize=11)
        ax.set_title(f'Distribution of {col}', fontsize=13, fontweight='bold')
        ax.grid(True, alpha=0.3)
        
        # Add statistics
        stats_text = f"Mean: {data.mean():.2f}\nStd: {data.std():.2f}\nN: {len(data)}"
        ax.text(0.02, 0.98, stats_text, transform=ax.transAxes, fontsize=10,
                verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
        
        canvas = FigureCanvasTkAgg(fig, chart_container)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=20, pady=20)
    
    def show_boxplot(self):
        col = self.get_numeric_column("Select column for box plot:")
        if not col:
            return
        
        chart_container = self.create_chart_frame(f"Box Plot of {col}")
        
        fig = plt.Figure(figsize=(10, 6), dpi=100)
        ax = fig.add_subplot(111)
        
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
        
        stats_text = f"Q1: {Q1:.2f}\nMedian: {data.median():.2f}\nQ3: {Q3:.2f}\nIQR: {IQR:.2f}"
        ax.text(0.02, 0.98, stats_text, transform=ax.transAxes, fontsize=10,
                verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
        
        canvas = FigureCanvasTkAgg(fig, chart_container)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=20, pady=20)
    
    def show_line_chart(self):
        # Simplified line chart - you can enhance this
        numeric_cols = self.cleaned_df.select_dtypes(include=['number']).columns
        
        if len(numeric_cols) < 2:
            messagebox.showinfo("Insufficient Data",
                              "Need at least 2 numeric columns for line chart")
            return
        
        chart_container = self.create_chart_frame("Line Chart")
        
        fig = plt.Figure(figsize=(10, 6), dpi=100)
        ax = fig.add_subplot(111)
        
        sample_data = self.cleaned_df[numeric_cols[:2]].head(50)
        
        for i, col in enumerate(sample_data.columns):
            ax.plot(sample_data.index, sample_data[col], 
                   marker='o', linewidth=2, label=col,
                   color=[self.colors['primary'], self.colors['accent']][i])
        
        ax.set_xlabel('Index', fontsize=11)
        ax.set_ylabel('Value', fontsize=11)
        ax.set_title('Line Chart Comparison', fontsize=13, fontweight='bold')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        canvas = FigureCanvasTkAgg(fig, chart_container)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=20, pady=20)
    
    def show_scatter_plot(self):
        numeric_cols = list(self.cleaned_df.select_dtypes(include=['number']).columns)
        
        if len(numeric_cols) < 2:
            messagebox.showinfo("Insufficient Data",
                              "Need at least 2 numeric columns for scatter plot")
            return
        
        chart_container = self.create_chart_frame("Scatter Plot")
        
        fig = plt.Figure(figsize=(10, 6), dpi=100)
        ax = fig.add_subplot(111)
        
        x_col = numeric_cols[0]
        y_col = numeric_cols[1] if len(numeric_cols) > 1 else numeric_cols[0]
        
        ax.scatter(self.cleaned_df[x_col], self.cleaned_df[y_col], 
                  alpha=0.6, color=self.colors['primary'], edgecolors='white')
        
        ax.set_xlabel(x_col, fontsize=11)
        ax.set_ylabel(y_col, fontsize=11)
        ax.set_title(f'{x_col} vs {y_col}', fontsize=13, fontweight='bold')
        ax.grid(True, alpha=0.3)
        
        canvas = FigureCanvasTkAgg(fig, chart_container)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=20, pady=20)
    
    def show_bar_chart(self):
        # For simplicity, using first categorical column
        categorical_cols = self.cleaned_df.select_dtypes(include=['object']).columns
        
        if len(categorical_cols) == 0:
            messagebox.showinfo("No Categorical Data",
                              "No categorical columns found for bar chart")
            return
        
        col = categorical_cols[0]
        top_values = self.cleaned_df[col].value_counts().head(10)
        
        chart_container = self.create_chart_frame(f"Bar Chart: Top 10 {col}")
        
        fig = plt.Figure(figsize=(10, 6), dpi=100)
        ax = fig.add_subplot(111)
        
        colors = plt.cm.Set3(np.linspace(0, 1, len(top_values)))
        bars = ax.bar(range(len(top_values)), top_values.values, color=colors, edgecolor='white')
        
        ax.set_xlabel(col, fontsize=11)
        ax.set_ylabel('Count', fontsize=11)
        ax.set_title(f'Top 10 Values in {col}', fontsize=13, fontweight='bold')
        ax.set_xticks(range(len(top_values)))
        ax.set_xticklabels(top_values.index, rotation=45, ha='right')
        ax.grid(True, alpha=0.3, axis='y')
        
        # Add value labels on bars
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                   f'{int(height)}', ha='center', va='bottom', fontsize=9)
        
        canvas = FigureCanvasTkAgg(fig, chart_container)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=20, pady=20)
    
    def show_pie_chart(self):
        # Using first categorical column for pie chart
        categorical_cols = self.cleaned_df.select_dtypes(include=['object']).columns
        
        if len(categorical_cols) == 0:
            messagebox.showinfo("No Categorical Data",
                              "No categorical columns found for pie chart")
            return
        
        col = categorical_cols[0]
        value_counts = self.cleaned_df[col].value_counts().head(6)  # Top 6 categories
        
        chart_container = self.create_chart_frame(f"Pie Chart: {col}")
        
        fig = plt.Figure(figsize=(8, 8), dpi=100)
        ax = fig.add_subplot(111)
        
        colors = plt.cm.Pastel1(np.linspace(0, 1, len(value_counts)))
        wedges, texts, autotexts = ax.pie(value_counts.values, 
                                         labels=value_counts.index,
                                         autopct='%1.1f%%',
                                         colors=colors,
                                         startangle=90,
                                         textprops={'fontsize': 10})
        
        ax.set_title(f'Distribution of {col}', fontsize=13, fontweight='bold')
        
        # Make the pie chart circular
        ax.axis('equal')
        
        canvas = FigureCanvasTkAgg(fig, chart_container)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=20, pady=20)
    
    def get_numeric_column(self, prompt):
        numeric_cols = list(self.cleaned_df.select_dtypes(include=['number']).columns)
        
        if len(numeric_cols) == 0:
            messagebox.showinfo("No Numeric Data",
                              "No numeric columns available for this visualization")
            return None
        
        # Create a simple dialog for column selection
        dialog = tk.Toplevel(self.root)
        dialog.title("Select Column")
        dialog.geometry("300x150")
        dialog.configure(bg="white")
        dialog.transient(self.root)
        dialog.grab_set()
        
        tk.Label(dialog, text=prompt, font=("Segoe UI", 11), 
                bg="white", fg=self.colors['dark']).pack(pady=20)
        
        selected_col = tk.StringVar()
        selected_col.set(numeric_cols[0])
        
        combobox = ttk.Combobox(dialog, textvariable=selected_col, 
                               values=numeric_cols, state="readonly")
        combobox.pack(pady=10, padx=20, fill="x")
        
        result = []
        
        def on_ok():
            result.append(selected_col.get())
            dialog.destroy()
        
        tk.Button(dialog, text="OK", command=on_ok, 
                 bg=self.colors['primary'], fg="white",
                 padx=20, pady=5).pack(pady=10)
        
        dialog.wait_window()
        
        return result[0] if result else None
    
    def show_statistics_panel(self):
        if self.df is None:
            messagebox.showinfo("No Data", "Please load a CSV file first.")
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
        
        # Create text widget with scrollbar for statistics
        text_frame = tk.Frame(stats_card, bg="white")
        text_frame.pack(fill="both", expand=True)
        
        scrollbar = ttk.Scrollbar(text_frame)
        scrollbar.pack(side="right", fill="y")
        
        stats_text = tk.Text(
            text_frame,
            font=("Consolas", 10),
            wrap="none",
            yscrollcommand=scrollbar.set,
            bg="#f8fafc",
            padx=15,
            pady=15,
            relief="flat"
        )
        stats_text.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=stats_text.yview)
        
        # Display statistics
        stats_text.insert("end", "=" * 70 + "\n")
        stats_text.insert("end", "DATASET STATISTICAL SUMMARY\n")
        stats_text.insert("end", "=" * 70 + "\n\n")
        
        # Basic info
        stats_text.insert("end", "BASIC INFORMATION:\n")
        stats_text.insert("end", "-" * 40 + "\n")
        stats_text.insert("end", f"Shape: {self.cleaned_df.shape[0]} rows × {self.cleaned_df.shape[1]} columns\n")
        stats_text.insert("end", f"Total cells: {self.cleaned_df.size:,}\n")
        stats_text.insert("end", f"Memory usage: {self.cleaned_df.memory_usage(deep=True).sum() / 1024 / 1024:.2f} MB\n\n")
        
        # Data types
        stats_text.insert("end", "DATA TYPES:\n")
        stats_text.insert("end", "-" * 40 + "\n")
        for dtype, count in self.cleaned_df.dtypes.value_counts().items():
            stats_text.insert("end", f"{dtype}: {count}\n")
        stats_text.insert("end", "\n")
        
        # Missing values
        stats_text.insert("end", "MISSING VALUES:\n")
        stats_text.insert("end", "-" * 40 + "\n")
        missing = self.cleaned_df.isnull().sum()
        missing = missing[missing > 0]
        if len(missing) == 0:
            stats_text.insert("end", "No missing values found\n")
        else:
            for col, count in missing.items():
                percentage = (count / len(self.cleaned_df)) * 100
                stats_text.insert("end", f"{col}: {count:,} ({percentage:.1f}%)\n")
        stats_text.insert("end", "\n")
        
        # Numerical statistics
        numeric_cols = self.cleaned_df.select_dtypes(include=['number'])
        if len(numeric_cols.columns) > 0:
            stats_text.insert("end", "NUMERICAL COLUMNS STATISTICS:\n")
            stats_text.insert("end", "-" * 40 + "\n")
            
            desc = numeric_cols.describe().T
            for col in numeric_cols.columns:
                stats_text.insert("end", f"\n{col}:\n")
                stats_text.insert("end", f"  Count:    {desc.loc[col, 'count']:,.0f}\n")
                stats_text.insert("end", f"  Mean:     {desc.loc[col, 'mean']:,.2f}\n")
                stats_text.insert("end", f"  Std:      {desc.loc[col, 'std']:,.2f}\n")
                stats_text.insert("end", f"  Min:      {desc.loc[col, 'min']:,.2f}\n")
                stats_text.insert("end", f"  25%:      {desc.loc[col, '25%']:,.2f}\n")
                stats_text.insert("end", f"  50%:      {desc.loc[col, '50%']:,.2f}\n")
                stats_text.insert("end", f"  75%:      {desc.loc[col, '75%']:,.2f}\n")
                stats_text.insert("end", f"  Max:      {desc.loc[col, 'max']:,.2f}\n")
        
        stats_text.config(state="disabled")
    
    def show_settings_panel(self):
        self.clear_content()
        
        settings_card = tk.Frame(self.card_container, bg="white", padx=20, pady=20)
        settings_card.pack(fill="both", expand=True)
        
        tk.Label(
            settings_card,
            text="⚙️ Application Settings",
            font=("Segoe UI", 16, "bold"),
            bg="white",
            fg=self.colors['dark']
        ).pack(anchor="w", pady=(0, 30))
        
        settings = [
            ("Theme", ["Light", "Dark", "System"]),
            ("Chart Style", ["Default", "Seaborn", "ggplot", "bmh"]),
            ("Default View", ["Welcome", "Data Preview", "Cleaning"]),
            ("Auto-save", ["Yes", "No"]),
            ("Display Rows", ["50", "100", "200", "500"]),
            ("Export Format", ["CSV", "Excel", "JSON"])
        ]
        
        for i, (label, options) in enumerate(settings):
            frame = tk.Frame(settings_card, bg="white")
            frame.pack(fill="x", pady=10)
            
            tk.Label(
                frame,
                text=label,
                font=("Segoe UI", 11),
                bg="white",
                fg=self.colors['dark'],
                width=15,
                anchor="w"
            ).pack(side="left")
            
            var = tk.StringVar(value=options[0])
            for j, option in enumerate(options):
                rb = tk.Radiobutton(
                    frame,
                    text=option,
                    variable=var,
                    value=option,
                    font=("Segoe UI", 10),
                    bg="white",
                    fg="#4a5568",
                    selectcolor=self.colors['light']
                )
                rb.pack(side="left", padx=10)
        
        # Save button
        save_btn = tk.Button(
            settings_card,
            text="💾 Save Settings",
            font=("Segoe UI", 11, "bold"),
            bg=self.colors['success'],
            fg="white",
            padx=30,
            pady=10,
            cursor="hand2",
            relief="flat"
        )
        save_btn.pack(pady=40)
        
        save_btn.bind("<Enter>", lambda e: save_btn.config(bg="#06d6a0"))
        save_btn.bind("<Leave>", lambda e: save_btn.config(bg=self.colors['success']))
    
    def export_cleaned_csv(self):
        if self.cleaned_df is None:
            messagebox.showinfo("No Data", "No data to export.")
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
                elif path.endswith('.xlsx'):
                    self.cleaned_df.to_excel(path, index=False)
                elif path.endswith('.json'):
                    self.cleaned_df.to_json(path, orient='records')
                
                self.update_status(f"Exported to {path.split('/')[-1]}")
                messagebox.showinfo("Success", 
                                  f"Data exported successfully!\n\n"
                                  f"File: {path}\n"
                                  f"Rows: {self.cleaned_df.shape[0]:,}\n"
                                  f"Columns: {self.cleaned_df.shape[1]}")
                
            except Exception as e:
                messagebox.showerror("Export Failed", f"Error during export:\n{str(e)}")
    
    def show_error(self, message):
        messagebox.showerror("Error", message)
        self.update_status("Error occurred")
    
    def adjust_color(self, color, amount=20):
        """Lighten or darken a color"""
        # Simplified color adjustment - you can implement a proper one
        return color

if __name__ == "__main__":
    root = tk.Tk()
    
    # Set window icon (optional)
    try:
        root.iconbitmap('icon.ico')
    except:
        pass
    
    app = EnhancedCSVAnalyzerApp(root)
    root.mainloop()