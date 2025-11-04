
import streamlit as st
import pandas as pd
import re
import os

@st.cache_data
def load_exhibit_data():
    """
    Parses the CUSTODY_COURT_EXHIBITS.txt file and returns a pandas DataFrame.
    This function is cached to ensure the data is loaded only once.
    """
    try:
        with open('CUSTODY_COURT_EXHIBITS.txt', 'r', encoding='utf-8') as f:
            file_content = f.read()
    except FileNotFoundError:
        # The calling function should handle this error
        return pd.DataFrame()

    exhibits = []
    current_category = "Uncategorized"
    current_folder = "Uncategorized"
    seen_exhibits = set()

    lines = file_content.splitlines()
    for i, line in enumerate(lines):
        line = line.strip()
        if not line:
            continue

        category_match = re.match(r'^(.* EVIDENCE):$', line, re.IGNORECASE)
        if category_match:
            category_title = category_match.group(1).title().replace(''S', 's')
            current_category = category_title
            continue

        folder_match = re.match(r'📁 FOLDER: (.*)', line)
        if folder_match:
            current_folder = folder_match.group(1)
            continue

        file_match = re.match(r'📄 (.*)', line)
        if file_match:
            try:
                filename = file_match.group(1)
                context = lines[i+1].strip().replace('Context: ', '')
                from_who = lines[i+2].strip().replace('From: ', '')
                score_str = lines[i+3].strip().replace('Score: ', '')
                score = float(score_str)

                exhibit_key = (current_folder, filename, context)
                if exhibit_key in seen_exhibits:
                    continue
                seen_exhibits.add(exhibit_key)

                exhibits.append({
                    'Category': current_category,
                    'Folder': current_folder,
                    'File': filename,
                    'Score': score,
                    'Context': context,
                    'Source': from_who,
                    'Path': os.path.join(current_folder, filename).replace('\\', '/')
                })
            except (IndexError, ValueError):
                pass

    df = pd.DataFrame(exhibits)
    if not df.empty:
        df['Exhibit ID'] = [f"A-{i+1}" for i in range(len(df))]
        df.set_index('Exhibit ID', inplace=True)
    return df
