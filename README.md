# 📊 CSV Explorer App

A powerful Streamlit web application for exploring and analyzing CSV files with interactive visualizations and professional PDF reports.

## ✨ Features

- **📈 Data Summary**: Quick overview of dataset structure, statistics, and data types
- **🔍 Smart Filters**: Column selection and row filtering capabilities
- **📊 Interactive Charts**: Bar, Line, Histogram, and Pie charts with colorful visualizations
- **📤 Export Options**: Download filtered CSV data and comprehensive PDF reports
- **🧭 Navigation Menu**: Quick jump to different sections
- **⚡ Performance Optimized**: Works best with datasets under 10,000 rows

## 🚀 Installation

1. Clone the repository:
```bash
git clone https://github.com/DeekshithaRamshetty/csv-explorer.git
cd csv-explorer
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## 💻 Usage

1. Run the application:
```bash
streamlit run app.py
```

2. Open your browser and go to `http://localhost:8501`

3. Upload a CSV file and start exploring!

## 📋 Requirements

- Python 3.7+
- Streamlit >= 1.28.0
- Pandas >= 1.5.0
- Plotly >= 5.15.0
- Matplotlib >= 3.6.0
- FPDF >= 2.7.0
- Kaleido >= 0.2.1

## 🎯 Best Performance

- CSV files with < 1,000 rows and < 20 columns
- File size under 10MB
- Clean data with minimal missing values

## 📊 Chart Types

- **Bar Chart**: Shows frequency distribution of values
- **Line Chart**: Displays value counts as connected points
- **Histogram**: Traditional bins for numeric data, value counts for categorical
- **Pie Chart**: Perfect for categorical data distribution

## 📝 PDF Reports

Generated reports include:
- Executive summary
- Dataset overview
- Key insights
- Column information
- Data visualizations

## 🤝 Contributing

Feel free to open issues and submit pull requests!

## 📄 License

This project is open source and available under the MIT License.