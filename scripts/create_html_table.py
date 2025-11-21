#!/usr/bin/env python3
"""
Create an HTML table view of the revision CSV for better readability
"""
import csv
import html

def create_html_table(csv_path, html_path, job_id=None):
    """Convert CSV to HTML table with styling"""
    
    rows = []
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)
    
    # Count stats first
    total = len(rows)
    with_revisions = sum(1 for r in rows if r.get('New target', '').strip())
    with_codes = sum(1 for r in rows if r.get('Code', '').strip())
    major_errors = sum(1 for r in rows if 'TE-2' in r.get('Code', ''))
    
    # Create HTML with escaped braces
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CoolerCat - Translation Quality Framework</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        :root {{
            --primary-gradient: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            --success-gradient: linear-gradient(135deg, #10b981 0%, #059669 100%);
            --warning-gradient: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
            --danger-gradient: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
            --info-gradient: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
            --shadow-sm: 0 2px 4px rgba(0, 0, 0, 0.05);
            --shadow-md: 0 4px 12px rgba(0, 0, 0, 0.1);
            --shadow-lg: 0 10px 30px rgba(0, 0, 0, 0.15);
            --shadow-xl: 0 20px 60px rgba(0, 0, 0, 0.25);
            --radius-sm: 8px;
            --radius-md: 12px;
            --radius-lg: 16px;
            --radius-xl: 24px;
            --transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }}
        
        body {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #667eea;
            min-height: 100vh;
            padding: 0;
            margin: 0;
            color: #1a202c;
            line-height: 1.6;
            -webkit-font-smoothing: antialiased;
            -moz-osx-font-smoothing: grayscale;
        }}
        
        .main-container {{
            max-width: 1920px;
            margin: 0 auto;
            padding: 32px 20px;
        }}
        
        .header {{
            text-align: center;
            margin-bottom: 48px;
            animation: fadeInDown 0.8s ease-out;
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 16px;
        }}
        
        @keyframes fadeInDown {{
            from {{
                opacity: 0;
                transform: translateY(-30px);
            }}
            to {{
                opacity: 1;
                transform: translateY(0);
            }}
        }}
        
        .header-logo {{
            width: 140px;
            height: 140px;
            object-fit: contain;
            filter: drop-shadow(0 12px 40px rgba(0, 0, 0, 0.3));
            animation: float 4s ease-in-out infinite;
            transition: transform 0.3s ease;
        }}
        
        .header-logo:hover {{
            transform: scale(1.05) rotate(5deg);
        }}
        
        @keyframes float {{
            0%, 100% {{
                transform: translateY(0px) rotate(0deg);
            }}
            50% {{
                transform: translateY(-12px) rotate(2deg);
            }}
        }}
        
        .header h1 {{
            font-size: clamp(2.5rem, 5vw, 4rem);
            font-weight: 900;
            color: #ffffff;
            margin: 0;
            text-shadow: 0 2px 10px rgba(0,0,0,0.2);
            letter-spacing: -0.03em;
        }}
        
        .header p {{
            color: rgba(255, 255, 255, 0.95);
            font-size: clamp(1rem, 2vw, 1.25rem);
            font-weight: 500;
            margin: 0;
            text-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
        }}
        
        .container {{
            background: rgba(255, 255, 255, 0.98);
            backdrop-filter: blur(30px) saturate(180%);
            border-radius: var(--radius-xl);
            padding: clamp(24px, 4vw, 48px);
            box-shadow: var(--shadow-xl), 0 0 0 1px rgba(255, 255, 255, 0.2);
            animation: fadeInUp 0.8s ease-out 0.2s both;
        }}
        
        @keyframes fadeInUp {{
            from {{
                opacity: 0;
                transform: translateY(30px);
            }}
            to {{
                opacity: 1;
                transform: translateY(0);
            }}
        }}
        
        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
            gap: 20px;
            margin-bottom: 40px;
        }}
        
        .stat-box {{
            background: rgba(255, 255, 255, 0.95);
            border: 1.5px solid #e2e8f0;
            border-radius: var(--radius-lg);
            padding: 28px 24px;
            transition: var(--transition);
            position: relative;
            overflow: hidden;
            animation: slideIn 0.6s ease-out both;
            cursor: pointer;
        }}
        
        .stat-box::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 3px;
            background: #667eea;
            transform: scaleX(0);
            transform-origin: left;
            transition: transform 0.3s ease;
        }}
        
        .stat-box:hover::before {{
            transform: scaleX(1);
        }}
        
        @keyframes slideIn {{
            from {{
                opacity: 0;
                transform: translateX(-30px);
            }}
            to {{
                opacity: 1;
                transform: translateX(0);
            }}
        }}
        
        .stat-box:nth-child(1) {{ animation-delay: 0.1s; }}
        .stat-box:nth-child(2) {{ animation-delay: 0.2s; }}
        .stat-box:nth-child(3) {{ animation-delay: 0.3s; }}
        .stat-box:nth-child(4) {{ animation-delay: 0.4s; }}
        
        .stat-box:hover {{
            transform: translateY(-6px);
            box-shadow: var(--shadow-lg);
            border-color: rgba(102, 126, 234, 0.4);
        }}
        
        .stat-box:active {{
            transform: translateY(-2px);
        }}
        
        .stat-box h3 {{
            font-size: clamp(2rem, 4vw, 2.75rem);
            font-weight: 900;
            color: #667eea;
            margin-bottom: 8px;
            line-height: 1;
            letter-spacing: -0.02em;
        }}
        
        .stat-box p {{
            color: #64748b;
            font-size: 0.95rem;
            font-weight: 600;
            margin: 0;
            letter-spacing: 0.01em;
        }}
        
        .stat-box.success {{
            background: rgba(255, 255, 255, 0.95);
        }}
        
        .stat-box.success h3 {{
            color: #10b981;
        }}
        
        .stat-box.success::before {{
            background: #10b981;
        }}
        
        .stat-box.warning {{
            background: rgba(255, 255, 255, 0.95);
        }}
        
        .stat-box.warning h3 {{
            color: #f59e0b;
        }}
        
        .stat-box.warning::before {{
            background: #f59e0b;
        }}
        
        .filter-controls {{
            background: rgba(255, 255, 255, 0.95);
            border: 1.5px solid #e2e8f0;
            border-radius: var(--radius-lg);
            padding: 32px;
            margin-bottom: 32px;
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 24px;
            align-items: start;
            box-shadow: var(--shadow-sm);
        }}
        
        .filter-group {{
            display: flex;
            flex-direction: column;
            gap: 10px;
        }}
        
        .filter-controls label {{
            font-weight: 700;
            color: #334155;
            font-size: 0.8rem;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            display: flex;
            align-items: center;
            gap: 8px;
            margin-bottom: 4px;
        }}
        
        .filter-controls label::before {{
            content: '';
            width: 4px;
            height: 4px;
            background: #667eea;
            border-radius: 50%;
            display: inline-block;
        }}
        
        .filter-controls select {{
            padding: 14px 16px;
            padding-right: 40px;
            border: 2px solid #e2e8f0;
            border-radius: var(--radius-md);
            font-size: 0.95rem;
            font-family: 'Inter', sans-serif;
            font-weight: 500;
            background: white;
            background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 12 12'%3E%3Cpath fill='%23667eea' d='M6 9L1 4h10z'/%3E%3C/svg%3E");
            background-repeat: no-repeat;
            background-position: right 14px center;
            background-size: 12px;
            appearance: none;
            -webkit-appearance: none;
            -moz-appearance: none;
            transition: var(--transition);
            outline: none;
            width: 100%;
            cursor: pointer;
            color: #1e293b;
        }}
        
        .filter-controls select:hover {{
            border-color: #cbd5e1;
            background-color: #f8fafc;
        }}
        
        .filter-controls select:focus {{
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
            background-color: white;
        }}
        
        .filter-controls select option {{
            padding: 12px;
            background: white;
            color: #1e293b;
        }}
        
        .filter-controls input[type="text"] {{
            padding: 14px 16px;
            border: 2px solid #e2e8f0;
            border-radius: var(--radius-md);
            font-size: 0.95rem;
            font-family: 'Inter', sans-serif;
            font-weight: 500;
            background: white;
            transition: var(--transition);
            outline: none;
            width: 100%;
            color: #1e293b;
        }}
        
        .filter-controls input[type="text"]::placeholder {{
            color: #94a3b8;
            font-weight: 400;
        }}
        
        .filter-controls input[type="text"]:hover {{
            border-color: #cbd5e1;
            background-color: #f8fafc;
        }}
        
        .filter-controls input[type="text"]:focus {{
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
            background-color: white;
        }}
        
        .checkbox-group {{
            display: flex;
            flex-direction: column;
            gap: 10px;
        }}
        
        .checkbox-wrapper {{
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 14px 16px;
            border: 2px solid #e2e8f0;
            border-radius: var(--radius-md);
            background: white;
            cursor: pointer;
            transition: var(--transition);
            margin-top: 24px;
        }}
        
        .checkbox-wrapper:hover {{
            border-color: #cbd5e1;
            background-color: #f8fafc;
        }}
        
        .checkbox-wrapper:has(input:checked) {{
            border-color: #667eea;
            background-color: rgba(102, 126, 234, 0.05);
        }}
        
        @supports not selector(:has(*)) {{
            .checkbox-wrapper.checked {{
                border-color: #667eea;
                background-color: rgba(102, 126, 234, 0.05);
            }}
        }}
        
        .checkbox-wrapper input[type="checkbox"] {{
            width: 20px;
            height: 20px;
            cursor: pointer;
            accent-color: #667eea;
            border-radius: 5px;
            transition: var(--transition);
            flex-shrink: 0;
            margin: 0;
        }}
        
        .checkbox-wrapper input[type="checkbox"]:hover {{
            transform: scale(1.05);
        }}
        
        .checkbox-wrapper span {{
            font-weight: 600;
            color: #475569;
            font-size: 0.9rem;
            text-transform: none;
            letter-spacing: 0;
            cursor: pointer;
            margin: 0;
            flex: 1;
            user-select: none;
        }}
        
        .checkbox-wrapper input[type="checkbox"]:checked ~ span {{
            color: #667eea;
            font-weight: 700;
        }}
        
        .table-wrapper {{
            overflow-x: auto;
            border-radius: var(--radius-lg);
            box-shadow: var(--shadow-md);
            position: relative;
            margin-top: 8px;
        }}
        
        .table-wrapper::-webkit-scrollbar {{
            height: 12px;
        }}
        
        .table-wrapper::-webkit-scrollbar-track {{
            background: #f1f5f9;
            border-radius: 10px;
        }}
        
        .table-wrapper::-webkit-scrollbar-thumb {{
            background: #667eea;
            border-radius: 10px;
            border: 2px solid #f1f5f9;
        }}
        
        .table-wrapper::-webkit-scrollbar-thumb:hover {{
            background: #5568d3;
        }}
        
        table {{
            width: 100%;
            border-collapse: separate;
            border-spacing: 0;
            font-size: 14px;
            background: white;
            border-radius: var(--radius-lg);
            overflow: hidden;
        }}
        
        th {{
            background: #667eea;
            color: white;
            padding: 20px 24px;
            text-align: left;
            font-weight: 800;
            font-size: 0.8rem;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            position: sticky;
            top: 0;
            z-index: 100;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
            white-space: nowrap;
        }}
        
        th:first-child {{
            border-top-left-radius: var(--radius-lg);
        }}
        
        th:last-child {{
            border-top-right-radius: var(--radius-lg);
        }}
        
        td {{
            padding: 20px 24px;
            border-bottom: 1px solid #f1f5f9;
            vertical-align: top;
            transition: var(--transition);
        }}
        
        tr {{
            transition: var(--transition);
        }}
        
        tr:not(.has-revision):hover {{
            background-color: #f8fafc;
        }}
        
        tr.has-revision {{
            background: rgba(220, 38, 38, 0.03);
        }}
        
        tr.has-revision td:first-child {{
            border-left: 5px solid #dc2626;
            position: relative;
            padding-left: 28px;
        }}
        
        tr.has-revision:hover {{
            background: rgba(220, 38, 38, 0.06);
            box-shadow: 0 1px 4px rgba(220, 38, 38, 0.1);
        }}
        
        tr.has-revision td {{
            background-color: transparent;
        }}
        
        .id-col {{
            font-family: 'Monaco', 'Courier New', monospace;
            font-size: 12px;
            color: #64748b;
            min-width: 160px;
            font-weight: 600;
        }}
        
        .source-col, .target-col {{
            max-width: 500px;
            word-wrap: break-word;
            line-height: 1.7;
            color: #334155;
        }}
        
        .new-target-col {{
            max-width: 500px;
            word-wrap: break-word;
            line-height: 1.7;
            position: relative;
        }}
        
        .new-target-col.has-revision {{
            background: rgba(220, 38, 38, 0.06);
            border: 2px solid #dc2626;
            border-radius: var(--radius-md);
            padding: 16px 20px;
            font-weight: 600;
            color: #991b1b;
        }}
        
        .new-target-col.has-revision::before {{
            content: '✨';
            position: absolute;
            top: -10px;
            right: -10px;
            font-size: 20px;
            background: white;
            border-radius: 50%;
            width: 32px;
            height: 32px;
            display: flex;
            align-items: center;
            justify-content: center;
            box-shadow: 0 4px 12px rgba(220, 38, 38, 0.3);
            animation: sparkle 2s ease-in-out infinite;
        }}
        
        @keyframes sparkle {{
            0%, 100% {{ transform: scale(1) rotate(0deg); }}
            50% {{ transform: scale(1.1) rotate(10deg); }}
        }}
        
        .new-target-col em {{
            color: #94a3b8;
            font-weight: normal;
            font-style: italic;
        }}
        
        .tag {{
            display: inline-block;
            background: rgba(102, 126, 234, 0.1);
            border: 1.5px solid rgba(102, 126, 234, 0.3);
            border-radius: 6px;
            padding: 3px 8px;
            margin: 2px 4px 2px 0;
            font-family: 'Monaco', 'Courier New', monospace;
            font-size: 11px;
            color: #667eea;
            font-weight: 700;
            transition: var(--transition);
        }}
        
        .tag:hover {{
            background: rgba(102, 126, 234, 0.15);
            transform: translateY(-1px);
        }}
        
        .tag-closing {{
            background: rgba(239, 68, 68, 0.1);
            border-color: rgba(239, 68, 68, 0.3);
            color: #ef4444;
        }}
        
        .text-content {{
            color: #1e293b;
            font-weight: 400;
        }}
        
        .code-col {{
            font-weight: 600;
            min-width: 140px;
        }}
        
        .code-TE-2 {{
            color: #dc2626;
            background: #fee2e2;
            padding: 6px 14px;
            border-radius: var(--radius-sm);
            display: inline-block;
            font-weight: 800;
            box-shadow: 0 1px 3px rgba(220, 38, 38, 0.2);
            border: 1.5px solid #fca5a5;
            font-size: 0.85rem;
        }}
        
        .code-LQ-05, .code-TC-05, .code-TE-05, .code-ST-05 {{
            color: #d97706;
            background: #fef3c7;
            padding: 6px 14px;
            border-radius: var(--radius-sm);
            display: inline-block;
            font-weight: 700;
            box-shadow: 0 1px 3px rgba(217, 119, 6, 0.2);
            border: 1.5px solid #fcd34d;
            font-size: 0.85rem;
        }}
        
        .comment-col {{
            max-width: 400px;
            font-size: 13px;
            color: #64748b;
            font-style: italic;
            line-height: 1.6;
            position: relative;
        }}
        
        .comment-wrapper {{
            position: relative;
        }}
        
        .state-col {{
            min-width: 120px;
            font-weight: 600;
        }}
        
        .state-badge {{
            display: inline-block;
            padding: 6px 14px;
            border-radius: 20px;
            font-size: 10px;
            font-weight: 800;
            text-transform: uppercase;
            letter-spacing: 0.08em;
        }}
        
        .state-translated {{
            background: #3b82f6;
            color: white;
            box-shadow: 0 1px 3px rgba(59, 130, 246, 0.3);
        }}
        
        .state-reviewed {{
            background: #10b981;
            color: white;
            box-shadow: 0 1px 3px rgba(16, 185, 129, 0.3);
        }}
        
        .state-final {{
            background: #8b5cf6;
            color: white;
            box-shadow: 0 1px 3px rgba(139, 92, 246, 0.3);
        }}
        
        .state-draft, .state-new {{
            background: #f59e0b;
            color: white;
            box-shadow: 0 1px 3px rgba(245, 158, 11, 0.3);
        }}
        
        .revision-badge {{
            display: inline-block;
            background: #dc2626;
            color: white;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 9px;
            font-weight: 800;
            margin-left: 10px;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            box-shadow: 0 1px 3px rgba(220, 38, 38, 0.3);
        }}
        
        .no-revision {{
            opacity: 0.65;
        }}
        
        .copy-button, .edit-button, .save-button, .cancel-button, .comment-copy-button {{
            background: #667eea;
            color: white;
            border: none;
            border-radius: var(--radius-md);
            padding: 10px 18px;
            font-size: 12px;
            font-weight: 700;
            cursor: pointer;
            transition: var(--transition);
            margin-top: 10px;
            margin-right: 8px;
            display: inline-flex;
            align-items: center;
            gap: 6px;
            box-shadow: var(--shadow-sm);
            letter-spacing: 0.02em;
        }}
        
        .copy-button:hover, .edit-button:hover, .comment-copy-button:hover {{
            background: #5568d3;
        }}
        
        .copy-button:hover, .edit-button:hover, .comment-copy-button:hover {{
            transform: translateY(-2px);
            box-shadow: var(--shadow-md);
        }}
        
        .copy-button:active, .edit-button:active, .comment-copy-button:active {{
            transform: translateY(0);
        }}
        
        .copy-button.copied {{
            background: #10b981;
        }}
        
        .edit-button {{
            background: #f59e0b;
        }}
        
        .edit-button:hover {{
            background: #d97706;
        }}
        
        .save-button {{
            background: #10b981;
        }}
        
        .save-button:hover {{
            background: #059669;
        }}
        
        .cancel-button {{
            background: #64748b;
        }}
        
        .cancel-button:hover {{
            background: #475569;
        }}
        
        .comment-copy-button {{
            background: #64748b;
            padding: 6px 12px;
            font-size: 11px;
            margin-top: 8px;
        }}
        
        .comment-copy-button:hover {{
            background: #475569;
        }}
        
        .copy-button svg, .edit-button svg, .save-button svg, .cancel-button svg, .comment-copy-button svg {{
            width: 14px;
            height: 14px;
        }}
        
        .button-group {{
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            margin-top: 10px;
        }}
        
        .revision-text {{
            margin-bottom: 10px;
        }}
        
        .revision-text.editing {{
            display: none;
        }}
        
        .revision-textarea {{
            display: none;
            width: 100%;
            min-height: 120px;
            padding: 14px;
            border: 2px solid #667eea;
            border-radius: var(--radius-md);
            font-family: 'Monaco', 'Courier New', monospace;
            font-size: 13px;
            line-height: 1.7;
            resize: vertical;
            margin-bottom: 10px;
            white-space: pre-wrap;
            word-wrap: break-word;
            transition: var(--transition);
        }}
        
        .revision-textarea:focus {{
            outline: none;
            border-color: #764ba2;
            box-shadow: 0 0 0 4px rgba(102, 126, 234, 0.1);
        }}
        
        .revision-textarea.editing {{
            display: block;
        }}
        
        .edited-badge {{
            display: inline-block;
            background: #f59e0b;
            color: white;
            padding: 3px 10px;
            border-radius: 12px;
            font-size: 9px;
            font-weight: 800;
            margin-left: 8px;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }}
        
        @media (max-width: 768px) {{
            .main-container {{
                padding: 20px 12px;
            }}
            
            .container {{
                padding: 24px 16px;
            }}
            
            .stats {{
                grid-template-columns: 1fr;
                gap: 16px;
            }}
            
            .filter-controls {{
                grid-template-columns: 1fr;
                padding: 24px;
                gap: 20px;
            }}
            
            .checkbox-wrapper {{
                margin-top: 0;
            }}
            
            .header h1 {{
                font-size: 2rem;
            }}
            
            th, td {{
                padding: 12px 16px;
                font-size: 13px;
            }}
        }}
        
        /* Loading state */
        .loading {{
            opacity: 0.6;
            pointer-events: none;
        }}
        
        /* Focus visible for accessibility */
        *:focus-visible {{
            outline: 3px solid #667eea;
            outline-offset: 2px;
        }}
        
        /* Smooth scroll */
        html {{
            scroll-behavior: smooth;
        }}
    </style>
