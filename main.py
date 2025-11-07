import pandas
import re
import json
import itertools
import csv
import argparse
import sys
import logging
from typing import List, Dict, Tuple, Optional

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def col_import(col_file: str) -> List[Dict[str, str]]:
    """
    Parse SFAF 1-column file and return list of dictionaries.
    
    Args:
        col_file: Path to the SFAF 1-column format file
        
    Returns:
        List of dictionaries containing parsed SFAF data
        
    Raises:
        FileNotFoundError: If the input file doesn't exist
        ValueError: If the file format is invalid
    """
    list_of_dict = []
    count_of_items = 0

    try:
        with open(col_file, 'r', encoding='utf-8') as sfaf1col:
            parse = False
            data_dict = {}
            for line in sfaf1col:
                if line.startswith('005'):
                    if parse and data_dict:
                        list_of_dict.append(data_dict)
                        logger.debug(f"Added record {len(list_of_dict)} to list (implicit terminator)")
                    data_dict = {}
                    exclude_n = 1
                    station_class_n = 1
                    transmitter_power_n = 1
                    emission_designator_n = 1
                    erp_n = 1
                    user_net_code_n = 1
                    operating_unit_n = 1
                    count_of_items += 1
                    parse = True
                    continue
                elif line.startswith('924'):
                    parse = False
                    list_of_dict.append(data_dict)
                    logger.debug(f"Added record {len(list_of_dict)} to list")
                elif parse:
                    try:
                        if line.startswith('010'):
                            data_dict['TYPE OF ACTION'] = line.split('.     ')[1].strip()
                        if line.startswith('102'):
                            data_dict['AGENCY SERIAL NUMBER'] = line.split('.     ')[1].strip()
                        if line.startswith('105'):
                            data_dict['LIST SERIAL NUMBER'] = line.split('.     ')[1].strip()
                        if line.startswith('110'):
                            data_dict['FREQUENCY'] = line.split('.     ')[1].strip()
                        if line.startswith('111'):
                            data_dict[f'EXCLUDED FREQUENCY BAND[{"{0:0=2d}".format(station_class_n)}]'] = line.split('.     ')[
                                1].strip()
                            exclude_n += 1
                        if line.startswith('113'):
                            data_dict[f'STATION CLASS[{"{0:0=2d}".format(station_class_n)}]'] = line.split('.     ')[1].strip()
                            station_class_n += 1
                        if line.startswith('114'):
                            data_dict[f'EMISSION DESIGNATOR[{"{0:0=2d}".format(emission_designator_n)}]'] = \
                                line.split('.     ')[1].strip()
                            emission_designator_n += 1
                        if line.startswith('115'):
                            data_dict[f'TRANSMITTER POWER[{"{0:0=2d}".format(transmitter_power_n)}]'] = line.split('.     ')[
                                1].strip()
                            transmitter_power_n += 1
                        if line.startswith('117'):
                            data_dict[f'EFFECTIVE RADIATED POWER[{"{0:0=2d}".format(erp_n)}]'] = line.split('.     ')[1].strip()
                            erp_n += 1
                        if line.startswith('140'):
                            data_dict['REQUIRED DATE (YYYYMMDD)'] = line.split('.     ')[1].strip()
                        if line.startswith('141'):
                            data_dict['EXPIRATION DATE (YYYYMMDD)'] = line.split('.     ')[1].strip()
                        if line.startswith('142'):
                            data_dict['REVIEW DATE (YYYYMMDD)'] = line.split('.     ')[1].strip()
                        if line.startswith('200'):
                            data_dict['AGENCY'] = line.split('.     ')[1].strip()
                        if line.startswith('203'):
                            data_dict['BUREAU'] = line.split('.     ')[1].strip()
                        if line.startswith('204'):
                            data_dict['COMMAND'] = line.split('.     ')[1].strip()
                        if line.startswith('205'):
                            data_dict['SUBCOMMAND'] = line.split('.     ')[1].strip()
                        if line.startswith('206'):
                            data_dict['INSTALLATION FREQUENCY MANAGER'] = line.split('.     ')[1].strip()
                        if line.startswith('207'):
                            data_dict[f'OPERATING UNIT[{"{0:0=2d}".format(operating_unit_n)}]'] = line.split('.     ')[
                                1].strip()
                            operating_unit_n += 1
                        if line.startswith('208'):
                            data_dict[f'USER NET/CODE[{"{0:0=2d}".format(user_net_code_n)}]'] = line.split('.     ')[1].strip()
                            user_net_code_n += 1
                        if line.startswith('303'):
                            data_dict['TX ANTENNA COORDINATES'] = line.split('.     ')[1].strip()
                        if line.startswith('306'):
                            data_dict['TX AUTHORIZED RADIUS'] = line.split('.     ')[1].strip()
                        if  line.startswith('340'):
                            data_dict['EQUIPMENT NOMENCLATURE'] = line.split('.     ')[1].strip()
                        if line.startswith('346'):
                            data_dict['PULSE DURATION'] = line.split('.     ')[1].strip()
                        if line.startswith('347'):
                            data_dict['PULSE REPETITION RATE'] = line.split('.     ')[1].strip()
                        if line.startswith('357'):
                            data_dict['ANTENNA GAIN'] = line.split('.     ')[1].strip()
                        if line.startswith('359'):
                            data_dict['TX ANTENNA FEEDPOINT HEIGHT'] = line.split('.     ')[1].strip()
                        if line.startswith('511'):
                            data_dict['MAJOR FUNCTION IDENTIFIER'] = line.split('.     ')[1].strip()
                        if line.startswith('512'):
                            data_dict['INTERMEDIATE FUNCTION IDENTIFIER'] = line.split('.     ')[1].strip()
                    except IndexError as e:
                        logger.warning(f"Failed to parse line: {line.strip()}. Error: {e}")
                        continue

            if parse and data_dict:
                list_of_dict.append(data_dict)
                logger.debug(f"Added record {len(list_of_dict)} to list (end of file)")
                        
    except FileNotFoundError:
        logger.error(f"File not found: {col_file}")
        raise
    except Exception as e:
        logger.error(f"Error reading file {col_file}: {e}")
        raise ValueError(f"Invalid file format: {e}")
        
    logger.info(f"Successfully parsed {count_of_items} SFAF records from {col_file}")
    logger.info(f"Actual records in list: {len(list_of_dict)}")
    return list_of_dict


