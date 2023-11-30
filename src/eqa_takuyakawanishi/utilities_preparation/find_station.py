# import datetime
# import matplotlib.pyplot as plt
# import numpy as np
import pandas as pd
# import sys


def main():
    dir_data = '../../../data/stationwise_fine_old_until_2019/'
    file2read_meta = '../../../intermediates/organized_codes_pre_02.csv'
    meta = pd.read_csv(file2read_meta)
    codes = list(meta["code_prime"])
    stations_having_int_D = []
    stations_having_int_7 = []
    for i_code, code in enumerate(codes):
        idx = meta.index[meta["code_prime"] == code]
        stations = eval(meta.loc[idx, "codes_ordered"].values[0])
        add = False
        add_7 = False
        for station in stations:
            try:
                df = pd.read_csv(dir_data + 'st_' + str(station) + '.txt')
            except Exception as ex:
                print(ex)
                continue
            df["intensity"] = df["intensity"].astype(str)
            intensities = df["intensity"].values
            if "D" in intensities:
                add = True
            if "7" in intensities:
                add_7 = True
        if add:
            stations_having_int_D.append(code)
        if add_7:
            stations_having_int_7.append(code)

    print(stations_having_int_7)
    print(stations_having_int_D)
    print(len(stations_having_int_D))


if __name__ == '__main__':
    main()
