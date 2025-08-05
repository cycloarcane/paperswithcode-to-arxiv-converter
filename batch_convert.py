#!/usr/bin/env python3
"""
Batch converter for multiple Markdown files.

Usage:
    python batch_convert.py file1.md file2.md file3.md
    python batch_convert.py *.md
    python batch_convert.py --directory ./docs --pattern "*.md"

Author: Claude Code Assistant
License: MIT
"""

import argparse
import sys
from pathlib import Path
from typing import List
import subprocess
import glob

def find_markdown_files(directory: str, pattern: str = "*.md") -> List[Path]:
    """Find all markdown files in a directory matching the pattern."""
    directory_path = Path(directory)
    if not directory_path.exists():
        print(f"Error: Directory '{directory}' not found!")
        return []
    
    files = list(directory_path.glob(pattern))
    return [f for f in files if f.is_file()]

def convert_file(input_file: Path, json_file: str, dry_run: bool = False) -> bool:
    """Convert a single file using the main converter script."""
    cmd = [
        sys.executable, 
        'convert_pwc_to_arxiv.py', 
        str(input_file),
        '--json-file', json_file
    ]
    
    if dry_run:
        cmd.append('--dry-run')
    
    try:
        print(f"\n{'='*60}")
        print(f"Converting: {input_file}")
        print(f"{'='*60}")
        
        result = subprocess.run(cmd, check=True, capture_output=False)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error converting {input_file}: {e}")
        return False
    except FileNotFoundError:
        print("Error: convert_pwc_to_arxiv.py not found in current directory!")
        return False

def main():
    parser = argparse.ArgumentParser(
        description="Batch convert multiple Markdown files from Papers with Code to arXiv links"
    )
    
    # Input methods - mutually exclusive
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument(
        'files',
        nargs='*',
        help='List of Markdown files to convert'
    )
    input_group.add_argument(
        '--directory', '-d',
        help='Directory containing Markdown files to convert'
    )
    
    parser.add_argument(
        '--pattern', '-p',
        default='*.md',
        help='File pattern to match (default: *.md)'
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
    parser.add_argument(
        '--continue-on-error',
        action='store_true',
        help='Continue processing other files if one fails'
    )
    
    args = parser.parse_args()
    
    # Determine files to process
    if args.directory:
        files_to_process = find_markdown_files(args.directory, args.pattern)
        if not files_to_process:
            print(f"No files matching '{args.pattern}' found in '{args.directory}'")
            sys.exit(1)
    else:
        files_to_process = []
        for file_pattern in args.files:
            if '*' in file_pattern or '?' in file_pattern:
                # Handle glob patterns
                matched_files = glob.glob(file_pattern)
                files_to_process.extend([Path(f) for f in matched_files])
            else:
                files_to_process.append(Path(file_pattern))
        
        # Validate files exist
        missing_files = [f for f in files_to_process if not f.exists()]
        if missing_files:
            print("Error: The following files were not found:")
            for f in missing_files:
                print(f"  - {f}")
            sys.exit(1)
    
    if not files_to_process:
        print("No files to process!")
        sys.exit(1)
    
    # Check if JSON file exists
    json_path = Path(args.json_file)
    if not json_path.exists():
        print(f"Error: JSON backup file '{args.json_file}' not found!")
        print("Please download it from: https://github.com/paperswithcode/paperswithcode-data")
        sys.exit(1)
    
    # Process files
    print(f"Found {len(files_to_process)} files to process:")
    for f in files_to_process:
        print(f"  - {f}")
    
    if args.dry_run:
        print(f"\nDry run mode - no files will be modified")
    
    successful = 0
    failed = 0
    
    for file_path in files_to_process:
        success = convert_file(file_path, args.json_file, args.dry_run)
        
        if success:
            successful += 1
        else:
            failed += 1
            if not args.continue_on_error:
                print(f"\nStopping due to error. Use --continue-on-error to process remaining files.")
                break
    
    # Final summary
    print(f"\n{'='*60}")
    print(f"BATCH CONVERSION SUMMARY")
    print(f"{'='*60}")
    print(f"Total files processed: {successful + failed}")
    print(f"Successful conversions: {successful}")
    print(f"Failed conversions: {failed}")
    
    if failed > 0:
        print(f"\n⚠️  {failed} files failed to convert. Check the output above for details.")
        sys.exit(1)
    else:
        print(f"\n🎉 All files converted successfully!")

if __name__ == "__main__":
    main()