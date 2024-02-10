import numpy as np
import pandas as pd
import os
import sys

def station_years(station, years, directory='./'):
    """ Return the DataFrame of stationwise records of earthquakes, 
        for the years in the list years.
    :param station:
    :param years: 
        List of years in the database
    :param directory:
        Directory of the data files, usually data_unzip
    :return: DataFrame
        containing station_code, intensity, year, month, day, etc.
    """
    dfyears = pd.DataFrame()
    for year in years:
        res = station_yearly(station, year, directory=directory)
        dfyears = pd.concat([dfyears, res])
    dfyears = dfyears.reset_index(drop=True)
    return dfyears


def station_yearly(station, year, directory='./'):
    """Return the DataFrame of the record of earthquakes at the station.

    :param station: station_code
    :param year: year for which extract data
    :param directory: to be set from the caller
    :return: Pandas DataFrame
        containing station_code, intensity, year, month, day
    """
    file = directory + 'i' + str(year) + '.dat'
    count = 0
    df = pd.DataFrame()
    with open(file, 'r', encoding='shift_jis') as f:
        while True:
            linecontent = f.readline()
            if not linecontent:
                break
            if not linecontent[0].isdigit():
                month = linecontent[5:7]
                # print(month)
            stc = linecontent[:7]
            if stc == str(station):
                df.at[count, 'station'] = str(station)
                df.at[count, 'intensity'] = linecontent[18]
                df.at[count, 'year'] = str(year)
                df.at[count, 'month'] = str(month)
                df.at[count, 'day'] = linecontent[8:10]
                df.at[count, 'hour'] = linecontent[10:12]
                df.at[count, 'minute'] = linecontent[12:14]
                df.at[count, 'second'] = linecontent[14:16] + '.' + \
                    linecontent[17]
                df.at[count, 'intensity_equip'] = linecontent[20:22]
                df.at[count, 'acceleration_max_comb'] = linecontent[29:34]
                count += 1
    return df


def main():
    directory_read = 'eqanalysis/data_2024/data_unzip/'
    directory_write = 'eqanalysis/data_2024/stationwise/'
    file2read = "eqanalysis/data_2024/code_p_20231205_df.csv"
    #
    # Find which year's files are in data_unzip
    #
    directory_unzip = "eqanalysis/data_2024/data_unzip"
    listyear = os.listdir(directory_unzip)
    years = []
    for iyear_dat in listyear:
        years.append(int(iyear_dat[1:5]))
    years.sort()
    print(years)
    # sys.exit()
    #
    # Find the station codes from code_p
    #
    dfstations = pd.read_csv(file2read)
    codes = list(dfstations['code'])
    print(len(codes))

    for code in codes:
        if code > 0:
            print('Now extracting for station {}'.format(code))
            df = station_years(code, years, directory=directory_read)
            file2write = directory_write + 'st_' + str(code) + '.txt'
            df.to_csv(file2write, index=None)


if __name__ == '__main__':
    main()
