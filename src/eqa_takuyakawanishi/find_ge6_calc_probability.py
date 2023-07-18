import datetime
import numpy as np
import pandas as pd
import src.eqa_takuyakawanishi.eqa as eqa


def extract_quakes_by_intensities(
        meta, intensities, dir_data):
    codes = list(meta["code_prime"])
    count = 0
    dfs = None
    for i_code, code in enumerate(codes):
        df = None
        try:
            df = eqa.find_intensities(
                meta, code, intensities, dir_data=dir_data)
            df["code_prime"] = code
        except Exception as ex:
            print(ex)
        if df is not None:
            if not df.empty:
                if count == 0:
                    dfs = df
                    count += 1
                else:
                    dfs = pd.concat([dfs, df], axis=0)
    return dfs


def main():
    dir_data = "../../data/stationwise/"
    file2read = "../../intermediates/organized_codes_pre_02.csv"
    meta = pd.read_csv(file2read)
    intensities = ["D"]
    dfs = extract_quakes_by_intensities(
        meta, intensities, dir_data=dir_data)
    dfs = dfs.reset_index(drop=True)
    print(dfs)
    file2save = "../../intermediates/intensity_D.csv"
    dfs.to_csv(file2save, index= None)




if __name__ == '__main__':
    main()