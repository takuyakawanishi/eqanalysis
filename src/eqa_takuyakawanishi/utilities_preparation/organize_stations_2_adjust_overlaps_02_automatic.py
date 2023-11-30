import copy
import datetime
import numpy as np
import pandas as pd
import sys


def calc_gaps(dfg):
    codes = list(dfg["code_prime"])
    gapss = []
    for i_code, code in enumerate(codes):
        stations = eval(dfg.loc[i_code, "codes_ordered"])
        n_st = len(stations)
        gaps = []
        count = 0
        if n_st > 1:
            date_b_s = eval(dfg.loc[i_code, "date_b_s"])
            date_e_s = eval(dfg.loc[i_code, "date_e_s"])
            for i in range(1, n_st):
                date_b_1 = datetime.datetime.strptime(date_b_s[i], "%Y-%m-%d")
                date_e_0 = datetime.datetime.strptime(
                    date_e_s[i - 1], "%Y-%m-%d")
                # print(date_b_s)
                # print(date_e_s)
                gap = (date_b_1 - date_e_0).days
                if gap < 0:
                    print("minus gaps found at ", code)
                # print(gap)
                gaps.append(gap)
                count += 1
            # print(code, gaps)

        gapss.append(gaps)
    dfg["gaps"] = gapss
    return dfg


