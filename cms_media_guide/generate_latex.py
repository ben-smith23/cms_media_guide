#!/usr/bin/env python3
"""
CMS Media Guide LaTeX Generator
Generates LaTeX tables from swimming/diving data with direct LaTeX code (no macros)
"""

import pandas as pd
import numpy as np

# Define the proper event order
EVENT_ORDER = [
    # Free
    '50 Free', '100 Free', '200 Free', '500 Free', '1000 Free', '1650 Free',
    # Back
    '50 Back', '100 Back', '200 Back', '300 Back',
    # Breast
    '50 Breast', '100 Breast', '200 Breast', '300 Breast',
    # Fly
    '100 Fly', '200 Fly', '300 Fly',
    # IM
    '200 IM', '300 IM', '400 IM',
    # DIVING (Meter)
    '1-Meter (6 dives)', '1-Meter (11 dives)', '1-Meter',
    '3-Meter (6 dives)', '3-Meter (11 dives)', '3-Meter',
    # Relay
    '200 Free Relay', '400 Free Relay', '500 Free Relay- (50-100-150-200)',
    '800 Free Relay', '200 Medley Relay', '400 Medley Relay',
    '500 Medley Relay - (200 Back-150 BR-100 FL-50 FS)',
    # Spl.
    '50 Free - Relay Spl.', '50 Free Spl.', '100 Free - Relay Spl.',
    '100 Free Spl.', '200 Free - Relay Spl.', '200 Free Spl.',
    '50 Back - Relay Spl.', '50 Back Spl.', '50 Breast - Relay Spl.',
    '50 Breast Spl.', '100 Breast - Relay Spl.', '100 Breast Spl.',
    '50 Fly - Relay Spl.', '50 Fly Spl.', '100 Fly - Relay Spl.', '100 Fly Spl.'
]

def escape_latex_special_chars(text):
    """Escape special LaTeX characters in text"""
    if pd.isna(text):
        return ''
    text_str = str(text)
    # Escape ampersands for LaTeX
    text_str = text_str.replace('&', '\\&')
    return text_str

def safe_year_conversion(year_value):
    """Convert year value to string, handling date formats"""
    if pd.isna(year_value):
        return ''
    
    year_str = str(year_value)
    
    # Handle date formats like '11.11.16' or '11/11/16'
    if '.' in year_str or '/' in year_str:
        parts = year_str.replace('/', '.').split('.')
        if len(parts) >= 3:
            year_part = parts[-1]
            if len(year_part) == 2:
                year_part = '20' + year_part
            return year_part
    
    try:
        return str(int(float(year_str)))
    except (ValueError, TypeError):
        return year_str

def detect_available_columns(data_subset):
    """Detect which columns have data and return list of available columns"""
    available_columns = []
    
    # Check TIME column - only include if it has valid data
    if data_subset['TIME'].notna().all() and (data_subset['TIME'] != 'nan').all():
        available_columns.append('TIME')
    
    # Check each optional column for data - only include if ALL rows have valid data
    if data_subset['NAME'].notna().all() and (data_subset['NAME'] != 'nan').all() and (data_subset['NAME'] != '').all():
        available_columns.append('NAME')
    if data_subset['YEAR'].notna().all() and (data_subset['YEAR'] != 'nan').all():
        available_columns.append('YEAR')
    if 'TEAM' in data_subset.columns and data_subset['TEAM'].notna().all() and (data_subset['TEAM'] != 'nan').all() and (data_subset['TEAM'] != '').all():
        available_columns.append('TEAM')
    if 'SITE' in data_subset.columns and data_subset['SITE'].notna().all() and (data_subset['SITE'] != 'nan').all() and (data_subset['SITE'] != '').all():
        available_columns.append('SITE')
    if 'MEET' in data_subset.columns and data_subset['MEET'].notna().all() and (data_subset['MEET'] != 'nan').all() and (data_subset['MEET'] != '').all():
        available_columns.append('MEET')
    if 'CONTEXT' in data_subset.columns and data_subset['CONTEXT'].notna().all() and (data_subset['CONTEXT'] != 'nan').all() and (data_subset['CONTEXT'] != '').all():
        available_columns.append('CONTEXT')
    
    return available_columns


