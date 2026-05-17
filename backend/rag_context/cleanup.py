import pandas as pd
import re
import json

def clean_vido_data(input_file, output_txt, output_jsonl):
    # Read the file and find the header line
    with open(input_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Find the line that starts with "Class ID"
    header_index = None
    for i, line in enumerate(lines):
        if line.strip().startswith("Class ID"):
            header_index = i
            break
    
    if header_index is None:
        print("Error: Could not find header line starting with 'Class ID'")
        return
    
    header_line = lines[header_index]
    
    # Find positions of target columns
    col_positions = {}
    for col in ['Preferred Label', 'Definitions', 'Synonyms']:
        pos = header_line.find(col)
        if pos != -1:
            col_positions[col] = pos
    
    if not col_positions:
        print("Error: Could not find target columns in header")
        return
    
    # Define colspecs for read_fwf
    colspecs = []
    sorted_cols = sorted(col_positions.items(), key=lambda x: x[1])
    for i, (col, pos) in enumerate(sorted_cols):
        start = pos
        end = sorted_cols[i+1][1] if i+1 < len(sorted_cols) else None
        colspecs.append((start, end))
    
    # Read the data using fixed width
    df = pd.read_fwf(input_file, colspecs=colspecs, skiprows=header_index + 1, names=[col for col, _ in sorted_cols], engine='python')
    
    clean_entries = []

    with open(output_txt, 'w', encoding='utf-8') as txt_file:
        for _, row in df.iterrows():
            label = str(row.get('Preferred Label', '')).strip()
            definition = str(row.get('Definitions', '')).strip()
            
            # Skip rows that are empty or just 'nan'
            if label.lower() == 'nan' or not label:
                continue

            # Remove URLs and brackets often found in ontology exports
            clean_def = re.sub(r'http\S+', '', definition)
            clean_def = re.sub(r'\[.*?\]', '', clean_def).strip()
            
            # Split on 'false' to get only the definition part
            clean_def = clean_def.split('false')[0].strip()
            
            # Truncate to reduce token waste
            if len(clean_def) > 200:
                clean_def = clean_def[:200] + '...'

            if clean_def and clean_def.lower() != 'nan':
                # Format for Semantic Search TXT
                line = f"Concept: {label}\nDefinition: {clean_def}\n\n"
                txt_file.write(line)
                
                # Format for Tuning (JSONL)
                clean_entries.append({
                    "input": f"Explain the viral pathogenesis concept: {label}",
                    "output": clean_def
                })

    # Save JSONL for watsonx Tuning Studio
    with open(output_jsonl, 'w', encoding='utf-8') as j_file:
        for entry in clean_entries:
            j_file.write(json.dumps(entry) + '\n')

    print(f"Success! Cleaned data saved to {output_txt} and {output_jsonl}")

# Usage
clean_vido_data('VIDO.txt', 'VIDO_Clean_Search.txt', 'VIDO_Training.jsonl')