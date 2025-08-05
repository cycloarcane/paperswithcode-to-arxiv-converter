#!/usr/bin/env python3
"""
Script to demonstrate the converter works with various file formats.

Usage:
    python test_various_formats.py

This creates sample files in different formats and tests the converter on each.
"""

import os
import sys
import subprocess
import json
from pathlib import Path

def create_test_files():
    """Create test files in various formats with Papers with Code URLs."""
    
    # Minimal JSON backup for testing
    test_backup = [
        {
            "paper_url": "https://paperswithcode.com/paper/attention-is-all-you-need",
            "paper_title": "Attention Is All You Need",
            "paper_arxiv_id": "1706.03762",
            "paper_url_abs": "https://arxiv.org/abs/1706.03762v5",
            "paper_url_pdf": "https://arxiv.org/pdf/1706.03762v5.pdf"
        },
        {
            "paper_url": "https://paperswithcode.com/paper/bert-pre-training-of-deep-bidirectional",
            "paper_title": "BERT: Pre-training of Deep Bidirectional Transformers",
            "paper_arxiv_id": "1810.04805",
            "paper_url_abs": "https://arxiv.org/abs/1810.04805v2",
            "paper_url_pdf": "https://arxiv.org/pdf/1810.04805v2.pdf"
        }
    ]
    
    with open('test_backup.json', 'w') as f:
        json.dump(test_backup, f, indent=2)
    
    # Test files in different formats
    test_files = {
        'test.html': '''<!DOCTYPE html>
<html>
<head><title>Papers</title></head>
<body>
    <p><a href="https://paperswithcode.com/paper/attention-is-all-you-need">Attention Paper</a></p>
    <p>BERT: https://paperswithcode.com/paper/bert-pre-training-of-deep-bidirectional</p>
</body>
</html>''',
        
        'test.tex': r'''\\documentclass{article}
\\begin{document}
\\href{https://paperswithcode.com/paper/attention-is-all-you-need}{Attention Paper}
\\url{https://paperswithcode.com/paper/bert-pre-training-of-deep-bidirectional}
\\end{document}''',
        
        'test.rst': '''Papers
======

`Attention Paper <https://paperswithcode.com/paper/attention-is-all-you-need>`_

BERT: https://paperswithcode.com/paper/bert-pre-training-of-deep-bidirectional''',
        
        'test.txt': '''Research Papers:
1. https://paperswithcode.com/paper/attention-is-all-you-need
2. https://paperswithcode.com/paper/bert-pre-training-of-deep-bidirectional''',
        
        'test.json': '''{
  "papers": [
    {
      "title": "Attention",
      "url": "https://paperswithcode.com/paper/attention-is-all-you-need"
    },
    {
      "title": "BERT", 
      "url": "https://paperswithcode.com/paper/bert-pre-training-of-deep-bidirectional"
    }
  ]
}''',
        
        'test.py': '''"""
Research papers module
"""

# Reference: https://paperswithcode.com/paper/attention-is-all-you-need
ATTENTION_URL = "https://paperswithcode.com/paper/attention-is-all-you-need"
BERT_URL = "https://paperswithcode.com/paper/bert-pre-training-of-deep-bidirectional"

def get_papers():
    """Get paper URLs"""
    return [ATTENTION_URL, BERT_URL]''',
        
        'test.yml': '''papers:
  - title: "Attention Is All You Need"
    url: "https://paperswithcode.com/paper/attention-is-all-you-need"
  - title: "BERT"
    url: "https://paperswithcode.com/paper/bert-pre-training-of-deep-bidirectional"''',
    }
    
    for filename, content in test_files.items():
        with open(filename, 'w') as f:
            f.write(content)
    
    print(f"✓ Created {len(test_files)} test files in different formats")
    return list(test_files.keys())

def test_converter_on_file(filename):
    """Test the converter on a specific file."""
    try:
        result = subprocess.run([
            sys.executable, 
            'convert_pwc_to_arxiv.py', 
            filename,
            '--json-file', 'test_backup.json'
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            # Extract key metrics
            converted_count = 0
            total_count = 0
            for line in lines:
                if "Successfully converted:" in line:
                    converted_count = int(line.split(':')[1].strip())
                elif "Total URLs found:" in line:
                    total_count = int(line.split(':')[1].strip())
            
            return True, converted_count, total_count
        else:
            return False, 0, 0
            
    except Exception as e:
        print(f"Error testing {filename}: {e}")
        return False, 0, 0

def cleanup_test_files(filenames):
    """Clean up test files."""
    files_to_remove = ['test_backup.json']
    files_to_remove.extend(filenames)
    files_to_remove.extend([f + '_arxiv' + Path(f).suffix for f in filenames])
    files_to_remove.extend([f + '_arxiv_not_found.txt' for f in filenames])
    
    for filename in files_to_remove:
        if Path(filename).exists():
            os.remove(filename)

def main():
    print("Testing Converter Versatility Across File Formats")
    print("=" * 50)
    
    if not Path('convert_pwc_to_arxiv.py').exists():
        print("✗ convert_pwc_to_arxiv.py not found!")
        sys.exit(1)
    
    # Create test files
    test_filenames = create_test_files()
    
    results = []
    total_success = 0
    total_files = len(test_filenames)
    
    print(f"\nTesting converter on {total_files} different file formats:")
    print("-" * 50)
    
    for filename in test_filenames:
        file_ext = Path(filename).suffix
        success, converted, total = test_converter_on_file(filename)
        
        if success:
            status = "✓ PASS"
            total_success += 1
            rate = f"{converted}/{total}" if total > 0 else "0/0"
        else:
            status = "✗ FAIL"
            rate = "N/A"
        
        print(f"{filename:<15} {file_ext:<6} {status:<8} ({rate} URLs)")
        results.append((filename, file_ext, success, converted, total))
    
    print("-" * 50)
    print(f"\nSUMMARY:")
    print(f"✓ Formats tested: {total_files}")
    print(f"✓ Successful conversions: {total_success}")
    print(f"✓ Success rate: {total_success/total_files*100:.1f}%")
    
    if total_success == total_files:
        print(f"\n🎉 ALL FILE FORMATS WORK! The converter is truly versatile.")
    else:
        print(f"\n⚠️  Some formats had issues. Check individual results above.")
        
    # Show format versatility
    successful_formats = [Path(r[0]).suffix for r in results if r[2]]
    if successful_formats:
        print(f"\n📄 Supported formats: {', '.join(set(successful_formats))}")
    
    # Cleanup
    cleanup_test_files(test_filenames)
    print(f"\n✓ Cleaned up test files")

if __name__ == "__main__":
    main()