def convert_dms_to_dd(dms_coords: str) -> Tuple[float, float]:
    """
    Convert SXXI Degrees Minutes Seconds (DMS) coordinates to Decimal Degrees (DD).
    
    Args:
        dms_coords: Coordinate string in DMS format (e.g., "395900N0222630E")
        
    Returns:
        Tuple of (latitude, longitude) in decimal degrees
        
    Raises:
        ValueError: If coordinate format is invalid
    """
    try:
        if len(dms_coords) != 15:
            raise ValueError(f"Invalid coordinate length: expected 15 characters, got {len(dms_coords)}")
            
        lat_degrees = int(dms_coords[0:2])
        lat_minutes = int(dms_coords[2:4])
        lat_seconds = int(dms_coords[4:6])
        lat_hemisphere = dms_coords[6]
        
        if lat_hemisphere not in ['N', 'S']:
            raise ValueError(f"Invalid latitude hemisphere: {lat_hemisphere}")
            
        lat_decimal_degrees = lat_degrees + (lat_minutes / 60) + (lat_seconds / 3600)
        if lat_hemisphere == "S":
            lat_decimal_degrees *= -1
            
        long_degrees = int(dms_coords[7:10])
        long_minutes = int(dms_coords[10:12])
        long_seconds = int(dms_coords[12:14])
        long_hemisphere = dms_coords[14]
        
        if long_hemisphere not in ['E', 'W']:
            raise ValueError(f"Invalid longitude hemisphere: {long_hemisphere}")
            
        long_decimal_degrees = long_degrees + (long_minutes / 60) + (long_seconds / 3600)
        if long_hemisphere == "W":
            long_decimal_degrees *= -1
            
        return lat_decimal_degrees, long_decimal_degrees
        
    except (ValueError, IndexError) as e:
        raise ValueError(f"Failed to parse coordinates '{dms_coords}': {e}")


