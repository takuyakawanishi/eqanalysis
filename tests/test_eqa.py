import unittest
from src.eqa import *


class MyTestCase(unittest.TestCase):

    def test_find_days_cros_the_intercept(self):
        x = [1, 2, 3, 4, 5]
        suvf = [.9, .8, .7, .6, .5]
        intercept = .55
        res = find_days_cros_the_intercept(x, suvf, intercept)
        res = list(res)
        self.assertListEqual(res, [4, 5])
    """
    
    def test_something(self):
        dir = '../../stationwise/'
        code = 3910000
        res = create_subdfs_by_intensities(code, dir=dir)
        print(res)
        expected = datetime.datetime.strptime('1997-03-16', '%Y-%m-%d')
        # self.assertEqual(res, expected)  # add assertion here
    """



if __name__ == '__main__':
    unittest.main()
