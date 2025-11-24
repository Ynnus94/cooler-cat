#!/usr/bin/env python3
"""
Create revision table with Quality Framework error codes
Columns: ID Matecat, Source, Target, New target, Code, Comment
"""
import xml.etree.ElementTree as ET
import csv
import re

# XLIFF namespace
NS = {
    'xliff': 'urn:oasis:names:tc:xliff:document:2.0',
    'mda': 'urn:oasis:names:tc:xliff:metadata:2.0',
    'memsource': 'http://www.memsource.com/xliff2.0/1.0',
    'matecat': 'https://www.matecat.com'
}

def clean_text(text):
    """Clean text from XML entities"""
    if text is None:
        return ""
    text = text.replace('&amp;', '&')
    text = text.replace('&lt;', '<')
    text = text.replace('&gt;', '>')
    text = text.replace('&quot;', '"')
    text = text.replace('&apos;', "'")
    return text

def extract_tags_from_unit(unit):
    """Extract tag mappings from originalData section"""
    tag_map = {}
    original_data = unit.find('.//xliff:originalData', NS)
    if original_data is not None:
        for data in original_data.findall('.//xliff:data', NS):
            data_id = data.get('id')
            if data_id and data.text:
                tag_content = clean_text(data.text)
                tag_map[data_id] = tag_content
    return tag_map

def replace_tags_in_element(elem, tag_map):
    """Replace ph/pc references with actual tags"""
    if elem is None:
        return ""
    
    result_parts = []
    
    if elem.text:
        result_parts.append(elem.text)
    
    for child in elem:
        tag_name = child.tag.split('}')[-1]
        
        if tag_name == 'ph':
            data_ref = child.get('dataRef')
            if data_ref and data_ref in tag_map:
                result_parts.append(tag_map[data_ref])
            if child.tail:
                result_parts.append(child.tail)
        elif tag_name == 'pc':
            data_ref_start = child.get('dataRefStart')
            if data_ref_start and data_ref_start in tag_map:
                result_parts.append(tag_map[data_ref_start])
            
            if child.text:
                result_parts.append(child.text)
            
            for subchild in child:
                result_parts.append(replace_tags_in_element(subchild, tag_map))
                if subchild.tail:
                    result_parts.append(subchild.tail)
            
            data_ref_end = child.get('dataRefEnd')
            if data_ref_end and data_ref_end in tag_map:
                result_parts.append(tag_map[data_ref_end])
            else:
                if data_ref_start and data_ref_start in tag_map:
                    opening_tag = tag_map[data_ref_start]
                    match = re.match(r'<([a-zA-Z]+)', opening_tag)
                    if match:
                        tag_name_only = match.group(1)
                        for key, value in tag_map.items():
                            if value == f'</{tag_name_only}>':
                                result_parts.append(value)
                                break
            
            if child.tail:
                result_parts.append(child.tail)
        else:
            result_parts.append(replace_tags_in_element(child, tag_map))
            if child.tail:
                result_parts.append(child.tail)
    
    return ''.join(result_parts)

def extract_text_with_tags(elem, tag_map):
    """Extract text preserving formatting tags"""
    if elem is None:
        return ""
    
    result = replace_tags_in_element(elem, tag_map)
    result = re.sub(r'\s+', ' ', result)
    result = re.sub(r'>\s+<', '><', result)
    return result.strip()