</head>
<body>
    <div class="main-container">
        <div class="header">
            <img src="{('/assets/coolercat.webp' if job_id else 'assets/coolercat.webp')}" alt="CoolerCat" class="header-logo">
            <h1>CoolerCat</h1>
            <p>Quality Framework Dashboard</p>
        </div>
        
        <div class="container">
            <div class="stats">
                <div class="stat-box">
                    <h3>{total}</h3>
                    <p>Total Translations</p>
                </div>
                <div class="stat-box success">
                    <h3>{with_revisions}</h3>
                    <p>With Revisions</p>
                </div>
                <div class="stat-box warning">
                    <h3>{with_codes}</h3>
                    <p>With Error Codes</p>
                </div>
                <div class="stat-box warning">
                    <h3>{major_errors}</h3>
                    <p>Major Errors (TE-2)</p>
                </div>
            </div>
            
            <div class="filter-controls">
                <div class="filter-group">
                    <label for="codeFilter">Filter by Code</label>
                    <select id="codeFilter" onchange="filterTable()">
                        <option value="">All Codes</option>
                        <option value="TE-2">TE-2 (Major Translation Error)</option>
                        <option value="TE-0.5">TE-0.5 (Minor Translation Error)</option>
                        <option value="TC-0.5">TC-0.5 (Terminology/Consistency)</option>
                        <option value="LQ-0.5">LQ-0.5 (Language Quality)</option>
                        <option value="ST-0.5">ST-0.5 (Style)</option>
                    </select>
                </div>
                <div class="filter-group">
                    <label for="stateFilter">Filter by State</label>
                    <select id="stateFilter" onchange="filterTable()">
                        <option value="">All States</option>
                        <option value="translated">Translated</option>
                        <option value="reviewed">Reviewed</option>
                        <option value="final">Final</option>
                        <option value="draft">Draft</option>
                        <option value="new">New</option>
                    </select>
                </div>
                <div class="filter-group">
                    <label for="searchBox">Search</label>
                    <input type="text" id="searchBox" placeholder="Search translations..." onkeyup="filterTable()">
                </div>
                <div class="checkbox-group">
                    <label for="revisionsOnly" style="margin-bottom: 0;">Options</label>
                    <label class="checkbox-wrapper" for="revisionsOnly">
                        <input type="checkbox" id="revisionsOnly" onchange="filterTable()">
                        <span>Show only revisions</span>
                    </label>
                </div>
            </div>
            
            <div class="table-wrapper">
                <table id="revisionTable">
                    <thead>
                        <tr>
                            <th>ID Matecat</th>
                            <th>State</th>
                            <th>Source</th>
                            <th>Target</th>
                            <th>New target</th>
                            <th>Code</th>
                            <th>Comment</th>
                        </tr>
                    </thead>
                    <tbody>
