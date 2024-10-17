import datetime
import pathlib
import numpy as np
import pandas as pd
import unittest
import sys

sys.path.append("./")
sys.path.append("../../")
# sys.path.append("./eqanalysis/tests/stationwise_test")
# sys.path.append("./eqanalysis/")
# sys.path.append("./eqanalysis/tests")
import eqanalysis.src.eqa_takuyakawanishi.eqa as eqa


root_eqanalysis = pathlib.Path(__file__).parent.parent


class TestIROR(unittest.TestCase):

    def test_create_instance(self):
        ros = [1, 2, 3, 4, np.nan, np.nan, np.nan]
        this_iror = eqa.IROR(ros)
        res = this_iror.ros
        exp = [1, 2, 3, 4, np.nan, np.nan, np.nan]
        np.testing.assert_equal(res, exp)

    def test_iror_upto_4(self):
        ros = np.array([0.6, 0.55, 0.26, 0.098])
        this_iror = eqa.IROR(ros)
        res = this_iror.find_iror(1)
        ress = np.array([res.slope, res.intercept, res.rvalue, res.pvalue])
        exps = np.array([-0.26861648, 0.15271955, -0.94993336, 0.050066630])
        np.testing.assert_almost_equal(ress, exps, decimal=5)

    def test_iror_upto_4_02(self):
        ros = np.array([0.6, 0.55, 0.26, np.nan])
        this_iror = eqa.IROR(ros)
        res = this_iror.find_iror(2)
        exp_slope = np.log10(ros[2]) - np.log10(ros[1])
        exp_intercept = np.log10(ros[1]) - 2 * exp_slope
        self.assertEqual(res.slope, exp_slope)
        self.assertEqual(res.intercept, exp_intercept)
        self.assertEqual(np.isnan(res.rvalue), True)


class TestUtilities(unittest.TestCase):

    def test_station_data_filename_handler(self):
        station = 1010541
        # print(root_eqanalysis)
        # print(type(root_eqanalysis))
        dir_data_plp = root_eqanalysis / "tests" / "stationwise_test"
        res = eqa.station_data_filename_handler(station, dir_data_plp)
        self.assertEqual(type(res), type(root_eqanalysis))

        dir_data = "eqanalysis/tests/stationwise_test/"
        res = eqa.station_data_filename_handler(station, dir_data)


class TestCountIntensityInDataframe(unittest.TestCase):

    def test_count_intensity_in_dataframe(self):
        df = pd.DataFrame(
            [
                [1, 1],
                [2, "2"],
                [3, 1],
                [4, "D"],
                [5, "A"],
                [6, "1"],
                [7, 2],
                [8, 1],
                [9, 1],
                [10, 1],
                [11, "C"],
                [12, 1],
                [13, 1],
                [14, 3],
                [15, 7],
            ],
            columns=["temp", "intensity"],
        )
        res = eqa.count_intensity_in_dataframe(df)
        expected = [15, 7, 5, 4, 4, 3, 1]
        np.testing.assert_array_equal(res, expected)


################################################################################
# Test Preiods and datetime handling
################################################################################