def main():
    dir_data = "../../../data/stationwise/"
    df = pd.read_csv("../../../intermediates/organized_codes_pre_01.csv")
    df = df.reset_index(drop=True)
    df["date_b_s_old"] = None
    df["date_e_s_old"] = None
    df["datetime_b_s_old"] = None
    df["datetime_e_s_old"] = None
    print("CAUTION")
    print("For station 3010031, we set dates of operation manually.")
    print("We have to update the date in date_e_s '2023-12-31' if necessary.")
    idx = df.index[df["code_prime"] == 3010031]
    df.loc[idx, "date_b_s_old"] = df.loc[idx, "date_b_s"].copy()
    df.loc[idx, "date_e_s_old"] = df.loc[idx, "date_e_s"].copy()
    df.loc[idx, "datetime_b_s_old"] = df.loc[idx, "datetime_b_s"].copy()
    df.loc[idx, "datetime_e_s_old"] = df.loc[idx, "datetime_e_s"].copy()
    df.loc[idx, "date_b_s"] = str(['1998-10-15', '2017-11-01'])
    df.loc[idx, "date_e_s"] = str(['2017-11-01', '2023-12-31'])
    df.loc[idx, "datetime_b_s"] = str(
        ['1998-10-15 12:00:00', '2017-11-01 12:00:00'])
    df.loc[idx, "datetime_e_s"] = str(
        ['2017-11-01 12:00:00', '2023-12-31 12:00:00'])

    print(df.loc[idx, :])
    # sys.exit()

    #
    df["gaps_old"] = df["gaps"].copy()
    dfgaps = df["gaps"].astype(str)
    dfgaps2 = dfgaps.str.contains("-")
    count = 0
    for i_code in range(len(dfgaps)):
        if dfgaps2[i_code] and df.at[i_code, "code_prime"] != 3010031:
            count += 1
            station_prime = df.at[i_code, "code_prime"]
            stations = eval(df.loc[i_code, "codes_ordered"])
            gaps = eval(df.loc[i_code, "gaps"])
            date_b_s = eval(df.loc[i_code, "date_b_s"])
            date_e_s = eval(df.loc[i_code, "date_e_s"])
            datetime_b_s = eval(df.loc[i_code, "datetime_b_s"])
            datetime_e_s = eval(df.loc[i_code, "datetime_e_s"])
            #
            # Using copy.deepcopy() is essential.
            #
            date_b_s_old = copy.deepcopy(date_b_s)
            date_e_s_old = copy.deepcopy(date_e_s)
            datetime_b_s_old = copy.deepcopy(datetime_b_s)
            datetime_e_s_old = copy.deepcopy(datetime_e_s)

            for i_gap, gap in enumerate(gaps):
                if gap < 0:
                    date_e_0 = datetime.datetime.strptime(
                        date_e_s[i_gap], "%Y-%m-%d")
                    date_b_1 = datetime.datetime.strptime(
                        date_b_s[i_gap + 1], "%Y-%m-%d")
                    datetime_e_0 = datetime.datetime.strptime(
                        datetime_e_s[i_gap], "%Y-%m-%d %H:%M:%S")
                    datetime_b_1 = datetime.datetime.strptime(
                        datetime_b_s[i_gap + 1], "%Y-%m-%d %H:%M:%S")
                    station_0 = stations[i_gap]
                    station_1 = stations[i_gap + 1]
                    dfst_0 = None
                    dfst_1 = None
                    try:
                        dfst_0 = pd.read_csv(
                            dir_data + "st_" + str(station_0) + ".txt")
                    except Exception as ex:
                        print("At station_0 ", station_0, ex)
                        continue
                    try:
                        dfst_1 = pd.read_csv(
                            dir_data + "st_" + str(station_1) + ".txt")
                    except Exception as ex:
                        print("At station_1 ", station_1, ex)
                        continue
                    print(station_prime)
                    dfst_1 = dfst_1[dfst_1['day'] != "  "]
                    dfst_1.loc[dfst_1['day'] == '//', 'day'] = '15'
                    dfst_1['date'] = pd.to_datetime(
                        dfst_1[['year', 'month', 'day']])

                    date_1_min = dfst_1['date'].min()

                    dfst_0 = dfst_0[dfst_0['day'] != "  "]
                    dfst_0.loc[dfst_0['day'] == '//', 'day'] = '15'
                    dfst_0['date'] = pd.to_datetime(
                        dfst_0[['year', 'month', 'day']])

                    date_0_max = dfst_0['date'].max()

                    if date_1_min > date_e_0:

                        new_date_b_1 = date_e_0
                        new_datetime_b_1 = datetime_e_0

                        date_b_s[i_gap + 1] = datetime.datetime.strftime(
                            new_date_b_1, "%Y-%m-%d")
                        datetime_b_s[i_gap + 1] = datetime.datetime.strftime(
                            new_datetime_b_1, "%Y-%m-%d %H:%M:%S")
                        df.loc[i_code, "date_b_s"] = str(date_b_s)
                        df.loc[i_code, "date_b_s_old"] = str(date_b_s_old)
                        df.loc[i_code, "datetime_b_s"] = str(datetime_b_s)
                        df.loc[i_code, "datetime_b_s_old"] = \
                            str(datetime_b_s_old)
                        #
                        # TODO: Suppressing the following print statement
                        #  together with the similar one for _e below
                        #  have altered the results. Why?

                        print(df.loc[i_code, ["date_b_s_old", "date_b_s"]])

                    elif date_0_max < date_b_1:
                        new_date_e_0 = date_b_1
                        new_datetime_e_0 = datetime_b_1
                        date_e_s[i_gap] = datetime.datetime.strftime(
                            new_date_e_0, "%Y-%m-%d"
                        )
                        datetime_e_s[i_gap] = datetime.datetime.strftime(
                            new_datetime_e_0, "%Y-%m-%d %H:%M:%S"
                        )
                        df.loc[i_code, "date_e_s"] = str(date_e_s)
                        df.loc[i_code, "date_e_s_old"] = str(date_e_s_old)
                        df.loc[i_code, "datetime_e_s"] = str(datetime_e_s)
                        df.loc[i_code, "datetime_e_s_old"] = \
                            str(datetime_e_s_old)
                        #
                        # TODO: Suppressing the following print statement
                        #  together with the similar one for _b above
                        #  have altered the results. Why?
                        # print(df.loc[i_code, ["date_e_s_old", "date_e_s"]])

                    else:
                        print("MANUAL ADJUSTMENT is NECESSARY at {}".format(
                            station_prime))

    print("Number of station_primes containing minus gap is {}, ".format(count))
    print()
    print()
    for i_code in range(len(dfgaps2)):
        if (df.loc[i_code, "datetime_e_s_old"] is not None) or \
                (df.loc[i_code, "datetime_b_s_old"] is not None):
            print(df.loc[i_code, "code_prime"])

            print(df.at[i_code, "datetime_b_s_old"])
            print(df.at[i_code, "datetime_b_s"])
            print(df.at[i_code, "datetime_e_s"])
            print(df.at[i_code, "datetime_e_s_old"])
            print()
    
    df = calc_gaps(df)
    df.to_csv("../../../intermediates/organized_codes_pre_02.csv", index=None)


if __name__ == '__main__':
    main()