"""
    
    def format_text_with_tags(text):
        """Format text to highlight tags"""
        if not text:
            return text
        
        import re
        tag_pattern = r'(<[^>]+>|</[^>]+>)'
        
        parts = re.split(tag_pattern, text)
        formatted_parts = []
        
        for part in parts:
            if re.match(tag_pattern, part):
                if part.startswith('</'):
                    formatted_parts.append(f'<span class="tag tag-closing">{html.escape(part)}</span>')
                else:
                    formatted_parts.append(f'<span class="tag">{html.escape(part)}</span>')
            else:
                if part.strip():
                    formatted_parts.append(f'<span class="text-content">{html.escape(part)}</span>')
                else:
                    formatted_parts.append(html.escape(part))
        
        return ''.join(formatted_parts)
    
    # Add rows
    for row in rows:
        matecat_id = html.escape(row.get('ID Matecat', ''))
        state = row.get('State', '').lower()
        source_raw = row.get('Source', '')
        target_raw = row.get('Target', '')
        new_target_raw = row.get('New target', '')
        code = html.escape(row.get('Code', ''))
        comment = html.escape(row.get('Comment', ''))
        
        # Format text with tags
        source = format_text_with_tags(source_raw)
        target = format_text_with_tags(target_raw)
        new_target = format_text_with_tags(new_target_raw) if new_target_raw else ''
        
        # Determine row class
        row_class = 'has-revision' if new_target_raw else 'no-revision'
        
        # Format code with styling
        code_html = ''
        if code:
            codes = [c.strip() for c in code.split(',')]
            code_spans = []
            for c in codes:
                css_class = f"code-{c.replace('.', '').replace('-', '')}"
                code_spans.append(f'<span class="{css_class}">{c}</span>')
            code_html = ' '.join(code_spans)
        
        # Format state badge
        state_badge = ''
        if state:
            state_badge = f'<span class="state-badge state-{state}">{state}</span>'
        else:
            state_badge = '<span style="color: #94a3b8;">—</span>'
        
        # Format comment with copy button
        comment_display = ''
        if comment:
            import base64
            comment_b64 = base64.b64encode(comment.encode('utf-8')).decode('utf-8')
            comment_display = f'''<div class="comment-wrapper">
                <div>{comment}</div>
                <button class="comment-copy-button" data-text-b64="{comment_b64}" onclick="copyCommentToClipboard(this)" title="Copy comment">
                    <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z"></path>
                    </svg>
                    Copy
                </button>
            </div>'''
        else:
            comment_display = ''
        
        # Format new target with highlighting, copy and edit buttons
        if new_target_raw:
            import base64
            new_target_b64 = base64.b64encode(new_target_raw.encode('utf-8')).decode('utf-8')
            new_target_display = f'''<div class="has-revision" data-matecat-id="{matecat_id}">
                <div class="revision-text" id="text-{matecat_id}">{new_target}<span class="edited-badge" id="badge-{matecat_id}" style="display: none;">EDITED</span></div>
                <textarea class="revision-textarea" id="textarea-{matecat_id}" data-original-b64="{new_target_b64}">{html.escape(new_target_raw)}</textarea>
                <div class="button-group">
                    <button class="copy-button" data-text-b64="{new_target_b64}" data-matecat-id="{matecat_id}" onclick="copyToClipboard(this)" title="Copy revised translation">
                        <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z"></path>
                        </svg>
                        Copy
                    </button>
                    <button class="edit-button" data-matecat-id="{matecat_id}" onclick="editRevision(this)" title="Edit revision">
                        <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"></path>
                        </svg>
                        Edit
                    </button>
                    <button class="save-button" data-matecat-id="{matecat_id}" onclick="saveRevision(this)" title="Save changes" style="display: none;">
                        <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
                        </svg>
                        Save
                    </button>
                    <button class="cancel-button" data-matecat-id="{matecat_id}" onclick="cancelEdit(this)" title="Cancel editing" style="display: none;">
                        <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                        </svg>
                        Cancel
                    </button>
                </div>
            </div>'''
            new_target_class = 'new-target-col has-revision'
        else:
            new_target_display = '<em>No revision</em>'
            new_target_class = 'new-target-col'
        
        # Set has_revision as lowercase string for JavaScript
        has_revision_str = 'true' if new_target_raw else 'false'
        
        html_content += f"""
                        <tr class="{row_class}" data-code="{code}" data-has-revision="{has_revision_str}" data-state="{state}">
                            <td class="id-col">{matecat_id}{'<span class="revision-badge">REVISED</span>' if new_target_raw else ''}</td>
                            <td class="state-col">{state_badge}</td>
                            <td class="source-col">{source}</td>
                            <td class="target-col">{target}</td>
                            <td class="{new_target_class}">{new_target_display}</td>
                            <td class="code-col">{code_html}</td>
                            <td class="comment-col">{comment_display}</td>
                        </tr>
