import datetime
import numpy as np
import pandas as pd
import src.eqa_takuyakawanishi.eqa as eqa


def main():
    set_period = {"set_from": "1919-01-01 00:00:00",
                  "set_to": "2020-12-31 23:59:59"}
    meta = pd.read_csv("../../intermediates/organized_codes_pre_02.csv")
    station = 1460600
    available = eqa.find_available_periods(meta, station)
    print(available)
    res = eqa.calc_periods_durations_to_seconds(available, set_period)
    print(res)




if __name__ == "__main__":
    main()