class TestEqaForOrganizedTS(unittest.TestCase):

    def test_find_available_periods_ts(self):
        meta = pd.DataFrame(
            columns=["code_prime", "codes_ordered", "date_b_s", "date_e_s"]
        )
        meta["codes_ordered"].astype("object")
        meta["date_b_s"].astype("object")
        meta["date_e_s"].astype("object")
        meta.loc[0, "code_prime"] = 1000
        meta.at[0, "codes_ordered"] = str([1000, 1001, 1002])
        meta.loc[0, "datetime_b_s"] = str(
            ["1996-04-01 12:00:00", "2000-12-18 12:00:00", "2008-01-01 12:00:00"]
        )
        meta.loc[0, "datetime_e_s"] = str(
            ["2000-11-30 12:00:00", "2008-01-01 12:00:00", "2023-12-31 23:59:59"]
        )
        res = eqa.find_available_periods_ts(meta, 1000)
        expected = pd.DataFrame(columns=["station", "from", "to"])
        expected["station"] = [1000, 1001, 1002]
        expected["from"] = [
            "1996-04-01 12:00:00",
            "2000-12-18 12:00:00",
            "2008-01-01 12:00:00",
        ]
        expected["to"] = [
            "2000-11-30 12:00:00",
            "2008-01-01 12:00:00",
            "2023-12-31 23:59:59",
        ]
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
            [
                [1000, "1996-04-01 12:00:00", "2000-01-01 12:00:00"],
                [1001, "2000-01-01 12:00:00", "2008-06-30 12:00:00"],
                [1002, "2008-09-16 12:00:00", "2023-12-31 23:59:59"],
            ],
            columns=["station", "from", "to"],
        )
        set_period = {
            "set_from": "2001-01-01 12:00:00",
            "set_to": "2010-12-31 23:59:59",
        }
        res = eqa.calc_periods_durations_ts(df_available, set_period)
        expected = pd.DataFrame(
            [
                [1001, "2001-01-01 12:00:00", "2008-06-30 12:00:00", 2737],
                [1002, "2008-09-16 12:00:00", "2010-12-31 23:59:59", 836],
            ],
            columns=["station", "from", "to", "duration"],
        )
        pd.testing.assert_frame_equal(res, expected)

    def test_calc_periods_durations_ts_02(self):
        available = [
            [7413630, "1998-10-15 12:00:00", "2005-04-01 12:00:00"],
            [7413631, "2005-04-01 12:00:00", "2022-01-01 00:00:00"],
        ]
        df_available = pd.DataFrame(available, columns=["station", "from", "to"])
        dict_set = {"set_from": "2016-04-17 01:25:09", "set_to": "2021.12.31 23:59:59"}
        res = eqa.calc_periods_durations_ts(df_available, dict_set)

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

    def test_find_datetime_beginning_01(self):
        dir_data = root_eqanalysis / "tests" / "stationwise_test"
        from_num = 999999999999
        datetime_beginning = "1910-04-06 12:00:00"
        res = eqa.find_datetime_beginning(1000, from_num, datetime_beginning, dir_data)
        self.assertEqual(datetime.datetime(1996, 1, 1, 12, 0, 0), res)

    def test_find_datetime_beginning_02(self):
        dir_data = root_eqanalysis / "tests" / "stationwise_test"
        from_num = 199604011200
        datetime_beginning = "1910-04-06 12:00:00"
        res = eqa.find_datetime_beginning(1000, from_num, datetime_beginning, dir_data)
        self.assertEqual(res, datetime.datetime(1996, 4, 1, 12, 0, 0))

    def test_find_datetime_beginning_03(self):
        dir_data = root_eqanalysis / "tests" / "stationwise_test"
        from_num = 199799999999
        datetime_beginning = "1996-04-01 12:00:00"
        res = eqa.find_datetime_beginning(1000, from_num, datetime_beginning, dir_data)
        self.assertEqual(res, datetime.datetime(1997, 1, 1, 12, 0, 0))

    def test_find_datetime_end_01(self):
        dir_data = root_eqanalysis / "tests" / "stationwise_test"
        str_from = 999999999999
        datetime_end = "2023-12-31 23:59:59"
        res = eqa.find_datetime_end(1000, str_from, datetime_end, dir_data)
        self.assertEqual(res, datetime.datetime(1998, 12, 31, 23, 59, 59))

    def test_find_datetime_end_02(self):
        dir_data = root_eqanalysis / "tests" / "stationwise_test"
        str_from = 999999999999
        datetime_end = "1997-12-31 23:59:59"
        res = eqa.find_datetime_end(1000, str_from, datetime_end, dir_data)
        self.assertEqual(res, datetime.datetime(1997, 12, 31, 23, 59, 59))

    def test_find_datetime_end_03(self):
        dir_data = root_eqanalysis / "tests" / "stationwise_test"
        str_from = 199799999999
        datetime_end = "1997-12-31 23:59:59"
        res = eqa.find_datetime_end(1000, str_from, datetime_end, dir_data)
        self.assertEqual(res, datetime.datetime(1997, 12, 28, 23, 59, 0))

    def test_find_operation_period_from_station_wise_data_ts(self):
        station = 1010541
        dir_data_plp = root_eqanalysis / "tests" / "stationwise_test"
        res = eqa.find_operation_period_from_station_wise_data_ts(station, dir_data_plp)
        # print(res)
        exp_beginning = "2011-01-01 12:00:00"
        exp_end = "2017-12-31 23:59:59"
        self.assertEqual(res[0], exp_beginning)
        self.assertEqual(res[1], exp_end)

    def test_calc_datetime_b_datetime_e_duration(self):
        dir_data = root_eqanalysis / "tests" / "stationwise_test"
        meta = pd.DataFrame(
            [
                [2000, 199404011200, 199612311200],
                [2001, 199612311200, 199804011200],
                [
                    2002,
                    199804011200,
                ],
            ],
            columns=["code", "from", "to"],
        )
        date_beginning = "1919-01-01 12:00:00"
        date_end = "2020-12-31 23:59:59"
        res = eqa.calc_datetime_b_datetime_e_duration(
            meta, date_beginning, date_end, dir_data
        )
        date_b_2000 = datetime.datetime(1994, 4, 1, 12, 0, 0)
        date_e_2000 = datetime.datetime(1996, 12, 31, 12, 0, 0)
        date_b_2001 = datetime.datetime(1996, 12, 31, 12, 0, 0)
        date_e_2001 = datetime.datetime(1998, 4, 1, 12, 0, 0)
        date_b_2002 = datetime.datetime(1998, 4, 1, 12, 0, 0)
        date_e_2002 = datetime.datetime(2020, 12, 31, 23, 59, 59)
        expected = pd.DataFrame(
            [
                [2000, 199404011200, 199612311200, date_b_2000, date_e_2000, 2.751597],
                [2001, 199612311200, 199804011200, date_b_2001, date_e_2001, 1.248486],
                [2002, 199804011200, np.nan, date_b_2002, date_e_2002, 22.752007],
            ],
            columns=["code", "from", "to", "datetime_b", "datetime_e", "duration_ts"],
        )
        pd.testing.assert_frame_equal(expected, res, check_exact=False)

    def test_find_first_and_last_record_of_station(self):
        station = 1010541
        dir_data_plp = root_eqanalysis / "tests" / "stationwise_test"
        res = eqa.find_first_and_last_record_of_station(station, dir_data_plp)
        first = "2011-03-11 14:49:10"
        last = "2017-11-21 16:30:08"
        # print(res)
        self.assertEqual(res[0], first)
        self.assertEqual(res[1], last)


