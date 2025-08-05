#!/usr/bin/env python3
"""
Helper script to search for arXiv links for papers not found in the backup data.

Usage:
    python search_missing_papers.py missing_papers.txt

This script assists with manual lookup of papers that couldn't be automatically converted.

Author: Claude Code Assistant
License: MIT
"""

import argparse
import sys
import urllib.parse
import webbrowser
from pathlib import Path
from typing import List

def extract_paper_info_from_url(pwc_url: str) -> dict:
    """Extract paper information from Papers with Code URL."""
    # Extract paper slug from URL
    if '/paper/' in pwc_url:
        paper_slug = pwc_url.split('/paper/')[-1]
        # Remove any query parameters or fragments
        paper_slug = paper_slug.split('?')[0].split('#')[0]
        
        # Convert slug to potential title
        title_words = paper_slug.replace('-', ' ').split()
        paper_title = ' '.join(word.capitalize() for word in title_words)
        
        return {
            'url': pwc_url,
            'slug': paper_slug,
            'title': paper_title
        }
    
    return {'url': pwc_url, 'slug': '', 'title': ''}

def search_arxiv_for_paper(paper_info: dict):
    """Generate arXiv search URLs and search terms for a paper."""
    title = paper_info['title']
    slug = paper_info['slug']
    
    search_strategies = [
        {
            'name': 'Title Search',
            'query': title,
            'url': f"https://arxiv.org/search/?query={urllib.parse.quote(title)}&searchtype=title"
        },
        {
            'name': 'All Fields Search',
            'query': title,
            'url': f"https://arxiv.org/search/?query={urllib.parse.quote(title)}&searchtype=all"
        },
        {
            'name': 'Google Scholar',
            'query': f'"{title}" site:arxiv.org',
            'url': f"https://scholar.google.com/scholar?q={urllib.parse.quote(f'"{title}" site:arxiv.org')}"
        }
    ]
    
    return search_strategies

def process_missing_papers_file(file_path: str, interactive: bool = True, open_browser: bool = False):
    """Process a file containing missing Papers with Code URLs."""
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found!")
        return
    
    # Extract URLs from the file
    lines = content.split('\n')
    urls = []
    for line in lines:
        line = line.strip()
        if line.startswith('http') and 'paperswithcode.com' in line:
            urls.append(line)
    
    if not urls:
        print("No Papers with Code URLs found in the file.")
        return
    
    print(f"Found {len(urls)} Papers with Code URLs to process\n")
    
    results = []
    
    for i, url in enumerate(urls, 1):
        print(f"{'='*60}")
        print(f"Paper {i}/{len(urls)}")
        print(f"{'='*60}")
        
        paper_info = extract_paper_info_from_url(url)
        
        print(f"Papers with Code URL: {paper_info['url']}")
        print(f"Extracted Title: {paper_info['title']}")
        print(f"Paper Slug: {paper_info['slug']}")
        print()
        
        search_strategies = search_arxiv_for_paper(paper_info)
        
        print("Search strategies:")
        for j, strategy in enumerate(search_strategies, 1):
            print(f"  {j}. {strategy['name']}: {strategy['url']}")
        
        if open_browser:
            print(f"\nOpening arXiv search in browser...")
            webbrowser.open(search_strategies[0]['url'])
        
        arxiv_url = None
        if interactive:
            while True:
                arxiv_input = input(f"\nEnter arXiv URL for this paper (or 'skip' to skip): ").strip()
                
                if arxiv_input.lower() == 'skip':
                    break
                elif arxiv_input.startswith('https://arxiv.org/'):
                    arxiv_url = arxiv_input
                    break
                elif arxiv_input:
                    print("Please enter a valid arXiv URL starting with 'https://arxiv.org/' or 'skip'")
                else:
                    break
        
        result = {
            'paperswithcode_url': paper_info['url'],
            'title': paper_info['title'],
            'arxiv_url': arxiv_url,
            'search_strategies': search_strategies
        }
        results.append(result)
        
        if interactive and arxiv_url:
            print(f"✓ Mapped: {paper_info['url']} -> {arxiv_url}")
        
        print()
    
    # Save results
    output_file = file_path.replace('.txt', '_search_results.txt')
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("Papers with Code to arXiv Mapping Results\n")
        f.write("="*50 + "\n\n")
        
        successful_mappings = []
        
        for result in results:
            f.write(f"Papers with Code URL: {result['paperswithcode_url']}\n")
            f.write(f"Extracted Title: {result['title']}\n")
            
            if result['arxiv_url']:
                f.write(f"arXiv URL: {result['arxiv_url']}\n")
                f.write(f"Replacement: {result['paperswithcode_url']} -> {result['arxiv_url']}\n")
                successful_mappings.append((result['paperswithcode_url'], result['arxiv_url']))
            else:
                f.write("Status: Not found - requires manual search\n")
                f.write("Search strategies:\n")
                for strategy in result['search_strategies']:
                    f.write(f"  - {strategy['name']}: {strategy['url']}\n")
            
            f.write("\n" + "-"*40 + "\n\n")
        
        if successful_mappings:
            f.write("\nSUCCESSFUL MAPPINGS FOR BATCH REPLACEMENT:\n")
            f.write("="*50 + "\n")
            for pwc_url, arxiv_url in successful_mappings:
                f.write(f"{pwc_url} -> {arxiv_url}\n")
    
    print(f"Results saved to: {output_file}")
    
    if interactive:
        mapped_count = len([r for r in results if r['arxiv_url']])
        print(f"\nSummary:")
        print(f"- Total papers processed: {len(results)}")
        print(f"- Successfully mapped: {mapped_count}")
        print(f"- Still need manual lookup: {len(results) - mapped_count}")

def main():
    parser = argparse.ArgumentParser(
        description="Search for arXiv links for papers not found in the backup data"
    )
    parser.add_argument(
        'input_file',
        help='File containing Papers with Code URLs to search for'
    )
    parser.add_argument(
        '--non-interactive',
        action='store_true',
        help='Run in non-interactive mode (just generate search URLs)'
    )
    parser.add_argument(
        '--open-browser',
        action='store_true',
        help='Automatically open arXiv search in browser for each paper'
    )
    
    args = parser.parse_args()
    
    if not Path(args.input_file).exists():
        print(f"Error: Input file '{args.input_file}' not found!")
        sys.exit(1)
    
    interactive = not args.non_interactive
    
    if interactive:
        print("Papers with Code to arXiv Search Assistant")
        print("="*40)
        print("This script will help you find arXiv URLs for papers that couldn't be")
        print("automatically converted. For each paper, you'll be given search URLs")
        print("and can enter the corresponding arXiv URL when found.\n")
    
    process_missing_papers_file(args.input_file, interactive, args.open_browser)

if __name__ == "__main__":
    main()