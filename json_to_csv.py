#!/usr/bin/env python3
"""
Convert JSON output from SFAF parser to a comprehensive CSV file.
"""
import json
import csv
import argparse
import sys


def json_to_csv(json_file, csv_file):
    """
    Convert JSON file to CSV with all fields.
    
    Args:
        json_file: Path to input JSON file
        csv_file: Path to output CSV file
    """
    try:
        # Read JSON data
        with open(json_file, 'r') as f:
            data = json.load(f)
        
        if not data:
            print(f"Warning: {json_file} is empty or contains no records")
            return
        
        # Get all unique keys from all records
        all_keys = set()
        for record in data:
            all_keys.update(record.keys())
        
        # Remove 'name' field if present
        all_keys.discard('name')
        
        # Sort keys for consistent column order
        fieldnames = sorted(all_keys)
        
        # Write CSV
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            for record in data:
                # Remove 'name' field from record
                record.pop('name', None)
                
                # Convert Hz to MHz for frequency fields
                if 'center_frequency' in record and record['center_frequency']:
                    record['center_frequency'] = record['center_frequency'] / 1e6
                if 'bandwidth' in record and record['bandwidth']:
                    record['bandwidth'] = record['bandwidth'] / 1e6
                if 'reference_frequency' in record and record['reference_frequency']:
                    record['reference_frequency'] = record['reference_frequency'] / 1e6
                
                # Handle nested 'stations' list by converting to string
                if 'stations' in record and isinstance(record['stations'], list):
                    record['stations'] = str(record['stations'])
                writer.writerow(record)
        
        print(f"Successfully converted {len(data)} records from {json_file} to {csv_file}")
        print(f"CSV contains {len(fieldnames)} columns: {', '.join(fieldnames[:5])}...")
        
    except FileNotFoundError:
        print(f"Error: File {json_file} not found")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in {json_file}: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description='Convert SFAF JSON output to comprehensive CSV format'
    )
    parser.add_argument('json_file', help='Input JSON file')
    parser.add_argument('--output', '-o', default=None,
                       help='Output CSV file (default: same name as JSON with .csv extension)')
    
    args = parser.parse_args()
    
    # Determine output filename
    if args.output:
        csv_file = args.output
    else:
        csv_file = args.json_file.rsplit('.', 1)[0] + '_full.csv'
    
    json_to_csv(args.json_file, csv_file)


if __name__ == "__main__":
    main()