class TestCountingIntensities(unittest.TestCase):

    def test_take_data_subset_by_period_ts(self):
        station = 1010541
        dir_data_plp = root_eqanalysis / "tests" / "stationwise_test"
        datetime_b = "2015-01-01 00:00:00"
        datetime_e = "2021-12-31 23:59:59"
        df = eqa.take_data_subset_by_period_ts(
            station, datetime_b, datetime_e, dir_data_plp
        )
        # print(df)
        # print(df.shape)
        self.assertEqual(df.shape, (24, 11))

    def test_create_intensity_ro_table_of_period_ts(self):
        dir_data = root_eqanalysis / "tests" / "stationwise_test"
        actual = [
            [2120100, "1996-04-01 12:00:00", "2009-08-21 15:00:00", 4890],
            [2120110, "2009-09-01 15:00:00", "2010-03-31 13:00:00", 210],
            [2120101, "2010-03-31 13:00:00", "2021-12-31 23:59:59", 4293],
        ]
        df_actual = pd.DataFrame(actual, columns=["station", "from", "to", "duration"])
        # print(df_actual)
        res = eqa.create_intensity_ro_table_of_period_ts(df_actual, dir_data)
        # print(res)
        # print(type(res))
        self.assertEqual(res[1]["duration"], 9393)


