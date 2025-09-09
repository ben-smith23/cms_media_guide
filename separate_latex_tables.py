#!/usr/bin/env python3
"""
Script to separate LaTeX tables from generated_latex.tex into three files:
- champs.tex: Championship records
- dual.tex: Dual meet records  
- team.tex: Team records

Based on the sheet names and sex values from the data processing.
"""

import re
import os
import random
import glob

def create_section_mapping():
    """Create mapping from sheet names to target files and sex values."""
    return {
        # Team Records
        'CMS All Time Top 10': 'team',
        'CMS Axelrood Pool Records': 'team', 
        'CMS Frosh Swimming & Diving Records': 'team',
        'Development of Team Records (October 2001 to March 2025)': 'team',
        
        # Dual Meet Records
        'CMS at UCSD': 'dual',
        'CMS at Cal Baptist Distance Meet': 'dual',
        'CMS at PP': 'dual',
        'CMS at PP Combined': 'dual',
        
        # Championship Records
        'CMS SCIAC Champions': 'champs',
        'SCIAC All Time Top 10 Performers': 'champs',
        'SCIAC Records': 'champs',
        'NCAA TOP 20': 'champs'
    }

def get_sex_mapping():
    """Map sex values to LaTeX subsubsection names."""
    return {
        'Athena': 'Athenas',
        'Stag': 'Stags', 
        'Women': 'Women',
        'Men': 'Men'
    }

def get_highlight_images():
    """Get list of all available highlight images."""
    image_path = "/home/ben/Desktop/Projects/media_guide/latex/assets/highlights/Highlights"
    # Get all JPG and HEIC files
    jpg_files = glob.glob(os.path.join(image_path, "*.JPG"))
    jpg_files.extend(glob.glob(os.path.join(image_path, "*.jpg")))
    jpg_files.extend(glob.glob(os.path.join(image_path, "*.HEIC")))
    
    # Convert to relative paths for LaTeX
    relative_paths = []
    for file_path in jpg_files:
        filename = os.path.basename(file_path)
        relative_paths.append(f"../assets/highlights/Highlights/{filename}")
    
    return relative_paths

def create_title_page_latex(section_name, subsection_name, image_path):
    """Create a beautiful title page with LaTeX code."""
    return f"""
\\newpage
\\thispagestyle{{empty}}
\\begin{{center}}
\\vspace*{{1cm}}

% Title section at the top
\\begin{{tikzpicture}}[overlay, remember picture]
    % Semi-transparent background for text
    \\fill[white, opacity=0.9] ($(current page.north) + (-6cm, -2cm)$) rectangle ($(current page.north) + (6cm, -6cm)$);
    
    % Section title
    \\node[anchor=center, text width=12cm, align=center] at ($(current page.north) + (0, -3.5cm)$) {{
        \\fontsize{{36pt}}{{40pt}}\\selectfont\\textbf{{\\textcolor{{teamprimary}}{{{section_name}}}}}
    }};
    
    % Subsection title
    \\node[anchor=center, text width=12cm, align=center] at ($(current page.north) + (0, -4.5cm)$) {{
        \\fontsize{{24pt}}{{28pt}}\\selectfont\\textbf{{\\textcolor{{teamsecondary}}{{{subsection_name}}}}}
    }};
\\end{{tikzpicture}}

% Image below the title
\\vspace*{{4cm}}
\\begin{{tikzpicture}}[overlay, remember picture]
    \\node[anchor=center] at ($(current page.center) + (0, -1cm)$) {{
        \\includegraphics[width=0.6\\textwidth, height=0.5\\textheight, keepaspectratio]{{{image_path}}}
    }};
\\end{{tikzpicture}}

\\vfill
\\end{{center}}
\\clearpage
"""

