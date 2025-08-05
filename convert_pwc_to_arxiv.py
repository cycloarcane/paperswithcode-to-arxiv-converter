#!/usr/bin/env python3
"""
Papers with Code to arXiv Link Converter

Converts Papers with Code URLs to arXiv URLs in Markdown files using the backup JSON data.

Usage:
    python convert_pwc_to_arxiv.py input.md [--output output.md] [--json-file backup.json]

Author: Claude Code Assistant
License: MIT
"""

import json
import re
import sys
import argparse
from pathlib import Path
from typing import Dict, List, Tuple
import urllib.parse

def load_url_mapping(json_file: str) -> Dict[str, str]:
    """
    Load URL mapping from the Papers with Code backup JSON file.
    
    Args:
        json_file: Path to the backup JSON file
        
    Returns:
        Dictionary mapping Papers with Code URLs to arXiv URLs
    """
    mapping = {}
    print(f"Loading URL mappings from {json_file}...")
    
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        for entry in data:
            paper_url = entry.get('paper_url', '')
            paper_url_abs = entry.get('paper_url_abs', '')
            
            if paper_url and paper_url_abs:
                mapping[paper_url] = paper_url_abs
                
                # Also handle cs.paperswithcode.com variant
                if 'paperswithcode.com' in paper_url:
                    cs_url = paper_url.replace('paperswithcode.com', 'cs.paperswithcode.com')
                    mapping[cs_url] = paper_url_abs
                    
    except FileNotFoundError:
        print(f"Error: JSON file '{json_file}' not found!")
        print("Please download the backup file from:")
        print("https://github.com/paperswithcode/paperswithcode-data")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON file: {e}")
        sys.exit(1)
        
    print(f"Loaded {len(mapping)} URL mappings")
    return mapping

def find_paperswithcode_urls(content: str) -> List[str]:
    """
    Find all Papers with Code URLs in the content.
    
    Args:
        content: Text content to search
        
    Returns:
        List of unique Papers with Code URLs found
    """
    patterns = [
        r'https?://paperswithcode\.com/paper/[^\s\)\]\>\"\'\;]+',
        r'https?://cs\.paperswithcode\.com/paper/[^\s\)\]\>\"\'\;]+'
    ]
    
    urls = []
    for pattern in patterns:
        found_urls = re.findall(pattern, content)
        # Clean up URLs - remove common trailing characters that might be captured
        cleaned_urls = []
        for url in found_urls:
            # Remove trailing punctuation that's not part of URLs
            url = re.sub(r'[\"\';\)\]\>\,\.\!]+$', '', url)
            cleaned_urls.append(url)
        urls.extend(cleaned_urls)
    
    return list(set(urls))  # Remove duplicates

def convert_links(content: str, url_mapping: Dict[str, str]) -> Tuple[str, int, List[str]]:
    """
    Convert Papers with Code links to arXiv links in the content.
    
    Args:
        content: Original content
        url_mapping: Dictionary mapping PWC URLs to arXiv URLs
        
    Returns:
        Tuple of (updated_content, replaced_count, not_found_urls)
    """
    pwc_urls = find_paperswithcode_urls(content)
    replaced_count = 0
    not_found_urls = []
    
    print(f"Found {len(pwc_urls)} Papers with Code URLs")
    
    updated_content = content
    for pwc_url in pwc_urls:
        if pwc_url in url_mapping:
            arxiv_url = url_mapping[pwc_url]
            updated_content = updated_content.replace(pwc_url, arxiv_url)
            replaced_count += 1
            print(f"✓ {pwc_url} -> {arxiv_url}")
        else:
            not_found_urls.append(pwc_url)
            print(f"✗ Not found: {pwc_url}")
    
    return updated_content, replaced_count, not_found_urls

def save_not_found_list(not_found_urls: List[str], output_file: str):
    """Save list of URLs that couldn't be converted for manual lookup."""
    if not not_found_urls:
        return
        
    not_found_file = output_file.replace('.md', '_not_found.txt')
    with open(not_found_file, 'w', encoding='utf-8') as f:
        f.write("URLs not found in backup data - manual lookup needed:\n\n")
        for url in not_found_urls:
            f.write(f"{url}\n")
            # Extract paper title from URL for easier searching
            paper_slug = url.split('/')[-1]
            paper_title = paper_slug.replace('-', ' ').title()
            f.write(f"  Search term: {paper_title}\n")
            f.write(f"  arXiv search: https://arxiv.org/search/?query={urllib.parse.quote(paper_title)}\n\n")
    
    print(f"URLs requiring manual lookup saved to: {not_found_file}")

def main():
    parser = argparse.ArgumentParser(
        description="Convert Papers with Code URLs to arXiv URLs in Markdown files"
    )
    parser.add_argument(
        'input_file', 
        help='Input Markdown file to convert'
    )
    parser.add_argument(
        '--output', '-o',
        help='Output file path (default: input_file_arxiv.md)'
    )
    parser.add_argument(
        '--json-file', '-j',
        default='links-between-papers-and-code.json',
        help='Path to Papers with Code backup JSON file'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be converted without making changes'
    )
    
    args = parser.parse_args()
    
    # Validate input file
    input_path = Path(args.input_file)
    if not input_path.exists():
        print(f"Error: Input file '{args.input_file}' not found!")
        sys.exit(1)
    
    # Determine output file
    if args.output:
        output_file = args.output
    else:
        output_file = input_path.stem + '_arxiv' + input_path.suffix
    
    # Load URL mapping
    url_mapping = load_url_mapping(args.json_file)
    
    # Read input file
    try:
        with open(args.input_file, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading input file: {e}")
        sys.exit(1)
    
    # Convert links
    updated_content, replaced_count, not_found_urls = convert_links(content, url_mapping)
    
    # Print summary
    total_urls = len(find_paperswithcode_urls(content))
    print(f"\nConversion Summary:")
    print(f"- Total URLs found: {total_urls}")
    print(f"- Successfully converted: {replaced_count}")
    print(f"- Conversion rate: {replaced_count/total_urls*100:.1f}%" if total_urls > 0 else "- No URLs found")
    print(f"- Manual lookup needed: {len(not_found_urls)}")
    
    if args.dry_run:
        print(f"\nDry run completed. No files were modified.")
        return
    
    # Save output file
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(updated_content)
        print(f"\nConverted file saved as: {output_file}")
    except Exception as e:
        print(f"Error writing output file: {e}")
        sys.exit(1)
    
    # Save list of URLs that need manual lookup
    if not_found_urls:
        save_not_found_list(not_found_urls, output_file)
        print(f"\n⚠️  {len(not_found_urls)} URLs require manual lookup and replacement.")
        print("Check the *_not_found.txt file for details.")
    else:
        print(f"\n🎉 All URLs successfully converted!")

if __name__ == "__main__":
    main()