class ColImport:
    def __init__(self, one_col_file):
        self.one_col_file = one_col_file
       
        
        
    def col_import(self):
        count_of_items = 0
        list_of_dict = []
        with open(self.one_col_file) as sfaf1col:
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
         

new_dict = ColImport("(u) ramstein 1 col 10 feb 21.txt")
print(new_dict.col_import)         