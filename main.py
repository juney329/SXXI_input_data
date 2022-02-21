import pandas
import re
import json
import itertools
import csv
import tkinter


# Used to return list of dictionaries from SXXI 1 column SFAF
def col_import(col_file):
    list_of_dict = []
    count_of_items = 0

    with open(col_file) as sfaf1col:
        parse = False
        for line in sfaf1col:

            if line.startswith('005'):
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
                # continue
            elif parse:
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
                if line.startswith('359'):
                    data_dict['TX ANTENNA FEEDPOINT HEIGHT'] = line.split('.     ')[1].strip()
                if line.startswith('511'):
                    data_dict['MAJOR FUNCTION IDENTIFIER'] = line.split('.     ')[1].strip()
                if line.startswith('512'):
                    data_dict['INTERMEDIATE FUNCTION IDENTIFIER'] = line.split('.     ')[1].strip()
    return list_of_dict


# Used to convert SXXI Degrees Minutes Seconds(DMS) coords to Dotted Decimal(DD) coords for import to Mission Manager
def convert_dms_to_dd(dms_coords):
    lat_degrees = int(dms_coords[0:2])
    lat_minutes = int(dms_coords[2:4])
    lat_seconds = int(dms_coords[4:6])
    lat_hemisphere = dms_coords[6]
    lat_decimal_degrees = lat_degrees + (lat_minutes / 60) + (lat_seconds / 3600)
    if lat_hemisphere == "S":
        lat_decimal_degrees *= -1
    long_degrees = int(dms_coords[7:10])
    long_minutes = int(dms_coords[10:12])
    long_seconds = int(dms_coords[12:14])
    long_hemisphere = dms_coords[14]
    long_decimal_degrees = long_degrees + (long_minutes / 60) + (long_seconds / 3600)
    if long_hemisphere == "W":
        long_decimal_degrees *= -1
    return lat_decimal_degrees, long_decimal_degrees


# Changes SXXI formatted line 110(Frequencies) into float of center freq in Hz
def convert_frequency(f):
    line_110_pattern = re.compile(
        "([KMGT])([0-9]{1,6}[.]?[0-9]{0,4})(-?)([KMGT]?)([0-9]{0,6}[.]?[0-9]{0,4})([(]?)"
        "([0-9]{0,6}[.]?[0-9]{0,4})([)]?)")
    matches = line_110_pattern.match(f)
    center_freq = 0
    ref_freq = None
    if "-" not in matches.group(3):
        if matches.group(1) == "M":
            center_freq = float(matches.group(2)) * 1e6
        elif matches.group(1) == "K":
            center_freq = float(matches.group(2)) * 1000
        elif matches.group(1) == "G":
            center_freq = float(matches.group(2)) * 1e9
    if matches.group(7) != "":
        if matches.group(1) == "M":
            ref_freq = float(matches.group(7)) * 1e6
        elif matches.group(1) == "K":
            ref_freq = float(matches.group(7)) * 1000
        elif matches.group(1) == "G":
            ref_freq = float(matches.group(7)) * 1e9
    return center_freq, ref_freq


# pulls the bandwidth out of the emission designator from line 114
def convert_emission_designator(e):
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
        return bw
    else:
        if bw == 0:
            bw += 10000
        return bw


# Converts SXXI line 110 formatted power into a float
def convert_power(p):
    power = 0
    if p[0] == "W":
        power += float(p[1:])
    elif p[0] == "K":
        power += float(p[1:]) * 1000
    return power

# Converts SXXI dates to YYYY MM DD
def convert_date(d):
    year = d[0:4]
    month = d[4:6]
    day = d[6:8]
    output = f"{year}-{month}-{day}T00:00:00Z"
    return output


# Reads Tab delimited fields from SXXI spreadsheet output
data = pandas.read_csv('NEW MM TEST.txt', sep='\t')
# Turns data into a LIST of dictionaries
# data_dict = data.to_dict('records')

data_dict = col_import('(u) ramstein 1 col 10 feb 21.txt')

