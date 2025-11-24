#!/usr/bin/env python3
"""
AI-powered revision system for French translations
Uses LLM (Gemini/OpenAI) to review translations based on documentation
"""
import csv
import json
import os
import sys
import re
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure AI
try:
    import google.generativeai as genai
    HAS_GEMINI = True
except ImportError:
    HAS_GEMINI = False

class LLMReviser:
    def __init__(self, knowledge_base_path=None):
        self.api_key = os.getenv('GEMINI_API_KEY')
        self.knowledge_base = ""
        
        # Load knowledge base - use absolute path
        if knowledge_base_path is None:
            # Default to knowledge_base.txt in project root
            script_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(script_dir)  # Go up one level from scripts/
            knowledge_base_path = os.path.join(project_root, 'knowledge_base.txt')
        
        if os.path.exists(knowledge_base_path):
            with open(knowledge_base_path, 'r', encoding='utf-8') as f:
                self.knowledge_base = f.read()
            print(f"Loaded knowledge base from: {knowledge_base_path}")
        else:
            print(f"WARNING: Knowledge base not found at: {knowledge_base_path}")
        
        if self.api_key and HAS_GEMINI:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-2.0-flash')
            print(f"✓ Gemini API configured successfully (using gemini-2.0-flash)")
        else:
            self.model = None
            print("WARNING: No API key found or google-generativeai not installed. Falling back to mock mode.")

    def revise(self, source_text, target_text, segment_id):
        """
        Revise a translation using LLM
        """
        if not target_text or not target_text.strip():
            return self._empty_result(target_text)
            
        # Skip tags-only segments
        if re.match(r'^<[^>]+>$', target_text.strip()):
            return self._empty_result(target_text, confidence=100)

        # If no model, use a simple fallback (mock) or just return original
        if not self.model:
            return self._mock_revision(source_text, target_text)

        try:
            prompt = self._build_prompt(source_text, target_text)
            response = self.model.generate_content(prompt)
            
            # Parse JSON response
            try:
                # Clean up markdown code blocks if present
                text = response.text.strip()
                if text.startswith('```json'):
                    text = text[7:]
                if text.endswith('```'):
                    text = text[:-3]
                
                result = json.loads(text.strip())
                
                # Debug: Print what AI returned
                print(f"  AI Response for {segment_id}:")
                print(f"    Revised: {result.get('revised_text', 'N/A')}")
                print(f"    Codes: {result.get('error_codes', [])}")
                print(f"    Comment: {result.get('comment', 'N/A')}")
                
                return {
                    'revised_text': result.get('revised_text', target_text),
                    'has_revision': len(result.get('error_codes', [])) > 0,  # Has revision if there are error codes
                    'error_codes': result.get('error_codes', []),
                    'comment': result.get('comment', ''),
                    'confidence': result.get('confidence_score', 0)
                }
            except json.JSONDecodeError:
                print(f"Error parsing JSON for segment {segment_id}")
                return self._empty_result(target_text)
                
        except Exception as e:
            print(f"Error calling AI for segment {segment_id}: {e}")
            return self._empty_result(target_text)

    def _build_prompt(self, source, target):
        return f"""You are a quality reviewer for Notion's French translations.

KNOWLEDGE BASE:
{self.knowledge_base}

TASK:
Source (English): "{source}"
Target (French): "{target}"

CRITICAL INSTRUCTIONS - MULTI-PASS REVIEW:

**PASS 1 - BASIC QUALITY CHECK (MANDATORY):**
1. **TYPOS**: Check for obvious spelling errors. ANY typo is LQ-0.5.
2. **VERB CONJUGATION**: Verify verbs are conjugated correctly (imperative, tense, subject agreement). Errors are TE-0.5 or LQ-0.5.
3. **GENDER/NUMBER AGREEMENT**: Check adjectives, articles, and participles agree with nouns. Errors are TE-0.5 or LQ-0.5.
4. **PUNCTUATION**: Check for proper punctuation (spaces before :;!?, etc.). Errors are LQ-0.5.
5. **MEANING ACCURACY**: Verify the translation conveys the same meaning as the source. Major changes or negation errors are TE-2.

**PASS 2 - GLOSSARY VALIDATION (MANDATORY):**
6. **TERMINOLOGY CHECK**: Identify ALL terms in the source text that might be in the Notion Glossary. For EACH term found in the glossary, verify the French translation matches the official fr_FR entry exactly. If ANY glossary term is translated incorrectly, assign TC-0.5 error code.

**PASS 3 - STYLE & CONSISTENCY:**
7. Check tone, formality, and style against Notion's style guide.

If you find ANY error in any pass, you MUST:
   - Provide a CORRECTED translation in "revised_text"
   - Assign ALL appropriate error code(s): TE-2, TE-0.5, TC-0.5, LQ-0.5, or ST-0.5
   - Explain EACH error briefly
   
If the translation is acceptable with no errors:
   - Return the ORIGINAL translation unchanged in "revised_text"
   - Return empty error_codes array []
   - Set comment to null

ERROR CODE REFERENCE:
- TE-2: Major translation error (meaning changed, negation missing, critical omission)
- TE-0.5: Minor translation error (grammar issues, verb conjugation, agreement problems)
- TC-0.5: Terminology/consistency violation (wrong term from glossary)
- LQ-0.5: Language quality (punctuation, SPELLING/TYPOS, grammar)
- ST-0.5: Style violation (wrong tone, unidiomatic)

OUTPUT FORMAT (JSON ONLY, NO MARKDOWN):
{{
    "revised_text": "CORRECTED French translation if error found, or ORIGINAL if no error",
    "error_codes": ["TE-0.5", "LQ-0.5"] or [],
    "comment": "Brief explanation of what was wrong and how you fixed it" or null,
    "confidence_score": 0-100
}}

EXAMPLES:

Example 1 - Missing negation:
Source: "I cannot do this"
Target: "Je peux faire cela"
Output: {{"revised_text": "Je ne peux pas faire cela", "error_codes": ["TE-2"], "comment": "Missing negation - 'cannot' was translated as 'can'", "confidence_score": 95}}

Example 2 - Typo:
Source: "Click here to continue"
Target: "Cliquez ici poru continuer"
Output: {{"revised_text": "Cliquez ici pour continuer", "error_codes": ["LQ-0.5"], "comment": "Typo: 'poru' → 'pour'", "confidence_score": 100}}

Example 3 - Verb conjugation + agreement:
Source: "Please share feedback and use thumbs up/down"
Target: "Partagez vos commentaires et utiliser les pouces levé/baissé"
Output: {{"revised_text": "Partagez vos commentaires et utilisez les pouces levés/baissés", "error_codes": ["TE-0.5", "TE-0.5"], "comment": "Verb conjugation: 'utiliser' → 'utilisez' (imperative); Agreement: 'levé/baissé' → 'levés/baissés' (plural)", "confidence_score": 100}}

Example 4 - No errors:
Source: "Hello world"
Target: "Bonjour le monde"
Output: {{"revised_text": "Bonjour le monde", "error_codes": [], "comment": null, "confidence_score": 100}}

REMEMBER: 
- Check BASIC ERRORS FIRST (typos, grammar, conjugation)
- Then check glossary terms
- If there's ANY error, FIX IT in revised_text
- ALWAYS assign appropriate error codes for EVERY error found
"""

    def _empty_result(self, text, confidence=0):
        return {
            'revised_text': text,
            'has_revision': False,
            'error_codes': [],
            'comment': None,
            'confidence': confidence
        }

    def _mock_revision(self, source, target):
        """Fallback for when no API key is present (matches old logic for testing)"""
        # Simple rule-based fallback for testing purposes
        revised = target
        codes = []
        comments = []
        
        if ("can't" in source.lower() or "cannot" in source.lower()) and "peuvent" in target and "ne" not in target:
            revised = target.replace("peuvent", "ne peuvent pas")
            codes.append("TE-2")
            comments.append("Mock: Missing negation")
            
        return {
            'revised_text': revised,
            'has_revision': revised != target,
            'error_codes': codes,
            'comment': " | ".join(comments) if comments else None,
            'confidence': 50
        }

