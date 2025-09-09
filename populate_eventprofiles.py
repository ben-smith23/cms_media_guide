#!/usr/bin/env python3
"""
Script to populate eventprofiles.tex with data from Excel files:
- SCIAC Event Profiles Updated 04.1.25.xlsx
- NCAA Event Profiles updated 4.1.25.xlsx

Each Excel file has two sheets: men and women.
"""

import pandas as pd
import os
import re
from pathlib import Path

def read_excel_file(file_path, sheet_name):
    """Read an Excel file and return the data from a specific sheet."""
    try:
        df = pd.read_excel(file_path, sheet_name=sheet_name)
        print(f"Successfully read {sheet_name} sheet from {os.path.basename(file_path)}")
        print(f"Shape: {df.shape}")
        print(f"Columns: {list(df.columns)}")
        print(f"First few rows:\n{df.head()}")
        print("-" * 50)
        return df
    except Exception as e:
        print(f"Error reading {sheet_name} sheet from {file_path}: {e}")
        return None

def examine_excel_structure():
    """Examine the structure of both Excel files to understand the data format."""
    base_path = "/home/ben/Desktop/Projects/media_guide/cms_media_guide/raw_25_data"
    csv_output_path = "/home/ben/Desktop/Projects/media_guide/cms_media_guide/processed_data"
    
    # Create output directory if it doesn't exist
    os.makedirs(csv_output_path, exist_ok=True)
    
    files = [
        "SCIAC Event Profiles Updated 04.1.25.xlsx",
        "NCAA Event Profiles updated 4.1.25.xlsx"
    ]
    
    sheets = ["men", "women"]
    
    for file_name in files:
        file_path = os.path.join(base_path, file_name)
        print(f"\n=== Examining {file_name} ===")
        
        if not os.path.exists(file_path):
            print(f"File not found: {file_path}")
            continue
            
        for sheet in sheets:
            print(f"\n--- Sheet: {sheet} ---")
            df = read_excel_file(file_path, sheet)
            if df is not None:
                # Try to identify the structure
                print(f"Data types:\n{df.dtypes}")
                print(f"Non-null counts:\n{df.count()}")
                
                # Save as CSV
                csv_filename = f"{file_name.replace('.xlsx', '')}_{sheet}.csv"
                csv_path = os.path.join(csv_output_path, csv_filename)
                df.to_csv(csv_path, index=False)
                print(f"Saved CSV: {csv_path}")

def create_latex_content_from_data(df, event_type, gender):
    """Create LaTeX content from DataFrame data."""
    if df is None or df.empty:
        return f"% No data available for {event_type} {gender}\n"
    
    latex_content = []
    
    # Skip the header rows and process the actual data
    # The data starts from row 5 (index 4) where we have the column headers
    if len(df) < 5:
        return f"% Insufficient data for {event_type} {gender}\n"
    
    # Get the column headers from row 4 (index 4)
    headers = df.iloc[4].tolist()
    
    # Process each event starting from row 5 (index 5)
    current_event = None
    event_data = []
    
    for i in range(5, len(df)):
        row = df.iloc[i]
        
        # Check if this is a new event (first column has event name)
        if pd.notna(row.iloc[0]) and row.iloc[0].strip():
            # Save previous event if exists
            if current_event and event_data:
                latex_content.extend(create_event_latex(current_event, event_data, headers))
            
            # Start new event
            current_event = row.iloc[0].strip()
            event_data = []
        
        # Add year data for current event
        if pd.notna(row.iloc[1]):  # Year column
            year = int(row.iloc[1]) if pd.notna(row.iloc[1]) else None
            if year:
                event_data.append({
                    'year': year,
                    'prelims': {
                        '1st': row.iloc[2] if pd.notna(row.iloc[2]) else '',
                        '8th': row.iloc[3] if pd.notna(row.iloc[3]) else '',
                        '9th': row.iloc[4] if pd.notna(row.iloc[4]) else '',
                        '16th': row.iloc[5] if pd.notna(row.iloc[5]) else ''
                    },
                    'finals': {
                        '1st': row.iloc[7] if pd.notna(row.iloc[7]) else '',
                        '8th': row.iloc[8] if pd.notna(row.iloc[8]) else '',
                        '9th': row.iloc[9] if pd.notna(row.iloc[9]) else '',
                        '16th': row.iloc[10] if pd.notna(row.iloc[10]) else ''
                    }
                })
    
    # Don't forget the last event
    if current_event and event_data:
        latex_content.extend(create_event_latex(current_event, event_data, headers))
    
    return "\n".join(latex_content)

