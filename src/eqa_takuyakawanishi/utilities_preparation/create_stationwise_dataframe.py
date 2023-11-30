import numpy as np
import pandas as pd


def station_years(
        station, year_b=1919, year_e=2020,
        directory='./'):
    """ Return the DataFrame of stationwise records of earthquakes from
        year_b to year_e

    :param station:
    :param year_b:
    :param year_e:
    :param directory:
    :return: DataFrame
        containing station_code, intensity, year, month, day
    """
    years = year_b + np.arange(year_e - year_b + 1)
    dfyears = pd.DataFrame()
    #    columns=['station', 'intensity', 'year', 'month', 'day'])
    # print(years)
    for year in years:
        res = station_yearly(station, year, directory=directory)
        # print(res)
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
    directory_read = '../../../data_download/data_unzip/'
    directory_write = '../../../data/stationwise/'
    file2read = "../../../data/code_p_df.csv"
    dfstations = pd.read_csv(file2read)
    codes = list(dfstations['code'])
    print(len(codes))
    # codes = [1000000, 1000001]
    # print(codes)
    for i_code, code in enumerate(codes):
        if code > 0:
            print('Now extracting for station {}'.format(code))
            df = station_years(code, directory=directory_read)
            file2write = directory_write + 'st_' + str(code) + '.txt'
            # print('CAUTION, Not saved.')
            df.to_csv(file2write, index=None)


if __name__ == '__main__':
    main()
