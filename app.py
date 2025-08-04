import streamlit as st
import pandas as pd
import io
import matplotlib.pyplot as plt
import plotly.express as px
from fpdf import FPDF
import tempfile
import os

# Set layout
st.set_page_config(page_title="CSV Explorer", layout="wide")
st.title("📊 CSV Explorer App")
st.markdown("*Optimized for small to medium datasets*")

# Initialize session state for clearing
if 'clear_data' not in st.session_state:
    st.session_state.clear_data = False

# Reset file uploader when clear is pressed
if st.session_state.clear_data:
    st.session_state.clear_data = False
    uploaded_file = None
else:
    uploaded_file = st.file_uploader("Upload CSV", type=["csv"])

# --- PDF Report Generation ---
def generate_pdf_report(df, stats_df, plot_type=None, plot_col=None, filtered_df=None):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # Title
    pdf.set_font("Arial", 'B', 18)
    pdf.cell(0, 15, "CSV Data Analysis Report", ln=True, align="C")
    pdf.ln(10)

    # Executive Summary
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, "Executive Summary", ln=True)
    pdf.set_font("Arial", '', 11)
    summary = f"This report analyzes a dataset containing {df.shape[0]:,} records across {df.shape[1]} variables. "
    if df.shape[0] > 1000:
        summary += "This is a large dataset suitable for comprehensive analysis."
    elif df.shape[0] > 100:
        summary += "This is a medium-sized dataset with good analytical potential."
    else:
        summary += "This is a small dataset ideal for detailed examination."
    pdf.multi_cell(0, 8, summary)
    pdf.ln(5)

    # Dataset Overview
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, "Dataset Overview", ln=True)
    pdf.set_font("Arial", '', 11)
    pdf.cell(0, 8, f"- Total Records: {df.shape[0]:,}", ln=True)
    pdf.cell(0, 8, f"- Total Variables: {df.shape[1]}", ln=True)
    pdf.cell(0, 8, f"- Missing Values: {df.isnull().sum().sum():,} ({(df.isnull().sum().sum()/(df.shape[0]*df.shape[1])*100):.1f}%)", ln=True)
    
    # Data types summary
    numeric_cols = df.select_dtypes(include=['number']).shape[1]
    text_cols = df.select_dtypes(include=['object']).shape[1]
    pdf.cell(0, 8, f"- Numeric Columns: {numeric_cols}", ln=True)
    pdf.cell(0, 8, f"- Text Columns: {text_cols}", ln=True)
    pdf.ln(5)

    # Key Insights
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, "Key Insights", ln=True)
    pdf.set_font("Arial", '', 11)
    
    # Generate insights based on data
    insights = []
    if numeric_cols > 0:
        numeric_df = df.select_dtypes(include=['number'])
        high_var_cols = [col for col in numeric_df.columns if numeric_df[col].std() > numeric_df[col].mean()]
        if high_var_cols:
            insights.append(f"High variability detected in: {', '.join(high_var_cols[:3])}")
    
    if df.isnull().sum().sum() > 0:
        missing_cols = df.isnull().sum()[df.isnull().sum() > 0].head(3)
        insights.append(f"Columns with missing data: {', '.join(missing_cols.index)}")
    
    if len(insights) == 0:
        insights.append("Dataset appears to be well-structured with consistent data quality.")
    
    for i, insight in enumerate(insights, 1):
        pdf.multi_cell(0, 8, f"- {insight}")
    pdf.ln(5)

    # Column Information
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, "Column Information", ln=True)
    pdf.set_font("Arial", '', 10)
    col_info = "\n".join([f"- {col} ({str(df[col].dtype)})" for col in df.columns[:10]])
    if len(df.columns) > 10:
        col_info += f"\n... and {len(df.columns) - 10} more columns"
    pdf.multi_cell(0, 6, col_info)
    pdf.ln(5)



    # Visualization - Generate only when PDF is created
    if plot_type and plot_col is not None and filtered_df is not None:
        pdf.add_page()
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(0, 15, "Data Visualization", ln=True, align="C")
        pdf.ln(5)
        
        pdf.set_font("Arial", '', 11)
        pdf.multi_cell(0, 8, "The chart below provides a visual representation of the selected data, helping to identify patterns, trends, and outliers that may not be immediately apparent in raw data.")
        pdf.ln(5)
        
        # Generate matplotlib chart only for PDF
        plt.figure(figsize=(10, 6))
        if plot_type == "Bar":
            value_counts = filtered_df[plot_col].value_counts()
            plt.bar(value_counts.index, value_counts.values, color='steelblue', alpha=0.7)
            plt.title(f"Bar Plot of {plot_col}")
            plt.xlabel(plot_col)
            plt.ylabel('Count')
        elif plot_type == "Line":
            value_counts = filtered_df[plot_col].value_counts().sort_index()
            plt.plot(value_counts.index, value_counts.values, color='red', linewidth=2, marker='o')
            plt.title(f"Line Plot of {plot_col}")
            plt.xlabel(plot_col)
            plt.ylabel('Count')
        elif plot_type == "Histogram":
            if pd.api.types.is_numeric_dtype(filtered_df[plot_col]):
                plt.hist(filtered_df[plot_col].dropna(), bins=20, color='green', alpha=0.7)
            else:
                value_counts = filtered_df[plot_col].value_counts()
                plt.bar(value_counts.index, value_counts.values, color='green', alpha=0.7)
                plt.xlabel(plot_col)
                plt.ylabel('Count')
            plt.title(f"Histogram of {plot_col}")
        elif plot_type == "Pie":
            pie_data = filtered_df[plot_col].value_counts()
            plt.pie(pie_data.values, labels=pie_data.index, autopct='%1.1f%%', colors=plt.cm.Set3.colors)
            plt.title(f"Pie Chart of {plot_col}")
        
        plt.tight_layout()
        
        # Save to temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
            plt.savefig(tmp.name, format='png', dpi=200, bbox_inches='tight', facecolor='white')
            tmp_path = tmp.name
        plt.close()
        
        pdf.image(tmp_path, x=15, w=180)
        os.remove(tmp_path)
        
        # Add footer
        pdf.ln(10)
        pdf.set_font("Arial", 'I', 9)
        pdf.multi_cell(0, 6, "Note: This visualization was generated based on the current data selection and filtering criteria applied in the CSV Explorer application.")

    # Footer
    pdf.ln(10)
    pdf.set_font("Arial", 'I', 8)
    pdf.cell(0, 5, f"Report generated by CSV Explorer - {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M')}", ln=True, align="C")
    
    return pdf.output(dest='S').encode('latin-1', errors='replace')


