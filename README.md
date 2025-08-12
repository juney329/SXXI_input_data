# SFAF to CSV/JSON Converter

This tool converts SFAF (Single Frequency Assignment File) 1-column format files into CSV and JSON formats for use with CRFS RFeye Site and CRFS Mission Manager.

## Purpose

The script processes SFAF data and extracts key information including:
- **Latitude** and **Longitude** coordinates (decimal degrees)
- **Center Frequency** (in Hz)
- **Bandwidth** (in Hz) 
- **Serial Number** (as label)

Records with missing coordinate data are included with lat/long set to 0, which prevents them from being displayed on maps according to the CRFS manual specification.

## Requirements

- Python 3.6+
- pandas

## Installation

1. Clone this repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Basic Usage
```bash
python main.py your_sfaf_file.txt
```

### With Custom Output Files
```bash
python main.py your_sfaf_file.txt --output my_data.csv --json-output my_data.json
```

### Using Short Options
```bash
python main.py your_sfaf_file.txt -o my_data.csv -j my_data.json
```

### Get Help
```bash
python main.py --help
```

## Output Format

### CSV Output
The CSV file contains 5 columns:
1. **Latitude** (decimal degrees) - 0 if coordinates missing
2. **Longitude** (decimal degrees) - 0 if coordinates missing  
3. **Center Frequency** (Hz)
4. **Bandwidth** (Hz)
5. **Serial Number** (label)

### JSON Output
The JSON file contains detailed structured data with all extracted SFAF fields.

## CRFS Compatibility

This tool is designed to work with:
- **CRFS RFeye Site**: For frequency monitoring and analysis
- **CRFS Mission Manager**: For mission planning and data visualization

According to the CRFS manual (17.3.1 Data Overlay - CSV File Format), setting latitude and longitude to 0 prevents data points from being displayed on maps, which is useful for records with missing coordinate information.

## Example

```bash
python main.py UNCLASS_GRC_AIR_AND_LARISSA_PLUS_20KM.txt
```

This will create:
- `recordsspreadsheet.csv` - CSV format for CRFS tools
- `records.json` - Detailed JSON data
