import datetime
import numpy as np
import pandas as pd
import sys
sys.path.append("./")
import eqanalysis.src.eqa_takuyakawanishi.eqa as eqa


def find_first_and_last_record_of_station(station, dir_data):
    fn = dir_data + "st_" + str(station) + ".txt"
    df = pd.read_csv(fn)
    df = eqa.add_datetime_column_to_dataframe(df)
    # print(df)
    first = datetime.datetime.strftime(
        df.at[df.index[0], "date_time"], "%Y-%m-%d %H:%M:%S")
    last = datetime.datetime.strftime(
        df.at[df.index[-1], "date_time"], "%Y-%m-%d %H:%M:%S")
    return [first, last]


def add_address_only_column_to_df(df):
    for i in df.index:
        s = df.at[i, "address"]
        if "（臨" in s:
            df.at[i, "address_only"] = s[:s.index("（")] + "（臨時）"
        elif "（測候所" in s:
            df.at[i, "address_only"] = s[:s.index("（")] + "（測候所）"
        elif "（" in s:
            df.at[i, "address_only"] = s[:s.index("（")]
        elif "＊" in s:
            df.at[i, "address_only"] = s[:s.index("＊")]
        else:
            df.at[i, "address_only"] = s
    return df


def find_kyu_index_and_order_them(df):
    n = len(df)
    if n == 1:
        return df
    else:
        for i in range(n):
            s = df.at[i, "remark"]
            if type(s) != str:
                df.at[i, "order"] = n - 1
            elif s[2] == "）":
                df.at[i, "order"] = 0
            elif s[2] == "２":
                df.at[i, "order"] = 1
            elif s[2] == "３":
                df.at[i, "order"] = 2
            elif s[2] == "４":
                df.at[i, "order"] = 3
            try:
                df = df.sort_values("order")
            except Exception as ex:
                print(ex)
                print("Exception occurred at", s)
            df = df.reset_index(drop=True)
    return df


def combine_kyu_indexed_stations(df):
    df = add_address_only_column_to_df(df)
    df["remark"] = df["address"].str.extract("(\uff08.+)")
    dfa = df.groupby("address_only")
    keys = dfa.groups.keys()
    dfc = pd.DataFrame(columns=["code_prime", "address", "codes_ordered"])
    dfc["codes_ordered"].astype("object")
    for key in keys:
        dfsel = df[df["address_only"] == key]
        dfsel = dfsel.reset_index(drop=True)
        if len(dfsel) > 1:
            dfsel = find_kyu_index_and_order_them(dfsel)
        dfc.loc[len(dfc.index)] = [
            dfsel.at[0, "code"], key, dfsel["code"].to_list(), 
            ]
    dfc = dfc.sort_values(by="code_prime")
    dfc = dfc.reset_index(drop=True)
    return dfc


def find_operation_years_from_station_wise_data_ts(code, dir_data):
    fn = dir_data + 'st_' + str(code) + '.txt'
    df = pd.read_csv(fn)
    beginning = str(df['year'].min()) + '-01-01 00:00:00'
    end = str(df['year'].max()) +'-12-31 23:59:59'
    return beginning, end


def organize_beginning_dates(station, date_from, dir_data):
    str_from = str(date_from)
    year = str_from[0:4]
    month = str_from[4:6]
    day = str_from[6:8]
    hour = str_from[8:10]
    minute = str_from[10:12]
    if year == '9999':
        dt_stw, _  = \
            find_operation_years_from_station_wise_data_ts(station, dir_data)
        dt_b = datetime.datetime.strptime(dt_stw, "%Y-%m-%d %H:%M:%S")
    else:
        if month == '99':
            month = '01'
        if day == '99':
            day = '01'
        if hour == '99':
            hour = '00'
        if minute == '99':
            minute = '00'
        year = int(year)
        month = int(month)
        day = int(day)
        hour = int(hour)
        minute = int(minute)
        dt_b = datetime.datetime(year, month, day, hour, minute, 0)
    dt_b_str = datetime.datetime.strftime(dt_b, "%Y-%m-%d %H:%M:%S")
    return dt_b_str
    

