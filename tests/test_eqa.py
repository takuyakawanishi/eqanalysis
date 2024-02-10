import datetime
import numpy as np
import pandas as pd
import unittest
import sys
sys.path.append("./")
sys.path.append("./eqanalysis/tests/stationwise_test")
sys.path.append("./eqanalysis/")
sys.path.append("./eqanalysis/tests")
import eqanalysis.src.eqa_takuyakawanishi.eqa as eqa


class TestEqaForOrganized(unittest.TestCase):

    def test_count_intensity_in_dataframe(self):
        df = pd.DataFrame(
            [
                [1, 1], [2, "2"], [3, 1], [4, "D"], [5, "A"], [6, "1"],
                [7, 2], [8, 1], [9, 1], [10, 1], [11, "C"], [12, 1],
                [13, 1], [14, 3], [15, 7]
            ], columns=["temp", "intensity"])
        res = eqa.count_intensity_in_dataframe(df)
        # [8, 2, 1, 0, 1, 2, 1]
        expected = [15, 7, 5, 4, 4, 3, 1]
        np.testing.assert_array_equal(res, expected)

    def test_find_regression_int_freq(self):
        freq = pd.Series()
        freq["int1"] = 1.24390244
        freq["int2"] = 0.36585366
        freq["int3"] = 0.17073171
        freq["int4"] = 0.04878049
        freq.astype(float)
        res, est7, est6, est6p5 = eqa.find_regression_int_freq(freq)
        res_array = np.array([
            res.slope, res.intercept, res.rvalue, est7, est6])
        expected_res_array = np.array([
            -0.43753062, 0.47388111, -0.99026230, 0.00257731, 0.00705825])
        np.testing.assert_almost_equal(res_array, expected_res_array, decimal=6)

################################################################################
# TS version        
################################################################################

