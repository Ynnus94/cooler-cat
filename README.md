# CoolerCat - Translation Quality Framework

A professional, AI-powered tool for reviewing and revising French translations for Notion. CoolerCat combines automated quality checks, AI-powered revision suggestions, and an intuitive web interface to streamline the translation review process.

## 🎯 What We're Building

CoolerCat is designed to solve the challenge of reviewing large volumes of French translations efficiently while maintaining high quality standards. The tool:

1. **Processes XLIFF (XLF) files** from translation platforms like Matecat
2. **Extracts existing revisions** that are already present in the XLF files (XLF revisions)
3. **Generates AI-powered revision suggestions** using built-in knowledge of French translation rules, Notion style guides, and quality frameworks
4. **Provides an interactive web interface** for reviewing, filtering, and editing translations
5. **Tracks quality issues** using a standardized error code system (TE-2, TE-0.5, TC-0.5, LQ-0.5, ST-0.5)

## 🏗️ Architecture Overview

### Core Components

```
┌─────────────────────────────────────────────────────────────┐
│                    Web Interface (index.html)                │
│  • Job management dashboard                                  │
│  • Interactive translation table with filtering             │
│  • Clickable stat cards for quick filtering                 │
│  • Inline editing with local storage persistence             │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       │ HTTP API
                       │
┌──────────────────────▼──────────────────────────────────────┐
│              Flask Server (scripts/server.py)                │
│  • File upload handling                                      │
│  • Job processing orchestration                              │
│  • API endpoints for CRUD operations                         │
└──────┬──────────────────┬──────────────────┬────────────────┘
       │                  │                  │
       │                  │                  │
┌──────▼──────┐  ┌───────▼──────┐  ┌───────▼──────┐
│ XLF Parser  │  │ AI Revision   │  │ HTML Generator│
│ (create_    │  │ (ai_revision  │  │ (create_html  │
│  revision_   │  │  .py)         │  │  _table.py)   │
│  table.py)   │  │               │  │               │
│              │  │               │  │               │
│ • Extracts   │  │ • Rule-based │  │ • Generates   │
│   segments   │  │   revision    │  │   interactive │
│ • Preserves  │  │ • Quality     │  │   table       │
│   tags       │  │   framework   │  │ • Diff        │
│ • Extracts   │  │   codes       │  │   highlighting│
│   XLF        │  │ • Style guide │  │ • Responsive   │
│   revisions  │  │   compliance │  │   design      │
└──────────────┘  └──────────────┘  └───────────────┘
```

## 📁 Project Structure

```
Notion-Translate/
├── assets/                    # Frontend assets
│   ├── css/style.css         # Notion-inspired styling
│   ├── js/app.js             # Main application logic
│   └── *.webp                # Optimized images (coolcat, proudcat, etc.)
│
├── docs/                      # Documentation and resources
│   ├── resources/            # Style guides, glossaries, learning journals (PDFs/CSVs)
│   ├── knowledge_base_resources.md  # Documentation of integrated resources
│   └── style_guide_french.md        # Extracted French style guide
│
├── jobs/                      # Job storage (auto-created)
│   └── <job-id>/             # Each job folder
│       ├── *.xlf             # Original XLF source file
│       ├── revision_table.csv    # Processed data
│       └── progress.json     # AI revision progress tracking
│
├── scripts/                   # Python backend
│   ├── server.py             # Flask API server
│   ├── create_revision_table.py  # XLF parsing
│   ├── ai_revision.py        # AI-powered revision (Gemini)
│   └── create_html_table.py  # HTML generator (legacy)
│
├── knowledge_base.txt         # AI knowledge base (style guide, glossary, rules)
├── index.html                 # Main web interface (SPA)
├── requirements.txt           # Python dependencies
└── README.md                  # This file
```

## 🚀 Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Setup

1. **Clone or download the repository**

2. **Create a virtual environment** (recommended):
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**:
```bash
pip install -r requirements.txt
```

## 💻 Usage

### Starting the Server

