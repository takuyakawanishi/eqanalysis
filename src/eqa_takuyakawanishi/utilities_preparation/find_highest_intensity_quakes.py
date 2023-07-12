import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import scipy.stats
import sys
import src.eqa_takuyakawanishi.eqa as eqa


def main():
    filename = "../../../intermediates/organized_codes_pre_02.csv"
    dir_data = "../../../data/stationwise_fine_old_until_2019/"
    meta = pd.read_csv(filename)
    station = 2502330
    res = eqa.find_highest(meta, station, dir_data=dir_data)


if __name__ == '__main__':
    main()