class TestEqaForOrganizedTS(unittest.TestCase):

    def test_find_available_periods_ts(self):
        meta = pd.DataFrame(columns=[
            "code_prime", "codes_ordered", "date_b_s", "date_e_s"])
        meta["codes_ordered"].astype("object")
        meta["date_b_s"].astype("object")
        meta["date_e_s"].astype("object")
        meta.loc[0, "code_prime"] = 1000
        meta.at[0, "codes_ordered"] = str([1000, 1001, 1002])
        meta.loc[0, "datetime_b_s"] = str(
            ["1996-04-01 12:00:00", "2000-12-18 12:00:00",
             "2008-01-01 12:00:00"])
        meta.loc[0, "datetime_e_s"] = str(
            ["2000-11-30 12:00:00", "2008-01-01 12:00:00",
             "2023-12-31 23:59:59"])
        res = eqa.find_available_periods_ts(meta, 1000)
        expected = pd.DataFrame(columns=["station", "from", "to"])
        expected["station"] = [1000, 1001, 1002]
        expected["from"] = \
            ["1996-04-01 12:00:00", "2000-12-18 12:00:00",
             "2008-01-01 12:00:00"]
        expected["to"] = \
            ["2000-11-30 12:00:00", "2008-01-01 12:00:00",
             "2023-12-31 23:59:59"]
        expected["station"] = expected["station"].astype(int)
        pd.testing.assert_frame_equal(expected, res)

    def test_calc_periods_intersection_ts_01(self):
        period_0 = ["1996-04-01　12:00:00", "2019-12-31 12:00:00"]
        period_1 = ["2006-04-01 12:00:00", "2008-12-31 23:59:59"]
        date_tuple_b = (2006, 4, 1, 12, 0, 0)
        date_tuple_e = (2008, 12, 31, 23, 59, 59)
        expected_b = datetime.datetime(*date_tuple_b)
        expected_e = datetime.datetime(*date_tuple_e)
        b, e = eqa.calc_periods_intersection_ts(period_0, period_1)
        self.assertEqual(expected_b, b)
        self.assertEqual(expected_e, e)

    def test_calc_periods_intersection_ts_02(self):
        period_0 = ["1996-04-01 12:00:00", "2008-12-31 12:00:00"]
        period_1 = ["2006-04-01 12:00:00", "2019-12-31 23:59:59"]
        date_tuple_b = (2006, 4, 1, 12, 0, 0)
        date_tuple_e = (2008, 12, 31, 12, 0, 0)
        expected_b = datetime.datetime(*date_tuple_b)
        expected_e = datetime.datetime(*date_tuple_e)
        b, e = eqa.calc_periods_intersection_ts(period_0, period_1)
        self.assertEqual(expected_b, b)
        self.assertEqual(expected_e, e)

    def test_calc_periods_intersection_ts_03(self):
        period_0 = ["1996-04-01 12:00:00", "2006-12-31 12:00:00"]
        period_1 = ["2008-04-01 12:00:00", "2019-12-31 23:59:59"]
        b, e = eqa.calc_periods_intersection_ts(period_0, period_1)
        self.assertTrue(np.isnan(b))
        self.assertTrue(np.isnan(e))

    def test_calc_periods_durations_ts(self):
        df_available = pd.DataFrame(
            [[1000, "1996-04-01 12:00:00", "2000-01-01 12:00:00"],
             [1001, "2000-01-01 12:00:00", "2008-06-30 12:00:00"],
             [1002, "2008-09-16 12:00:00", "2023-12-31 23:59:59"]],
            columns=["station", "from", "to"])
        set_period = \
            {"set_from": "2001-01-01 12:00:00",
             "set_to": "2010-12-31 23:59:59"}
        res = eqa.calc_periods_durations_ts(df_available, set_period)
        expected = pd.DataFrame(
            [[1000, "", "", 0],
             [1001, "2001-01-01 12:00:00", "2008-06-30 12:00:00", 2737],
             [1002, "2008-09-16 12:00:00", "2010-12-31 23:59:59", 836]],
            columns=["station", "from", "to", "duration"])
        pd.testing.assert_frame_equal(res, expected)

    def test_add_datetime_column_to_dataframe(self):
        df = pd.DataFrame(columns=["year", "month", "day"])
        df.loc[0, "year"] = 1999
        df.loc[0, "month"] = 12
        df.loc[0, "day"] = 31
        df.loc[0, "hour"] = 12
        df.loc[0, "minute"] = 15
        df.loc[0, "second"] = 25
        df.loc[1, "year"] = 2000
        df.loc[1, "month"] = 1
        df.loc[1, "day"] = "  "
        df.loc[1, "hour"] = 23
        df.loc[1, "minute"] = 22
        df.loc[1, "second"] = 1
        df.loc[2, "year"] = 2001
        df.loc[2, "month"] = 11
        df.loc[2, "day"] = "//"
        df.loc[2, "hour"] = 1
        df.loc[2, "minute"] = 5
        df.loc[2, "second"] = 5
        res = eqa.add_datetime_column_to_dataframe(df)
        dfr = df.copy()
        dfr = dfr.drop(index=1)
        dfr.at[0, "date_time"] = datetime.datetime(*(1999, 12, 31, 12, 15, 25))
        dfr.at[2, "date_time"] = datetime.datetime(*(2001, 11, 15, 1, 5, 5))
        dfr.at[2, "day"] = 15
        pd.testing.assert_frame_equal(res, dfr)
    