def revise_translation(source, target):
    """
    Revise French translation based on Quality Framework and Enterprise Style Guide
    Resources:
    - Quality Framework: Notion Quality Framework PDF
    - Style Guide: https://docs.google.com/spreadsheets/d/1O4mBYna7NDkWr-3vfkOtinIwDbjcRxdF7DZXwQZvHCk
    - Notion Glossary: https://notion.notion.site/Notion-Glossary-3a85fe79a5a147c0b6d7ebd55f06ae36
    """
    if not target:
        return target, None, None
    
    revised = target
    codes = []
    comments = []
    
    # TE-2: Translation Error - Major - Mistranslation (opposite meaning)
    if "peuvent être ajoutés à des groupes" in revised and "can't be added" in source.lower():
        revised = revised.replace("peuvent être ajoutés", "ne peuvent pas être ajoutés")
        codes.append("TE-2")
        comments.append("Mistranslation Major: Meaning reversed - 'can' instead of 'cannot'")
    
    # LQ-0.5: Language Quality - Grammar - "bénéficiants" -> "bénéficiant"
    if "bénéficiants" in revised:
        revised = revised.replace("bénéficiants", "bénéficiant")
        if "LQ-0.5" not in codes:
            codes.append("LQ-0.5")
            comments.append("Grammar Minor: Incorrect participle form")
    
    # TC-0.5: Terminology - "approvisionnement" -> "provisionnement" (IT context)
    if "approvisionnement" in revised and "provisioning" in source.lower():
        revised = revised.replace("approvisionnement", "provisionnement")
        if "TC-0.5" not in codes:
            codes.append("TC-0.5")
            comments.append("Terminology Minor: Wrong term - 'approvisionnement' (supply) should be 'provisionnement' (IT provisioning)")
    
    # TC-0.5: Terminology - "par place" -> "par siège" (billing context)
    if "par place" in revised and ("per seat" in source.lower() or "pay per seat" in source.lower()):
        revised = revised.replace("par place", "par siège")
        if "TC-0.5" not in codes:
            codes.append("TC-0.5")
            comments.append("Terminology Minor: Inconsistent term - 'place' should be 'siège' for billing context")
    
    # LQ-0.5: Language Quality - Grammar - Article issues with "provisionnement"
    if "l'provisionnement" in revised:
        revised = re.sub(r"l'provisionnement", "le provisionnement", revised)
        if "LQ-0.5" not in codes:
            codes.append("LQ-0.5")
            comments.append("Grammar Minor: Incorrect article form")
    
    if "d'provisionnement" in revised:
        revised = re.sub(r"d'provisionnement", "de provisionnement", revised)
        if "LQ-0.5" not in codes:
            codes.append("LQ-0.5")
            comments.append("Grammar Minor: Incorrect article form")
    
    if "de l'provisionnement" in revised:
        revised = re.sub(r"de l'provisionnement", "du provisionnement", revised)
        if "LQ-0.5" not in codes:
            codes.append("LQ-0.5")
            comments.append("Grammar Minor: Incorrect article form")
    
    if "à l'provisionnement" in revised:
        revised = re.sub(r"à l'provisionnement", "au provisionnement", revised)
        if "LQ-0.5" not in codes:
            codes.append("LQ-0.5")
            comments.append("Grammar Minor: Incorrect article form")
    
    # LQ-0.5: Language Quality - Spelling - "pdans" typo
    if "pdans" in revised:
        revised = revised.replace("pdans", "dans")
        if "LQ-0.5" not in codes:
            codes.append("LQ-0.5")
            comments.append("Spelling Minor: Typo")
    
    # LQ-0.5: Language Quality - Punctuation - spacing issues and non-breaking spaces
    original_revised = revised
    revised = re.sub(r'\s+', ' ', revised)
    
    # French typography: non-breaking space (narrow no-break space U+202F) before : ; ! ?
    # Replace regular space before these with narrow no-break space
    narrow_nbsp = '\u202f'  # Narrow no-break space
    revised = re.sub(r'\s+([:;!?])', narrow_nbsp + r'\1', revised)
    
    # Remove space before comma and period (English style)
    revised = re.sub(r'\s+([,\.])', r'\1', revised)
    
    # Ensure space after punctuation
    revised = re.sub(r'([,\.;:])\s*([A-Z])', r'\1 \2', revised)
    
    if revised != original_revised and "LQ-0.5" not in codes:
        codes.append("LQ-0.5")
        comments.append("Punctuation Minor: Spacing issues - added non-breaking spaces before : ; ! ?")
    
    # TE-0.5: Translation Error - Omission - "dans" missing
    if "Ce que nous couvrirons cette section" in revised:
        revised = re.sub(r'Ce que nous couvrirons cette section', 'Ce que nous couvrirons dans cette section', revised)
        if "TE-0.5" not in codes:
            codes.append("TE-0.5")
            comments.append("Omission Minor: Missing preposition 'dans'")
    
    # Style Guide Rule 9: Inclusive language - Put people first when mentioning disabilities
    if "utilisateurs handicapés" in revised.lower():
        revised = re.sub(r'utilisateurs handicapés', 'utilisateurs avec des handicaps', revised, flags=re.IGNORECASE)
        if "TC-0.5" not in codes:
            codes.append("TC-0.5")
            comments.append("Style Guide Rule 9: Use people-first language for disabilities")
    
    # Style Guide Rule 12: Use formal "vous" form (check for "tu" in formal contexts)
    # This is context-dependent, so we'll flag it but not auto-correct
    if re.search(r'\btu\s+(?:as|es|vas|peux|dois|veux)', revised, re.IGNORECASE):
        # Only flag if it's clearly a formal context (instructions, help text)
        if any(word in source.lower() for word in ['you', 'your', 'create', 'select', 'click', 'go to']):
            if "TC-0.5" not in codes:
                codes.append("TC-0.5")
                comments.append("Style Guide Rule 12: Consider using formal 'vous' instead of 'tu'")
    
    # Style Guide Rule 18: Avoid anglicisms - check for common ones
    anglicisms = {
        r'\bcheck\b': 'vérifier',
        r'\bweek-end\b': 'fin de semaine',
        r'\bemail\b': 'courriel',
        r'\blogin\b': 'connexion',
        r'\blogout\b': 'déconnexion',
    }
    for anglicism, french_term in anglicisms.items():
        if re.search(anglicism, revised, re.IGNORECASE):
            if "TC-0.5" not in codes:
                codes.append("TC-0.5")
                comments.append(f"Style Guide Rule 18: Consider replacing anglicism with French term")
            break
    
    # Style Guide Rule 15: Avoid repetitions - flag if same word repeated in short span
    words = re.findall(r'\b\w{4,}\b', revised.lower())
    if len(words) > 3:
        word_counts = {}
        for word in words:
            word_counts[word] = word_counts.get(word, 0) + 1
        repeated = [w for w, count in word_counts.items() if count > 2]
        if repeated:
            if "ST-0.5" not in codes:
                codes.append("ST-0.5")
                comments.append("Style Guide Rule 15: Consider using synonyms to avoid repetition")
    
    # Combine codes and comments
    code = ", ".join(codes) if codes else None
    comment = " | ".join(comments) if comments else None
    
    return revised.strip(), code, comment