"""
    
    html_content += """
                    </tbody>
                </table>
            </div>
        </div>
    </div>
    
    <script>
        // Format text with tags for display
        function formatTextWithTags(text) {
            const tagPattern = /(<[^>]+>|<\\/[^>]+>)/g;
            let result = text;
            result = result.replace(tagPattern, function(match) {
                const escaped = match.replace(/</g, '&lt;').replace(/>/g, '&gt;');
                if (match.startsWith('</')) {
                    return '<span class="tag tag-closing">' + escaped + '</span>';
                } else {
                    return '<span class="tag">' + escaped + '</span>';
                }
            });
            result = result.replace(/([^<]+)/g, function(match) {
                if (match.trim()) {
                    return '<span class="text-content">' + match.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;') + '</span>';
                }
                return match;
            });
            return result;
        }
        
        // Load saved edits from localStorage on page load
        window.addEventListener('DOMContentLoaded', function() {
            const revisions = document.querySelectorAll('.has-revision[data-matecat-id]');
            revisions.forEach(function(rev) {
                const matecatId = rev.getAttribute('data-matecat-id');
                const savedText = localStorage.getItem('revision_' + matecatId);
                if (savedText) {
                    const textDiv = document.getElementById('text-' + matecatId);
                    const textarea = document.getElementById('textarea-' + matecatId);
                    const badge = document.getElementById('badge-' + matecatId);
                    const copyButton = rev.querySelector('.copy-button');
                    
                    if (textDiv && textarea && badge && copyButton) {
                        const formattedText = formatTextWithTags(savedText);
                        textDiv.innerHTML = formattedText + '<span class="edited-badge">EDITED</span>';
                        textarea.value = savedText;
                        badge.style.display = 'inline-block';
                        
                        const editedB64 = btoa(unescape(encodeURIComponent(savedText)));
                        copyButton.setAttribute('data-text-b64', editedB64);
                    }
                }
            });
        });
        
        // Properly decode UTF-8 from base64
        function base64ToUtf8(base64) {
            const binaryString = atob(base64);
            const bytes = new Uint8Array(binaryString.length);
            for (let i = 0; i < binaryString.length; i++) {
                bytes[i] = binaryString.charCodeAt(i);
            }
            // Use TextDecoder to properly decode UTF-8
            const decoder = new TextDecoder('utf-8');
            return decoder.decode(bytes);
        }
        
        // Decode HTML entities and remove tags to get plain text
        function getPlainText(htmlText) {
            // Create a temporary div to decode HTML entities and extract text
            const tempDiv = document.createElement('div');
            tempDiv.innerHTML = htmlText;
            // Get plain text content (this automatically decodes entities and removes tags)
            let plainText = tempDiv.textContent || tempDiv.innerText || '';
            // Clean up any remaining issues
            plainText = plainText.replace(/\\s+/g, ' ').trim();
            return plainText;
        }
        
        // Copy comment to clipboard function
        function copyCommentToClipboard(button) {
            const textB64 = button.getAttribute('data-text-b64');
            // Properly decode UTF-8 from base64
            let text = base64ToUtf8(textB64);
            // The text should already be plain text, but remove any HTML tags just in case
            const tempDiv = document.createElement('div');
            tempDiv.textContent = text;
            text = tempDiv.textContent || text;
            
            navigator.clipboard.writeText(text).then(function() {
                const originalText = button.innerHTML;
                button.innerHTML = `
                    <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
                    </svg>
                    Copied!
                `;
                button.classList.add('copied');
                
                setTimeout(function() {
                    button.innerHTML = originalText;
                    button.classList.remove('copied');
                }, 2000);
            }).catch(function(err) {
                console.error('Failed to copy: ', err);
                alert('Failed to copy to clipboard');
            });
        }
        
        // Copy to clipboard function
        function copyToClipboard(button) {
            const textB64 = button.getAttribute('data-text-b64');
            // Properly decode UTF-8 from base64
            let text = base64ToUtf8(textB64);
            // The text should already be plain text, but remove any HTML tags just in case
            const tempDiv = document.createElement('div');
            tempDiv.textContent = text;
            text = tempDiv.textContent || text;
            
            navigator.clipboard.writeText(text).then(function() {
                const originalText = button.innerHTML;
                button.innerHTML = `
                    <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
                    </svg>
                    Copied!
                `;
                button.classList.add('copied');
                
                setTimeout(function() {
                    button.innerHTML = originalText;
                    button.classList.remove('copied');
                }, 2000);
            }).catch(function(err) {
                console.error('Failed to copy: ', err);
                alert('Failed to copy to clipboard');
            });
        }
        
        // Edit revision function
        function editRevision(button) {
            const matecatId = button.getAttribute('data-matecat-id');
            const textDiv = document.getElementById('text-' + matecatId);
            const textarea = document.getElementById('textarea-' + matecatId);
            const editButton = button;
            const saveButton = button.parentElement.querySelector('.save-button');
            const cancelButton = button.parentElement.querySelector('.cancel-button');
            const copyButton = button.parentElement.querySelector('.copy-button');
            
            textDiv.classList.add('editing');
            textarea.classList.add('editing');
            
            editButton.style.display = 'none';
            saveButton.style.display = 'inline-flex';
            cancelButton.style.display = 'inline-flex';
            copyButton.style.display = 'none';
            
            textarea.focus();
            textarea.setSelectionRange(textarea.value.length, textarea.value.length);
        }
        
        // Save revision function
        function saveRevision(button) {
            const matecatId = button.getAttribute('data-matecat-id');
            const textDiv = document.getElementById('text-' + matecatId);
            const textarea = document.getElementById('textarea-' + matecatId);
            const editButton = button.parentElement.querySelector('.edit-button');
            const saveButton = button;
            const cancelButton = button.parentElement.querySelector('.cancel-button');
            const copyButton = button.parentElement.querySelector('.copy-button');
            const badge = document.getElementById('badge-' + matecatId);
            
            const newText = textarea.value;
            
            const formattedText = formatTextWithTags(newText);
            textDiv.innerHTML = formattedText + '<span class="edited-badge">EDITED</span>';
            textDiv.classList.remove('editing');
            textarea.classList.remove('editing');
            
            if (badge) {
                badge.style.display = 'inline-block';
            }
            
            localStorage.setItem('revision_' + matecatId, newText);
            
            const newTextB64 = btoa(unescape(encodeURIComponent(newText)));
            copyButton.setAttribute('data-text-b64', newTextB64);
            
            editButton.style.display = 'inline-flex';
            saveButton.style.display = 'none';
            cancelButton.style.display = 'none';
            copyButton.style.display = 'inline-flex';
            
            const originalText = button.innerHTML;
            button.innerHTML = `
                <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
                </svg>
                Saved!
            `;
            setTimeout(function() {
                button.innerHTML = originalText;
            }, 1500);
        }
        
        // Cancel edit function
        function cancelEdit(button) {
            const matecatId = button.getAttribute('data-matecat-id');
            const textDiv = document.getElementById('text-' + matecatId);
            const textarea = document.getElementById('textarea-' + matecatId);
            const editButton = button.parentElement.querySelector('.edit-button');
            const saveButton = button.parentElement.querySelector('.save-button');
            const cancelButton = button;
            const copyButton = button.parentElement.querySelector('.copy-button');
            
            const originalB64 = textarea.getAttribute('data-original-b64');
            const savedText = localStorage.getItem('revision_' + matecatId);
            const textToShow = savedText || atob(originalB64);
            
            const badge = document.getElementById('badge-' + matecatId);
            if (savedText && badge) {
                textDiv.innerHTML = formatTextWithTags(textToShow) + '<span class="edited-badge">EDITED</span>';
                badge.style.display = 'inline-block';
            } else {
                textDiv.innerHTML = formatTextWithTags(textToShow);
                if (badge) badge.style.display = 'none';
            }
            
            textarea.value = textToShow;
            textDiv.classList.remove('editing');
            textarea.classList.remove('editing');
            
            editButton.style.display = 'inline-flex';
            saveButton.style.display = 'none';
            cancelButton.style.display = 'none';
            copyButton.style.display = 'inline-flex';
        }
        
        // Update checkbox wrapper styling
        document.getElementById('revisionsOnly').addEventListener('change', function() {
            const wrapper = this.closest('.checkbox-wrapper');
            if (this.checked) {
                wrapper.classList.add('checked');
            } else {
                wrapper.classList.remove('checked');
            }
        });
        
        // Filter table function
        function filterTable() {
            const codeFilter = document.getElementById('codeFilter').value;
            const stateFilter = document.getElementById('stateFilter').value;
            const revisionsOnly = document.getElementById('revisionsOnly').checked;
            const searchText = document.getElementById('searchBox').value.toLowerCase();
            const table = document.getElementById('revisionTable');
            const rows = table.getElementsByTagName('tr');
            
            // Update checkbox wrapper styling
            const checkboxWrapper = document.getElementById('revisionsOnly').closest('.checkbox-wrapper');
            if (revisionsOnly) {
                checkboxWrapper.classList.add('checked');
            } else {
                checkboxWrapper.classList.remove('checked');
            }
            
            let visibleCount = 0;
            
            for (let i = 1; i < rows.length; i++) {
                const row = rows[i];
                const code = row.getAttribute('data-code') || '';
                const state = row.getAttribute('data-state') || '';
                const hasRevision = row.getAttribute('data-has-revision') === 'true';
                const source = row.cells[2].textContent.toLowerCase();
                const target = row.cells[3].textContent.toLowerCase();
                const newTarget = row.cells[4].textContent.toLowerCase();
                
                let show = true;
                
                if (codeFilter && !code.includes(codeFilter)) {
                    show = false;
                }
                
                if (stateFilter && state !== stateFilter) {
                    show = false;
                }
                
                if (revisionsOnly && !hasRevision) {
                    show = false;
                }
                
                if (searchText && !source.includes(searchText) && !target.includes(searchText) && !newTarget.includes(searchText)) {
                    show = false;
                }
                
                if (show) {
                    row.style.display = '';
                    visibleCount++;
                    row.style.animation = 'fadeInUp 0.3s ease-out';
                } else {
                    row.style.display = 'none';
                }
            }
        }
        
        // Keyboard shortcuts
        document.addEventListener('keydown', function(e) {
            // Ctrl/Cmd + F to focus search
            if ((e.ctrlKey || e.metaKey) && e.key === 'f') {
                e.preventDefault();
                document.getElementById('searchBox').focus();
            }
        });
    </script>
</body>
</html>
"""
    
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"✨ Unicorn-grade HTML table created: {html_path}")
    print(f"🎨 Open it in your browser to see the amazing design!")

if __name__ == '__main__':
    import sys
    import os
    
    if len(sys.argv) >= 3:
        # Command line arguments: csv_file html_file [job_id]
        csv_file = sys.argv[1]
        html_file = sys.argv[2]
        job_id = sys.argv[3] if len(sys.argv) >= 4 else None
    else:
        # Default behavior for backward compatibility
        script_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(script_dir)
        
        csv_file = os.path.join(project_root, 'output', 'revision_table.csv')
        html_file = os.path.join(project_root, 'revision_table.html')
        job_id = None
    
    create_html_table(csv_file, html_file, job_id)
