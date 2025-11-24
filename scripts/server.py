#!/usr/bin/env python3
"""
Simple Flask server for job management and file uploads
"""
import os
import json
import shutil
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import subprocess
import uuid
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Get project root (parent of scripts directory)
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JOBS_DIR = os.path.join(PROJECT_ROOT, 'jobs')
# Ensure directories exist
os.makedirs(JOBS_DIR, exist_ok=True)

def get_jobs():
    """Get list of all jobs"""
    jobs = []
    if not os.path.exists(JOBS_DIR):
        return jobs
    
    for job_id in os.listdir(JOBS_DIR):
        job_path = os.path.join(JOBS_DIR, job_id)
        if os.path.isdir(job_path):
            # Find XLF file
            xlf_files = [f for f in os.listdir(job_path) if f.endswith('.xlf') or f.endswith('.xlf.xlf')]
            if xlf_files:
                xlf_file = xlf_files[0]
                xlf_path = os.path.join(job_path, xlf_file)
                stat = os.stat(xlf_path)
                
                jobs.append({
                    'id': job_id,
                    'name': xlf_file,
                    'created': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    'size': stat.st_size
                })
    
    # Sort by creation time (newest first)
    jobs.sort(key=lambda x: x['created'], reverse=True)
    return jobs

@app.route('/api/jobs', methods=['GET'])
def list_jobs():
    """List all jobs"""
    return jsonify(get_jobs())

