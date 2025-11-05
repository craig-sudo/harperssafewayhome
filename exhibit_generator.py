
import re
import os

def generate_exhibit_book():
    # Read the data file
    try:
        with open('CUSTODY_COURT_EXHIBITS.txt', 'r', encoding='utf-8') as f:
            file_content = f.read()
    except FileNotFoundError:
        print("Error: CUSTODY_COURT_EXHIBITS.txt not found.")
        return

    # Parse the data
    exhibits = []
    current_category = None
    current_folder = None
    seen_exhibits = set()

    lines = file_content.splitlines()
    for i, line in enumerate(lines):
        line = line.strip()
        if not line:
            continue

        category_match = re.match(r'^(.* Beweise):$', line, re.IGNORECASE) or re.match(r'^(.* EVIDENCE):$', line, re.IGNORECASE)
        if category_match:
            category_title = category_match.group(1)
            current_category = category_title.replace(' BEHAVIOR EVIDENCE', '').replace(' ABUSE EVIDENCE', '').replace(' VIOLATIONS EVIDENCE', '').replace(' ISSUES EVIDENCE', '').strip()
            continue

        folder_match = re.match(r'📁 FOLDER: (.*)', line)
        if folder_match:
            current_folder = folder_match.group(1)
            continue

        file_match = re.match(r'📄 (.*)', line)
        if file_match and current_category and current_folder:
            filename = file_match.group(1)
            # Create a unique key for each exhibit to handle duplicates
            exhibit_key = (current_folder, filename, lines[i+1].strip())
            if exhibit_key in seen_exhibits:
                continue
            seen_exhibits.add(exhibit_key)

            try:
                context = lines[i+1].strip().replace('Context: ', '')
                from_who = lines[i+2].strip().replace('From: ', '')
                score = lines[i+3].strip().replace('Score: ', '')
                
                exhibits.append({
                    'id': f"A-{len(exhibits) + 1}",
                    'category': current_category,
                    'folder': current_folder,
                    'filename': filename,
                    'path': os.path.join(current_folder, filename).replace('\\', '/'),
                    'context': context,
                    'from': from_who,
                    'score': score
                })
            except IndexError:
                # In case there are not enough lines after the filename
                pass

    # Start generating the HTML
    html = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>FDSJ-739-24 Exhibit Book</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
        body { font-family: 'Inter', sans-serif; background-color: #f7f7f7; }
        .document-page {
            width: 8.5in;
            min-height: 11in;
            margin: 0 auto 1rem;
            padding: 1in;
            background: white;
            box-shadow: 0 0 8px rgba(0, 0, 0, 0.1);
            position: relative;
        }
        @media print {
            .no-print { display: none !important; }
            body { background: white !important; }
            .document-page { box-shadow: none; margin: 0; padding: 1in; }
        }
        .jurant-text { font-size: 10pt; line-height: 1.5; text-transform: uppercase; }
        .file-number-header { position: absolute; top: 0.5in; right: 0.5in; font-size: 10pt; font-weight: 600; }
        .break-before-page { page-break-before: always; }
    </style>
</head>
<body class="p-8">

    <div class="no-print mb-8 p-4 bg-white rounded-lg shadow-lg max-w-4xl mx-auto">
        <h1 class="text-2xl font-bold text-gray-800">Exhibit Book Generator</h1>
        <p class="text-sm text-gray-600 mb-4">Generated from CUSTODY_COURT_EXHIBITS.txt</p>
        <button onclick="window.print()" class="bg-indigo-600 hover:bg-indigo-700 text-white font-bold py-2 px-4 rounded transition duration-200">
            Print to PDF
        </button>
    </div>

    <div id="output" class="max-w-4xl mx-auto">
        <!-- Cover Sheet -->
        <div class="document-page text-center flex flex-col justify-center items-center">
            <p class="file-number-header">COURT FILE NO.: FDSJ-739-24</p>
            <h1 class="text-3xl font-extrabold text-gray-800 mt-20">EXHIBIT BOOK OF THE RESPONDENT</h1>
            <h2 class="text-xl font-bold mt-2">CRAIG SCHULZ</h2>
            <h3 class="text-lg mt-8">FILED IN SUPPORT OF CLAIM FOR PARENTING ORDER (FORM 81B)</h3>
            <p class="mt-12 text-gray-600">Date Filed: NOVEMBER 6, 2025</p>
        </div>

        <!-- Master Exhibit List -->
        <div class="document-page">
            <p class="file-number-header">COURT FILE NO.: FDSJ-739-24</p>
            <h2 class="text-2xl font-bold mb-4">Master Exhibit List</h2>
            <table class="w-full table-fixed border-collapse">
                <thead>
                    <tr class="bg-gray-100 border-b-2">
                        <th class="w-1/12 p-2 text-left text-xs font-medium uppercase">Exhibit No.</th>
                        <th class="w-5/12 p-2 text-left text-xs font-medium uppercase">Description of Evidence</th>
                        <th class="w-3/12 p-2 text-left text-xs font-medium uppercase">Category</th>
                        <th class="w-3/12 p-2 text-left text-xs font-medium uppercase">File Path</th>
                    </tr>
                </thead>
                <tbody>
    '''

    # Add TOC rows
    for exhibit in exhibits:
        html += f'''
                    <tr class="border-b">
                        <td class="p-2 text-sm font-semibold">{exhibit['id']}</td>
                        <td class="p-2 text-sm">{exhibit['context']}</td>
                        <td class="p-2 text-sm">{exhibit['category']}</td>
                        <td class="p-2 text-sm font-mono">{exhibit['path']}</td>
                    </tr>
        '''

    html += '''
                </tbody>
            </table>
        </div>
    '''

    # Jurat function
    def generate_jurat(exhibit_id):
        return f'''
            <div class="jurant-text border-b border-gray-400 pb-2 mb-4">
                <p class="font-bold">COURT FILE NO.: FDSJ-739-24</p>
                <p class="mt-4">THIS IS EXHIBIT **"{exhibit_id}"**</p>
                <p>REFERRED TO IN THE AFFIDAVIT OF CRAIG SCHULZ SWORN BEFORE ME THIS **6th day of NOVEMBER, 2025**</p>
            </div>
            <div class="flex justify-between text-xs mt-10">
                <p>_________________________________________</p>
                <p>_________________________________________</p>
            </div>
            <div class="flex justify-between text-xs mb-8">
                <p>A COMMISSIONER FOR OATHS IN AND FOR THE PROVINCE OF NEW BRUNSWICK</p>
                <p>COMMISSION EXPIRES: (Insert Date)</p>
            </div>
        '''

    # Individual Exhibit Pages
    for exhibit in exhibits:
        html += f'''
        <div class="document-page break-before-page">
            <p class="file-number-header">COURT FILE NO.: FDSJ-739-24</p>
            {generate_jurat(exhibit['id'])}

            <h3 class="text-lg font-bold mt-10 mb-4">EXHIBIT {exhibit['id']} - {exhibit['category']}</h3>
            <div class="border p-4 bg-gray-50 text-sm">
                <p class="font-semibold mb-2">FILE: {exhibit['path']}</p>
                <p class="mb-2"><strong>CONTENT SUMMARY:</strong> {exhibit['context']}</p>
                <p class="mt-4 text-xs text-gray-700">FROM: <span class="font-mono">{exhibit['from']}</span></p>
                <p class="mt-4 text-xs text-gray-700">RELEVANCE SCORE: <span class="font-mono">{exhibit['score']}</span></p>
            </div>
            
            <div class="mt-8 border border-gray-300 p-8 text-center text-gray-500 italic h-48 flex items-center justify-center">
                <img src="{exhibit['path']}" alt="{exhibit['filename']}" style="max-height: 100%; max-width: 100%;" onerror="this.parentElement.innerHTML = '[Image not found for &quot;{exhibit['path']}&quot;]';">
            </div>
        </div>
        '''

    html += '''
    </div>
</body>
</html>
    '''

    # Write the HTML file
    with open('public/index.html', 'w', encoding='utf-8') as f:
        f.write(html)
    
    print("Successfully generated public/index.html")

if __name__ == "__main__":
    generate_exhibit_book()
