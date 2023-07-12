import datetime
import numpy as np
import pandas as pd
import unittest
import src.eqa_takuyakawanishi.eqa as eqa


class TestEqaForOrganized(unittest.TestCase):

    def test_find_available_periods(self):
        filename = "../intermediates/organized_codes_pre_02.csv"
        meta = pd.read_csv(filename)
        dir_data = "../data/stationwise_fine_old_until_2019/"
        set_dict = {"set_from": "1919-01-01", "set_to": "2019-12-31"}
        station = 1070200
        frequency, regression, summary = \
            eqa.find_intensity_frequency_regression_summarize(
                meta, station, set_dict, dir_data=dir_data
            )