class TestEqaForOrganized02(unittest.TestCase):

    def test_find_datetime_beginning_01(self):
        dir_data = "./eqanalysis/tests/stationwise_test/"
        from_num = 999999999999
        datetime_beginning = "1910-04-06 12:00:00"
        res = eqa.find_datetime_beginning(
            1000, from_num, datetime_beginning, dir_data=dir_data)
        # print(res)
        self.assertEqual(datetime.datetime(1996, 1, 1, 12, 0, 0), res)

    def test_find_datetime_beginning_02(self):
        dir_data = "./eqanalysis/tests/stationwise_test/"
        from_num = 199604011200
        datetime_beginning = "1910-04-06 12:00:00"
        res = eqa.find_datetime_beginning(
            1000, from_num, datetime_beginning, dir_data=dir_data)
        # print(res)
        self.assertEqual(res, datetime.datetime(1996, 4, 1, 12, 0, 0))

    def test_find_datetime_beginning_03(self):
        dir_data = "./eqanalysis/tests/stationwise_test/"
        from_num = 199799999999
        datetime_beginning = "1996-04-01 12:00:00"
        res = eqa.find_datetime_beginning(
            1000, from_num, datetime_beginning, dir_data=dir_data)
        # print(res)
        self.assertEqual(res, datetime.datetime(1997, 1, 1, 12, 0, 0))

    def test_find_datetime_end_01(self):
        dir_data = "./eqanalysis/tests/stationwise_test/"
        str_from = 999999999999
        datetime_end = "2023-12-31 23:59:59"
        res = eqa.find_datetime_end(
            1000, str_from, datetime_end, dir_data=dir_data)
        # print(res)
        self.assertEqual(res, datetime.datetime(1998, 12, 31, 23, 59, 59))

    def test_find_datetime_end_02(self):
        dir_data = "./eqanalysis/tests/stationwise_test/"
        str_from = 999999999999
        datetime_end = "1997-12-31 23:59:59"
        res = eqa.find_datetime_end(
            1000, str_from, datetime_end, dir_data=dir_data)
        # print(res)
        self.assertEqual(res, datetime.datetime(1997, 12, 31, 23, 59, 59))

    def test_find_datetime_end_03(self):
        dir_data = "./eqanalysis/tests/stationwise_test/"
        str_from = 199799999999
        datetime_end = "1997-12-31 23:59:59"
        res = eqa.find_datetime_end(
            1000, str_from, datetime_end, dir_data=dir_data)
        # print(res)
        self.assertEqual(res, datetime.datetime(1997, 12, 28, 23, 59, 0))

    def test_calc_datetime_b_datetime_e_duration(self):
        dir_data = "./eqanalysis/tests/stationwise_test/"
        meta = pd.DataFrame(
            [[2000, 199404011200, 199612311200],
             [2001, 199612311200, 199804011200],
             [2002, 199804011200,]],
            columns=["code", "from", "to"])
        date_beginning = "1919-01-01 12:00:00"
        date_end = "2020-12-31 23:59:59"
        res = eqa.calc_datetime_b_datetime_e_duration(
            meta, date_beginning, date_end, dir_data=dir_data)
        date_b_2000 = datetime.datetime(1994, 4, 1, 12, 0, 0)
        date_e_2000 = datetime.datetime(1996, 12, 31, 12, 0, 0)
        date_b_2001 = datetime.datetime(1996, 12, 31, 12, 0, 0)
        date_e_2001 = datetime.datetime(1998, 4, 1, 12, 0, 0)
        date_b_2002 = datetime.datetime(1998, 4, 1, 12, 0, 0)
        date_e_2002 = datetime.datetime(2020, 12, 31, 23, 59, 59)
        expected = pd.DataFrame(
            [[2000, 199404011200, 199612311200, date_b_2000, date_e_2000,
              2.751597],
             [2001, 199612311200, 199804011200, date_b_2001, date_e_2001,
              1.248486],
             [2002, 199804011200, np.nan, date_b_2002, date_e_2002,
              22.752007]],
            columns=["code", "from", "to", "datetime_b", "datetime_e",
                     "duration_ts"])
        pd.testing.assert_frame_equal(expected, res, check_exact=False)


class MyTestCase(unittest.TestCase):

    def test_find_days_cros_the_intercept(self):
        x = [1, 2, 3, 4, 5]
        suvf = [.9, .8, .7, .6, .5]
        intercept = .55
        res = eqa.find_days_cros_the_intercept(x, suvf, intercept)
        res = list(res)
        self.assertListEqual(res, [4, 5])

class TestEqaForLatLons(unittest.TestCase):

    def test_calc_latitude(self):
        lat = 3448
        res = eqa.calc_latitude(lat)
        expected = 34.8
        self.assertEqual(res, expected)

    def test_calc_longitude(self):
        lon = 13524
        res = eqa.calc_longitude(lon)
        expected = 135.4
        self.assertEqual(res, expected)

    def test_lonlat_for_station(self):
        df = pd.read_csv("eqanalysis/tests/code_p_test.csv")
        res = eqa.find_lonlat_for_station(3900131, df)
        expected = [136.766666666, 37.2833333333]
        np.testing.assert_almost_equal(res, expected, decimal=6)


if __name__ == '__main__':
    unittest.main()