def extract_sections_from_latex(file_path):
    """Extract all sections from the generated LaTeX file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find all subsection and subsubsection patterns
    sections = []
    
    # Pattern to match subsection and subsubsection with content
    pattern = r'(\\subsection\{[^}]+\})\s*(\\subsubsection\{[^}]+\})\s*(.*?)(?=\\subsection\{|\\end\{document\}|$)'
    
    matches = re.findall(pattern, content, re.DOTALL)
    
    for match in matches:
        subsection = match[0].strip()
        subsubsection = match[1].strip()
        content_section = match[2].strip()
        
        # Extract the section name from \subsection{...}
        section_name = re.search(r'\\subsection\{([^}]+)\}', subsection).group(1)
        
        # Extract the sex from \subsubsection{...}
        sex = re.search(r'\\subsubsection\{([^}]+)\}', subsubsection).group(1)
        
        sections.append({
            'section_name': section_name,
            'sex': sex,
            'subsection': subsection,
            'subsubsection': subsubsection,
            'content': content_section
        })
    
    return sections

def write_section_to_file(sections, target_file, section_mapping, sex_mapping, highlight_images):
    """Write sections to the appropriate target file with artistic title pages."""
    file_sections = []
    
    for section in sections:
        section_name = section['section_name']
        sex = section['sex']
        
        # Check if this section belongs to this target file
        if section_mapping.get(section_name) == target_file:
            file_sections.append(section)
    
    if not file_sections:
        print(f"No sections found for {target_file}.tex")
        return
    
    # Write to file
    output_path = f"/home/ben/Desktop/Projects/media_guide/latex/sections/{target_file}.tex"
    
    with open(output_path, 'w', encoding='utf-8') as f:
        # Write header based on target file
        if target_file == 'champs':
            f.write("\\section{Championship Records}\n\n")
        elif target_file == 'dual':
            f.write("\\section{Dual Meet Records}\n\n")
        elif target_file == 'team':
            f.write("% chktex-file 8\n\n\\section{Team Records}\n\n")
        
        # Group sections by section name
        current_section = None
        for section in file_sections:
            section_name = section['section_name']
            sex = section['sex']
            
            # If this is a new section, write the subsection header
            if current_section != section_name:
                if current_section is not None:
                    f.write("\n")  # Add spacing between sections
                f.write(f"\\subsection{{{section_name}}}\n")
                current_section = section_name
            
            # Create artistic title page for each subsection
            mapped_sex = sex_mapping.get(sex, sex)
            random_image = random.choice(highlight_images)
            title_page = create_title_page_latex(section_name, mapped_sex, random_image)
            f.write(title_page)
            
            # Write the content
            if section['content'].strip():
                f.write(section['content'].strip())
                f.write("\n\n")
    
    print(f"Written {len(file_sections)} sections to {target_file}.tex with artistic title pages")

def main():
    """Main function to separate the LaTeX tables."""
    input_file = "/home/ben/Desktop/Projects/media_guide/latex/sections/generated_latex.tex"
    
    if not os.path.exists(input_file):
        print(f"Error: Input file {input_file} not found!")
        return
    
    print("Extracting sections from generated_latex.tex...")
    sections = extract_sections_from_latex(input_file)
    print(f"Found {len(sections)} sections")
    
    # Get highlight images
    print("Loading highlight images...")
    highlight_images = get_highlight_images()
    print(f"Found {len(highlight_images)} highlight images")
    
    # Create mappings
    section_mapping = create_section_mapping()
    sex_mapping = get_sex_mapping()
    
    # Print mapping for verification
    print("\nSection mapping:")
    for sheet, target in section_mapping.items():
        print(f"  {sheet} -> {target}.tex")
    
    # Write to each target file
    for target_file in ['champs', 'dual', 'team']:
        print(f"\nWriting sections to {target_file}.tex...")
        write_section_to_file(sections, target_file, section_mapping, sex_mapping, highlight_images)
    
    print("\nSeparation complete with artistic title pages!")

if __name__ == "__main__":
    main()
