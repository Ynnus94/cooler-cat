# CoolerCat - Translation Quality Framework

A professional tool for reviewing and revising French translations with quality framework error codes.

## Project Structure

```
Notion-Translate/
├── assets/              # Images and static files
│   └── coolercat.webp   # Logo
├── docs/                # Documentation
│   └── [SHARED WITH LINGUISTS] Quality Framework - Notion - Main.pdf
├── jobs/                # Job folders (created automatically when you upload XLF files)
│   └── <job-id>/        # Each job has its own folder
│       ├── *.xlf        # XLF source file
│       ├── revision_table.csv
│       └── revision_table.html
├── index.html           # Main job management interface
├── requirements.txt     # Python dependencies
└── scripts/             # Python scripts
    ├── server.py        # Flask server for job management
    ├── create_revision_table.py  # Extracts translations and applies revisions
    └── create_html_table.py      # Generates the HTML interface
```

**Note:** The old `job/` folder (if present) is legacy and not used by the new system. All jobs are now managed through the `jobs/` folder via the web interface.

## Installation

1. Create a virtual environment and install dependencies:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Usage

### Start the Server

1. Activate the virtual environment and start the CoolerCat server:
```bash
source venv/bin/activate  # On Windows: venv\Scripts\activate
cd scripts
python3 server.py
```

The server will start at `http://localhost:5000`

### Open the Web Interface

2. **Important:** Make sure the server is running! Then:
   - Navigate to `http://localhost:5001` in your browser (recommended)
   - Or open `index.html` directly (server must be running on port 5001)

### Workflow

1. **Upload XLF File**: 
   - Drag and drop an XLF file onto the upload area, or click to browse
   - The file will be automatically processed

2. **View Jobs**:
   - All your jobs are listed on the main page
   - Click "Open" to view the revision table for a job
   - Click "Reprocess" to regenerate the revision table
   - Click "Delete" to remove a job

3. **Review Translations**:
   - View all translations with revisions
   - Filter by error code, state, or search
   - Edit revisions inline
   - Copy revised translations to clipboard
   - See formatted tags and error codes

### Command Line Usage (Alternative)

You can also use the scripts directly:

```bash
cd scripts
python3 create_revision_table.py <xlf_file> <csv_output>
python3 create_html_table.py <csv_file> <html_output> [job_id]
```

## Features

- **Quality Framework Integration**: Automatic error detection with codes (TE-2, TE-0.5, TC-0.5, LQ-0.5, ST-0.5)
- **Style Guide Compliance**: Checks against Enterprise Style Guide rules
- **Tag Preservation**: Maintains formatting tags from XLF
- **Interactive Editing**: Edit revisions directly in the browser
- **Local Storage**: Your edits persist across sessions
- **Export Ready**: Copy revised translations for Matecat

## Error Codes

- **TE-2**: Translation Error - Major (2 points)
- **TE-0.5**: Translation Error - Minor (0.5 points)
- **TC-0.5**: Terminology/Consistency - Minor
- **LQ-0.5**: Language Quality - Minor (Grammar, Punctuation, Spelling)
- **ST-0.5**: Style - Minor

## Resources

### Primary Resources
- **Quality Framework**: `docs/[SHARED WITH LINGUISTS] Quality Framework - Notion - Main.pdf`
- **French Style Guide (Notion)**: https://www.notion.so/notion/Style-Guide-French-France-ef2af5b11a9a4ec79fbadf848111f09c?t=2b2339a8f7ce80c7b2dc00a96954a457
- **Notion Help Center (French - Live Reference)**: https://www.notion.com/fr/help
  - ⚠️ **Important**: Use this as a reference to cross-check terminology and style since it's already live

### Additional Resources
- Style Guide Spreadsheet: https://docs.google.com/spreadsheets/d/1O4mBYna7NDkWr-3vfkOtinIwDbjcRxdF7DZXwQZvHCk
- Notion Glossary: https://notion.notion.site/Notion-Glossary-3a85fe79a5a147c0b6d7ebd55f06ae36

## About

This tool is used for reviewing and revising **French translations for Notion**. Always cross-reference with the live [Notion Help Center (French)](https://www.notion.com/fr/help) to ensure consistency with published content.

