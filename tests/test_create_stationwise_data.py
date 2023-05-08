import numpy as np
import unittest
from eqanalysis.src.eqa_takuyakawanishi.create_stationwise_dataframe import *


class MyTestCase(unittest.TestCase):
    def test_station_yearly_for_1000000(self):
        res = station_yearly(1000000, 2019, directory='../../../data_unzip/')
        intensities = list(res['intensity'])
        expected_intensities = ['4', '1', '1', '2', '1', '1', '1', '1']
        # print(intensities)
        self.assertListEqual(intensities, expected_intensities)

    def test_station_years_for_5503332(self):
        res = station_years(5503332, year_b=2017, year_e=2019,
                            directory='../../../data_unzip/')
        intensities = list(res['intensity'])
        expected_intensities = ['1', '1', '1', '3', '1', '1', '3']
        self.assertListEqual(intensities, expected_intensities)


if __name__ == '__main__':
    unittest.main()