def revise_csv_with_ai(csv_path, output_path=None, progress_callback=None):
    """
    Revise a CSV file using AI.
    """
    if output_path is None:
        output_path = csv_path
    
    print(f"Starting AI revision of {csv_path}...")
    
    # Setup progress file
    job_dir = os.path.dirname(csv_path)
    progress_file = os.path.join(job_dir, 'progress.json')
    
    def update_progress(current, total, message="Processing..."):
        try:
            with open(progress_file, 'w') as f:
                json.dump({
                    'current': current,
                    'total': total,
                    'percentage': int((current / total) * 100) if total > 0 else 0,
                    'message': message,
                    'status': 'processing'
                }, f)
        except Exception as e:
            print(f"Error writing progress: {e}")
    
    reviser = LLMReviser()
    
    rows = []
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        fieldnames = list(reader.fieldnames) if reader.fieldnames else []
        
        # Add AI columns if they don't exist
        if 'AI Revision' not in fieldnames:
            if 'New target' in fieldnames:
                new_target_index = fieldnames.index('New target')
                fieldnames.insert(new_target_index + 1, 'AI Revision')
            else:
                fieldnames.append('AI Revision')
        
        if 'Confidence Score' not in fieldnames:
            fieldnames.append('Confidence Score')
        
        for row in reader:
            if 'AI Revision' not in row:
                row['AI Revision'] = ''
            if 'Confidence Score' not in row:
                row['Confidence Score'] = ''
            rows.append(row)
    
    total = len(rows)
    revised_count = 0
    
    # Initial progress
    update_progress(0, total, "Initializing AI...")
    
    for i, row in enumerate(rows):
        source = row.get('Source', '')
        target = row.get('Target', '')
        new_target = row.get('New target', '').strip()
        segment_id = row.get('ID Matecat', f'segment-{i}')
        
        # Decide which translation to check
        # Priority: Revision (if exists) > Target
        translation_to_check = new_target if new_target else target
        translation_type = "Revision" if new_target else "Target"
        
        if not translation_to_check.strip():
            continue
        
        # Update progress
        update_progress(i + 1, total, f"Reviewing {translation_type} for segment {segment_id}...")
        print(f"Progress: {i+1}/{total} ({(i+1)/total*100:.1f}%) - Reviewing {translation_type} for segment {segment_id}")
        
        if progress_callback:
            progress_callback(i + 1, total, segment_id)
        
        # Rate limiting for API - Gemini free tier allows 15 RPM
        if reviser.model:
            time.sleep(0.25)  # 4 requests/second = safe margin 
            
        try:
            result = reviser.revise(source, translation_to_check, segment_id)
            
            # Only mark as revised if there are actual error codes
            if result.get('error_codes') and len(result['error_codes']) > 0:
                row['AI Revision'] = result['revised_text']
                
                # Write to existing Code and Comment columns
                row['Code'] = ", ".join(result['error_codes'])
                
                # Add note about which version was checked
                comment = result.get('comment', '')
                if new_target:
                    comment = f"[AI - Checked: Revision] {comment}"
                else:
                    comment = f"[AI - Checked: Target] {comment}"
                row['Comment'] = comment
                
                row['Confidence Score'] = str(result['confidence'])
                revised_count += 1
            else:
                # No errors found - leave AI Revision empty but don't touch Code/Comment
                row['AI Revision'] = ""
                row['Confidence Score'] = "100"
                
        except Exception as e:
            print(f"Error processing segment {segment_id}: {e}")
            row['AI Revision'] = ""
            row['Comment'] = f"[AI Error] {str(e)}"
            row['Confidence Score'] = "0"
    
    # Write output
    with open(output_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    
    # Final progress
    update_progress(total, total, "Completed!")
    try:
        with open(progress_file, 'w') as f:
            json.dump({
                'current': total,
                'total': total,
                'percentage': 100,
                'message': "Revision Complete!",
                'status': 'completed'
            }, f)
    except:
        pass
    
    print(f"\n✓ AI revision complete!")
    print(f"  Total segments: {total}")
    print(f"  Revised: {revised_count}")
    print(f"  Output: {output_path}")
    
    return {'total': total, 'revised': revised_count}

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python ai_revision.py <input_csv> [output_csv]")
        sys.exit(1)
        
    input_csv = sys.argv[1]
    output_csv = sys.argv[2] if len(sys.argv) > 2 else input_csv
    
    revise_csv_with_ai(input_csv, output_csv)