def organize_ending_dates(
        station, date_to, datetime_end_record, dir_data):
    if np.isnan(date_to):
        dt_e = datetime.datetime.strptime(
            datetime_end_record, "%Y-%m-%d %H:%M:%S")
    else:
        str_to = str(date_to)
        year = str_to[:4]
        month = str_to[4:6]
        day = str_to[6:8]
        hour = str_to[8:10]
        minute = str_to[10:12]
        if year == '9999':
            _, end = find_operation_years_from_station_wise_data_ts(station, dir_data)
            dt_e = datetime.datetime.strptime(end, "%Y-%m-%d %H:%M:%S")
        else:
            if month == '99':
                month = '12'
            if day == '99':
                day = '28'
            if hour == '99':
                hour = '23'
            if minute == '99':
                minute = '59'
            year = int(year)
            month = int(month)
            day = int(day)
            hour = int(hour)
            minute = int(minute)
            dt_e = datetime.datetime(year, month, day, hour, minute, 0)
    dt_e_str = datetime.datetime.strftime(dt_e, "%Y-%m-%d %H:%M:%S")
    return dt_e_str


def organize_beginnings_and_endings(
        stations, df_code_p, datetime_end_record, dir_data):
    # print(stations)
    dtbfs = []
    dtefs = []
    for station in stations:
        dtbl = df_code_p.loc[df_code_p["code"] == station, "from"].to_list()
        dtbf = organize_beginning_dates(station, dtbl[0], dir_data)
        dtbfs.append(dtbf)
        dtel = df_code_p.loc[df_code_p["code"] == station, "to"].to_list()
        dtef = organize_ending_dates(
            station, dtel[0], datetime_end_record, dir_data)
        dtefs.append(dtef)
    return dtbfs, dtefs


def add_datetime_beginning_and_end(
        df_org_01, df_code_p, datetime_end_record, dir_data):
    df_org_02 = df_org_01.copy()
    df_org_02["datetime_b_s"] = pd.Series(
        [[] for i in range(len(df_org_02.index))])
    df_org_02["datetime_e_s"] = pd.Series(
        [[] for i in range(len(df_org_02.index))])
    df_org_02["datetime_b_s"] = df_org_02["datetime_b_s"].astype("object")
    df_org_02["datetime_e_s"] = df_org_02["datetime_e_s"].astype("object")
    for idx in df_org_01.index:
        stations = df_org_01.at[idx, "codes_ordered"]
        if type(stations) is str:
            stations = eval(stations)
        dtbfs, dtefs = organize_beginnings_and_endings(
            stations, df_code_p, datetime_end_record, dir_data)
        df_org_02.at[idx, "datetime_b_s"] = dtbfs
        df_org_02.at[idx, "datetime_e_s"] = dtefs
    return df_org_02


def calc_gaps(df_in):
    df = df_in.copy()
    df["gaps"] = pd.Series([[] for i in range(len(df.index))])
    df["gaps"].astype("object")
    for idx in df.index:
        stations = df.at[idx, "codes_ordered"]
        if type(stations) is str:
            stations = eval(stations)
        n_station = len(stations)
        datetime_b_s = df.at[idx, "datetime_b_s"]
        datetime_e_s = df.at[idx, "datetime_e_s"]
        gaps = []
        if n_station > 1:
            for i in range(n_station - 1):
                datetime_b = datetime_b_s[i + 1]
                datetime_e = datetime_e_s[i]
                datetime_b = datetime.datetime.strptime(
                    datetime_b, "%Y-%m-%d %H:%M:%S")
                datetime_e = datetime.datetime.strptime(
                    datetime_e, "%Y-%m-%d %H:%M:%S")
                gap = (datetime_b - datetime_e).days
                gaps.append(gap)
        df.at[idx, "gaps"] = gaps
    return df


def adjust_periods(i_gap, stations, dtbs, dtes, dir_data):
    if type(dtbs) is str:
        dtbs = eval(dtbs)
    if type(dtes) is str:
        dtes = eval(dtes)
    if type(stations) is str:
        stations = eval(stations)
    overwrapped = [dtbs[i_gap + 1], dtes[i_gap]]
    prec_period = find_first_and_last_record_of_station(
        stations[i_gap], dir_data)
    foll_period = find_first_and_last_record_of_station(
        stations[i_gap + 1], dir_data)
    pe = datetime.datetime.strptime(prec_period[1], "%Y-%m-%d %H:%M:%S")
    ob = datetime.datetime.strptime(overwrapped[0], "%Y-%m-%d %H:%M:%S")
    oe = datetime.datetime.strptime(overwrapped[1], "%Y-%m-%d %H:%M:%S")
    fb = datetime.datetime.strptime(foll_period[0], "%Y-%m-%d %H:%M:%S")
    if pe < ob:
        dtes[i_gap] = dtbs[i_gap + 1]
        print("Preceding period was adjusted at station {}".\
              format(stations[i_gap]))
    elif oe < fb:
        dtbs[i_gap + 1] = dtes[i_gap]
        print("Following period was adjusted at station {}".\
              format(stations[i_gap + 1]))
    else:
        print("Data should be handled manually at {}".format(stations[0]))
    return dtbs, dtes


