
import pandas as pd
import os
from datetime import datetime
import email
from email import policy
from email.parser import BytesParser

def parse_eml(file_path):
    """Parses a .eml file and extracts relevant information."""
    try:
        with open(file_path, 'rb') as f:
            msg = BytesParser(policy=policy.default).parse(f)
        
        date_str = msg['Date']
        # Use pd.to_datetime for robust date parsing
        timestamp = pd.to_datetime(date_str, errors='coerce')

        if pd.isna(timestamp):
            return None # Skip if date can't be parsed

        details = f"From: {msg['From']}\n"
        details += f"To: {msg['To']}\n"
        details += f"Subject: {msg['Subject']}\n\n"

        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                content_disposition = str(part.get("Content-Disposition"))
                if content_type == 'text/plain' and 'attachment' not in content_disposition:
                    body = part.get_payload(decode=True)
                    details += body.decode('utf-8', errors='ignore')
                    break # Take the first plain text part
        else:
            body = msg.get_payload(decode=True)
            details += body.decode('utf-8', errors='ignore')

        return {
            'timestamp': timestamp,
            'source': os.path.basename(file_path),
            'event_type': 'Email (.eml)',
            'details": details.strip()
        }
    except Exception as e:
        print(f"Error parsing EML file {file_path}: {e}")
        return None

def generate_timeline(sources):
    """
    Generates a chronological timeline from various evidence sources.

    Args:
        sources (list): A list of file paths for the evidence files.

    Returns:
        pandas.DataFrame: A sorted DataFrame representing the timeline.
    """
    timeline_entries = []

    for source in sources:
        print(f"Processing source: {source}")
        if source.lower().endswith('.csv'):
            # ... (CSV processing logic remains the same)
            pass
        elif source.lower().endswith('.eml'):
            eml_event = parse_eml(source)
            if eml_event:
                timeline_entries.append(eml_event)

    if not timeline_entries:
        return pd.DataFrame(columns=['timestamp', 'source', 'event_type', 'details'])

    timeline_df = pd.DataFrame(timeline_entries)
    timeline_df.sort_values(by='timestamp', inplace=True)
    timeline_df.reset_index(drop=True, inplace=True)

    return timeline_df

if __name__ == '__main__':
    # Example Usage with a dummy EML file
    print("Running stand-alone timeline generation example with EML...")

    dummy_eml_content = """
Date: Tue, 17 Jan 2023 14:05:01 -0500
From: "Jane Doe" <jane.doe@example.com>
To: "Craig Schulz" <craig.schulz@example.com>
Subject: Regarding Harper's school project

Hi Craig,

Just wanted to follow up on Harper's science project. She mentioned needing some materials from the garage.

Thanks,
Jane
"""
    dummy_eml_path = 'dummy_email.eml'
    with open(dummy_eml_path, 'w') as f:
        f.write(dummy_eml_content)

    full_timeline = generate_timeline([dummy_eml_path])

    print("\n--- Generated Timeline from EML ---")
    print(full_timeline)

    os.remove(dummy_eml_path)