class TestIntervals(unittest.TestCase):

    def test_combine_if_no_gaps(self):
        gaps = [15, 0]
        dfss = []
        for i in range(3):
            dfs = []
            for j in range(7):
                df = pd.DataFrame()
                df = pd.DataFrame(
                    np.array([[4 * i + j, i, j, 0], [i, j, i + j, 4 * i + j]]),
                    columns=["i", "j", "k", "l"],
                )
                dfs.append(df)

            dfss.append(dfs)
        res = eqa.combine_if_no_gaps(gaps, dfss)
        res_2_4 = res[1][3]
        res_2_4 = res_2_4.reset_index(drop=True)
        res_2_1 = res[1][0]
        res_2_1 = res_2_1.reset_index(drop=True)
        res_length = len(res)
        res_inner_length = len(res[0])

        exp_2_1 = [[4, 1, 0, 0], [1, 0, 1, 4], [8, 2, 0, 0], [2, 0, 2, 8]]
        exp_2_4 = [[7, 1, 3, 0], [1, 3, 4, 7], [11, 2, 3, 0], [2, 3, 5, 11]]
        exp_df_2_1 = pd.DataFrame(exp_2_1, columns=["i", "j", "k", "l"])
        exp_df_2_4 = pd.DataFrame(exp_2_4, columns=["i", "j", "k", "l"])
        pd.testing.assert_frame_equal(res_2_1, exp_df_2_1)
        pd.testing.assert_frame_equal(res_2_4, exp_df_2_4)
        self.assertEqual(res_length, 2)
        self.assertEqual(res_inner_length, 7)

    def test_create_stationwise_dataframe(self):
        dir_data = root_eqanalysis / "tests" / "stationwise_test"
        actual = [
            [2120100, "1996-04-01 12:00:00", "2009-08-21 15:00:00", 4890],
            [2120110, "2009-09-01 15:00:00", "2010-03-31 13:00:00", 210],
            [2120101, "2010-03-31 13:00:00", "2021-12-31 23:59:59", 4293],
        ]
        df_actual = pd.DataFrame(actual, columns=["station", "from", "to", "duration"])
        res = eqa.create_stationwise_dataframe(df_actual, dir_data)

        exp_length_res = 3
        exp_length_res0 = 7
        self.assertEqual(len(res), exp_length_res)
        self.assertEqual(len(res[0]), exp_length_res0)

    def test_create_interval_datasets_ts(self):
        station_prime = 2120100
        filename = (
            root_eqanalysis
            / "data_2024"
            / "intermediates"
            / "organized_code_2024_04.csv"
        )
        df_org = pd.read_csv(filename)
        dir_data = root_eqanalysis / "tests" / "stationwise_test"
        set_dict = {"from": "1996-04-01 12:00:00", "to": "2021-12-31 23:59:59"}
        res = eqa.create_interval_datasets_ts(df_org, station_prime, set_dict, dir_data)
        self.assertEqual(len(res), 7)
        self.assertEqual(len(res[3]), 20)

    def test_create_subdfs_by_intensities_essentials(self):
        dir_data = root_eqanalysis / "tests" / "stationwise_test"
        station = 1010541
        fn = eqa.station_data_filename_handler(station, dir_data)
        df = pd.read_csv(fn)
        datetime_b = "2012-01-01 00:00:00"
        datetime_e = "2013-12-31 23:59:59"
        res = eqa.create_subdfs_by_intensities_essentials(df, datetime_b, datetime_e)
        res_int_2 = len(res[5])
        exp_int_2 = 6
        res_int_3 = len(res[4])
        exp_int_3 = 2
        res_d3 = res[4]
        res_d3 = res_d3.reset_index(drop=True)
        self.assertEqual(res_int_2, exp_int_2)
        self.assertEqual(res_int_3, exp_int_3)

        exp_d3 = [
            [1010541, 3, 2012, 8, 25, 23, 16, 46.0, 28, 257, "2012-08-25 23:16:46"],
            [1010541, 3, 2013, 2, 2, 23, 18, 7.0, 25, 203, "2013-02-02 23:18:07"],
        ]
        exp_d3 = pd.DataFrame(
            exp_d3,
            columns=[
                "station",
                "intensity",
                "year",
                "month",
                "day",
                "hour",
                "minute",
                "second",
                "intensity_equip",
                "acceleration_max_comb",
                "date_time",
            ],
        )
        exp_d3["intensity"] = exp_d3["intensity"].astype(str)
        exp_d3["date_time"] = pd.to_datetime(
            exp_d3["date_time"], format="%Y-%m-%d %H:%M:%S"
        )

        pd.testing.assert_frame_equal(res_d3, exp_d3)


class TestLatLons(unittest.TestCase):

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
        filename = root_eqanalysis / "tests" / "code_p_test.csv"
        df = pd.read_csv(filename)
        res = eqa.find_lonlat_for_station(3900131, df)
        expected = [136.766666666, 37.2833333333]
        np.testing.assert_almost_equal(res, expected, decimal=6)


