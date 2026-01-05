#!/usr/bin/env python3
"""
Line Counter for Production-Ready Code

This script counts the number of lines in production-ready code files,
excluding tests, samples, and documentation.
"""

import os
from pathlib import Path
from typing import Dict, List, Tuple


def is_production_file(filepath: Path) -> bool:
    """
    Determine if a file is production-ready code.
    
    Excludes:
    - Test files
    - Sample/example files
    - Documentation files
    - Git files
    - Build artifacts
    """
    filepath_str = str(filepath)
    
    # Exclude patterns
    exclude_patterns = [
        'test_',
        'Sample_',
        '.git',
        '__pycache__',
        'node_modules',
        'output_json',
        '.pyc',
        '.pyo',
        'claude.md',
        '.gitignore'
    ]
    
    for pattern in exclude_patterns:
        if pattern in filepath_str:
            return False
    
    # Include only specific extensions
    production_extensions = ['.py', '.js', '.html', '.css', '.json']
    if filepath.suffix in production_extensions:
        # Exclude sample JSON files
        if filepath.suffix == '.json' and 'Sample' in filepath_str:
            return False
        return True
    
    return False


def count_lines_in_file(filepath: Path) -> Tuple[int, int, int]:
    """
    Count total lines, code lines, and comment/blank lines in a file.
    
    Returns:
        Tuple of (total_lines, code_lines, non_code_lines)
    """
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
        
        total_lines = len(lines)
        code_lines = 0
        non_code_lines = 0
        
        extension = filepath.suffix
        
        for line in lines:
            stripped = line.strip()
            
            # Empty line
            if not stripped:
                non_code_lines += 1
                continue
            
            # Comment detection based on file type
            is_comment = False
            if extension == '.py':
                is_comment = stripped.startswith('#')
            elif extension in ['.js', '.css']:
                is_comment = (stripped.startswith('//') or 
                             stripped.startswith('/*') or 
                             stripped.startswith('*'))
            elif extension == '.html':
                is_comment = (stripped.startswith('<!--') or 
                             stripped.startswith('-->'))
            
            if is_comment:
                non_code_lines += 1
            else:
                code_lines += 1
        
        return total_lines, code_lines, non_code_lines
    
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
        return 0, 0, 0


def count_production_lines(root_dir: Path) -> Dict[str, any]:
    """
    Count lines in all production-ready files.
    
    Returns:
        Dictionary with statistics
    """
    production_files = []
    
    # Walk through directory
    for root, dirs, files in os.walk(root_dir):
        # Skip excluded directories
        dirs[:] = [d for d in dirs if not d.startswith('.') and 
                  d not in ['__pycache__', 'node_modules', 'output_json', 'Sample_json_outputs']]
        
        for file in files:
            filepath = Path(root) / file
            if is_production_file(filepath):
                production_files.append(filepath)
    
    # Count lines
    file_stats = []
    total_lines = 0
    total_code = 0
    total_non_code = 0
    
    for filepath in sorted(production_files):
        lines, code, non_code = count_lines_in_file(filepath)
        total_lines += lines
        total_code += code
        total_non_code += non_code
        
        relative_path = filepath.relative_to(root_dir)
        file_stats.append({
            'file': str(relative_path),
            'total': lines,
            'code': code,
            'non_code': non_code
        })
    
    return {
        'files': file_stats,
        'summary': {
            'file_count': len(production_files),
            'total_lines': total_lines,
            'code_lines': total_code,
            'non_code_lines': total_non_code
        }
    }


def print_report(stats: Dict[str, any]):
    """Print a formatted report of line counts."""
    print("\n" + "=" * 80)
    print("PRODUCTION-READY CODE LINE COUNT REPORT")
    print("=" * 80)
    print()
    
    # File details
    print(f"{'File':<50} {'Total':>10} {'Code':>10} {'Non-Code':>10}")
    print("-" * 80)
    
    for file_stat in stats['files']:
        print(f"{file_stat['file']:<50} "
              f"{file_stat['total']:>10} "
              f"{file_stat['code']:>10} "
              f"{file_stat['non_code']:>10}")
    
    print("-" * 80)
    
    # Summary
    summary = stats['summary']
    print(f"{'TOTAL':<50} "
          f"{summary['total_lines']:>10} "
          f"{summary['code_lines']:>10} "
          f"{summary['non_code_lines']:>10}")
    
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Number of production files: {summary['file_count']}")
    print(f"Total lines: {summary['total_lines']}")
    print(f"Code lines (excluding comments/blanks): {summary['code_lines']}")
    print(f"Non-code lines (comments + blank): {summary['non_code_lines']}")
    
    if summary['total_lines'] > 0:
        code_percentage = (summary['code_lines'] / summary['total_lines']) * 100
        print(f"Code percentage: {code_percentage:.1f}%")
    
    print("=" * 80)
    print()


def main():
    """Main entry point."""
    # Get repository root (where this script is located)
    repo_root = Path(__file__).parent
    
    print(f"Analyzing production-ready code in: {repo_root}")
    print()
    
    stats = count_production_lines(repo_root)
    print_report(stats)
    
    return stats['summary']['total_lines']


if __name__ == '__main__':
    exit_code = main()