def adjust_overwrap(cp_1, dir_data):
    gaps = cp_1.at[0, "gaps"]
    stations = cp_1.at[0, "codes_ordered"]
    dtbs = cp_1.at[0, "datetime_b_s"]
    dtes = cp_1.at[0, "datetime_e_s"]
    # print(dtbs)
    # print(type(dtbs))
    if type(gaps) is str:
        gaps = eval(gaps)
    for i_gap, gap in enumerate(gaps):
        if gap < 0:
            dtbs, dtes = adjust_periods(i_gap, stations, dtbs, dtes, dir_data)
    return dtbs, dtes
            

def organize_negative_gaps(df, dir_data):
    df_new = df.copy()
    for idx in df_new.index:
        # print(df_new.at[idx, "code_prime"])
        code_prime = df_new.at[idx, "code_prime"]
        gaps = df_new.at[idx, "gaps"]
        if type(gaps) is str:
            gaps = eval(gaps)
        # print(gaps)
        gaps = np.array(gaps)
        if len(gaps) == 0:
            continue
        elif gaps.min() < 0:
            cp_1 = df_new[df_new["code_prime"] == code_prime]
            cp_1 = cp_1.reset_index(drop=True)
            dtbs, dtes = adjust_overwrap(cp_1, dir_data)
            df_new.at[idx, "datetime_b_s"] = dtbs
            df_new.at[idx, "datetime_e_s"] = dtes
    return df_new


def add_latitude_longitude(df, df_code_p):
    df = df.copy()
    df["lat"] = np.zeros(len(df))
    df["lon"] = np.zeros(len(df))
    # print(df.head(3))
    for idx in df.index:
        code = df.at[idx, "code_prime"]
        # print("code = ", code)
        ix = df_code_p[df_code_p["code"] == code].index[0]
        # print(ix)
        # print(int(df_code_p.at[ix, "lat"]))
        # sys.exit()
        df.at[idx, "lat"] = int(df_code_p.at[ix, "lat"])
        df.at[idx, "lon"] = int(df_code_p.at[ix, "lon"])
    df["lat"] = df["lat"].astype(int)
    df["lon"] = df["lon"].astype(int)
    return df


def main():
    dir_data = "eqanalysis/data_2024/stationwise_2021/"
    end_year = dir_data[-5:-1]
    datetime_end_record = str(eval(end_year)) + "-12-31 23:59:59"
    print(datetime_end_record)
    #
    fn_code_p = "eqanalysis/data_2024/code_p_20231205_df.csv"
    fn_org_01 = \
        "eqanalysis/data_2024/intermediates/organized_code_2024_01.csv"
    fn_org_02 = \
        "eqanalysis/data_2024/intermediates/organized_code_2024_02.csv"
    fn_org_03 = \
        "eqanalysis/data_2024/intermediates/organized_code_2024_03.csv"
    fn_org_04 = \
        "eqanalysis/data_2024/intermediates/organized_code_2024_04.csv"
    fn_org_05 = \
        "eqanalysis/data_2024/intermediates/organized_code_2024_05.csv"
    #
    # Read and correct df_code_p
    #
    df_code_p = pd.read_csv(fn_code_p)
    df_code_p.at[3592, "address"] ="浜松天竜区佐久間町（修）＊"
    df_code_p.at[3542, "address"] = "牧之原市静波（修）＊"
    df_code_p.at[5767, "address"] = " 岩国市今津（修）"
    df_code_p.at[5768, "address"] = " 岩国市今津（修２）"
    df_code_p.at[5770, "address"] = " 光市岩田（修２）"
    #
    df_org_01 = combine_kyu_indexed_stations(df_code_p)
    df_org_01 = add_latitude_longitude(df_org_01, df_code_p)
    df_org_01.to_csv(fn_org_01, index=False)
    # sys.exit()
    df_org_02 = add_datetime_beginning_and_end(
        df_org_01, df_code_p, datetime_end_record, dir_data)
    df_org_03 = calc_gaps(df_org_02)
    df_tmp = organize_negative_gaps(df_org_03, dir_data)
    df_org_04 = calc_gaps(df_tmp)

    df_org_02.to_csv(fn_org_02, index=False)
    df_org_03.to_csv(fn_org_03, index=False)
    df_org_04.to_csv(fn_org_04, index=False)


if __name__ == "__main__":
    main()

    