class TestForeshockAftershockSwarmCorrection(unittest.TestCase):

    def test_find_correction_factor_internsity(self):
        intervals = [3, 6, 7, 10]
        suvf = [4 / 4, 3 / 4, 2 / 4, 1 / 4]
        thres = 5
        res = eqa.find_correction_factor_internsity(intervals, suvf, thres)
        exp_factor = 0.8
        exp_slope = np.nan
        self.assertEqual(res["factor"], exp_factor)

    def test_find_correction_factor_internsity_01(self):
        intervals = [3, 6, 7, 20, 50]
        suvf = [5 / 5, 4 / 5, 3 / 5, 2 / 5, 1 / 5]
        thres = 5
        res = eqa.find_correction_factor_internsity(intervals, suvf, thres)
        exp_factor = 5 / 6
        self.assertAlmostEqual(res["factor"], exp_factor, places=4)

    def test_find_correction_factor_internsity_02(self):
        intervals = [3, 6, 7]
        suvf = [3 / 3, 2 / 3, 1 / 3]
        thres = 5
        res = eqa.find_correction_factor_internsity(intervals, suvf, thres)
        exp_factor = 0.75
        self.assertAlmostEqual(res["factor"], exp_factor)

    def test_find_correction_factor(self):
        df0 = pd.DataFrame(columns=["interval", "suvf", "counts"])
        df1 = pd.DataFrame(columns=["interval", "suvf", "counts"])
        df2 = pd.DataFrame(columns=["interval", "suvf", "counts"])
        df3 = pd.DataFrame(columns=["interval", "suvf", "counts"])
        df4 = pd.DataFrame(columns=["interval", "suvf", "counts"])
        df0["interval"] = [3, 6, 7, 20, 50]
        df0["suvf"] = [5 / 5, 4 / 5, 3 / 5, 2 / 5, 1 / 5]
        df0["counts"] = [5, 4, 3, 2, 1]
        df1["interval"] = [3, 6, 7, 10]
        df1["suvf"] = [1, 0.75, 0.5, 0.25]
        df1["counts"] = [4, 3, 2, 1]
        df2["interval"] = [3, 6, 7]
        df2["suvf"] = [1, 2 / 3, 1 / 3]
        df2["counts"] = [3, 2, 1]
        dfs = [df0, df1, df2, df3, df4]
        res = eqa.find_correction_factor(dfs, thres_int=[5, 5, 5, 5, 5])
        exp_d = [
            [5 / 6, np.nan, np.nan, np.nan],
            [0.8, np.nan, np.nan, np.nan],
            [0.75, np.nan, np.nan, np.nan],
            [0, np.nan, np.nan, np.nan],
            [0, np.nan, np.nan, np.nan],
        ]
        exp_df = pd.DataFrame(exp_d)
        exp_df.columns = ["factor", "intercept", "slope", "rvalue"]
        pd.testing.assert_frame_equal(res, exp_df, rtol=1e-3)

    def test_calc_corrected_ro(self):
        factor_data = [
            [0.55, np.log10(0.55), -0.05, -0.998],
            [0.71, np.log10(0.71), -0.02, -0.999],
            [0.8, np.log10(0.8), -0.005, -0.9995],
            [1, np.nan, np.nan, np.nan],
        ]
        df_factor = pd.DataFrame(
            factor_data, columns=["factor", "intercept", "slope", "rvalue"]
        )
        ro = np.array([75, 26, 5, 2])
        res = eqa.calc_corrected_ro(df_factor, ro)
        exp_df_corrected = pd.DataFrame(
            np.nan,
            index=[0, 1, 2, 3, 4, 5, 6],
            columns=[
                "intensity",
                "factor",
                "intercept",
                "slope",
                "rvalue",
                "ro",
                "corrected",
            ],
        )
        exp_df_corrected["intensity"] = [1, 2, 3, 4, 5, 6, 7]
        exp_df_corrected["factor"] = [0.55, 0.71, 0.8, 1, np.nan, np.nan, np.nan]
        exp_df_corrected["intercept"] = [
            np.log10(0.55),
            np.log10(0.71),
            np.log10(0.8),
            np.nan,
            np.nan,
            np.nan,
            np.nan,
        ]
        exp_df_corrected.loc[:2, "slope"] = [-0.05, -0.02, -0.005]
        exp_df_corrected.loc[:2, "rvalue"] = [-0.998, -0.999, -0.9995]
        exp_df_corrected.loc[:3, "ro"] = ro
        exp_df_corrected.loc[:3, "corrected"] = [0.55 * 75, 0.71 * 26, 0.8 * 5, 2]
        pd.testing.assert_frame_equal(res, exp_df_corrected, rtol=1e-3)