def convert_frequency(f: str) -> Tuple[float, Optional[float]]:
    """
    Convert SXXI formatted frequency line 110 into center frequency in Hz.
    
    Args:
        f: Frequency string in SXXI format (e.g., "M138.025")
        
    Returns:
        Tuple of (center_frequency_hz, reference_frequency_hz or None)
        
    Raises:
        ValueError: If frequency format is invalid
    """
    try:
        line_110_pattern = re.compile(
            "([KMGT])([0-9]{1,6}[.]?[0-9]{0,4})(-?)([KMGT]?)([0-9]{0,6}[.]?[0-9]{0,4})([(]?)"
            "([0-9]{0,6}[.]?[0-9]{0,4})([)]?)")
        matches = line_110_pattern.match(f)
        
        if not matches:
            raise ValueError(f"Invalid frequency format: {f}")
            
        center_freq = 0
        ref_freq = None
        
        if "-" not in matches.group(3):
            if matches.group(1) == "M":
                center_freq = float(matches.group(2)) * 1e6
            elif matches.group(1) == "K":
                center_freq = float(matches.group(2)) * 1000
            elif matches.group(1) == "G":
                center_freq = float(matches.group(2)) * 1e9
            else:
                raise ValueError(f"Unsupported frequency unit: {matches.group(1)}")
                
        if matches.group(7) != "":
            if matches.group(1) == "M":
                ref_freq = float(matches.group(7)) * 1e6
            elif matches.group(1) == "K":
                ref_freq = float(matches.group(7)) * 1000
            elif matches.group(1) == "G":
                ref_freq = float(matches.group(7)) * 1e9
                
        return center_freq, ref_freq
        
    except Exception as e:
        raise ValueError(f"Failed to parse frequency '{f}': {e}")


def convert_emission_designator(e: str) -> float:
    """
    Extract bandwidth from emission designator line 114.
    
    Args:
        e: Emission designator string
        
    Returns:
        Bandwidth in Hz
        
    Raises:
        ValueError: If emission designator format is invalid
    """
    try:
        bw = 0
        line_114_pattern = re.compile("([0-9]{1,3})([HKMG])([0-9]{0,2})([A-Z])([0-9])([A-Z])")
        matches = line_114_pattern.match(e)
        
        if matches:
            bw_1 = int(matches.group(1))
            if matches.group(3) == "":
                bw_2 = 0
            else:
                bw_2 = float(matches.group(3))
            bw_freq = matches.group(2)
            
            if bw_freq == "H":
                bw += bw_1 + bw_2 / 100
            elif matches.group(2) == "K":
                bw += (bw_1 + bw_2 / 100) * 1000
            elif matches.group(2) == "M":
                bw += (bw_1 + bw_2 / 100) * 1e6
            elif matches.group(2) == "G":
                bw += (bw_1 + bw_2 / 100) * 1e9
            else:
                raise ValueError(f"Unsupported bandwidth unit: {bw_freq}")
                
            return bw
        else:
            logger.warning(f"Could not parse emission designator: {e}, using default bandwidth")
            return 10000.0
            
    except Exception as e:
        logger.warning(f"Failed to parse emission designator '{e}': {e}, using default bandwidth")
        return 10000.0


def convert_power(p: str) -> float:
    """
    Convert SXXI line 110 formatted power into a float.
    
    Args:
        p: Power string (e.g., "W100" or "K1.5")
        
    Returns:
        Power in Watts
        
    Raises:
        ValueError: If power format is invalid
    """
    try:
        power = 0
        if p[0] == "W":
            power += float(p[1:])
        elif p[0] == "K":
            power += float(p[1:]) * 1000
        else:
            raise ValueError(f"Unsupported power unit: {p[0]}")
        return power
        
    except Exception as e:
        raise ValueError(f"Failed to parse power '{p}': {e}")


def convert_date(d: str) -> str:
    """
    Convert SXXI date format to ISO format.
    
    Args:
        d: Date string in YYYYMMDD format
        
    Returns:
        Date string in ISO format (YYYY-MM-DDTHH:MM:SSZ)
        
    Raises:
        ValueError: If date format is invalid
    """
    try:
        if len(d) != 8:
            raise ValueError(f"Invalid date length: expected 8 characters, got {len(d)}")
            
        year = d[0:4]
        month = d[4:6]
        day = d[6:8]
        
        # Validate date components
        if not (1900 <= int(year) <= 2100):
            raise ValueError(f"Invalid year: {year}")
        if not (1 <= int(month) <= 12):
            raise ValueError(f"Invalid month: {month}")
        if not (1 <= int(day) <= 31):
            raise ValueError(f"Invalid day: {day}")
            
        output = f"{year}-{month}-{day}T00:00:00Z"
        return output
        
    except Exception as e:
        raise ValueError(f"Failed to parse date '{d}': {e}")


