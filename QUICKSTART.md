# Quick Start Guide

## 1. Install Dependencies

```bash
pip install -r requirements.txt
```

## 2. Start the Server

```bash
cd scripts
python3 server.py
```

You should see:
```
🚀 Starting CoolerCat Translation Server...
📁 Jobs directory: /path/to/jobs
🌐 Server running at http://localhost:5001
```

## 3. Open the Interface

**Important:** The server must be running! Then open:
- Navigate to `http://localhost:5001` in your browser (recommended)
- Or open `index.html` directly (but make sure the server is running on port 5001)

## 4. Upload Your First XLF File

1. Drag and drop an XLF file onto the upload area, or click to browse
2. Wait for processing (you'll see a loading screen)
3. Click "Open" on your job to view the revision table

## Features

- **Upload XLF files** - Drag & drop or click to browse
- **View all jobs** - See all your translation jobs in one place
- **Open jobs** - Click "Open" to view the revision table
- **Reprocess** - Regenerate the revision table if needed
- **Delete** - Remove jobs you no longer need

## Troubleshooting

**Server won't start?**
- Make sure Flask is installed: `pip install -r requirements.txt`
- Check if port 5001 is already in use (port 5000 is often used by AirPlay on macOS)

**Can't upload files?**
- Make sure the server is running
- Check browser console for errors
- Verify the file is a valid .xlf or .xlf.xlf file

**Jobs not showing?**
- Refresh the page
- Check that the server is running
- Look at server logs for errors

