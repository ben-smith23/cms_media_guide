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

def generate_direct_latex_table(event_name, event_data, is_wide_sheet=False, sheet_name=""):
    """Generate direct LaTeX table content (just the tabular, no wrapper)"""
    
    # Sort data appropriately
    if "diving" in event_name.lower() or "meter" in event_name.lower():
        event_data_sorted = event_data.sort_values('TIME', ascending=False)
    else:
        event_data_sorted = event_data.sort_values('TIME', ascending=True)
    
    # Get available columns
    available_columns = detect_available_columns(event_data_sorted)
    
    # Check if this is a full relay event
    is_full_relay = "relay" in event_name.lower() and "spl" not in event_name.lower()
    
    # Define column headers based on available columns
    headers = []
    column_spec = "@{}"
    
    # Check sheet-specific needs
    is_development_records = "development of team records" in sheet_name.lower() if sheet_name else False
    is_sciac_records = "sciac records" in sheet_name.lower() if sheet_name else False
    is_cms_pp_combined = "cms at pp combined" in sheet_name.lower() if sheet_name else False
    is_cms_all_time = "cms all time top 10" in sheet_name.lower() if sheet_name else False
    is_axelrood = "axelrood" in sheet_name.lower() if sheet_name else False
    
    # Determine column width tier
    if is_development_records:
        # Very narrow for development of team records
        width_tier = "very_narrow"
    elif is_full_relay and (is_sciac_records or is_cms_pp_combined or is_cms_all_time or is_axelrood):
        # These sheets' relays use narrow columns
        width_tier = "narrow"
    elif is_full_relay:
        # All other relay tables get extra wide columns
        width_tier = "extra_wide"
    elif is_wide_sheet:
        # Wide for full-width sheets
        width_tier = "wide"
    else:
        # Normal for side-by-side tables
        width_tier = "normal"
    
    if 'TIME' in available_columns:
        # Check if this is a diving event (contains "meter" or "Meter")
        if "meter" in event_name.lower() or "Meter" in event_name:
            headers.append("\\textbf{Score}")
        else:
            headers.append("\\textbf{Time}")
        widths = {"extra_wide": "p{4.5cm}", "wide": "p{2.5cm}", "narrow": "p{2.7cm}", "very_narrow": "p{2.0cm}", "normal": "p{1.8cm}"}
        column_spec += widths[width_tier]
    
    if 'NAME' in available_columns:
        headers.append("\\textbf{Name}")
        widths = {"extra_wide": "p{8.5cm}", "wide": "p{4.5cm}", "narrow": "p{4.3cm}", "very_narrow": "p{3.2cm}", "normal": "p{3.0cm}"}
        column_spec += widths[width_tier]
    
    if 'YEAR' in available_columns:
        headers.append("\\textbf{Year}")
        widths = {"extra_wide": "p{2.5cm}", "wide": "p{1.5cm}", "narrow": "p{1.6cm}", "very_narrow": "p{1.2cm}", "normal": "p{1.0cm}"}
        column_spec += widths[width_tier]
    
    if 'SITE' in available_columns:
        headers.append("\\textbf{Site}")
        widths = {"extra_wide": "p{4.5cm}", "wide": "p{2.5cm}", "narrow": "p{2.7cm}", "very_narrow": "p{2.0cm}", "normal": "p{1.5cm}"}
        column_spec += widths[width_tier]
    
    if 'TEAM' in available_columns:
        headers.append("\\textbf{Team}")
        widths = {"extra_wide": "p{4.5cm}", "wide": "p{2.5cm}", "narrow": "p{2.7cm}", "very_narrow": "p{2.0cm}", "normal": "p{1.5cm}"}
        column_spec += widths[width_tier]
    
    if 'MEET' in available_columns:
        headers.append("\\textbf{Meet}")
        widths = {"extra_wide": "p{4.5cm}", "wide": "p{2.5cm}", "narrow": "p{2.7cm}", "very_narrow": "p{2.0cm}", "normal": "p{1.5cm}"}
        column_spec += widths[width_tier]
    
    if 'CONTEXT' in available_columns:
        headers.append("\\textbf{Context}")
        widths = {"extra_wide": "p{5.0cm}", "wide": "p{3.0cm}", "narrow": "p{3.2cm}", "very_narrow": "p{2.5cm}", "normal": "p{2.0cm}"}
        column_spec += widths[width_tier]
    
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
    
    # Return table content without resizebox
    latex_table = f"""\\centering
\\small
\\renewcommand{{\\arraystretch}}{{1.0}}
\\setlength{{\\tabcolsep}}{{4pt}}
\\begin{{tabular}}{{{column_spec}}}
\\toprule
{(' & '.join(headers))} \\\\
\\midrule
{table_content}
\\bottomrule
\\end{{tabular}}"""
    
    return latex_table

def sanitize_filename(name):
    """Convert sheet name to valid filename"""
    # Replace spaces and special characters with underscores
    filename = name.lower()
    filename = filename.replace(' & ', '_and_')
    filename = filename.replace('&', '_and_')
    filename = filename.replace(' ', '_')
    filename = filename.replace('-', '_')
    filename = filename.replace('(', '')
    filename = filename.replace(')', '')
    filename = filename.replace('.', '')
    filename = filename.replace(',', '')
    return filename