def safe_get_column(row, column_name, default=''):
    """Safely get column value, handling missing columns and NaN values"""
    if column_name not in row.index:
        return default
    value = row[column_name]
    if pd.isna(value) or value == 'nan':
        return default
    return str(value)

def sort_events_by_order(events):
    """Sort events according to the predefined EVENT_ORDER"""
    event_order_dict = {event: i for i, event in enumerate(EVENT_ORDER)}
    
    def event_sort_key(event):
        # If event is in our predefined order, use that position
        if event in event_order_dict:
            return event_order_dict[event]
        # Otherwise, put it at the end
        return len(EVENT_ORDER)
    
    return sorted(events, key=event_sort_key)

def generate_direct_latex_table(event_name, event_data):
    """Generate direct LaTeX table content (just the tabular, no wrapper)"""
    
    # Sort data appropriately
    if "diving" in event_name.lower() or "meter" in event_name.lower():
        event_data_sorted = event_data.sort_values('TIME', ascending=False)
    else:
        event_data_sorted = event_data.sort_values('TIME', ascending=True)
    
    # Get available columns
    available_columns = detect_available_columns(event_data_sorted)
    
    # Define column headers based on available columns
    headers = []
    column_spec = "@{}"
    
    if 'TIME' in available_columns:
        # Check if this is a diving event (contains "meter" or "Meter")
        if "meter" in event_name.lower() or "Meter" in event_name:
            headers.append("\\textbf{Score}")
        else:
            headers.append("\\textbf{Time}")
        column_spec += "p{1.2cm}"
    
    if 'NAME' in available_columns:
        headers.append("\\textbf{Name}")
        column_spec += "p{1.8cm}"
    
    if 'YEAR' in available_columns:
        headers.append("\\textbf{Year}")
        column_spec += "p{0.6cm}"
    
    if 'SITE' in available_columns:
        headers.append("\\textbf{Site}")
        column_spec += "p{0.8cm}"
    
    if 'TEAM' in available_columns:
        headers.append("\\textbf{Team}")
        column_spec += "p{0.8cm}"
    
    if 'MEET' in available_columns:
        headers.append("\\textbf{Meet}")
        column_spec += "p{0.8cm}"
    
    if 'CONTEXT' in available_columns:
        headers.append("\\textbf{Context}")
        column_spec += "p{1.2cm}"
    
    column_spec += "@{}"
    
    # Build table rows dynamically
    table_rows = []
    for _, row in event_data_sorted.iterrows():
        row_parts = []
        
        for col in available_columns:
            if col == 'TIME':
                row_parts.append(safe_get_column(row, 'TIME', ''))
            elif col == 'NAME':
                row_parts.append(safe_get_column(row, 'NAME', ''))
            elif col == 'YEAR':
                row_parts.append(safe_year_conversion(row['YEAR']))
            elif col == 'TEAM':
                row_parts.append(escape_latex_special_chars(safe_get_column(row, 'TEAM', '')))
            elif col == 'SITE':
                row_parts.append(escape_latex_special_chars(safe_get_column(row, 'SITE', '')))
            elif col == 'MEET':
                row_parts.append(escape_latex_special_chars(safe_get_column(row, 'MEET', '')))
            elif col == 'CONTEXT':
                row_parts.append(escape_latex_special_chars(safe_get_column(row, 'CONTEXT', '')))
        
        table_row = " & ".join(row_parts)
        table_rows.append(table_row)
    
    # Join rows with \\ - ALL rows need \\ including the last one
    if len(table_rows) > 1:
        table_content = " \\\\\n".join(table_rows) + " \\\\"
    else:
        table_content = table_rows[0] + " \\\\"
    
    # Return just the table content
    latex_table = f"""\\centering
\\tiny
\\renewcommand{{\\arraystretch}}{{0.75}}
\\setlength{{\\tabcolsep}}{{2pt}}
\\resizebox{{\\textwidth}}{{!}}{{
\\begin{{tabular}}{{{column_spec}}}
\\toprule
{(' & '.join(headers))} \\\\
\\midrule
{table_content}
\\bottomrule
\\end{{tabular}}%
}}"""
    
    return latex_table