1. **Activate the virtual environment** (if not already active):
```bash
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. **Start the Flask server**:
```bash
cd scripts
python3 server.py
```

You should see:
```
🚀 Starting CoolerCat Translation Server...
📁 Jobs directory: /path/to/Notion-Translate/jobs
🌐 Server running at http://localhost:5001
```

### Opening the Web Interface

**Important:** The server must be running!

- Navigate to `http://localhost:5001` in your browser (recommended)
- The interface will automatically load and connect to the server

### Complete Workflow

#### 1. Upload XLF File

- **Drag and drop** an XLF file onto the upload area, or **click to browse**
- The file is automatically uploaded and processed
- A new job is created with a unique ID
- Processing includes:
  - Extracting all translation segments
  - Parsing existing XLF revisions (if present)
  - Preserving formatting tags
  - Generating the initial revision table

#### 2. View Job Dashboard

The main page displays:
- **All jobs** in a card-based layout
- **Job metadata**: filename, creation date, file size
- **Quick actions**: Open, Reprocess, Delete, Revise

#### 3. Open a Job

Click on a job card (or the "Open" button) to view the translation table:

**Translation Table Features:**
- **Statistics Cards** (clickable filters):
  - Total Translations
  - AI Revisions ✨ (purple)
  - XLF Revisions 📄 (teal/cyan)
  - With Error Codes (orange)
  - Major Errors (TE-2) (orange)

- **Dual Revision System**:
  - **XLF Revisions**: Revisions already present in the XLF file (from Matecat reviewers)
  - **AI Revisions**: AI-generated suggestions based on quality framework rules

- **Columns**:
  - ID Matecat: Unique segment identifier
  - State: Translation state (translated, reviewed, final, etc.)
  - Source: Original English text
  - Target: Original translation
  - 📄 XLF Revision: Revisions from XLF file
  - ✨ AI Revision: AI-generated revision suggestions
  - Code: Quality framework error codes
  - Comment: Detailed explanations of issues

#### 4. Filter and Search

**Clickable Stat Cards:**
- Click any stat card to filter the table instantly
- Click again to clear the filter
- Visual indicator shows which filter is active

**Advanced Filters:**
- **Filter by Code**: TE-2, TE-0.5, TC-0.5, LQ-0.5, ST-0.5
- **Filter by State**: translated, reviewed, final, draft, new
- **ID Range**: Filter by Matecat ID range (e.g., 4778127503 to 4778127875)
- **Search**: Full-text search across source, target, and revisions
- **Show only revisions**: Toggle to show only segments with revisions

#### 5. AI Revision

Click the **"Revise"** button to run AI-powered revision on all segments:

**AI Revision Process:**
- Analyzes each translation segment individually
- Applies quality framework rules:
  - **TE-2**: Major translation errors (mistranslations, missing negation)
  - **TE-0.5**: Minor translation errors (grammar issues)
  - **TC-0.5**: Terminology/consistency issues
  - **LQ-0.5**: Language quality (punctuation, spelling, grammar)
  - **ST-0.5**: Style guide compliance
- Checks against Notion French Style Guide
- Detects common issues:
  - Missing non-breaking spaces before punctuation
  - Anglicisms
  - Informal "tu" instead of formal "vous"
  - Repetitions
  - Person-first language violations
  - Capitalization errors

**AI Revision Output:**
- Revised text in the "✨ AI Revision" column
- Error codes automatically assigned
- Detailed comments explaining issues
- Diff highlighting showing exact changes

#### 6. Review and Edit

**Inline Editing:**
- Click the **Edit** button on any revision cell
- Make changes directly in the browser
- Click **Save** to store your edits
- Edits are saved to browser local storage (persist across sessions)
- **Copy** button copies the revised text to clipboard

**Visual Features:**
- **Diff highlighting**: See exactly what changed between original and AI revision
- **Color coding**: 
  - Purple for AI revisions
  - Teal/Cyan for XLF revisions
  - Orange for error codes
- **Tag preservation**: Formatting tags from XLF are preserved and displayed

#### 7. Export and Use

- **Copy revised translations** to clipboard
- Paste directly into Matecat or your translation platform
- All formatting tags are preserved
- Error codes and comments help track quality metrics

## 🎨 Key Features

### 1. Dual Revision System