class TestFindCorrectionFactorVariousThresholds(unittest.TestCase):

    def test_find_correction_factor_vt_01(self):
        df0 = pd.DataFrame(columns=["interval", "suvf", "counts"])
        df1 = pd.DataFrame(columns=["interval", "suvf", "counts"])
        df2 = pd.DataFrame(columns=["interval", "suvf", "counts"])
        df3 = pd.DataFrame(columns=["interval", "suvf", "counts"])
        df4 = pd.DataFrame(columns=["interval", "suvf", "counts"])
        thres_int_given = [5, 10, 11, 66, 78]
        df0["interval"] = [3, 6, 7, 20, 50]  # over thres 4/5 -> 5/6
        df0["suvf"] = [5 / 5, 4 / 5, 3 / 5, 2 / 5, 1 / 5]
        df0["counts"] = [5, 4, 3, 2, 1]
        df1["interval"] = [2, 4, 12, 16]  # over thres 2/4 -> 3/5
        df1["suvf"] = [1, 0.75, 0.5, 0.25] 
        df1["counts"] = [4, 3, 2, 1]
        df2["interval"] = [9, 15, 30]  # over thres 2/3 -> 3/4
        df2["suvf"] = [1, 2 / 3, 1 / 3]
        df2["counts"] = [3, 2, 1]
        dfs = [df0, df1, df2, df3, df4]
        res = eqa.find_correction_factor(dfs, thres_int_given)
        exp_d = [
            [5 / 6, np.nan, np.nan, np.nan],
            [0.6, np.nan, np.nan, np.nan],
            [0.75, np.nan, np.nan, np.nan],
            [0, np.nan, np.nan, np.nan],
            [0, np.nan, np.nan, np.nan],
        ]
        exp_df = pd.DataFrame(exp_d)
        exp_df.columns = ["factor", "intercept", "slope", "rvalue"]
        pd.testing.assert_frame_equal(res, exp_df, rtol=1e-3)


class TestWithRealData(unittest.TestCase):

    def test_do_aftershock_correction(self):
        # filename = "eqanalysis/data_2024/" + "intermediates/organized_code_2024_04.csv"
        filename = (
            root_eqanalysis
            / "data_2024"
            / "intermediates"
            / "organized_code_2024_04.csv"
        )
        df_org = pd.read_csv(filename)
        # dir_data = "eqanalysis/data_2024/stationwise_2021/"
        dir_data = root_eqanalysis / "data_2024" / "stationwise_2021"
        set_dict = {"set_from": "1996-04-01 12:00:00", "set_to": "2021-12-31 23:59:59"}
        dfs_intervals = eqa.create_interval_datasets_ts(
            df_org, 3500000, set_dict, dir_data
        )
        ro, summary = eqa.find_intensity_ro_summarize_ts(
            df_org, 3500000, set_dict, dir_data=dir_data
        )
        ro = np.array(ro.astype(np.float64))
        thres_int = [5, 10, 11, 66, 78]
        df_factor = eqa.find_correction_factor(dfs_intervals, thres_int)
        print()
        print(df_factor)
        dfs_intervals, df_corrected, summary = \
            eqa.do_aftershock_correction(
                df_org, 3500000, set_dict, dir_data, thres_int=thres_int
            )
        print(df_corrected)
        print(summary)
        thres_int = [4, 8, 16, 32, 64]
        df_factor = eqa.find_correction_factor(dfs_intervals, thres_int)
        print()
        print(df_factor)
        dfs_intervals, df_corrected, summary = \
            eqa.do_aftershock_correction(
                df_org, 3500000, set_dict, dir_data
            )
        print(df_corrected)
        print(summary)

    # def test_find_having_int_7(self):
    #     #
    #     # TODO use "stationwise_test"
    #     #
    #     fn_meta = root_eqanalysis / "data_2024" / "code_p_20231205_df.csv"
    #     meta = pd.read_csv(fn_meta)
    #     dir_data = root_eqanalysis / "data_2024" / "stationwise_2021"
    #     res = eqa.find_having_int_7(meta, dir_data)
    #     print(res)


if __name__ == "__main__":
    unittest.main()
