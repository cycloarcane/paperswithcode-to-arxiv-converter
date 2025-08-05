#!/usr/bin/env python3
"""
Simple test script to verify the converter works correctly.

Usage:
    python test_converter.py

This script creates a minimal test case and runs the converter to verify functionality.

Author: Claude Code Assistant
License: MIT
"""

import os
import sys
import subprocess
import json
from pathlib import Path

def create_test_data():
    """Create minimal test data for the converter."""
    # Create minimal JSON data with a few known papers
    test_data = [
        {
            "paper_url": "https://paperswithcode.com/paper/attention-is-all-you-need",
            "paper_title": "Attention Is All You Need",
            "paper_arxiv_id": "1706.03762",
            "paper_url_abs": "https://arxiv.org/abs/1706.03762v5",
            "paper_url_pdf": "https://arxiv.org/pdf/1706.03762v5.pdf",
            "repo_url": "https://github.com/tensorflow/tensor2tensor",
            "is_official": True,
            "mentioned_in_paper": False,
            "mentioned_in_github": True,
            "framework": "tensorflow"
        },
        {
            "paper_url": "https://paperswithcode.com/paper/bert-pre-training-of-deep-bidirectional",
            "paper_title": "BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding",
            "paper_arxiv_id": "1810.04805",
            "paper_url_abs": "https://arxiv.org/abs/1810.04805v2",
            "paper_url_pdf": "https://arxiv.org/pdf/1810.04805v2.pdf",
            "repo_url": "https://github.com/google-research/bert",
            "is_official": True,
            "mentioned_in_paper": False,
            "mentioned_in_github": True,
            "framework": "tensorflow"
        }
    ]
    
    # Write test JSON file
    with open('test_links.json', 'w') as f:
        json.dump(test_data, f, indent=2)
    
    # Create test markdown file
    test_md = """# Test Paper Collection

## Transformer Papers

- **Attention Is All You Need**
  **Paper**: [Link](https://paperswithcode.com/paper/attention-is-all-you-need)
  **Summary**: Introduces the Transformer architecture.

- **BERT Paper**
  **Paper**: [Link](https://paperswithcode.com/paper/bert-pre-training-of-deep-bidirectional)
  **Summary**: Pre-trained bidirectional representations.

## References

1. [Attention paper](https://paperswithcode.com/paper/attention-is-all-you-need)
"""
    
    with open('test_input.md', 'w') as f:
        f.write(test_md)
    
    print("✓ Created test data files")

def run_converter_test():
    """Run the converter on test data."""
    try:
        # Run the converter
        result = subprocess.run([
            sys.executable, 
            'convert_pwc_to_arxiv.py', 
            'test_input.md',
            '--json-file', 'test_links.json',
            '--output', 'test_output.md'
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✓ Converter ran successfully")
            print("Output:")
            print(result.stdout)
            return True
        else:
            print("✗ Converter failed")
            print("Error:")
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"✗ Error running converter: {e}")
        return False

def verify_output():
    """Verify the output is correct."""
    if not Path('test_output.md').exists():
        print("✗ Output file not created")
        return False
    
    with open('test_output.md', 'r') as f:
        output = f.read()
    
    # Check that Papers with Code links were replaced
    if 'paperswithcode.com' in output:
        print("✗ Some Papers with Code links were not replaced")
        return False
    
    # Check that arXiv links are present
    if 'arxiv.org/abs/1706.03762' not in output:
        print("✗ Expected arXiv link not found")
        return False
    
    if 'arxiv.org/abs/1810.04805' not in output:
        print("✗ Expected BERT arXiv link not found")
        return False
    
    print("✓ Output verification passed")
    return True

def cleanup():
    """Clean up test files."""
    test_files = [
        'test_links.json',
        'test_input.md', 
        'test_output.md'
    ]
    
    for file in test_files:
        if Path(file).exists():
            os.remove(file)
    
    print("✓ Cleaned up test files")

def main():
    print("Papers with Code to arXiv Converter - Test Suite")
    print("="*50)
    
    # Check if main converter script exists
    if not Path('convert_pwc_to_arxiv.py').exists():
        print("✗ convert_pwc_to_arxiv.py not found!")
        print("Make sure you're running this from the converter directory.")
        sys.exit(1)
    
    try:
        # Run tests
        create_test_data()
        
        if run_converter_test() and verify_output():
            print("\n🎉 All tests passed! The converter is working correctly.")
            success = True
        else:
            print("\n❌ Some tests failed. Check the output above for details.")
            success = False
        
        cleanup()
        
        if not success:
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user.")
        cleanup()
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        cleanup()
        sys.exit(1)

if __name__ == "__main__":
    main()