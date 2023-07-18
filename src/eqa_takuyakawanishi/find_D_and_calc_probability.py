import datetime
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import src.eqa_takuyakawanishi.eqa as eqa


def main():
    dir_data = "../../data/stationwise/"
    meta2read = "../../intermediates/organized_codes_pre_02.csv"
    meta = pd.read_csv(meta2read)
    file2read = "../../intermediates/intensity_D.csv"
    df = pd.read_csv(file2read)
    print(df)
    pno_s =[]
    for i in range(len(df)):
        station = df.at[i, "code_prime"]
        # print(station, type(station))
        [year, month, day] = df.loc[i, ["year", "month", "day"]]
        try:
            date = datetime.datetime(int(year), int(month), int(day))
        except Exception as ex:
            print(ex)
            continue
        day_before = date - datetime.timedelta(days=1)
        # print(date, day_before)
        day_before_str = datetime.datetime.strftime(day_before, "%Y-%m-%d")
        set_dict = {"set_from": "1919-01-01", "set_to": day_before_str}
        frequency, regression, summary = \
            eqa.find_intensity_frequency_regression_summarize(
                meta, station, set_dict, dir_data=dir_data)
        duration = summary["duration"]
        est7 = summary["est7"]
        est_6 = summary["est6"]
        pno = np.exp(- est_6 * (duration / 365.2425))
        pno_s.append(pno)
        print(station, pno)

    fig, ax = plt.subplots()
    ser = pd.Series(pno_s)
    ser.hist(ax=ax)
    plt.show()


if __name__ == "__main__":
    main()