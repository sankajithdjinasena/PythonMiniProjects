# CSV Data Analyzer

A Python desktop application that enables users to upload a CSV file and perform instant data analysis through an interactive graphical interface.
The application provides insights such as summary statistics, missing value detection, duplicate record identification, and outlier analysis, all implemented using Tkinter for the user interface and Pandas for data processing.

---

## 🚀 Features

### Data Managememnt

- Load CSV and Excel files
- Real-time data preview
- Memory usage tracking
- Multiple export formats (CSV, Excel, JSON)

### Data Cleaning

- Missing value handling (mean, median, mode, forward/backward fill)
- Outlier detection and removal (IQR method)
- Duplicate row removal
- Column-wise data imputation

### Data Visualization

- Interactive charts: Histogram, Box Plot, Scatter Plot, Line Chart, Bar Chart, Pie Chart
- Customizable X/Y axis selection
- Save charts as PNG, PDF, or SVG
- Real-time statistical overlays

### Statistical Analysis

- Comprehensive descriptive statistics
- Correlation analysis
- Data type distribution
- Normality testing
- Time series analysis
- Hypothesis testing

### User Interface

- Modern sidebar navigation
- Dashboard with key metrics
- Responsive layout
- Custom message dialogs
- Progress indicators
- Hover effects and animations

---

## 🛠 Technologies Used

- Python 3
- Tkinter (GUI)
- Pandas (Data analysis)

---

## Installation

#### 1. Clone the repository
```bash
git clone https://github.com/sankajithdjinasena/python_mini_project/csv_analyzer.git
cd csv-analyzer-pro
```

#### 2. Install dependencies
```bash 
pip install -r requirements.txt
```

#### 3. Run application
```bash
python app.py
```

## 📂 Project Structure

```text
├── CSV_Analyzer/
   ├── README.md
   ├── CSV analyzer.bat
   └── app.py
```

## Usage Guide

### 1. Loading Data

- Click "📁 Load Data" in the sidebar
- Select a CSV or Excel file
- View dataset overview in the dashboard

### 2. Data Cleaning

- Navigate to "🧹 Data Cleaning"
- Select a column from the dropdown
- Choose a cleaning method:
    - Mean/Median/Mode Imputation: Fill missing values
    - Drop Rows: Remove rows with missing values
    - Forward/Backward Fill: Propagate values
    - Remove Outliers: Eliminate statistical outliers
    - Remove Duplicates: Delete duplicate rows

### 3. Data Visualization

- Go to "📈 Visualizations"
- Select chart type from dropdown
- Choose X-axis and Y-axis columns
- Click "Generate Chart"
- Save chart using "💾 Save Chart" button

### 4. Statistical Analysis

- Open "📊 Statistics" panel
- View comprehensive statistics in three tabs:
    - Column Details: Data types, missing values, unique counts
    - Numerical Statistics: Mean, median, std, quartiles
    - Overall Statistics: Dataset summary and distributions

### 5. Exporting Data

- Click "💾 Export Data" in sidebar
- Choose format (CSV, Excel, JSON)
- Select save location
- View export confirmation with details

## Advanced Features

### Custom Message Dialogs
- The application features custom-styled message boxes with:
- Success messages (green checkmarks ✅)
- Warning messages (yellow exclamation ⚠️)
- Error messages (red X ❌)
- Question dialogs with Yes/No options

### Real-time Dashboard
- Live metrics display
- Quick action buttons
- Data preview
- Memory usage monitoring

### Column Type Detection
- Automatic detection of numeric, text, and date columns
- Intelligent filtering for appropriate chart types
- Type indicators in dropdowns

## Limitations / Future Improvements

- Currently supports CSV files only
- Large files may take longer to process
- Future: add Excel support, charts, filters, export to PDF

## License / Academic Note

Depending on use:
- “This project is for educational purposes”
- Or an open-source license (MIT)

### <i>Thank you<i>