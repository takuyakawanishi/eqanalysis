import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import scipy.stats
import src.eqa_takuyakawanishi.eqa as eqa


def main():
    dir_data = "../../data/stationwise_fine_old_until_2019/"
    file2read = "../../intermediates/organized_codes_pre_02.csv"
    meta = pd.read_csv(file2read)

    codes = meta["code_prime"]
    set_dict = {"set_from": "1919-01-01", "set_to": "2020-12-31"}
    count = 0
    for i_code, code in enumerate(codes):
        frequency, regression, summary = \
            eqa.find_intensity_frequency_regression_summarize(
                meta, code, set_dict, dir_data=dir_data
            )
        if summary["duration"] > 20 * 365.2425:
            print("Station {} satisfies the condition.".format(code))
            count += 1
            highest = len(frequency)
            est = highest + 1
            est_freq = np.exp(
                - 10 ** (regression.intercept + regression.slope * est) * \
                (summary["duration"] / 365.2425)
            )
            print(code, est, est_freq)
    print(count)
    print(len(meta))


if __name__ == "__main__":
    main()
