import datetime
import numpy as np
import pandas as pd
import src.eqa_takuyakawanishi.eqa as eqa


def main():
    dir_data = "../../data/stationwise/"
    file2read = "../../intermediates/organized_codes_pre_02.csv"
    meta = pd.read_csv(file2read)
    intensities = ["D", "C", "7"]
    str = ""
    for intensity in intensities:
        str = str + intensity
    dfs = eqa.extract_quakes_by_intensities(
        meta, intensities, dir_data=dir_data)
    dfs = dfs.reset_index(drop=True)
    print(dfs)
    file2save = "../../intermediates/intensity_" + str + ".csv"
    dfs.to_csv(file2save, index=None)


if __name__ == '__main__':
    main()