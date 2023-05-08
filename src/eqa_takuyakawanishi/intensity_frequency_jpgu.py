import datetime
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import src.eqa_takuyakawanishi.eqa as eqa


def calc_duration(meta):
    meta = meta.reset_index(drop=True)
    datefrom = str(meta.at[0, 'from'])[:8]
    datefrom = datetime.datetime.strptime(datefrom, "%Y%m%d")
    dateto = None
    try:
        dateto = str(meta.at[0, 'to'])[:8]
        dateto = datetime.datetime.strptime(dateto, "%Y%m%d")
    except:
        dateto = datetime.datetime(2019, 12, 31)
    duration = (dateto - datefrom) / datetime.timedelta(days=1) / 365.2425
    print(datefrom, dateto, duration)
    return duration


def main():
    station = 3900000
    dir_data = '../../data/stationwise_fine/'
    file2read_meta = '../../data/code_p_df.csv'
    conf = eqa.Settings()
    meta = pd.read_csv(file2read_meta)
    meta_sel = meta[meta['code'] == station]
    meta_sel = meta_sel.reset_index(drop=True)
    res = eqa.calc_date_b_date_e_duration(meta_sel, '1919-01-01', '2019-12-31')
    duration = res.at[0, 'duration']
    print(duration)
    try:
        d7, d6, d5, d4, d3, d2, d1 = eqa.create_subdfs_by_intensities(station)
    except Exception as ex:
        print(ex)






if __name__ == '__main__':
    main()