**XLF Revisions** (Teal/Cyan):
- Revisions already present in the XLF file
- Typically from human reviewers in Matecat
- Preserved exactly as they appear in the source file

**AI Revisions** (Purple):
- AI-generated suggestions based on:
  - Quality framework rules
  - Notion French Style Guide
  - Common translation patterns
  - Terminology consistency

### 2. Quality Framework Integration

Automatic error detection and classification:

- **TE-2**: Translation Error - Major (2 points)
  - Mistranslations
  - Missing negation
  - Meaning reversals

- **TE-0.5**: Translation Error - Minor (0.5 points)
  - Grammar issues
  - Agreement errors

- **TC-0.5**: Terminology/Consistency (0.5 points)
  - Wrong terminology
  - Inconsistent translations

- **LQ-0.5**: Language Quality (0.5 points)
  - Punctuation errors
  - Spelling mistakes
  - Grammar issues

- **ST-0.5**: Style (0.5 points)
  - Style guide violations
  - Tone issues
  - Formality level

### 3. Interactive Web Interface

**Modern UI/UX:**
- Clean, minimalist design (better than shadcn)
- Responsive layout
- Smooth animations and transitions
- Color-coded visual hierarchy
- Clickable stat cards for instant filtering
- Inline editing with auto-save
- Local storage persistence

**Filtering Capabilities:**
- Click stat cards to filter instantly
- Combine multiple filters
- ID range filtering for specific segments
- Full-text search
- Real-time filter updates

### 4. Tag Preservation

- All formatting tags from XLF are preserved
- Tags are displayed in a readable format
- Tags are maintained when copying revisions
- Compatible with Matecat tag system

### 5. Job Management

- **Upload**: Drag & drop or browse for XLF files
- **Reprocess**: Regenerate revision table if needed
- **Delete**: Remove jobs you no longer need
- **Rename**: Change job filenames
- **Auto-processing**: Jobs are processed automatically on upload

## 📊 Error Codes Reference

| Code | Category | Points | Description |
|------|----------|--------|-------------|
| **TE-2** | Translation Error - Major | 2.0 | Major mistranslations, meaning reversals, missing critical negation |
| **TE-0.5** | Translation Error - Minor | 0.5 | Minor translation errors, grammar issues, agreement problems |
| **TC-0.5** | Terminology/Consistency | 0.5 | Wrong terminology, inconsistent translations across segments |
| **LQ-0.5** | Language Quality | 0.5 | Punctuation, spelling, grammar issues |
| **ST-0.5** | Style | 0.5 | Style guide violations, tone issues, formality problems |

## 📚 Resources

### Primary Resources

- **Quality Framework**: `docs/[SHARED WITH LINGUISTS] Quality Framework - Notion - Main.pdf`
  - Complete quality framework documentation
  - Error code definitions and examples
  - Scoring system

- **French Style Guide (Notion)**: https://www.notion.so/notion/Style-Guide-French-France-ef2af5b11a9a4ec79fbadf848111f09c
  - Official Notion French style guide
  - Terminology guidelines
  - Tone and voice standards

- **Notion Help Center (French - Live Reference)**: https://www.notion.com/fr/help
  - ⚠️ **Important**: Use this as a reference to cross-check terminology and style
  - Shows how translations are used in production
  - Helps ensure consistency with published content

### Additional Resources

- **Style Guide Spreadsheet**: https://docs.google.com/spreadsheets/d/1O4mBYna7NDkWr-3vfkOtinIwDbjcRxdF7DZXwQZvHCk
  - Detailed style guide in spreadsheet format
  - Searchable terminology database

- **Notion Glossary**: https://notion.notion.site/Notion-Glossary-3a85fe79a5a147c0b6d7ebd55f06ae36
  - Official terminology glossary
  - Consistent term usage

## 🔧 Technical Details

### API Endpoints

The Flask server provides the following REST API:

- `GET /api/jobs` - List all jobs
- `POST /api/jobs` - Upload and create a new job
- `GET /api/jobs/<job_id>` - Get job details
- `GET /api/jobs/<job_id>/data` - Get job CSV data as JSON
- `POST /api/jobs/<job_id>/process` - Reprocess a job
- `POST /api/jobs/<job_id>/revise` - Run AI revision on a job
- `DELETE /api/jobs/<job_id>` - Delete a job

