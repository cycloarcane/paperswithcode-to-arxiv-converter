# Usage Guide

This guide provides detailed instructions for using the Papers with Code to arXiv Link Converter.

## Quick Start

1. **Download the Papers with Code backup data**:
   ```bash
   # Download from the official backup repository
   wget https://github.com/paperswithcode/paperswithcode-data/raw/main/links-between-papers-and-code.json
   ```

2. **Convert a single file**:
   ```bash
   python convert_pwc_to_arxiv.py your_paper_list.md
   ```

3. **Check the output**:
   - Converted file: `your_paper_list_arxiv.md`
   - Missing papers (if any): `your_paper_list_arxiv_not_found.txt`

## Detailed Usage

### Single File Conversion

```bash
# Basic usage
python convert_pwc_to_arxiv.py README.md

# Specify custom output file
python convert_pwc_to_arxiv.py README.md --output README_updated.md

# Use custom JSON backup file
python convert_pwc_to_arxiv.py README.md --json-file my_backup.json

# Dry run (see what would be changed without making changes)
python convert_pwc_to_arxiv.py README.md --dry-run
```

### Batch Processing

```bash
# Convert multiple specific files
python batch_convert.py file1.md file2.md file3.md

# Convert all markdown files in current directory
python batch_convert.py *.md

# Convert all markdown files in a directory
python batch_convert.py --directory ./docs

# Convert with custom pattern
python batch_convert.py --directory ./papers --pattern "*.markdown"

# Continue processing even if some files fail
python batch_convert.py --continue-on-error *.md

# Dry run for batch processing
python batch_convert.py --dry-run *.md
```

### Manual Search for Missing Papers

If some papers aren't found in the backup data:

```bash
# Interactive search assistant
python search_missing_papers.py your_file_arxiv_not_found.txt

# Non-interactive (just generate search URLs)
python search_missing_papers.py --non-interactive missing_papers.txt

# Automatically open search URLs in browser
python search_missing_papers.py --open-browser missing_papers.txt
```

## File Formats Supported

### Input Formats
- **Markdown files** (`.md`, `.markdown`)
- Any text file containing Papers with Code URLs

### URL Patterns Detected
- `https://paperswithcode.com/paper/paper-name`
- `https://cs.paperswithcode.com/paper/paper-name`
- URLs with query parameters: `?tab=results&sort=stars`
- URLs with fragments: `#abstract`

### Output
- **Converted file**: Original filename with `_arxiv` suffix
- **Missing papers list**: Filename with `_not_found.txt` suffix
- **Search results**: For manual lookup assistance

## Examples

### Before Conversion
```markdown
- **Attention Is All You Need**
  **Paper**: [Link](https://paperswithcode.com/paper/attention-is-all-you-need)
  **Summary**: Introduces the Transformer architecture.

- **BERT Paper**
  Link: https://paperswithcode.com/paper/bert-pre-training-of-deep-bidirectional
```

### After Conversion
```markdown
- **Attention Is All You Need**
  **Paper**: [Link](https://arxiv.org/abs/1706.03762v5)
  **Summary**: Introduces the Transformer architecture.

- **BERT Paper**
  Link: https://arxiv.org/abs/1810.04805v2
```

## Troubleshooting

### Common Issues

**Error: JSON file not found**
```
Error: JSON file 'links-between-papers-and-code.json' not found!
Please download the backup file from:
https://github.com/paperswithcode/paperswithcode-data
```
**Solution**: Download the backup JSON file as shown in Quick Start.

**Error: Input file not found**
```
Error: Input file 'myfile.md' not found!
```
**Solution**: Check that the file path is correct and the file exists.

**Low conversion rate**
```
Conversion rate: 45.2%
Manual lookup needed: 12
```
**Solution**: Use the `search_missing_papers.py` script to find arXiv URLs for the remaining papers.

### Performance Tips

1. **Large files**: The converter handles large files efficiently, but very large repositories may take a few minutes.

2. **Memory usage**: The JSON backup file is ~150MB and loads into memory. Ensure you have sufficient RAM.

3. **Network**: No internet connection required for basic conversion (only for manual search assistance).

### Validation

Use the test script to verify everything works:
```bash
python test_converter.py
```

This will run a simple test with known papers to ensure the converter is working correctly.

## Integration with Git

### Before committing conversions:
```bash
# Check what will be changed
python convert_pwc_to_arxiv.py README.md --dry-run

# Run the conversion
python convert_pwc_to_arxiv.py README.md

# Review changes
git diff README_arxiv.md

# If satisfied, replace original and commit
mv README_arxiv.md README.md
git add README.md
git commit -m "Convert Papers with Code links to arXiv links"
```

### Batch processing for entire repository:
```bash
# Find all markdown files and convert them
find . -name "*.md" -exec python /path/to/batch_convert.py {} \;

# Or use the batch converter directly
python batch_convert.py --directory . --pattern "**/*.md"
```

## Support

If you encounter issues:

1. Check this usage guide for common solutions
2. Run the test script to verify installation
3. Check that you have the backup JSON file
4. Create an issue on GitHub with details about your problem

## Advanced Usage

### Custom URL Patterns

To extend the converter for additional URL patterns, modify the `find_paperswithcode_urls()` function in `convert_pwc_to_arxiv.py`:

```python
patterns = [
    r'https?://paperswithcode\.com/paper/[^\s\)\]\>]+',
    r'https?://cs\.paperswithcode\.com/paper/[^\s\)\]\>]+',
    # Add custom patterns here
]
```

### Integration with Other Tools

The converter can be easily integrated into existing workflows:

```bash
# Pre-commit hook example
#!/bin/bash
if [ -f "links-between-papers-and-code.json" ]; then
    python convert_pwc_to_arxiv.py README.md --output README_temp.md
    if [ $? -eq 0 ]; then
        mv README_temp.md README.md
    fi
fi
```