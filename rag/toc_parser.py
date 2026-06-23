"""
Table of Contents extraction for hierarchical document structure.

Extracts sections and subsections with page ranges from PDFs.
Returns hierarchical structure for multi-stage retrieval.
"""

import re
from typing import List, Dict


def extract_toc(pdf) -> List[Dict]:
    """
    Extract DRHP table of contents with hierarchical structure.
    
    Returns:
        List of section dictionaries with proper page ranges:
        [
            {
                "section_name": "Risk Factors",
                "section_number": "I",
                "start_page": 33,
                "end_page": 120,
                "subsections": []
            },
            ...
        ]
    """
    sections = []
    toc_entries = {}
    
    # Scan first 30 pages for TOC
    for page_idx, page in enumerate(pdf.pages[:30]):
        try:
            text = page.extract_text()
            if not text:
                continue
            
            lines = text.split("\n")
            for line in lines:
                # Match patterns like "RISK FACTORS ... 33" or "I. RISK FACTORS ... 33"
                match = re.search(r"(?:^|\s)(?:SECTION\s+)?([IVX]+\.?\s+)?(.+?)\s+\.{2,}\s*(\d+)", line)
                if match:
                    section_num = match.group(1) or ""
                    section_name = match.group(2).strip()
                    page_num = int(match.group(3))
                    
                    # Filter out boilerplate
                    if len(section_name) > 3 and page_num > 0:
                        toc_entries[section_name.lower()] = {
                            "name": section_name,
                            "number": section_num.strip(),
                            "page": page_num
                        }
        except Exception as e:
            print(f"[TOC] Error parsing page {page_idx}: {e}")
            continue
    
    if not toc_entries:
        print("[TOC] No TOC entries found, returning empty structure")
        return []
    
    # Sort by page number and compute ranges
    sorted_entries = sorted(toc_entries.items(), key=lambda x: x[1]["page"])
    
    for idx, (key, entry) in enumerate(sorted_entries):
        # End page is the start of next section, or last page of document
        end_page = sorted_entries[idx + 1][1]["page"] - 1 if idx + 1 < len(sorted_entries) else len(pdf.pages)
        
        section = {
            "section_name": entry["name"],
            "section_number": entry["number"],
            "start_page": entry["page"],
            "end_page": end_page,
            "subsections": []  # Can be filled in if needed
        }
        sections.append(section)
    
    print(f"[TOC] Extracted {len(sections)} sections from TOC")
    for s in sections[:5]:  # Log first 5
        print(f"  - {s['section_name']} (pages {s['start_page']}-{s['end_page']})")
    
    return sections