def main() -> None:
    """
    Main function to process SFAF files and convert to CSV/JSON formats.
    
    Parses command line arguments, processes the SFAF file, and outputs
    results in CSV and JSON formats for use with CRFS tools.
    """
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Process SFAF 1-column file and convert to CSV with lat, long, center freq, bandwidth, and serial number')
    parser.add_argument('sfaf_file', help='Path to the SFAF 1-column file to process')
    parser.add_argument('--output', '-o', default='recordsspreadsheet.csv', 
                       help='Output CSV filename (default: recordsspreadsheet.csv)')
    parser.add_argument('--json-output', '-j', default='records.json',
                       help='Output JSON filename (default: records.json)')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Enable verbose logging')
    
    # Parse arguments
    args = parser.parse_args()
    
    # Set logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    logger.info(f"Starting SFAF processing for file: {args.sfaf_file}")
    
    # Check if input file exists
    try:
        with open(args.sfaf_file, 'r') as f:
            pass
    except FileNotFoundError:
        logger.error(f"File not found: {args.sfaf_file}")
        sys.exit(1)
    
    # Process the SFAF file
    try:
        data_dict = col_import(args.sfaf_file)
    except Exception as e:
        logger.error(f"Failed to process SFAF file: {e}")
        sys.exit(1)
    
    processed_records = []
    csv_records = []
    skipped_count = 0
    
    logger.info(f"Processing {len(data_dict)} records...")
    
    for n in range(0, len(data_dict)):
        try:
            processed_dict = {}
            csv_sfaf = []
            current_dict = data_dict[n]
            clean_current_dict = {k: v for k, v in current_dict.items() if str(v) != 'nan'}

            if convert_frequency(clean_current_dict['FREQUENCY'])[0] != 0:
                # Get serial number for error reporting
                serial_number = clean_current_dict.get('AGENCY SERIAL NUMBER', 'UNKNOWN')
                
                # Check if required fields exist
                if "EMISSION DESIGNATOR[01]" not in clean_current_dict:
                    logger.warning(f"Skipping record {n+1} (Serial: {serial_number}) - missing EMISSION DESIGNATOR")
                    skipped_count += 1
                    continue
                    
                transmitter_power_list = [k for k, v in clean_current_dict.items() if "TRANSMITTER" in k]
                emission_designator_list = [k for k, v in clean_current_dict.items() if "EMISSION" in k]
                station_class_list = [k for k, v in clean_current_dict.items() if "STATION" in k]
                erp_list = [k for k, v in clean_current_dict.items() if "EFFECTIVE" in k]
                
                # Handle missing coordinates by setting to 0 (won't show on map)
                if "TX ANTENNA COORDINATES" not in clean_current_dict:
                    logger.warning(f"Record {n+1} (Serial: {serial_number}) - missing TX ANTENNA COORDINATES, setting lat/long to 0")
                    latlong = (0, 0)
                else:
                    try:
                        latlong = convert_dms_to_dd(clean_current_dict["TX ANTENNA COORDINATES"])
                    except ValueError as e:
                        logger.warning(f"Record {n+1} (Serial: {serial_number}) - invalid coordinates: {e}, setting lat/long to 0")
                        latlong = (0, 0)
                        
                try:
                    converted_frequencies = convert_frequency(clean_current_dict['FREQUENCY'])
                except ValueError as e:
                    logger.warning(f"Record {n+1} (Serial: {serial_number}) - invalid frequency: {e}, skipping")
                    skipped_count += 1
                    continue
                    
                emissions_list = []
                for (sc, tp, ec) in itertools.zip_longest(station_class_list, transmitter_power_list, erp_list):
                    if sc in clean_current_dict.keys():
                        station_class = clean_current_dict[sc]
                    else:
                        station_class = "FX"
                    if tp in clean_current_dict.keys():
                        try:
                            transmitter_power = convert_power(clean_current_dict[tp])
                        except ValueError:
                            logger.warning(f"Record {n+1} (Serial: {serial_number}) - invalid transmitter power, using default")
                            transmitter_power = 1
                    else:
                        transmitter_power = 1
                    if ec in clean_current_dict.keys():
                        erp = clean_current_dict[ec]
                    else:
                        erp = 0

                    emissions_group = {"station_class": station_class,
                                       "transmitter_power": transmitter_power,
                                       "effective_radiated_power": erp}
                    emissions_list.append(emissions_group)

                # Extract optional fields with defaults
                list_serial = clean_current_dict.get("LIST SERIAL NUMBER", "")
                bureau = clean_current_dict.get("BUREAU", "")
                agency = clean_current_dict.get("AGENCY", "")
                command = clean_current_dict.get("COMMAND", "")
                subcommand = clean_current_dict.get("SUBCOMMAND", "")
                ism = clean_current_dict.get("INSTALLATION FREQUENCY MANAGER", "")
                user_net_code = clean_current_dict.get("USER NET/CODE[01]", "")
                major_function = clean_current_dict.get("MAJOR FUNCTION IDENTIFIER", "")
                inter_function = clean_current_dict.get("INTERMEDIATE FUNCTION IDENTIFIER", "")
                equipment_nomenclature = clean_current_dict.get("EQUIPMENT NOMENCLATURE", "")
                pulse_duration = clean_current_dict.get("PULSE DURATION", "")
                pulse_repetition_rate = clean_current_dict.get("PULSE REPETITION RATE", "")
                antenna_gain = clean_current_dict.get("ANTENNA GAIN", "")
                transmitter_power_raw = clean_current_dict.get("TRANSMITTER POWER[01]", "")
                # Build processed dictionary
                processed_dict["stations"] = emissions_list
                processed_dict["name"] = clean_current_dict['AGENCY SERIAL NUMBER']
                processed_dict["center_frequency"] = converted_frequencies[0]
                processed_dict["bandwidth"] = convert_emission_designator(clean_current_dict['EMISSION DESIGNATOR[01]'])
                processed_dict["agency_serial"] = clean_current_dict['AGENCY SERIAL NUMBER']
                processed_dict["list_serial"] = list_serial
                processed_dict["reference_frequency"] = converted_frequencies[1]
                processed_dict["agency"] = agency
                processed_dict["bureau"] = bureau
                processed_dict["command"] = command
                processed_dict["subcommand"] = subcommand
                processed_dict["installation_frequency_manager"] = ism
                processed_dict["user_net"] = user_net_code
                processed_dict["latitude"] = latlong[0]
                processed_dict["longitude"] = latlong[1]
                processed_dict["major_function_identifier"] = major_function
                processed_dict["intermediate_function_identifier"] = inter_function
                processed_dict["equipment_nomenclature"] = equipment_nomenclature
                processed_dict["pulse_duration"] = pulse_duration
                processed_dict["pulse_repetition_rate"] = pulse_repetition_rate
                processed_dict["antenna_gain"] = antenna_gain
                processed_dict["transmitter_power"] = transmitter_power_raw

                # Build CSV record
                csv_sfaf.append(latlong[0])
                csv_sfaf.append(latlong[1])
                csv_sfaf.append(converted_frequencies[0])
                csv_sfaf.append(convert_emission_designator(clean_current_dict['EMISSION DESIGNATOR[01]']))
                csv_sfaf.append(clean_current_dict['AGENCY SERIAL NUMBER'])
                csv_records.append(csv_sfaf)

                processed_records.append(processed_dict)
            else:
                # Debug: Show which records are being filtered out due to frequency being 0
                serial_number = clean_current_dict.get('AGENCY SERIAL NUMBER', 'UNKNOWN')
                frequency_value = clean_current_dict.get('FREQUENCY', 'MISSING')
                logger.warning(f"Record {n+1} (Serial: {serial_number}) - frequency converts to 0: {frequency_value}")
                skipped_count += 1
                
        except Exception as e:
            logger.error(f"Error processing record {n+1}: {e}")
            skipped_count += 1
            continue

    logger.info(f"Successfully processed {len(csv_records)} records, skipped {skipped_count} records")
    logger.debug(f"CSV records: {csv_records}")

    # Write output files
    try:
        json_file = json.dumps(processed_records, indent=4)

        with open(args.output, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerows(csv_records)

        with open(args.json_output, mode="w") as file:
            file.write(json_file)
        
        logger.info(f"CSV output saved to: {args.output}")
        logger.info(f"JSON output saved to: {args.json_output}")
        
    except Exception as e:
        logger.error(f"Failed to write output files: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