if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    
    # Dataset size warning and navigation
    if df.shape[0] > 10000:
        st.warning("⚠️ This app works best with smaller datasets (<10,000 rows). Large datasets may cause performance issues.")
    
    # Navigation menu
    st.markdown("""
    ### 🧭 Quick Navigation
    - [📊 Data Summary](#data-summary)
    - [🔍 Filters](#filters)
    - [📈 Visualizations](#visualizations) 
    - [📤 Export Options](#export-options)
    """)
    
   
    
    st.subheader("📌 Dataset Preview")
    st.dataframe(df.head(10), use_container_width=True)

    # --- Summary Section ---
    st.markdown('<a name="data-summary"></a>', unsafe_allow_html=True)
    st.markdown("### 📊 Data Summary")
    col1, col2 = st.columns(2)
    with col1:
        st.write("**Shape:**", df.shape)
        st.write("**Columns:**", list(df.columns))
        st.write("**Missing Values:**", df.isnull().sum())
        st.write("**Data Types:**")
        st.dataframe(df.dtypes.astype(str))
    with col2:
        st.write("**Descriptive Statistics:**")
        stats_df = df.describe(include='all')
        st.dataframe(stats_df, use_container_width=True)

    st.markdown("---")
    st.markdown('<a name="filters"></a>', unsafe_allow_html=True)
    st.subheader("🔍 Filter Columns & Rows")
    columns = st.multiselect("Select columns to display", df.columns.tolist(), default=df.columns.tolist())
    filtered_df = df[columns]

    filter_expander = st.expander("Row Filter Options")
    with filter_expander:
        filter_col = st.selectbox("Select column to filter", columns)
        if pd.api.types.is_numeric_dtype(filtered_df[filter_col]):
            min_val, max_val = st.slider(
                f"Select range for {filter_col}",
                float(filtered_df[filter_col].min()),
                float(filtered_df[filter_col].max()),
                (float(filtered_df[filter_col].min()), float(filtered_df[filter_col].max()))
            )
            filtered_df = filtered_df[(filtered_df[filter_col] >= min_val) & (filtered_df[filter_col] <= max_val)]
        else:
            unique_vals = filtered_df[filter_col].dropna().unique().tolist()
            selected_vals = st.multiselect(f"Select values for {filter_col}", unique_vals, default=unique_vals)
            filtered_df = filtered_df[filtered_df[filter_col].isin(selected_vals)]

    st.dataframe(filtered_df.head(50), use_container_width=True)

    st.markdown("---")
    st.markdown('<a name="visualizations"></a>', unsafe_allow_html=True)
    st.subheader("📈 Visualizations")
    plot_type = st.selectbox("Select plot type", ["Bar", "Line", "Histogram", "Pie"])
    
    plot_col = st.selectbox("Select column to plot", columns)

    fig = None
    plotly_bytes = None

    try:
        if plot_col is not None:
            if plot_type == "Bar":
                value_counts = filtered_df[plot_col].value_counts().reset_index()
                value_counts.columns = [plot_col, 'count']
                fig = px.bar(value_counts, x=plot_col, y='count', title=f"Bar Plot of {plot_col}", color_discrete_sequence=px.colors.qualitative.Set3)
            elif plot_type == "Line":
                value_counts = filtered_df[plot_col].value_counts().sort_index().reset_index()
                value_counts.columns = [plot_col, 'count']
                fig = px.line(value_counts, x=plot_col, y='count', title=f"Line Plot of {plot_col}", color_discrete_sequence=['#1f77b4'])
            elif plot_type == "Histogram":
                if pd.api.types.is_numeric_dtype(filtered_df[plot_col]):
                    fig = px.histogram(filtered_df, x=plot_col, title=f"Histogram of {plot_col}", color_discrete_sequence=['#ff7f0e'])
                else:
                    value_counts = filtered_df[plot_col].value_counts().reset_index()
                    value_counts.columns = [plot_col, 'count']
                    fig = px.bar(value_counts, x=plot_col, y='count', title=f"Histogram of {plot_col}", color_discrete_sequence=['#ff7f0e'])
            elif plot_type == "Pie":
                st.markdown("**Note:** Pie charts are best for categorical data.")
                pie_data = filtered_df[plot_col].value_counts().reset_index()
                pie_data.columns = [plot_col, 'count']
                fig = px.pie(pie_data, names=plot_col, values='count', title=f"Pie Chart of {plot_col}", color_discrete_sequence=px.colors.qualitative.Pastel)

            st.plotly_chart(fig, use_container_width=True)
            plotly_bytes = fig.to_image(format="png", width=800, height=600)
            st.download_button(
                label="📥 Download Plot as PNG",
                data=plotly_bytes,
                file_name="plot.png",
                mime="image/png"
            )
    except Exception as e:
        st.warning(f"Could not plot: {e}")

    st.markdown("---")
    st.markdown('<a name="export-options"></a>', unsafe_allow_html=True)
    st.subheader("📤 Export Options")

    csv_buffer = io.StringIO()
    filtered_df.to_csv(csv_buffer, index=False)
    st.download_button(
        label="📥 Download Filtered CSV",
        data=csv_buffer.getvalue(),
        file_name="filtered_data.csv",
        mime="text/csv"
    )

    pdf_bytes = generate_pdf_report(filtered_df, stats_df, plot_type, plot_col, filtered_df)
    st.download_button(
        label="📝 Download PDF Report",
        data=pdf_bytes,
        file_name="csv_report.pdf",
        mime="application/pdf"
    )
else:
    st.info("📂 Please upload a CSV file to get started.")
    st.markdown("""
    ### 📝 About CSV Explorer
    This tool is **optimized for smaller datasets** (under 10,000 rows) and provides:
    - 📊 **Data Summary**: Quick overview of your dataset structure
    - 🔍 **Smart Filters**: Column and row filtering capabilities  
    - 📈 **Interactive Charts**: Bar, line, histogram, and pie charts
    - 📤 **Export Options**: Download filtered data and PDF reports
    
    **Best Performance**: CSV files with < 1,000 rows and < 20 columns
    """)
