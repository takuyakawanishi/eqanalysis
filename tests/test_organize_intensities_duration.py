import unittest
from src.eqa import *
from src.create_stationwise_dataframe import *

class MyTestCase(unittest.TestCase):


    def test_date_beginning(self):
        strdt = '192012311230'
        dt_res = date_beginning_to_datetime(strdt)
        dt_expected = datetime.datetime(1920, 12, 31, 12, 30)
        self.assertEqual(dt_res, dt_expected)

    def test_date_beginning_02(self):
        strdt = '999999999999'
        dt_res = date_beginning_to_datetime(strdt)
        dt_expected = np.nan
        np.testing.assert_equal(dt_res, dt_expected)

    def test_date_beginning_03(self):
        strdt = '196099999999'
        dt_res = date_beginning_to_datetime(strdt)
        dt_expected = datetime.datetime(1960, 1, 1, 0, 0)
        self.assertEqual(dt_res, dt_expected)

    def test_calc_date_beginning(self):
        meta = pd.read_csv('../../code_p_df_old.csv')
        meta_sel = meta.iloc[[732, 765, 807]]
        meta_sel = meta_sel.reset_index(drop=True)
        res = calc_date_beginning(meta_sel)
        print(res)
        res_date_b = list(res['date_b'])
        dt_a_exp = datetime.datetime(1919, 1, 1, 0, 0)
        dt_b_exp = pd.NaT
        dt_c_exp = datetime.datetime(1958, 8, 1, 0, 0)
        expected = [dt_a_exp, dt_b_exp, dt_c_exp]
        self.assertListEqual(res_date_b, expected)

    def test_date_end(self):
        strdt = '192806281200'
        res = date_end_to_datetime(strdt)
        expected = datetime.datetime(1928, 6, 28, 12, 0)
        self.assertEqual(res, expected)

    def test_date_end(self):
        strdt = '192806281200'
        res = date_end_to_datetime(strdt)
        expected = datetime.datetime(1928, 6, 28, 12, 0)
        self.assertEqual(res, expected)

    def test_date_end_02(self):
        strdt = '999906281200'
        res = date_end_to_datetime(strdt)
        expected = np.nan
        np.testing.assert_equal(res, expected)

    def test_date_end_03(self):
        strdt = '196099999999'
        res = date_end_to_datetime(strdt)
        expected = datetime.datetime(1960, 12, 28, 23, 59)
        self.assertEqual(res, expected)

    def test_calc_date_end(self):
        meta = pd.read_csv('../../code_p_df_old.csv')
        meta_sel = meta.iloc[[140, 156, 240]]
        meta_sel = meta_sel.reset_index(drop=True)
        # print(meta_sel['to'])
        res = calc_date_end(meta_sel)
        print(meta_sel)
        res_date_e = list(res['date_e'])
        a = datetime.datetime(1975, 1, 25, 23, 59)
        b = pd.NaT
        c = datetime.datetime(2011, 5, 12, 13, 00)
        expected = [a, b, c]
        self.assertListEqual(res_date_e, expected)

    def test_calc_latlon(self):
        meta = pd.read_csv('../../code_p_df_old.csv')
        meta_sel = meta.iloc[[4298, 4299, 4300]]
        meta_sel = meta_sel.reset_index(drop=True)
        print(meta_sel)
        res = calc_latlon(meta_sel)
        lats = list(res['latitude'])
        lons = list(res['longitude'])
        lat_a = 34 + 32 / 60
        lon_a = 134 + 59 / 60
        lat_c = 34 + 42 / 60
        lon_c = 135 + 50 / 60
        lats_expected = [lat_a, np.nan, lat_c]
        lons_expected = [lon_a, np.nan, lon_c]
        print(meta_sel)
        np.testing.assert_almost_equal(lats, lats_expected, decimal=2)
        np.testing.assert_almost_equal(lons, lons_expected, decimal=2)

if __name__ == '__main__':
    unittest.main()