def create_event_latex(event_name, event_data, headers):
    """Create LaTeX content for a specific event."""
    latex_content = []
    
    latex_content.append(f"\\textbf{{{event_name}}}")
    latex_content.append("")
    
    # Create a table for this event with coloring
    latex_content.append("\\begin{flushleft}")
    latex_content.append("\\begin{tabular}{|>{\\columncolor{blue!20}}c|c|c|c|c|c|c|c|c|}")
    latex_content.append("\\hline")
    latex_content.append("\\rowcolor{blue!30}")
    latex_content.append("Year & \\multicolumn{4}{c|}{Prelims} & \\multicolumn{4}{c|}{Finals} \\\\")
    latex_content.append("\\cline{2-9}")
    latex_content.append("\\rowcolor{blue!30}")
    latex_content.append("& 1st & 8th & 9th & 16th & 1st & 8th & 9th & 16th \\\\")
    latex_content.append("\\hline")
    
    # Add data rows with alternating colors
    for i, data in enumerate(event_data):
        year = data['year']
        prelims = data['prelims']
        finals = data['finals']
        
        # Alternate row colors
        if i % 2 == 0:
            latex_content.append("\\rowcolor{gray!10}")
        else:
            latex_content.append("\\rowcolor{white}")
        
        row = f"{year} & {prelims['1st']} & {prelims['8th']} & {prelims['9th']} & {prelims['16th']} & {finals['1st']} & {finals['8th']} & {finals['9th']} & {finals['16th']} \\\\"
        latex_content.append(row)
    
    latex_content.append("\\hline")
    latex_content.append("\\end{tabular}")
    latex_content.append("\\end{flushleft}")
    latex_content.append("")
    
    return latex_content

def populate_eventprofiles_tex():
    """Main function to populate the eventprofiles.tex file."""
    csv_base_path = "/home/ben/Desktop/Projects/media_guide/cms_media_guide/processed_data"
    output_path = "/home/ben/Desktop/Projects/media_guide/latex/sections/eventprofiles.tex"
    
    # File mappings for CSV files
    files = {
        "SCIAC": "SCIAC Event Profiles Updated 04.1.25",
        "NCAA": "NCAA Event Profiles updated 4.1.25"
    }
    
    # Start building the LaTeX content
    latex_content = []
    latex_content.append("\\section{Event Profiles}")
    latex_content.append("")
    
    for event_type, file_prefix in files.items():
        latex_content.append(f"\\subsection{{{event_type}s}}")
        latex_content.append("")
        
        for gender in ["men", "women"]:
            latex_content.append(f"\\subsubsection{{{gender.title()}}}")
            latex_content.append("")
            
            # Read the CSV data
            csv_file = f"{file_prefix}_{gender}.csv"
            csv_path = os.path.join(csv_base_path, csv_file)
            
            if not os.path.exists(csv_path):
                print(f"Warning: CSV file not found: {csv_path}")
                latex_content.append(f"% No data available for {event_type} {gender}")
                latex_content.append("")
                continue
            
            try:
                df = pd.read_csv(csv_path)
                print(f"Successfully read {csv_file}")
                
                # Create LaTeX content from the data
                content = create_latex_content_from_data(df, event_type, gender)
                latex_content.append(content)
                
            except Exception as e:
                print(f"Error reading {csv_file}: {e}")
                latex_content.append(f"% Error reading data for {event_type} {gender}")
                latex_content.append("")
    
    # Write to file
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("\n".join(latex_content))
    
    print(f"\nEvent profiles written to: {output_path}")

def main():
    """Main function."""
    print("=== Event Profiles Data Extractor ===")
    print("This script will populate eventprofiles.tex with data from CSV files")
    print()
    
    # Check if CSV files exist, if not, create them first
    csv_base_path = "/home/ben/Desktop/Projects/media_guide/cms_media_guide/processed_data"
    csv_files = [
        "SCIAC Event Profiles Updated 04.1.25_men.csv",
        "SCIAC Event Profiles Updated 04.1.25_women.csv", 
        "NCAA Event Profiles updated 4.1.25_men.csv",
        "NCAA Event Profiles updated 4.1.25_women.csv"
    ]
    
    missing_files = []
    for csv_file in csv_files:
        if not os.path.exists(os.path.join(csv_base_path, csv_file)):
            missing_files.append(csv_file)
    
    if missing_files:
        print("Step 1: Creating CSV files from Excel...")
        examine_excel_structure()
        print()
    
    print("Step 2: Populating eventprofiles.tex...")
    populate_eventprofiles_tex()
    
    print("\nScript completed!")
    print("Please examine the output and let me know what adjustments are needed.")

if __name__ == "__main__":
    main()