processed_records = []
csv_records = []
for n in range(0, len(data_dict)):
    processed_dict = {}
    csv_sfaf = []
    current_dict = data_dict[n]
    clean_current_dict = {k: v for k, v in current_dict.items() if str(v) != 'nan'}

    if convert_frequency(clean_current_dict['FREQUENCY'])[0] != 0:
        transmitter_power_list = [k for k, v in clean_current_dict.items() if "TRANSMITTER" in k]
        emission_designator_list = [k for k, v in clean_current_dict.items() if "EMISSION" in k]
        station_class_list = [k for k, v in clean_current_dict.items() if "STATION" in k]
        erp_list = [k for k, v in clean_current_dict.items() if "EFFECTIVE" in k]
        latlong = convert_dms_to_dd(clean_current_dict["TX ANTENNA COORDINATES"])
        converted_frequencies = convert_frequency(clean_current_dict['FREQUENCY'])
        emissions_list = []
        for (sc, tp, ec) in itertools.zip_longest(station_class_list, transmitter_power_list, erp_list):
            if sc in clean_current_dict.keys():
                station_class = clean_current_dict[sc]
            else:
                station_class = "FX"
            if tp in clean_current_dict.keys():
                transmitter_power = convert_power(clean_current_dict[tp])
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

        if "LIST SERIAL NUMBER" in clean_current_dict.keys():
            list_serial = clean_current_dict["LIST SERIAL NUMBER"]
        else:
            list_serial = ""
        if "BUREAU" in clean_current_dict.keys():
            bureau = clean_current_dict["BUREAU"]
        else:
            bureau = ""
        if "AGENCY" in clean_current_dict.keys():
            agency = clean_current_dict["AGENCY"]
        else:
            agency = ""
        if "COMMAND" in clean_current_dict.keys():
            command = clean_current_dict["COMMAND"]
        else:
            command = ""
        if "SUBCOMMAND" in clean_current_dict.keys():
            subcommand = clean_current_dict["SUBCOMMAND"]
        else:
            subcommand = ""

        if "INSTALLATION FREQUENCY MANAGER" in clean_current_dict.keys():
            ism = clean_current_dict["INSTALLATION FREQUENCY MANAGER"]
        else:
            ism = ""
        if "USER NET/CODE[01]" in clean_current_dict.keys():
            user_net_code = clean_current_dict["USER NET/CODE[01]"]
        else:
            user_net_code = ""

        if "MAJOR FUNCTION IDENTIFIER" in clean_current_dict.keys():
            major_function = clean_current_dict["MAJOR FUNCTION IDENTIFIER"]
        else:
            major_function = ""

        if "INTERMEDIATE FUNCTION IDENTIFIER" in clean_current_dict.keys():
            inter_function = clean_current_dict["INTERMEDIATE FUNCTION IDENTIFIER"]
        else:
            inter_function = ""

        # processed_dict["modulations"] = []
        processed_dict["stations"] = emissions_list
        processed_dict["name"] = clean_current_dict['AGENCY SERIAL NUMBER']
        # processed_dict["start_timestamp"] = ""
        # processed_dict["end_timestamp"] = None
        # processed_dict["repeat_interval"] = None
        # processed_dict["repeat_end_timestamp"] = None
        processed_dict["center_frequency"] = converted_frequencies[0]
        processed_dict["bandwidth"] = convert_emission_designator(clean_current_dict['EMISSION DESIGNATOR[01]'])
        # processed_dict["filter_type"] = "WHITELIST"
        processed_dict["agency_serial"] = clean_current_dict['AGENCY SERIAL NUMBER']
        processed_dict["list_serial"] = list_serial
        # processed_dict["authorization_date"] = None
        processed_dict["reference_frequency"] = converted_frequencies[1]
        # processed_dict["min_occupancy"] = 0.0
        # processed_dict["max_occupancy"] = 100.0
        processed_dict["agency"] = agency
        processed_dict["bureau"] = bureau
        processed_dict["command"] = command
        processed_dict["subcommand"] = subcommand
        processed_dict["installation_frequency_manager"] = ism
        processed_dict["user_net"] = user_net_code
        processed_dict["latitude"] = latlong[0]
        processed_dict["longitude"] = latlong[1]
        # processed_dict["altitude"] = None
        processed_dict["major_function_identifier"] = major_function
        processed_dict["intermediate_function_identifier"] = inter_function
        # processed_dict["is_all_modulation"] = True
        # processed_dict["icon"] = None
        # processed_dict["groups"] = []
        # processed_dict["operation_zones"] = []
        # processed_dict["exclusion_zones"] = []

        csv_sfaf.append(latlong[0])
        csv_sfaf.append(latlong[1])
        csv_sfaf.append(converted_frequencies[0])
        csv_sfaf.append(convert_emission_designator(clean_current_dict['EMISSION DESIGNATOR[01]']))
        csv_sfaf.append(clean_current_dict['AGENCY SERIAL NUMBER'])
        csv_records.append(csv_sfaf)

        processed_records.append(processed_dict)

# print(data_dict)
# print(csv_records)

json_file = json.dumps(processed_records, indent=4, )

with open('recordsspreadsheet.csv', 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerows(csv_records)

with open("records.json", mode="w") as file:
    file.write(json_file)
