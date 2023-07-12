import datetime
import numpy as np
import pandas as pd


def calc_periodes_intersection(period_0, period_1):
    b_0 = datetime.datetime.strptime(period_0[0], "%Y-%m-%d")
    e_0 = datetime.datetime.strptime(period_0[1], "%Y-%m-%d")
    b_1 = datetime.datetime.strptime(period_1[0], "%Y-%m-%d")
    e_1 = datetime.datetime.strptime(period_1[1], "%Y-%m-%d")
    b = max(b_0, b_1)
    e = min(e_0, e_1)
    if b > e:
        b = np.nan
        e = np.nan
    return b, e


def calc_durations(dfg, set_b, set_e, station):
    idx = dfg.index[dfg["code_prime"] == station]
    date_b_s = eval(dfg.loc[idx, "date_b_s"].tolist()[0])
    date_e_s = eval(dfg.loc[idx, "date_e_s"].tolist()[0])
    periods = []
    for i_b, date_b in enumerate(date_b_s):
        periods.append([date_b, date_e_s[i_b]])

    # print(periods)
    set_period = [set_b, set_e]
    durations = []
    periods_str = []
    for period in periods:
        b, e = calc_periodes_intersection(set_period, period)
        print(b, type(b))
        duration = 0
        b_str = ""
        e_str = ""
        try:
            duration = (e - b).days
        except Exception as ex:
            print(ex)
        else:
            b_str = datetime.datetime.strftime(b, "%Y-%m-%d")
            e_str = datetime.datetime.strftime(e, "%Y-%m-%d")
        finally:
            print(b, e, duration)
        periods_str.append([b_str, e_str])
        durations.append(duration)
    durations = np.array(durations)
    return periods_str, durations


def main():
    filename = "../../intermediates/organized_codes.csv"
    dfg = pd.read_csv(filename)
    set_b = "2010-04-01"
    set_e = "2019-12-31"
    station = 1450510
    res = calc_durations(dfg, set_b, set_e, station)
    print(repr(res), res[1].sum())


if __name__ == '__main__':
    main()