@app.route('/api/jobs', methods=['POST'])
def create_job():
    """Create a new job from uploaded XLF file"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not (file.filename.endswith('.xlf') or file.filename.endswith('.xlf.xlf')):
        return jsonify({'error': 'Invalid file type. Please upload an XLF file.'}), 400
    
    # Create job ID
    job_id = str(uuid.uuid4())
    job_dir = os.path.join(JOBS_DIR, job_id)
    os.makedirs(job_dir, exist_ok=True)
    
    # Save file
    filename = file.filename
    file_path = os.path.join(job_dir, filename)
    file.save(file_path)
    
    # Process the job
    try:
        result = process_job(job_id)
        if result['success']:
            return jsonify({
                'job_id': job_id,
                'name': filename,
                'message': 'Job created and processed successfully',
                'stats': result.get('stats', {})
            })
        else:
            return jsonify({'error': result.get('error', 'Processing failed')}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def process_job(job_id):
    """Process a job: generate CSV and HTML"""
    job_dir = os.path.join(JOBS_DIR, job_id)
    
    # Find XLF file
    xlf_files = [f for f in os.listdir(job_dir) if f.endswith('.xlf') or f.endswith('.xlf.xlf')]
    if not xlf_files:
        return {'success': False, 'error': 'No XLF file found in job'}
    
    xlf_file = xlf_files[0]
    xlf_path = os.path.join(job_dir, xlf_file)
    
    # Output paths
    csv_path = os.path.join(job_dir, 'revision_table.csv')
    html_path = os.path.join(job_dir, 'revision_table.html')
    
    # Run create_revision_table.py
    scripts_dir = os.path.dirname(os.path.abspath(__file__))
    revision_script = os.path.join(scripts_dir, 'create_revision_table.py')
    
    # Check if script exists
    if not os.path.exists(revision_script):
        return {'success': False, 'error': f'Script not found: {revision_script}'}
    
    try:
        # Use sys.executable to use the same Python interpreter
        import sys
        python_exe = sys.executable
        
        print(f"[{job_id}] Starting revision processing...")
        print(f"[{job_id}] Running: {python_exe} {revision_script} {xlf_path} {csv_path}")
        
        result = subprocess.run(
            [python_exe, revision_script, xlf_path, csv_path],
            capture_output=True,
            text=True,
            cwd=scripts_dir,
            timeout=300  # 5 minute timeout
        )
        
        # Log output for debugging
        if result.stdout:
            print(f"[{job_id}] Script output:\n{result.stdout}")
        if result.stderr:
            print(f"[{job_id}] Script errors:\n{result.stderr}")
        
        if result.returncode != 0:
            error_msg = result.stderr or result.stdout or 'Unknown error'
            print(f"[{job_id}] ERROR: CSV generation failed: {error_msg}")
            return {'success': False, 'error': f'CSV generation failed: {error_msg}'}
        
        # Check if CSV was created
        if not os.path.exists(csv_path):
            print(f"[{job_id}] ERROR: CSV file was not created at {csv_path}")
            return {'success': False, 'error': 'CSV file was not created'}
        
        # Verify CSV has content
        import csv as csv_module
        row_count = 0
        with_revisions_count = 0
        try:
            with open(csv_path, 'r', encoding='utf-8') as f:
                reader = csv_module.DictReader(f)
                for row in reader:
                    row_count += 1
                    if row.get('New target', '').strip():
                        with_revisions_count += 1
        except Exception as e:
            print(f"[{job_id}] WARNING: Could not verify CSV content: {e}")
        
        print(f"[{job_id}] CSV created: {row_count} rows, {with_revisions_count} with revisions")
        
        # Parse stats from output
        stats = {}
        for line in result.stdout.split('\n'):
            if 'Total translations:' in line:
                try:
                    stats['total'] = int(line.split(':')[-1].strip())
                except:
                    pass
            elif 'With revisions:' in line:
                try:
                    stats['with_revisions'] = int(line.split(':')[-1].strip())
                except:
                    pass
            elif 'With error codes:' in line:
                try:
                    stats['with_codes'] = int(line.split(':')[-1].strip())
                except:
                    pass
        
        # Use actual counts if parsing failed
        if not stats.get('total'):
            stats['total'] = row_count
        if not stats.get('with_revisions'):
            stats['with_revisions'] = with_revisions_count
        
        # Run create_html_table.py
        html_script = os.path.join(scripts_dir, 'create_html_table.py')
        if not os.path.exists(html_script):
            return {'success': False, 'error': f'HTML script not found: {html_script}'}
        
        result = subprocess.run(
            [python_exe, html_script, csv_path, html_path, job_id],
            capture_output=True,
            text=True,
            cwd=scripts_dir,
            timeout=300  # 5 minute timeout
        )
        
        if result.returncode != 0:
            error_msg = result.stderr or result.stdout or 'Unknown error'
            return {'success': False, 'error': f'HTML generation failed: {error_msg}'}
        
        return {'success': True, 'stats': stats}
        
    except subprocess.TimeoutExpired:
        return {'success': False, 'error': 'Processing timed out after 5 minutes'}
    except FileNotFoundError as e:
        return {'success': False, 'error': f'Python or script not found: {str(e)}'}
    except Exception as e:
        return {'success': False, 'error': f'Processing error: {str(e)}'}

@app.route('/api/jobs/<job_id>/process', methods=['POST'])
def reprocess_job(job_id):
    """Reprocess an existing job"""
    result = process_job(job_id)
    if result['success']:
        return jsonify({
            'message': 'Job reprocessed successfully',
            'stats': result.get('stats', {})
        })
    else:
        return jsonify({'error': result.get('error', 'Processing failed')}), 500

@app.route('/api/jobs/<job_id>/revise', methods=['POST'])
def revise_job(job_id):
    """AI-powered revision of all translations in a job using built-in AI"""
    job_dir = os.path.join(JOBS_DIR, job_id)
    csv_path = os.path.join(job_dir, 'revision_table.csv')
    
    if not os.path.exists(csv_path):
        return jsonify({'error': 'CSV file not found. Please process the job first.'}), 404
    
    try:
        import sys
        python_exe = sys.executable
        scripts_dir = os.path.dirname(os.path.abspath(__file__))
        ai_revision_script = os.path.join(scripts_dir, 'ai_revision.py')
        
        if not os.path.exists(ai_revision_script):
            return jsonify({'error': 'AI revision script not found'}), 500
        
        print(f"[{job_id}] Starting AI revision using built-in knowledge...")
        print(f"[{job_id}] Running: {python_exe} {ai_revision_script} {csv_path} {csv_path}")
        
        # Run AI revision script (no API key needed - uses built-in AI)
        result = subprocess.run(
            [python_exe, ai_revision_script, csv_path, csv_path],
            capture_output=True,
            text=True,
            cwd=scripts_dir,
            timeout=1800  # 30 minute timeout for AI processing
        )
        
        if result.stdout:
            print(f"[{job_id}] AI revision output:\n{result.stdout}")
        if result.stderr:
            print(f"[{job_id}] AI revision errors:\n{result.stderr}")
        
        if result.returncode != 0:
            error_msg = result.stderr or result.stdout or 'Unknown error'
            return jsonify({'error': f'AI revision failed: {error_msg}'}), 500
        
        # Parse stats from output
        stats = {}
        for line in result.stdout.split('\n'):
            if 'Total segments:' in line:
                try:
                    stats['total'] = int(line.split(':')[-1].strip())
                except:
                    pass
            elif 'Revised:' in line:
                try:
                    stats['revised'] = int(line.split(':')[-1].strip())
                except:
                    pass
        
        # Regenerate HTML table with updated CSV
        html_path = os.path.join(job_dir, 'revision_table.html')
        html_script = os.path.join(scripts_dir, 'create_html_table.py')
        if os.path.exists(html_script):
            subprocess.run(
                [python_exe, html_script, csv_path, html_path, job_id],
                capture_output=True,
                text=True,
                cwd=scripts_dir,
                timeout=300
            )
        
        return jsonify({
            'message': 'AI revision completed successfully',
            'stats': stats
        })
        
    except subprocess.TimeoutExpired:
        return jsonify({'error': 'AI revision timed out after 30 minutes'}), 500
    except Exception as e:
        print(f"[{job_id}] AI revision error: {str(e)}")
        return jsonify({'error': f'AI revision error: {str(e)}'}), 500

@app.route('/api/jobs/<job_id>/progress', methods=['GET'])
def get_job_progress(job_id):
    job_dir = os.path.join(JOBS_DIR, job_id)
    progress_file = os.path.join(job_dir, 'progress.json')
    
    if os.path.exists(progress_file):
        try:
            with open(progress_file, 'r') as f:
                data = json.load(f)
            return jsonify(data)
        except Exception:
            pass
            
    return jsonify({'status': 'unknown', 'percentage': 0, 'message': 'Waiting to start...'})

@app.route('/api/jobs/<job_id>', methods=['GET'])
def get_job(job_id):
    """Get job details"""
    job_dir = os.path.join(JOBS_DIR, job_id)
    if not os.path.exists(job_dir):
        return jsonify({'error': 'Job not found'}), 404
    
    # Find XLF file
    xlf_files = [f for f in os.listdir(job_dir) if f.endswith('.xlf') or f.endswith('.xlf.xlf')]
    if not xlf_files:
        return jsonify({'error': 'No XLF file found'}), 404
    
    xlf_file = xlf_files[0]
    csv_path = os.path.join(job_dir, 'revision_table.csv')
    html_path = os.path.join(job_dir, 'revision_table.html')
    
    return jsonify({
        'id': job_id,
        'name': xlf_file,
        'has_csv': os.path.exists(csv_path),
        'has_html': os.path.exists(html_path)
    })

@app.route('/api/jobs/<job_id>/data', methods=['GET'])
def get_job_data(job_id):
    """Get job CSV data as JSON - auto-process if needed"""
    import csv
    
    job_dir = os.path.join(JOBS_DIR, job_id)
    csv_path = os.path.join(job_dir, 'revision_table.csv')
    
    # If CSV doesn't exist, process the job first
    if not os.path.exists(csv_path):
        result = process_job(job_id)
        if not result['success']:
            return jsonify({'error': result.get('error', 'Processing failed')}), 500
    
    # Read CSV and return as JSON
    rows = []
    try:
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                rows.append(row)
        return jsonify({'data': rows, 'job_id': job_id})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/jobs/<job_id>/html', methods=['GET'])
def get_job_html(job_id):
    """Get HTML file for a job - auto-process if needed"""
    job_dir = os.path.join(JOBS_DIR, job_id)
    html_path = os.path.join(job_dir, 'revision_table.html')
    
    # If HTML doesn't exist, process the job first
    if not os.path.exists(html_path):
        result = process_job(job_id)
        if not result['success']:
            # Return an error page instead of JSON
            error_html = f"""
            <!DOCTYPE html>
            <html>
            <head><title>Error</title></head>
            <body style="font-family: Arial; padding: 40px; text-align: center;">
                <h1>Job Not Processed</h1>
                <p>This job needs to be processed first.</p>
                <p>Error: {result.get('error', 'Unknown error')}</p>
                <p><a href="/">← Back to Jobs</a></p>
            </body>
            </html>
            """
            return error_html, 404
    
    return send_from_directory(job_dir, 'revision_table.html')

@app.route('/')
def index():
    """Serve the main index.html"""
    index_path = os.path.join(PROJECT_ROOT, 'index.html')
    if os.path.exists(index_path):
        return send_from_directory(PROJECT_ROOT, 'index.html')
    else:
        return "index.html not found", 404

@app.route('/assets/<path:filename>')
def serve_assets(filename):
    """Serve static assets"""
    assets_dir = os.path.join(PROJECT_ROOT, 'assets')
    return send_from_directory(assets_dir, filename)

@app.route('/api/jobs/<job_id>', methods=['DELETE'])
def delete_job(job_id):
    """Delete a job"""
    job_dir = os.path.join(JOBS_DIR, job_id)
    if not os.path.exists(job_dir):
        return jsonify({'error': 'Job not found'}), 404
    
    try:
        shutil.rmtree(job_dir)
        return jsonify({'message': 'Job deleted successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("🚀 Starting CoolerCat Translation Server...")
    print(f"📁 Jobs directory: {JOBS_DIR}")
    print(f"🌐 Server running at http://localhost:5001")
    print(f"🏠 Network access at http://10.0.0.146:5001")
    print("\nPress Ctrl+C to stop the server")
    app.run(debug=True, host='0.0.0.0', port=5001)

