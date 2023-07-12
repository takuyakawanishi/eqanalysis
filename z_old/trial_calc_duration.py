import numpy as np
import pandas as pd
import src.eqa_takuyakawanishi.eqa as eqa



def main():
    a = 1
    dir_data = '../../data/stationwise_fine_old_until_2019/'
    file2read_meta = '../../data/code_p_df_old.csv'
    conf = eqa.Settings()

    station = 2421270
    meta = pd.read_csv(file2read_meta)
    meta_sel = meta[meta['code'] == station]
    meta_sel = meta_sel.reset_index(drop=True)
    to = meta_sel.at[0, 'to']
    dfrom = meta_sel.at[0, 'from']
    res = eqa.find_date_end(station, to, '2019-12-31', dir_data=dir_data)
    print(res)
    res = eqa.find_date_beginning(
        station, dfrom, '1919-01-01', dir_data=dir_data)
    print(res)
    #
    #
    #
    meta_sub = meta.head(2000)
    meta_sub = meta_sub.reset_index(drop=True)
    #meta_sub = meta_sub.tail(100)
    res = eqa.calc_date_b_date_e_duration(
        meta_sub, '1919-01-01', '2019-12-31', dir_data=dir_data)
    print(res)





if __name__ == '__main__':
    main()