def generate_complete_latex(df):
    """Generate complete LaTeX for all data"""
    
    latex_content = []
    latex_content.append("% ===== CMS MEDIA GUIDE - GENERATED LATEX =====")
    latex_content.append("% This file contains all swimming and diving tables")
    latex_content.append("% Generated automatically from ordered_times.csv")
    latex_content.append("")
    
    # Get all unique sheet/sex combinations
    combinations = df.groupby(['SHEET', 'SEX']).size().reset_index()
    
    print(f"=== GENERATING LATEX FOR {len(combinations)} SECTIONS ===")
    
    current_section = None
    
    for _, row in combinations.iterrows():
        sheet_name = row['SHEET']
        sex_name = row['SEX']
        
        # Filter data for this section
        section_data = df[(df['SHEET'] == sheet_name) & (df['SEX'] == sex_name)]
        
        if len(section_data) == 0:
            continue
            
        # Add section header if this is a new section
        if current_section != sheet_name:
            if current_section is not None:
                latex_content.append("\\vspace{-0.5em}")
            # Escape special characters in sheet name for LaTeX
            escaped_sheet_name = escape_latex_special_chars(sheet_name)
            latex_content.append("\\clearpage")
            latex_content.append(f"\\section{{{escaped_sheet_name}}}")
            current_section = sheet_name
        
        # Add subsection for sex
        latex_content.append("\\clearpage")
        latex_content.append(f"\\subsection{{{sex_name}}}")
        latex_content.append("\\vspace{-0.3em}")
        
        # Group by event and generate tables
        events = sort_events_by_order(section_data['EVENT'].unique())
        
        # Collect all events as (name, content) tuples
        all_events = []
        for event in events:
            event_data = section_data[section_data['EVENT'] == event]
            event_latex = generate_direct_latex_table(event, event_data)
            all_events.append((event, event_latex))
        
        # Output events in pairs (side by side)
        for i in range(0, len(all_events), 2):
            latex_content.append("\\vspace{0.8em}")
            
            if i + 1 < len(all_events):
                # Two events side by side
                latex_content.append("\\noindent\\begin{minipage}[t]{0.48\\textwidth}")
                latex_content.append("\\centering")
                latex_content.append(f"\\textbf{{\\textcolor{{teamprimary}}{{{all_events[i][0]}}}}}\\par")
                latex_content.append("\\vspace{0.5em}")
                latex_content.append(all_events[i][1])
                latex_content.append("\\end{minipage}")
                latex_content.append("\\hfill")
                latex_content.append("\\begin{minipage}[t]{0.48\\textwidth}")
                latex_content.append("\\centering")
                latex_content.append(f"\\textbf{{\\textcolor{{teamprimary}}{{{all_events[i+1][0]}}}}}\\par")
                latex_content.append("\\vspace{0.5em}")
                latex_content.append(all_events[i+1][1])
                latex_content.append("\\end{minipage}")
            else:
                # Single event
                latex_content.append("\\noindent\\begin{minipage}[t]{0.98\\textwidth}")
                latex_content.append("\\centering")
                latex_content.append(f"\\textbf{{\\textcolor{{teamprimary}}{{{all_events[i][0]}}}}}\\par")
                latex_content.append("\\vspace{0.5em}")
                latex_content.append(all_events[i][1])
                latex_content.append("\\end{minipage}")
        
        print(f"Generated: {sheet_name} - {sex_name} ({len(events)} events)")
    
    return "\n".join(latex_content)

def main():
    """Main function to generate LaTeX file"""
    
    # Load the data
    print("Loading data...")
    df = pd.read_csv('cms_media_guide/processed_data/ordered_times.csv')
    print(f"Loaded {len(df)} records")
    
    # Generate LaTeX
    print("Starting LaTeX generation...")
    complete_latex = generate_complete_latex(df)
    
    # Save to file
    output_file = "latex/sections/generated_latex.tex"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(complete_latex)
    
    print(f"\n=== LATEX GENERATION COMPLETE ===")
    print(f"Generated {len(complete_latex)} characters")
    print(f"Saved to: {output_file}")
    print(f"File size: {len(complete_latex)} characters")
    
    # Show a preview
    print(f"\n=== PREVIEW (first 1000 characters) ===")
    print(complete_latex[:1000] + "..." if len(complete_latex) > 1000 else complete_latex)

if __name__ == "__main__":
    main()
