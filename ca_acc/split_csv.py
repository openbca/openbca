#!/usr/bin/env python3
"""
Script to split a large CSV file into 10 equal-sized smaller CSV files.

Usage:
    python split_csv.py <input_file.csv>
    python split_csv.py <input_file.csv> [output_prefix]
"""

import csv
import os
import sys
import math
from pathlib import Path


def split_csv(input_file, output_prefix=None, num_parts=10):
    """
    Split a CSV file into multiple equal-sized parts.
    
    Args:
        input_file: Path to the input CSV file
        output_prefix: Prefix for output files (default: input file name without extension)
        num_parts: Number of parts to split into (default: 10)
    """
    input_path = Path(input_file)
    
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_file}")
    
    # Set output prefix if not provided
    if output_prefix is None:
        output_prefix = input_path.stem
    
    # Count total rows first (excluding header)
    print(f"Reading {input_file}...")
    with open(input_path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        header = next(reader)  # Read header
        total_rows = sum(1 for _ in reader)
    
    print(f"Total rows: {total_rows}")
    print(f"Splitting into {num_parts} parts...")
    
    # Calculate rows per part
    rows_per_part = math.ceil(total_rows / num_parts)
    
    # Reset and read again to split
    with open(input_path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader)  # Skip header
        
        for part_num in range(1, num_parts + 1):
            output_file = f"{output_prefix}_part_{part_num:02d}.csv"
            output_path = input_path.parent / output_file
            
            print(f"Writing {output_file}...", end=' ')
            
            with open(output_path, 'w', encoding='utf-8', newline='') as out_f:
                writer = csv.writer(out_f)
                writer.writerow(header)  # Write header to each file
                
                rows_written = 0
                for row in reader:
                    writer.writerow(row)
                    rows_written += 1
                    if rows_written >= rows_per_part:
                        break
            
            print(f"({rows_written} rows)")
            
            # If we've written all remaining rows, break early
            if rows_written < rows_per_part:
                break
    
    print(f"\nSuccessfully split {input_file} into {num_parts} parts!")
    print(f"Output files saved in: {input_path.parent}")


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_prefix = sys.argv[2] if len(sys.argv) > 2 else None
    
    try:
        split_csv(input_file, output_prefix)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

