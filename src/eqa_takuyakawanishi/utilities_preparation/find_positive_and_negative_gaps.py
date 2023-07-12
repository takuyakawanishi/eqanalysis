import numpy as np
import pandas as pd


def find_positive_gaps(meta):
    meta = meta.reset_index(drop=True)
    codes = meta["code_prime"]
    gaps = meta.at[13, "gaps"]
    gaps = eval(gaps)
    print(type(gaps))
    print(gaps)
    for gap in gaps:
        print(type(gap))
    count = 0
    for i_code, code in enumerate(codes):
        gaps = meta.at[i_code, "gaps"]
        gaps = eval(gaps)
        flag = 0
        for gap in gaps:
            if gap > 0:
                count += 1
                flag = 1
        if flag == 1:
            print("Gap in station {}, {}".format(code, gaps))
    return count


def main():
    dir_data = "../../../data/stationwise_fine_old_until_2019/"
    df = pd.read_csv("../../../intermediates/olds/organized_codes_pre_01.csv")

    count = find_positive_gaps(df)
    print("Number of stations having positive gaps in measurement periods is {}".format(count))

    dfgaps = df["gaps"].astype(str)
    dfgaps2 = dfgaps.str.contains("-")
    count = 0
    count_i = 0
    for i in range(len(dfgaps2)):
        if dfgaps2[i]:
            count += 1
            # print(i, df.at[i, "codes_ordered"],  dfgaps[i])
            stations = eval(df.at[i, "codes_ordered"])
            # print(stations)
            date_maxs = []
            date_mins = []

            for station in stations:
                dfsts = []
                # print(station)
                try:
                    dfst = pd.read_csv(dir_data + 'st_' + str(station) + '.txt')
                except Exception as ex:
                    print(ex)
                else:
                    dfsts.append(dfst)
                for dfst in dfsts:
                    dfst = dfst[dfst['day'] != "  "]
                    dfst.loc[dfst['day'] == '//', 'day'] = '15'
                    dfst['date'] = pd.to_datetime(dfst[['year', 'month', 'day']])
                    date_max = dfst['date'].max()
                    date_min = dfst['date'].min()
                    date_maxs.append(date_max)
                    date_mins.append(date_min)
            #print(date_mins, date_maxs)
            for i_date, date_max in enumerate(date_maxs[:-1]):
                #print(date_max, date_mins[i_date + 1])
                if date_max > date_mins[i_date + 1]:
                    print("INCONSISTENCY, at {}".format(stations))
                    count_i += 1

    print("Number of stations containing minus gap is {}, ".format(count))
    print("in which having overlapped data is {}.".format(count_i))
    # print(dfgaps2)

if __name__ == '__main__':
    main()