def parse_xlf_file(xlf_path):
    """Parse XLF file and extract translations with Matecat IDs"""
    translations = []
    
    print(f"Parsing {xlf_path}...")
    
    tree = ET.parse(xlf_path)
    root = tree.getroot()
    
    units = root.findall('.//xliff:unit', NS)
    print(f"Found {len(units)} units")
    
    for unit in units:
        unit_id = unit.get('id', '')
        matecat_segment_id = unit.get('{https://www.matecat.com}segment-id', '')
        
        # Extract tag mappings
        tag_map = extract_tags_from_unit(unit)
        
        # Find all segments
        segments = unit.findall('.//xliff:segment', NS)
        
        for segment in segments:
            segment_id = segment.get('id', '')
            
            source_elem = segment.find('.//xliff:source', NS)
            target_elem = segment.find('.//xliff:target', NS)
            
            if source_elem is None:
                continue
            
            source_text = extract_text_with_tags(source_elem, tag_map)
            target_text = extract_text_with_tags(target_elem, tag_map) if target_elem is not None else ""
            
            # Skip empty source texts
            if not source_text or source_text.strip() == "" or source_text.strip() in ['<', '>']:
                continue
            
            # Get segment state
            segment_state = segment.get('state', '')
            
            # Revise translation
            revised_target, error_code, comment = revise_translation(source_text, target_text)
            
            # Only include if there's a revision or if it has a target
            if revised_target != target_text or target_text:
                translations.append({
                    'matecat_id': matecat_segment_id or f"{unit_id}-{segment_id}",
                    'state': segment_state,
                    'source': source_text,
                    'target': target_text,
                    'new_target': revised_target if revised_target != target_text else '',
                    'code': error_code or '',
                    'comment': comment or ''
                })
    
    return translations

def write_revision_table(translations, csv_path):
    """Write revision table with Quality Framework columns"""
    print(f"Writing {len(translations)} translations to {csv_path}...")
    
    with open(csv_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=[
            'ID Matecat',
            'State',
            'Source', 
            'Target',
            'New target',
            'Code',
            'Comment'
        ])
        writer.writeheader()
        
        for trans in translations:
            writer.writerow({
                'ID Matecat': trans['matecat_id'],
                'State': trans.get('state', ''),
                'Source': trans['source'],
                'Target': trans['target'],
                'New target': trans['new_target'],
                'Code': trans['code'],
                'Comment': trans['comment']
            })
    
    print(f"Revision table created: {csv_path}")
    
    # Summary
    with_revisions = sum(1 for t in translations if t['new_target'])
    with_codes = sum(1 for t in translations if t['code'])
    print(f"\nSummary:")
    print(f"Total translations: {len(translations)}")
    print(f"With revisions: {with_revisions}")
    print(f"With error codes: {with_codes}")

if __name__ == '__main__':
    xlf_file = '27553414#8LdupGeAn8.xlf.xlf'
    csv_file = 'revision_table.csv'
    
    translations = parse_xlf_file(xlf_file)
    write_revision_table(translations, csv_file)