### Data Flow

1. **Upload**: XLF file → Server → Job folder created
2. **Processing**: XLF file → Parser → CSV with XLF revisions
3. **AI Revision**: CSV → AI Engine → Updated CSV with AI revisions
4. **Display**: CSV → JSON API → Web interface → Interactive table

### File Formats

- **XLF (XLIFF)**: Standard translation file format
- **CSV**: Intermediate data format (revision_table.csv)
- **JSON**: API response format
- **HTML**: Web interface (single-page application)

## 🎯 Use Cases

### 1. Quality Review Workflow

1. Upload XLF file from Matecat
2. Review existing XLF revisions
3. Run AI revision to catch additional issues
4. Filter by error codes to focus on critical issues
5. Edit revisions inline
6. Copy revised translations back to Matecat

### 2. Terminology Consistency Check

1. Upload multiple XLF files
2. Use search to find specific terms
3. Check for consistent translations
4. Use TC-0.5 filter to find terminology issues
5. Standardize terminology across files

### 3. Style Guide Compliance

1. Run AI revision to check style compliance
2. Filter by ST-0.5 to see style issues
3. Review AI suggestions
4. Apply corrections
5. Export for use in Matecat

### 4. Quality Metrics Tracking

1. View stat cards for overview
2. Filter by error codes to see distribution
3. Track major errors (TE-2) separately
4. Monitor revision rates

## 🐛 Troubleshooting

### Server Issues

**Server won't start?**
- Make sure Flask is installed: `pip install -r requirements.txt`
- Check if port 5001 is already in use (port 5000 is often used by AirPlay on macOS)
- Try a different port by modifying `server.py`

**Can't connect to server?**
- Verify the server is running: check terminal output
- Make sure you're accessing `http://localhost:5001` (not 5000)
- Check firewall settings

### File Upload Issues

**Can't upload files?**
- Make sure the server is running
- Check browser console for errors (F12)
- Verify the file is a valid `.xlf` or `.xlf.xlf` file
- Check file size (very large files may take time)

**Upload fails silently?**
- Check server logs in terminal
- Verify `jobs/` directory is writable
- Check disk space

### Display Issues

**Jobs not showing?**
- Refresh the page
- Check that the server is running
- Look at server logs for errors
- Verify jobs exist in `jobs/` directory

**Table not loading?**
- Check browser console for JavaScript errors
- Verify CSV file exists in job folder
- Try reprocessing the job

**Filters not working?**
- Clear browser cache
- Check browser console for errors
- Try refreshing the page

## 🔄 Command Line Usage (Alternative)

You can also use the scripts directly without the web interface:

```bash
# Extract translations and XLF revisions
cd scripts
python3 create_revision_table.py <xlf_file> <csv_output>

# Run AI revision
python3 ai_revision.py <input_csv> <output_csv>

# Generate HTML table (legacy)
python3 create_html_table.py <csv_file> <html_output> [job_id]
```

## 📝 Notes

- **Local Storage**: Your edits are saved in browser local storage and persist across sessions
- **No Database**: All data is stored in the `jobs/` directory as files
- **No External APIs**: AI revision uses built-in knowledge, no API keys needed
- **Offline Capable**: Once loaded, the interface works offline (except for server API calls)

## 🎨 Design Philosophy

CoolerCat follows a "unicorn grade" design philosophy:
- **No gradients**: Clean, solid colors
- **Subtle shadows**: Modern depth without overdoing it
- **Color-coded**: Visual hierarchy through color
- **Responsive**: Works on all screen sizes
- **Fast**: Optimized assets (WebP), efficient rendering
- **Accessible**: High contrast, readable text

## 🤝 Contributing

This is a specialized tool for Notion's French translation workflow. For questions or improvements, please refer to the project maintainers.

## 📄 License

Internal tool for Notion translation quality assurance.

---

**About**: CoolerCat is used for reviewing and revising **French translations for Notion**. Always cross-reference with the live [Notion Help Center (French)](https://www.notion.com/fr/help) to ensure consistency with published content.