def generate_complete_latex(df):
    """Generate complete LaTeX for all data - creates separate files per section"""
    
    # Get all unique sheet names
    sheets = df['SHEET'].unique()
    
    print(f"=== GENERATING LATEX FOR {len(sheets)} SECTIONS ===")
    
    section_files = []
    
    for sheet_name in sheets:
        # Filter data for this sheet
        sheet_data = df[df['SHEET'] == sheet_name]
        
        if len(sheet_data) == 0:
            continue
        
        # Create filename for this section
        filename = sanitize_filename(sheet_name) + '.tex'
        section_files.append(filename)
        
        latex_content = []
        latex_content.append(f"% ===== {sheet_name} =====")
        latex_content.append("% Generated automatically from ordered_times.csv")
        latex_content.append("")
        
        # Escape special characters in sheet name for LaTeX
        escaped_sheet_name = escape_latex_special_chars(sheet_name)
        latex_content.append("\\clearpage")
        latex_content.append(f"\\section{{{escaped_sheet_name}}}")
        
        # Get unique sex values for this sheet
        sex_values = sheet_data['SEX'].unique()
        
        for sex_name in sex_values:
            # Filter data for this subsection
            section_data = sheet_data[sheet_data['SEX'] == sex_name]
            
            if len(section_data) == 0:
                continue
            
            # Add subsection for sex
            latex_content.append("\\clearpage")
            latex_content.append(f"\\subsection{{{sex_name}}}")
            
            # Group by event and generate tables
            events = sort_events_by_order(section_data['EVENT'].unique())
            
            # Check if this sheet should use full-width tables only
            full_width_sheets = [
                'CMS at PP combined',
                'development of team records',
                'NCAA top 20',
                'SCIAC All Time Top 10 Performers',
                'SCIAC records',
                'CMS Axelrood Pool Records'
            ]
            use_full_width = any(sheet.lower() in sheet_name.lower() for sheet in full_width_sheets)
            
            # Separate full relays from other events
            relay_events = []
            minipage_events = []
            
            for event in events:
                # Check if this is a full relay (not a relay split)
                is_full_relay = "relay" in event.lower() and "spl" not in event.lower()
                if is_full_relay:
                    relay_events.append(event)
                else:
                    minipage_events.append(event)
            
            # Collect minipage events as (name, content) tuples
            all_events = []
            for event in minipage_events:
                event_data = section_data[section_data['EVENT'] == event]
                event_latex = generate_direct_latex_table(event, event_data, is_wide_sheet=use_full_width, sheet_name=sheet_name)
                all_events.append((event, event_latex))
            
            # Output events - full-width for special sheets, side-by-side for others
            if use_full_width:
                # Output all events as single full-width minipages
                for idx, (event_name, event_latex) in enumerate(all_events):
                    latex_content.append("\\vspace{1.2em}")
                    latex_content.append("\\noindent\\begin{minipage}[t]{0.98\\textwidth}")
                    latex_content.append("\\centering")
                    latex_content.append(f"\\textbf{{\\textcolor{{teamprimary}}{{{event_name}}}}}\\par")
                    latex_content.append("\\vspace{0.5em}")
                    latex_content.append(event_latex)
                    latex_content.append("\\end{minipage}")
            else:
                # Output events in pairs (side by side)
                for i in range(0, len(all_events), 2):
                    latex_content.append("\\vspace{1.2em}")
                    
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
                    
                    # Add extra spacing after the first row
                    if i == 0:
                        latex_content.append("\\vspace{0.3em}")
            
            # Output full relay events as single full-width minipages
            for event in relay_events:
                event_data = section_data[section_data['EVENT'] == event]
                event_latex = generate_direct_latex_table(event, event_data, is_wide_sheet=use_full_width, sheet_name=sheet_name)
                
                latex_content.append("\\vspace{1.2em}")
                latex_content.append("\\noindent\\begin{minipage}[t]{0.98\\textwidth}")
                latex_content.append("\\centering")
                latex_content.append(f"\\textbf{{\\textcolor{{teamprimary}}{{{event}}}}}\\par")
                latex_content.append("\\vspace{0.5em}")
                latex_content.append(event_latex)
                latex_content.append("\\end{minipage}")
            
            print(f"Generated: {sheet_name} - {sex_name} ({len(events)} events)")
        
        # Write this section to its own file
        output_file = f"latex/sections/{filename}"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("\n".join(latex_content))
        print(f"  Saved to: {output_file}")
    
    return section_files

def main():
    """Main function to generate LaTeX files"""
    
    # Load the data
    print("Loading data...")
    df = pd.read_csv('cms_media_guide/processed_data/ordered_times.csv')
    print(f"Loaded {len(df)} records")
    
    # Generate LaTeX files
    print("Starting LaTeX generation...")
    section_files = generate_complete_latex(df)
    
    print(f"\n=== LATEX GENERATION COMPLETE ===")
    print(f"Generated {len(section_files)} section files")
    
    # Update main.tex with the new section includes
    main_tex_path = "latex/main/main.tex"
    with open(main_tex_path, 'r', encoding='utf-8') as f:
        main_content = f.read()
    
    # Find the line with generated_latex.tex and replace it with all section files
    lines = main_content.split('\n')
    new_lines = []
    for line in lines:
        if 'generated_latex.tex' in line:
            # Replace with all section file includes
            for section_file in section_files:
                new_lines.append(f"\\input{{../sections/{section_file}}}")
        else:
            new_lines.append(line)
    
    # Write updated main.tex
    with open(main_tex_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(new_lines))
    
    print(f"Updated {main_tex_path} with {len(section_files)} section includes")
    print("\nGenerated sections:")
    for section_file in section_files:
        print(f"  - {section_file}")

if __name__ == "__main__":
    main()
