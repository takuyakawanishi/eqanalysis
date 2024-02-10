import numpy as np
import pandas as pd
from pandas.testing import assert_frame_equal
import unittest
import sys
sys.path.append("./")
import eqanalysis.src.eqa_takuyakawanishi.utilities_preparation.\
    organize_stations_2024 as os2024


class TestOrganizeStations2024(unittest.TestCase):

    def test_first_and_last_record_of_station(self):
        dir_data = "eqanalysis/data_2024/stationwise_2021/"
        station = 1220131
        res_1, res_2 = os2024.find_first_and_last_record_of_station(
            station, dir_data)
        expected_1 = "2002-08-25 03:42:33"
        expected_2 = "2011-04-07 23:34:51"
        self.assertEqual(res_1, expected_1)
        self.assertEqual(res_2, expected_2)    
    
    def test_add_address_only_column_to_df(self):
        df = pd.read_csv("eqanalysis/tests/code_p_test.csv")
        df_res = os2024.add_address_only_column_to_df(df)
        df_exp = pd.read_csv(
            "eqanalysis/tests/code_p_test_01_address_only_added.csv")
        # df_exp["to"].astype(float)
        assert_frame_equal(df_res, df_exp)

    def test_find_kyu_index_and_order_them(self):
        df = {"address":["金沢（旧２）", "金沢（旧）", "金沢", "金沢（修３）"],
              "address_only":["金沢", "金沢", "金沢", "金沢"]}
        df = pd.DataFrame.from_dict(df)
        df["remark"] = df["address"].str.extract("(\uff08.+)")
        df_res = os2024.find_kyu_index_and_order_them(df)        
        df_exp = {
            "address":["金沢（旧）", "金沢（旧２）", "金沢（修３）", "金沢"],
             "address_only":["金沢", "金沢", "金沢", "金沢"],
             "remark":["（旧）", "（旧２）", "（修３）", np.nan],
             "order":[0., 1., 2., 3.]}
        df_exp = pd.DataFrame.from_dict(df_exp)
        assert_frame_equal(df_res, df_exp)

    def test_combine_kyu_indexed_stations(self):
        df = {
            "code": [3001, 3002, 3010, 3020, 3021, 3023],
            "address":["野々市", "野々市（旧）", "小松（旧）", "小松（旧２）", "小松", "加賀"]}
        df = pd.DataFrame.from_dict(df)
        dfc_res = os2024.combine_kyu_indexed_stations(df)
        dfc_exp = {
            "code_prime":[3002, 3010, 3023],
            "address": ["野々市", "小松", "加賀"],       
            "codes_ordered":[[3002, 3001], [3010, 3020, 3021], [3023]]}
        dfc_exp = pd.DataFrame.from_dict(dfc_exp)
        assert_frame_equal(dfc_res, dfc_exp)

    def test_operation_years_from_station_wise_data_ts(self):
        dir_data = "eqanalysis/tests/stationwise_test/"
        code = 1000
        res_b, res_e = os2024.find_operation_years_from_station_wise_data_ts(
            code, dir_data
        )
        exp_b = "1996-01-01 00:00:00"
        exp_e = "1998-12-31 23:59:59"
        self.assertEqual(res_b, exp_b)
        self.assertEqual(res_e, exp_e)

    def test_organize_beginning_dates(self):
        df = {"code":10100,
              "address":["札幌中央区北２条"],
              "lat":4304,
              "lon":14120,
              "from":187699999999}
        df = pd.DataFrame.from_dict(df)
        date_from = "187699999999"
        res = os2024.organize_beginning_dates(10100, date_from, "")
        exp = "1876-01-01 00:00:00"
        self.assertEqual(res, exp)

    def test_organize_beginning_dates_02(self):
        station = 2205271
        dir_data = "eqanalysis/tests/stationwise_test/"
        date_from = "999999999999"
        res = os2024.organize_beginning_dates(station, date_from, dir_data)
        exp = "1951-01-01 00:00:00"
        self.assertEqual(res, exp)

    def test_organize_ending_dates(self):
        station = 2205271
        dir_data = "eqanalysis/tests/stationwise_test/"
        date_to = 999999999999.0
        datetime_end_record = "2022-01-01 00:00:00"
        res = os2024.organize_ending_dates(
            station, date_to, datetime_end_record, dir_data)
        exp = "1977-12-31 23:59:59"
        self.assertEqual(res, exp)

    def test_organize_ending_dates_02(self):
        station = 2502330
        dir_data = "eqanalysis/tests/stationwise_test/"
        date_to = 201006259999.9
        datetime_end_record = "2022-01-01 00:00:00"
        res = os2024.organize_ending_dates(
            station, date_to, datetime_end_record, dir_data)
        exp = "2010-06-25 23:59:00"
        self.assertEqual(res, exp)

    def test_organize_beginnings_and_endings(self):

        lst = [[2501530, "大玉村玉井（旧）＊", 3732, 14022, 
                200112121200,201210111200.0],
               [2501531, "大玉村玉井（旧２）＊", 3732, 14022,
                201210111200, 201303141200.0],
               [2501532, "大玉村玉井＊", 3732, 14022, 201303141200,	np.nan]]
        df = pd.DataFrame(
            lst, columns=["code", "address", "lat", "lon", "from", "to"]
        )
        datetime_end_record = "2022-01-01 00:00:00"
        # print(df)
        stations = [2501530, 2501531, 2501532]
        res_dtbfs, res_dtefs = os2024.organize_beginnings_and_endings(
            stations, df, datetime_end_record, "")
        exp_dtbfs = [
            "2001-12-12 12:00:00", "2012-10-11 12:00:00",
            "2013-03-14 12:00:00"
        ]
        exp_dtefs = [
            "2012-10-11 12:00:00", "2013-03-14 12:00:00",
            "2022-01-01 00:00:00"
        ]
        self.assertEqual(res_dtbfs, exp_dtbfs)
        self.assertEqual(res_dtefs, exp_dtefs)

    ###########################################################################
    # We skip the test for add_datetime_beginning_and_end
    ###########################################################################

    def test_calc_gaps(self):
        list = [[3001, [3001, 3002, 3003], 4210, 13500, 
                ["1996-04-01 12:00:00", "2001-10-10 12:00:00",
                 "2006-02-03 12:00:00"],
                ["2001-12-11 12:00:00", "2005-12-31 12:00:00",
                 "2022-01-01 00:00:00"]
        ]]
        df = pd.DataFrame(list, columns=[
            "code_prime", "codes_ordered", "lat", "lon",
            "datetime_b_s", "datetime_e_s"
        ])
        # print(df)
        df_res = os2024.calc_gaps(df)
        df_gaps = pd.DataFrame(columns=["gaps"])
        df_gaps["gaps"] = [[-62, 34]]
        # print(df_gaps)
        df_exp = pd.concat([df, df_gaps], axis=1)
        assert_frame_equal(df_res, df_exp)

    def test_adjust_overwrap(self):
        fn_code_p02 = "eqanalysis/data_2024/intermediates/organized_code_2024_03.csv" 
        dir_data = "eqanalysis/data_2024/stationwise_2021/"
        code_p02 = pd.read_csv(fn_code_p02)
        code_prime = 1220131
        cp_1 = code_p02[code_p02["code_prime"] == code_prime]
        cp_1 = cp_1.reset_index(drop=True)
        # print(cp_1)
        res = os2024.adjust_overwrap(cp_1, dir_data)
        expected_dtbs = eval(cp_1.at[0, "datetime_b_s"])
        expected_dtes = [
            '2011-05-12 13:00:00', '2016-02-19 12:00:00', 
            '2022-01-01 00:00:00']
        self.assertListEqual(res[0], expected_dtbs)
        self.assertListEqual(res[1], expected_dtes)

    ###########################################################################
    # We skip the test for organize_negativ_gaps
    ###########################################################################

    ###########################################################################
    # We skip the test for add_latitude_longitude
    ###########################################################################


if __name__ == '__main__':
    unittest.main()
