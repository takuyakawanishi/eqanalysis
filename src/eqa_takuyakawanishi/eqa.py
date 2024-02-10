import datetime
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import scipy.stats
import scipy.ndimage as ndimage
import warnings
import sys


class Settings:

    def __init__(self):
        self.date_beginning = '1919-01-01'
        self.date_end = '2100-12-31'
        self.datetime_beginning = "1919-01-01 12:00:00"
        dt_now = datetime.datetime.now()
        self.datetime_end = datetime.datetime.strftime(
            dt_now, "%Y-%m-%d %H:%M:%S")
        self.duration_min = 5
        self.remiflt = {
            '1': 7, '2': 10, '3': 32, '4': 46, '5': 46, '6': 46, '7': 46
        }
        self.range_exp_fit_low = [20, 20, 50, 50, 50, 50, 50]
        self.range_exp_fit_upp = [100, 100, 1000, 1000, 1000, 1000, 1000]
        self.intensities = [1, 2, 3, 4, 5, 6, 7]
        self.n_int3_min = 1
        self.n_int4_min = 1
        self.n_int5_min = 0
        self.n_int6_min = 0

################################################################################
#  Utility
################################################################################

def round_to_k(x, k):
    return round(x, -int(np.floor(np.log10(abs(x)))) - 1 + k)


# The following is from
# https://towardsdatascience.com/dealing-with-list-values-in-pandas-dataframes-a177e534f173
def clean_alt_list(list_):
    list_ = list_.replace(', ', '","')
    list_ = list_.replace('[', '["')
    list_ = list_.replace(']', '"]')
    return list_


################################################################################
#
#   Analysis based on organized_meta
#
################################################################################


# def find_available_periods(meta, station):
#     meta_1 = meta[meta["code_prime"] == station]
#     meta_1 = meta_1.reset_index(drop=True)
#     dfsp = pd.DataFrame(columns=["station", "from", "to"])
#     dfsp["station"] = eval(meta_1.at[0, "codes_ordered"])
#     dfsp["from"] = eval(meta_1.at[0, "date_b_s"])
#     dfsp["to"] = eval(meta_1.at[0, "date_e_s"])
#     return dfsp


# def calc_periods_durations(df_available, set_period):
#     """
#     Input
#         df_available: see above
#         set_period = dict {"set_from": "%Y-%m-%d", "set_to": "%Y-%m-%d"}
#     """
#     available_periods = df_available[["from", "to"]].values.tolist()
#     set_period = list(set_period.values())
#     periods_durations = []
#     for period in available_periods:
#         b, e = calc_periods_intersection(set_period, period)
#         duration = 0
#         b_str = ""
#         e_str = ""
#         if isinstance(b, datetime.datetime):
#             duration = (e - b).days
#             b_str = datetime.datetime.strftime(b, "%Y-%m-%d")
#             e_str = datetime.datetime.strftime(e, "%Y-%m-%d")
#         periods_durations.append([b_str, e_str, duration])
#     df = pd.DataFrame(periods_durations, columns=["from", "to", "duration"])
#     df["station"] = df_available["station"]
#     df = df[["station", "from", "to", "duration"]]
#     return df


# def calc_periods_intersection(period_0, period_1):
#     try:
#         b_0 = datetime.datetime.strptime(period_0[0], "%Y-%m-%d")
#         e_0 = datetime.datetime.strptime(period_0[1], "%Y-%m-%d")
#         b_1 = datetime.datetime.strptime(period_1[0], "%Y-%m-%d")
#         e_1 = datetime.datetime.strptime(period_1[1], "%Y-%m-%d")
#     except Exception as ex:
#         # print(ex)
#         b = np.nan
#         e = np.nan
#     else:
#         b = max(b_0, b_1)
#         e = min(e_0, e_1)
#     if b > e:
#         b = np.nan
#         e = np.nan
#     return b, e


def count_intensity_in_dataframe(df):
    df["intensity"] = df["intensity"].astype(str)
    # print(df)
    counts = np.zeros(7)
    cum_counts = np.zeros(7)
    counts[0] = len(df[df["intensity"] == "1"])
    counts[1] = len(df[df["intensity"] == "2"])
    counts[2] = len(df[df["intensity"] == "3"])
    counts[3] = len(df[df["intensity"] == "4"])
    counts[4] = len(df[df["intensity"] == "5"]) + \
        len(df[df["intensity"] == "A"]) + \
        len(df[df["intensity"] == "B"])
    counts[5] = len(df[df["intensity"] == "6"]) + \
        len(df[df["intensity"] == "C"]) + \
        len(df[df["intensity"] == "D"])
    counts[6] = len(df[df["intensity"] == "7"])
    # print(counts, counts.sum(), len(df))
    if counts.sum() != len(df):
        print("Inconsistency in counts, sum of counts is not equal to len(df).")
        print(df)
    for i in range(len(counts)):
        cum_counts[i] = counts[i:].sum()
    return cum_counts


# def add_date_column_to_dataframe(df):
#     df.loc[df['day'] == '//', 'day'] = 15
#     df = df.drop(df[df.day == "  "].index)
#     df = df.drop(df[df.day == '00'].index)
#     df['date'] = pd.to_datetime(df[['year', 'month', 'day']])
#     return df


# def take_data_subset_by_period(station, date_b, date_e, dir_data):
#     try:
#         df = pd.read_csv(dir_data + 'st_' + str(station) + '.txt')
#     except Exception as ex:
#         df = None
#         print(ex, " at ", station)
#     else:
#         date_b = datetime.datetime.strptime(date_b, "%Y-%m-%d")
#         date_e = datetime.datetime.strptime(date_e, "%Y-%m-%d")
#         df = add_date_column_to_dataframe(df)
#         df = df[(df["date"] >= date_b) & (df["date"] <= date_e)]
#     return df


# def create_intensity_frequency_table_of_period(actual, dir_data='./'):
#     columns = ["int1", "int2", "int3", "int4", "int5", "int6", "int7"]
#     stations = actual["station"].values
#     cum_counts_s = []
#     for i_station, station in enumerate(stations):
#         if actual.at[i_station, "duration"] == 0:
#             cum_counts = np.zeros(7)
#         else:
#             date_b = actual.at[i_station, "from"]
#             date_e = actual.at[i_station, "to"]
#             df = take_data_subset_by_period(station, date_b, date_e, dir_data)
#             if df is not None:
#                 cum_counts = count_intensity_in_dataframe(df)
#             else:
#                 cum_counts = np.zeros(7)
#         cum_counts_s.append(cum_counts)
#     df_c = pd.DataFrame(cum_counts_s, columns=columns)
#     actual_res = pd.concat([actual, df_c], axis=1)
#     actual_res_sum = actual_res.sum()
#     actual_res_sum["station"] = actual_res.at[0, "station"]
#     duration = actual_res_sum["duration"]
#     frequency = actual_res_sum[columns]
#     frequency = frequency[frequency > 0] / duration * 365.2425
#     return frequency, actual_res_sum


def find_regression_int_freq(frequency):
    freq_values = frequency.values
    n = len(freq_values)
    ints = np.arange(n) + 1
    lfreq = np.log10(freq_values.astype(np.float64))
    res = None
    est7 = None
    est6 = None
    est6p5 = None
    try:
        res = scipy.stats.linregress(ints[1:], lfreq[1:])
    except Exception as ex:
        print(ex)
    else:
        est7 = 10 ** (res.intercept + res.slope * 7)
        est6 = 10 ** (res.intercept + res.slope * 6)
        est6p5 = 10 ** (res.intercept + res.slope * 6.5)
    return res, est7, est6, est6p5


# def find_intensity_frequency_regression_summarize(
#         meta, station, set_dict, dir_data='./'):
#     available = find_available_periods(meta, station)
#     actual = calc_periods_durations(available, set_dict)
#     frequency, summary = \
#         create_intensity_frequency_table_of_period(actual, dir_data)
#     summary["from"] = summary["from"][:10]
#     summary["to"] = summary["to"][-10:]
#     summary["slope"] = np.nan
#     summary["intercept"] = np.nan
#     summary["rvalue"] = np.nan
#     summary["est7"] = np.nan
#     summary["est6p5"] = np.nan
#     summary["est6"] = np.nan
#     regression = None
#     if len(frequency) > 2:
#         regression, est7, est6, est6p5 = find_regression_int_freq(frequency)
#         summary["slope"] = np.round(regression.slope, 3)
#         summary["intercept"] = np.round(regression.intercept, 3)
#         summary["rvalue"] = np.round(regression.rvalue, 3)
#         summary["est7"] = round_to_k(est7, 3)
#         summary["est6"] = round_to_k(est6, 3)
#         summary["est6p5"] = round_to_k(est6p5, 3)
#     return frequency, regression, summary


################################################################################
#    Considering the time up to seconds (TS)
################################################################################


def find_available_periods_ts(meta, station):
    meta_1 = meta[meta["code_prime"] == station]
    meta_1 = meta_1.reset_index(drop=True)
    return find_available_periods_meta_1_ts(meta_1)
   

def find_available_periods_meta_1_ts(meta_1):
    dfsp = pd.DataFrame(columns=["station", "from", "to"])
    dfsp["station"] = eval(meta_1.at[0, "codes_ordered"])
    dfsp["from"] = eval(meta_1.at[0, "datetime_b_s"])
    dfsp["to"] = eval(meta_1.at[0, "datetime_e_s"])
    return dfsp


def calc_periods_intersection_ts(period_0, period_1):
    try:
        b_0 = datetime.datetime.strptime(period_0[0], "%Y-%m-%d %H:%M:%S")
        e_0 = datetime.datetime.strptime(period_0[1], "%Y-%m-%d %H:%M:%S")
        b_1 = datetime.datetime.strptime(period_1[0], "%Y-%m-%d %H:%M:%S")
        e_1 = datetime.datetime.strptime(period_1[1], "%Y-%m-%d %H:%M:%S")
    except Exception as ex:
        # print(ex)
        b = np.nan
        e = np.nan
    else:
        b = max(b_0, b_1)
        e = min(e_0, e_1)
    if b > e:
        b = np.nan
        e = np.nan
    return b, e


def calc_periods_durations_ts(df_available, set_period):
    available_periods = df_available[["from", "to"]].values
    set_period = list(set_period.values())
    periods_durations = []
    for period in available_periods:
        b, e = calc_periods_intersection_ts(set_period, period)
        duration = 0
        b_str = ""
        e_str = ""
        if isinstance(b, datetime.datetime):
            duration = (e - b).days
            b_str = datetime.datetime.strftime(b, "%Y-%m-%d %H:%M:%S")
            e_str = datetime.datetime.strftime(e, "%Y-%m-%d %H:%M:%S")
        periods_durations.append([b_str, e_str, duration])
    df = pd.DataFrame(periods_durations, columns=["from", "to", "duration"])
    df["station"] = df_available["station"]
    df = df[["station", "from", "to", "duration"]]
    return df


def add_datetime_column_to_dataframe(df):
    """
    Feb 2. 2024, df["second"] == '  . ' added.
    """
    df = df.drop(df[df.day == "  "].index)
    df = df.drop(df[df.day == '00'].index)
    df.loc[df['day'] == '//', 'day'] = 15
    df.loc[df['hour'] == '//', 'hour'] = 12
    df.loc[df['hour'] == '  ', 'hour'] = 12
    df.loc[df['minute'] == '//', 'minute'] = 0
    df.loc[df['minute'] == '  ', 'minute'] = 0
    df.loc[df['second'] == '//. ', 'second'] = 0
    df.loc[df['second'] == '  . ', 'second'] = 0
    df.loc[df['second'] == '2 . ', 'second'] = 0
    df.loc[df['second'] == '3 . ', 'second'] = 0
    df.loc[df['second'] == '4 . ', 'second'] = 0
    df.loc[df['second'] == '5 . ', 'second'] = 0
    df.loc[df['second'] == '7 . ', 'second'] = 0
    df.loc[df['second'] == '0 . ', 'second'] = 0
    try:
        df['date_time'] = pd.to_datetime(
            df[['year', 'month', 'day', 'hour', 'minute', 'second']])
        return df
    except Exception as ex:
        print(ex)
        sys.exit()


def take_data_subset_by_period_ts(station, datetime_b, datetime_e, dir_data):
    try:
        df = pd.read_csv(dir_data + 'st_' + str(station) + '.txt')
    except Exception as ex:
        df = None
        print(ex, " at ", station)
    else:
        date_b = datetime.datetime.strptime(datetime_b, "%Y-%m-%d %H:%M:%S")
        date_e = datetime.datetime.strptime(datetime_e, "%Y-%m-%d %H:%M:%S")
        df = add_datetime_column_to_dataframe(df)
        df = df[(df["date_time"] >= date_b) & (df["date_time"] <= date_e)]
    return df


def create_intensity_frequency_table_of_period_ts(actual, dir_data='./'):
    columns = ["int1", "int2", "int3", "int4", "int5", "int6", "int7"]
    stations = actual["station"].values
    cum_counts_s = []
    for i_station, station in enumerate(stations):
        if actual.at[i_station, "duration"] == 0:
            cum_counts = np.zeros(7)
        else:
            date_b = actual.at[i_station, "from"]
            date_e = actual.at[i_station, "to"]
            df = take_data_subset_by_period_ts(
                station, date_b, date_e, dir_data)
            if df is not None:
                cum_counts = count_intensity_in_dataframe(df)
            else:
                cum_counts = np.zeros(7)
        cum_counts_s.append(cum_counts)
    df_c = pd.DataFrame(cum_counts_s, columns=columns)
    actual_res = pd.concat([actual, df_c], axis=1)
    actual_res_sum = actual_res.sum()
    actual_res_sum["station"] = actual_res.at[0, "station"]
    duration = actual_res_sum["duration"]
    frequency = actual_res_sum[columns]
    frequency = frequency[frequency > 0] / duration * 365.2425
    return frequency, actual_res_sum


def find_intensity_frequency_regression_summarize_ts(
        meta, station, set_dict, dir_data='./'):
    meta_1 = meta[meta["code_prime"] == station]
    meta_1 = meta_1.reset_index(drop=True)
    available = find_available_periods_meta_1_ts(meta_1)
    actual = calc_periods_durations_ts(available, set_dict)
    frequency, summary = \
        create_intensity_frequency_table_of_period_ts(actual, dir_data)
    summary["from"] = summary["from"][:10]
    summary["to"] = summary["to"][:10]
    summary["slope"] = np.nan
    summary["intercept"] = np.nan
    summary["rvalue"] = np.nan
    summary["est7"] = np.nan
    summary["est6p5"] = np.nan
    summary["est6"] = np.nan
    summary["address"] = meta_1.at[0, "address"]
    regression = None
    if len(frequency) > 2:
        regression, est7, est6, est6p5 = find_regression_int_freq(frequency)
        summary["slope"] = np.round(regression.slope, 3)
        summary["intercept"] = np.round(regression.intercept, 3)
        summary["rvalue"] = np.round(regression.rvalue, 3)
        summary["est7"] = round_to_k(est7, 3)
        summary["est6"] = round_to_k(est6, 3)
        summary["est6p5"] = round_to_k(est6p5, 3)
    return frequency, regression, summary


def find_first_and_last_record_of_station(station, dir_data):
    fn = dir_data + "st_" + str(station) + ".txt"
    df = pd.read_csv(fn)
    df = add_datetime_column_to_dataframe(df)
    # print(df)
    first = datetime.datetime.strftime(
        df.at[df.index[0], "date_time"], "%Y-%m-%d %H:%M:%S")
    last = datetime.datetime.strftime(
        df.at[df.index[-1], "date_time"], "%Y-%m-%d %H:%M:%S")
    return [first, last]


def find_datetime_beginning(code, num_from, datetime_beginning, dir_data='./'):
    datetime_beginning = datetime.datetime.strptime(
        datetime_beginning, "%Y-%m-%d %H:%M:%S")
    str_from = str(num_from)
    year = str_from[0:4]
    month = str_from[4:6]
    day = str_from[6:8]
    hour = str_from[8:10]
    minute = str_from[10:12]
    if year == '9999':
        stationwise_from, _ = find_operation_period_from_station_wise_data_ts(
            code, dir_data)
        datetime_beginning_read = datetime.datetime.strptime(
            stationwise_from, "%Y-%m-%d %H:%M:%S")
    else:
        if month == '99':
            month = '01'
        if day == '99':
            day = '01'
        if hour == '99':
            hour = '12'
        if minute == '99':
            minute = '00'
        year = int(year)
        month = int(month)
        day = int(day)
        hour = int(hour)
        minute = int(minute)
        datetime_beginning_read = datetime.datetime(
            year, month, day, hour, minute, 0)
    if datetime_beginning_read > datetime_beginning:
        datetime_beginning = datetime_beginning_read
    return datetime_beginning


def find_datetime_end(code, to, datetime_end, dir_data='./'):
    datetime_end = datetime.datetime.strptime(
        datetime_end, "%Y-%m-%d %H:%M:%S")
    if np.isnan(to):
        return datetime_end
    else:
        str_to = str(to)
        year = str_to[:4]
        month = str_to[4:6]
        day = str_to[6:8]
        hour = str_to[8:10]
        minute = str_to[10:12]
    if year == '9999':
        _, end = find_operation_period_from_station_wise_data_ts(code, dir_data)
        datetime_end_read = datetime.datetime.strptime(end, "%Y-%m-%d %H:%M:%S")
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
        datetime_end_read = datetime.datetime(year, month, day, hour, minute, 0)
    if datetime_end_read < datetime_end:
        datetime_end = datetime_end_read
    return datetime_end


def find_operation_period_from_station_wise_data_ts(code, dir_data):
    fn = dir_data + 'st_' + str(code) + '.txt'
    df = pd.read_csv(fn)
    beginning = str(df['year'].min()) + '-01-01 12:00:00'
    end = str(df['year'].max()) + '-12-31 23:59:59'
    return beginning, end


def calc_datetime_b_datetime_e_duration(
        meta_in, date_beginning, date_end, dir_data='./'):
    meta = meta_in.copy()
    codes = list(meta['code'])
    for i_code, code in enumerate(codes):
        date_b = find_datetime_beginning(
            code, meta.at[i_code, 'from'], date_beginning, dir_data)
        date_e = find_datetime_end(
            code, meta.at[i_code, 'to'], date_end, dir_data)
        meta.at[i_code, 'datetime_b'] = date_b
        meta.at[i_code, 'datetime_e'] = date_e
        meta.at[i_code, 'duration_ts'] = (date_e - date_b).days / 365.2425
    return meta

#
# def read_12digit_datetime(dt12):
#     dt12 = dt12
#     year = dt12[:4]
#     month = dt12[4:6]
#     day = dt12[6:8]
#     hour = dt12[8:10]
#     minute = dt12[10:12]
#     return datetime.datetime(year, month, day, hour, minute, 0)


################################################################################
#   Find high intensity earthquakes
################################################################################


def extract_quakes_by_intensities(
        meta, intensities, dir_data):
    codes = list(meta["code_prime"])
    count = 0
    dfs = None
    for i_code, code in enumerate(codes):
        df = None
        try:
            df = find_intensities(
                meta, code, intensities, dir_data=dir_data)
            df["code_prime"] = code
        except Exception as ex:
            print(ex)
        if df is not None:
            if not df.empty:
                if count == 0:
                    dfs = df
                    count += 1
                else:
                    dfs = pd.concat([dfs, df], axis=0)
    return dfs


def find_intensities(meta, station, intensities, dir_data="./"):
    available = find_available_periods(meta, station)
    stations = available["station"]
    df_sub_s = []
    for station in stations:
        filename = dir_data + "st_" + str(station) + ".txt"
        df = pd.read_csv(filename)
        df["intensity"] = df["intensity"].astype(str)
        for intensity in intensities:
            idx = df.index[df["intensity"] == intensity]
            df_sub = df.loc[idx]
            if df_sub is not None:
                if not df_sub.empty:
                    df_sub_s.append(df_sub)
    df_ext = None
    if len(df_sub_s) != 0:
        df_ext = pd.concat(df_sub_s, axis=0)
        df_ext = df_ext.sort_values(by="intensity", ascending=False)
    return df_ext


def screening_stations(meta, cond_dict, set_dict, dir_data='./'):
    codes = meta["code_prime"].values
    n_code = len(codes)
    satisfied = np.ones(n_code)
    est6s = np.zeros(n_code)
    est7s = np.zeros(n_code)
    for i_code, code in enumerate(codes):
        if np.mod(i_code, 100) == 0:
            print("Now processing {}/{}, number = {}".
                  format(i_code, n_code, code))
        available = find_available_periods(meta, code)
        df = calc_periods_durations(available, set_dict)
        if df['duration'].sum() < cond_dict["duration"] * 365.2425:
            satisfied[i_code] = 0
            continue
        cum_counts = count_intensities(df, dir_data=dir_data)
        index = "int" + str(cond_dict["intensity"])
        if cum_counts[index].sum() == 0:
            satisfied[i_code] = 0
            continue
        if satisfied[i_code] == 1:
            frequency, actual_res_sum = \
                create_intensity_frequency_table_of_period(df, dir_data)
            res, est7, est6 = find_regression_int_freq(frequency)
            est7s[i_code] = est7
            est6s[i_code] = est6
    summary = pd.DataFrame(
        [satisfied, est7s, est6s], columns=["satisfied", "est7", "est6"])
    print(summary)
    return summary


################################################################################
#
#   Based on codes_p
#
################################################################################

################################################################################
#   Dates, Periods
################################################################################

# def organize_record_period_of_station(meta, code):
#     str_b = meta['from']
#     str_d = meta['to']
#     meta['date_b'] = calc_date_beginning(str_b)
#     meta['date_e'] = date_end_to_datetime(str_e)
#     return meta


def find_date_beginning(code, dfrom, date_beginning, dir_data='./'):
    strfrom = str(dfrom)
    year = strfrom[0:4]
    month = strfrom[4:6]
    day = strfrom[6:8]
    if year == '9999':
        dfrom, _ = find_operation_period_from_station_wise_data(
            code, dir_data)
    else:
        if month == '99':
            month = '01'
        if day == '99':
            day = '01'
        dfrom = year + '-' + month + '-' + day
    date_beginning_read = datetime.datetime.strptime(dfrom, "%Y-%m-%d")
    date_beginning = datetime.datetime.strptime(date_beginning, "%Y-%m-%d")
    if date_beginning_read > date_beginning:
        date_beginning = date_beginning_read
    return date_beginning


def find_date_end(code, to, date_end, dir_data='./'):
    if np.isnan(to):
        return datetime.datetime.strptime(date_end, "%Y-%m-%d")
    else:
        strto = str(to)
        year = strto[:4]
        month = strto[4:6]
        day = strto[6:8]
    # print(strto)
    if year == '9999':
        _, end = find_operation_period_from_station_wise_data(
            code, dir_data)
    else:
        if month == '99':
            month = '12'
        if day == '99':
            day = '28'
        end = year + '-' + month + '-' + day
    date_end_read = datetime.datetime.strptime(end, "%Y-%m-%d")
    date_end = datetime.datetime.strptime(date_end, "%Y-%m-%d")
    if date_end_read < date_end:
        date_end = date_end_read
    return date_end


def find_operation_period_from_station_wise_data(code, dir_data):
    fn = dir_data + 'st_' + str(code) + '.txt'
    df = pd.read_csv(fn)
    beginning = str(df['year'].min()) + '-01-01'
    end = str(df['year'].max()) + '-12-31'
    return beginning, end


def calc_date_b_date_e_duration(
        meta_in, date_beginning, date_end, dir_data='./'):
    meta = meta_in.copy()
    codes = list(meta['code'])
    for i_code, code in enumerate(codes):
        date_b = find_date_beginning(
            code, meta.at[i_code, 'from'], date_beginning, dir_data)
        date_e = find_date_end(
            code, meta.at[i_code, 'to'], date_end, dir_data)
        meta.at[i_code, 'date_b'] = date_b
        meta.at[i_code, 'date_e'] = date_e
        meta.at[i_code, 'duration'] = (date_e - date_b).days / 365.2425
    return meta


# def calc_date_b_date_e_duration_old(meta, date_beginning, date_end):
#     meta = calc_date_beginning(meta)
#     meta = calc_date_end(meta)
#     meta.loc[:, 'beginning'] = datetime.datetime.strptime(
#         date_beginning, "%Y-%m-%d")
#     meta.loc[:, 'end'] = datetime.datetime.strptime(date_end, "%Y-%m-%d")
#     meta['date_b_sub'] = meta[['date_b', 'beginning']].max(axis=1)
#     meta['date_e_sub'] = meta[['date_e', 'end']].min(axis=1)
#     # codes = list(meta['code'])
#     # for i_code, code in enumerate(codes):
#     #     a = meta.at[i_code, 'date_e_sub']
#     #     if np.isnan(a):
#     #         print("date_e is nan at {}".format(i_code))
#     meta['duration'] = (meta['date_e_sub'] - meta['date_b_sub']) / \
#                        np.timedelta64(1, 'Y')
#     return meta
#
#
#
# def datetime_from_to(meta):
#     meta = calc_date_beginning(meta)
#     meta = calc_date_end(meta)
#     return meta
#
#
# def calc_date_beginning(df):
#     dt_earliest = datetime.datetime(1919, 1, 1)
#     codes = list(df['code'])
#     for i_code, code in enumerate(codes):
#         # print(i_code)
#         # print(df.at[i_code, 'from'])
#         strdt = str(df.at[i_code, 'from'])[:8]
#         # print(strdt)
#         dt_beginning = date_beginning_to_datetime(strdt)
#         try:
#             if dt_beginning < dt_earliest:
#                 dt_beginning = dt_earliest
#                 # print(i_code, 'dt_b < dt_e')
#             df.at[i_code, 'date_b'] = dt_beginning
#             # print(i_code, dt_beginning)
#         except:
#             df.at[i_code, 'date_b'] = pd.NaT
#             # print(i_code, df.at[i_code, 'date_b'])
#     return df
#
#
# def calc_date_end(df):
#     codes = list(df['code'])
#     for i_code, code in enumerate(codes):
#         if np.isnan(df.at[i_code, 'to']):
#             df.at[i_code, 'date_e'] = datetime.datetime(2019, 12, 31)
#         else:
#             dt_end = date_end_to_datetime(str(df.at[i_code, 'to']))
#             df.at[i_code, 'date_e'] = dt_end
#     return df
#
#
# def date_beginning_to_datetime(strdt):
#     year = strdt[:4]
#     month = strdt[4:6]
#     day = strdt[6:8]
#     # time = strdt[8:12]
#     if year == '9999':
#         return np.nan
#     else:
#         if month == '99':
#             month = '01'
#         if day == '99':
#             day = '01'
#         # if time == '9999':
#         #     time = '0000'
#         dt = datetime.datetime.strptime(year + month + day, '%Y%m%d')
#         return dt
#
#
# def date_end_to_datetime(strdt):
#     year = strdt[:4]
#     month = strdt[4:6]
#     day = strdt[6:8]
#     # time = strdt[8:12]
#     if year == '9999':
#         return np.nan
#     else:
#         if month == '99':
#             month = '12'
#         if day == '99':
#             day = '28'
#         # if time == '9999':
#         #     time = '2359'
#         dt = datetime.datetime.strptime(year + month + day, '%Y%m%d')
#         return dt


###############################################################################
#   Intervals
################################################################################

def calc_intervals(dir_data, code, beginning='1919-01-01', end='2100-12-31'):
    print(dir_data, code, beginning, end)
    try:
        d7, d6, d5, d4, d3, d2, d1 = create_subdfs_by_intensities(
            code, beginning=beginning, end=end,
            dir_data=dir_data)
        # print(d4)
    except ValueError as ve:
        print(code, 'cannot be read.', ve)
        # st.dfoc['rawc'] = np.nan
        # st.dfoc['aasc'] = np.nan
    except TypeError as te:
        print(code, 'cannot be read.', te)
        # st.dfoc['rawc'] = np.nan
        # st.dfoc['aasc'] = np.nan
    dfis = []
    for i in range(5):
        intensity = i + 1
        # print(intensity)
        df = eval('d' + str(intensity))
        df['date'] = pd.to_datetime(df[['year', 'month', 'day']])
        df['diff'] = df['date'].diff() / np.timedelta64(1, "D")
        intervals = (np.array(df['diff']).astype(np.float64))[1:]
        intervals = np.sort(intervals)
        n = len(intervals)
        suvf = 1 - (np.arange(n) + 1) / (n + 1)
        counts = n - np.arange(n)
        dfi = pd.DataFrame()
        dfi['interval'] = intervals
        dfi['suvf'] = suvf
        dfi['counts'] = counts
        dfis.append(dfi)
    return dfis


def calc_intervals_n_raw_counts(
        dir_data, code, beginning='1919-01-01', end='2019-12-31'):
    # print(dir_data, code, beginning, end)
    try:
        d7, d6, d5, d4, d3, d2, d1 = create_subdfs_by_intensities(
            code, beginning=beginning, end=end,
            dir_data=dir_data)
        # print(d4)
    except ValueError as ve:
        print(code, 'cannot be read.', ve)
        # st.dfoc['rawc'] = np.nan
        # st.dfoc['aasc'] = np.nan
    except TypeError as te:
        print(code, 'cannot be read.', te)
        # st.dfoc['rawc'] = np.nan
        # st.dfoc['aasc'] = np.nan
    dfis = []
    n_raws = []
    for i in range(7):
        intensity = i + 1
        # print(intensity)
        df = eval('d' + str(intensity))
        if df is not None:
            n_raws.append(len(df))
            df['date'] = pd.to_datetime(df[['year', 'month', 'day']])
            df['diff'] = df['date'].diff() / np.timedelta64(1, "D")
            intervals = (np.array(df['diff']).astype(np.float64))[1:]
            intervals = np.sort(intervals)
            n = len(intervals)
            suv_f = 1 - (np.arange(n) + 1) / (n + 1)
            counts = n - np.arange(n)
            dfi = pd.DataFrame()
            dfi['interval'] = intervals
            dfi['suvf'] = suv_f
            dfi['counts'] = counts
            dfis.append(dfi)
        else:
            n_raws.append(0)
            dfis.append(None)
    return dfis, n_raws


def calc_regression_intervals(dfis, reg_thres, upto=5):
    results = []
    for i in range(upto):
        dfi = dfis[i]
        reg_l = int(reg_thres[i, 0])
        reg_u = int(reg_thres[i, 1])
        dfi['interval'].astype(int)
        dfisel = dfi[dfi['interval'] >= reg_l]
        dfisel = dfisel[dfisel['interval'] <= reg_u]
        n_reg = len(dfisel)
        if n_reg < 3:
            print('Counts are not enough for linear regression.')
            results.append(None)
        else:
            log10suvf = np.log10(np.array(dfisel['suvf']).astype(np.float64))
            results.append(
                scipy.stats.linregress(dfisel['interval'], log10suvf))
    return results


###############################################################################
#   Longitude, Latitude
################################################################################

def calc_latitude(lat):
    lat = str(lat)
    return int(lat[:2]) + int(lat[2:4]) / 60


def calc_longitude(lon):
    lon = str(lon)
    # print(lon)
    # print(type(lon))
    return int(lon[:3]) + int(lon[3:5]) / 60


def find_lonlat_for_station(station, code_p):
    dfsel = code_p[code_p["code"] == station]
    dfsel = dfsel.reset_index(drop=True)
    # print(dfsel)
    return [calc_longitude(dfsel.at[0, "lon"]), calc_latitude(dfsel.at[0, "lat"])]


def calc_latlon(meta):
    temp = meta.loc[:, ['lat', 'lon']]
    temp['lats'] = temp['lat'].apply(str)
    temp.loc[:, 'lat0'] = temp.loc[:, 'lats'].str[:2]
    temp['lat1'] = temp['lats'].str[2:4]
    temp['lon0'] = temp['lon'].astype(str).str[:3]
    temp['lon1'] = temp['lon'].astype(str).str[3:5]
    meta['latitude'] = pd.to_numeric(temp['lat0'], errors='coerce') + \
        pd.to_numeric(temp['lat1'], errors='coerce') / 60
    meta['longitude'] = pd.to_numeric(temp['lon0'], errors='coerce') + \
        pd.to_numeric(temp['lon1'], errors='coerce') / 60
    return meta


def calc_range_latlon(meta, include_all_japan_lands):
    #
    # Consider put this in the Settings class
    #
    if include_all_japan_lands:
        lal = 20 + 25 / 60 + 31 / 3600
        lau = 45 + 33 / 60 + 26 / 3600
        lol = 122 + 55 / 60 + 57 / 3600
        lou = 153 + 59 / 60 + 12 / 3600
    else:
        lal = meta['latitude'].min()
        lau = meta['latitude'].max()
        lol = meta['longitude'].min()
        lou = meta['longitude'].max()
    return lal, lau, lol, lou


################################################################################
#   Analyze counts at intensities, with or without considering the aftershocks
################################################################################

def create_subdfs_by_intensities_new(
        station, beginning, end, dir_data='./'):
    file2read = dir_data + 'st_' + str(station) + '.txt'
    try:
        df = pd.read_csv(file2read)
    except Exception as ex:
        print('Empty data at ', station, ex)
        return None
    df = df[df['day'] != "  "]
    df.loc[df['day'] == '//', 'day'] = 15
    df = df.drop(df[df.day == '00'].index)
    df['date'] = pd.to_datetime(df[['year', 'month', 'day']])
    # beginning_dt = datetime.datetime.strptime(beginning, "%Y-%m-%d")
    # end_dt = datetime.datetime.strptime(end, "%Y-%m-%d")
    df = df[df['date'] > beginning]
    df = df[df['date'] < end]
    df['intensity'] = df['intensity'].astype(str)
    df = df.reset_index(drop=True)
    l7 = ['7']
    l6 = ['6', '7', 'C', 'D']
    l5 = ['5', '6', '7', 'A', 'B', 'C', 'D']
    l4 = ['4', '5', '6', '7', 'A', 'B', 'C', 'D']
    l3 = ['3', '4', '5', '6', '7', 'A', 'B', 'C', 'D']
    l2 = ['2', '3', '4', '5', '6', '7', 'A', 'B', 'C', 'D']
    l1 = ['1', '2', '3', '4', '5', '6', '7', 'A', 'B', 'C', 'D']
    d7 = df[df['intensity'].isin(l7)]
    d6 = df[df['intensity'].isin(l6)]
    d5 = df[df['intensity'].isin(l5)]
    d4 = df[df['intensity'].isin(l4)]
    d3 = df[df['intensity'].isin(l3)]
    d2 = df[df['intensity'].isin(l2)]
    d1 = df[df['intensity'].isin(l1)]
    return d7, d6, d5, d4, d3, d2, d1


def create_subdfs_by_intensities(
        station, beginning='1919-01-01', end='2019-12-31', dir_data='./'
):
    file2read = dir_data + 'st_' + str(station) + '.txt'
    try:
        df = pd.read_csv(file2read)
    except Exception as ex:
        print('Empty data at ', station, ex)
        return None
    df.loc[df['day'] == '//', 'day'] = 15
    df = df.drop(df[df.day == '00'].index)
    df['date'] = pd.to_datetime(df[['year', 'month', 'day']])
    beginning_dt = datetime.datetime.strptime(beginning, "%Y-%m-%d")
    end_dt = datetime.datetime.strptime(end, "%Y-%m-%d")
    df = df[df['date'] > beginning_dt]
    df = df[df['date'] < end_dt]
    df['intensity'] = df['intensity'].astype(str)
    df = df.reset_index(drop=True)
    l7 = ['7']
    l6 = ['6', '7', 'C', 'D']
    l5 = ['5', '6', '7', 'A', 'B', 'C', 'D']
    l4 = ['4', '5', '6', '7', 'A', 'B', 'C', 'D']
    l3 = ['3', '4', '5', '6', '7', 'A', 'B', 'C', 'D']
    l2 = ['2', '3', '4', '5', '6', '7', 'A', 'B', 'C', 'D']
    l1 = ['1', '2', '3', '4', '5', '6', '7', 'A', 'B', 'C', 'D']
    d7 = df[df['intensity'].isin(l7)]
    d6 = df[df['intensity'].isin(l6)]
    d5 = df[df['intensity'].isin(l5)]
    d4 = df[df['intensity'].isin(l4)]
    d3 = df[df['intensity'].isin(l3)]
    d2 = df[df['intensity'].isin(l2)]
    d1 = df[df['intensity'].isin(l1)]
    return d7, d6, d5, d4, d3, d2, d1


def count_considering_aftershocks(df, intensity, remiflt):
    n_raw_count = len(df)
    df.loc[df['day'] == '//', 'day'] = 15
    # df.loc[df['day'] == '00', 'day'] = 15
    df['diff'] = df['date'].diff() / np.timedelta64(1, "D")
    dfrem = df[df['diff'] < remiflt[str(intensity)]]
    n_to_rem = len(dfrem)
    n_rem_aftsk = n_raw_count - n_to_rem
    return n_raw_count, n_rem_aftsk


def find_regression_intensity_occurrence(
        meta, i_code, reg_for_which, reg_start, reg_end):
    ints = np.arange(reg_start, reg_end + 1)
    cols = []
    for i in ints:
        if reg_for_which == 'ras':
            cols.append('rge' + str(i) + '_ras')
        elif reg_for_which == 'raw':
            cols.append('ge' + str(i) + 'raw')
    res = None
    if meta.at[i_code, 'rge4_ras'] > 0:
        ys = meta.loc[i_code, cols]
        ys = np.array(ys)
        ys = ys.astype(np.float64)
        lys = np.log10(ys)
        try:
            res = scipy.stats.linregress(ints, lys)
        except ValueError as ve:
            print(i_code, 'regression failed.', ve)
    return res


def find_days_cros_the_intercept(x, suvf, intercept):
    df = pd.DataFrame({'x': x, 'suvf': suvf})
    # print(df)
    dfupp = df[df['suvf'] > intercept]
    dflow = df[df['suvf'] <= intercept]
    d1 = dfupp['x'].max()
    d2 = dflow['x'].min()
    return d1, d2


################################################################################
#   Find the stations recorded intensity 7 or intensity 6
################################################################################

def find_having_int_7(meta, dir_data):
    codes = list(meta['code'])
    count_int_7 = 0
    having_int_7 = []
    for code in codes:
        try:
            df = pd.read_csv(dir_data + 'st_' + str(code) + '.txt')
        except Exception as ex:
            print(ex)
        else:
            if '7' in set(df['intensity']):
                having_int_7.append(code)
    return having_int_7


def find_having_int_6(meta, dir_data):
    codes = list(meta['code'])
    count_int_7 = 0
    having_int_7 = []
    for code in codes:
        try:
            df = pd.read_csv(dir_data + 'st_' + str(code) + '.txt')
        except Exception as ex:
            print(ex)
        else:
            if '6' in set(df['intensity']) or 'C' in set(df['intensity']) or \
                    'D' in set(df['intensity']) or '7' in set(df['intensity']):
                having_int_7.append(code)
    return having_int_7


################################################################################
#   Utilities
################################################################################

def find_highest_occurrence_of_intensity_5(meta, dir_data, conf):
    dfoc_raw = pd.DataFrame()
    codes = list(meta['code'])
    for i_code, code in enumerate(codes):
        dfoc_raw.at[i_code, 'code'] = code
        dfoc_raw.at[i_code, 'ge7'] = np.nan
        dfoc_raw.at[i_code, 'ge6'] = np.nan
        dfoc_raw.at[i_code, 'ge5'] = np.nan
        dfoc_raw.at[i_code, 'ge4'] = np.nan
        dfoc_raw.at[i_code, 'ge3'] = np.nan
        dfoc_raw.at[i_code, 'ge2'] = np.nan
        dfoc_raw.at[i_code, 'ge1'] = np.nan
        try:
            d7, d6, d5, d4, d3, d2, d1 = create_subdfs_by_intensities(
                code, beginning=conf.date_beginning, end=conf.date_end,
                dir=dir_data)
        except ValueError as ve:
            print(code, 'cannot be read.', ve)
            continue
        except TypeError as te:
            print(code, 'cannot be read.', te)
            continue
        dfoc_raw.at[i_code, 'ge7'] = len(d7)
        dfoc_raw.at[i_code, 'ge6'] = len(d6)
        dfoc_raw.at[i_code, 'ge5'] = len(d5)
        dfoc_raw.at[i_code, 'ge4'] = len(d4)
        dfoc_raw.at[i_code, 'ge3'] = len(d3)
        dfoc_raw.at[i_code, 'ge2'] = len(d2)
        dfoc_raw.at[i_code, 'ge1'] = len(d1)
    dfoc_raw = dfoc_raw.sort_values(by='ge5', ascending=False)
    return dfoc_raw


def find_largest_files(dir_data):
    dfsize = pd.DataFrame(columns=['code', 'filesize'])
    with os.scandir(dir_data) as it:
        i_code = 0
        for entry in it:
            dfsize.at[i_code, 'code'] = entry.path[-11:-4]
            dfsize.at[i_code, 'filesize'] = entry.stat().st_size
            i_code += 1
    dfsize = dfsize.sort_values(by='filesize', ascending=False)
    return dfsize.head(10)


################################################################################
#   Figures
################################################################################

def create_figure_intensity_vs_occurrence(
        ser, code, intercept, slope, intensities):
    strraws = ['ge1_raw', 'ge2_raw', 'ge3_raw', 'ge4_raw', 'ge5_raw',
               'ge6_raw', 'ge7_raw']
    strrass = ['rge1_ras', 'rge2_ras', 'rge3_ras', 'rge4_ras', 'rge5_ras',
               'rge6_ras', 'rge7_ras']
    xls = np.linspace(1, 7)
    yls = 10 ** (intercept + slope * xls)
    fig = plt.figure(figsize=(2.7, 2.7))
    ax = fig.add_axes([4 / 18, 4 / 18, 3 / 4, 3 / 4])
    ax.set_yscale('log')
    ax.scatter(intensities, ser[strraws])
    ax.scatter(intensities, ser[strrass])
    ax.annotate(str(code), xy=(.9, .9), xytext=(.9, .9),
                xycoords='axes fraction',
                textcoords='axes fraction', ha='right',
                va='top')
    ax.annotate('Intensity', xy=(0.5, 0), xytext=(4 / 18 + 3 / 8, .02),
                xycoords='figure fraction',
                textcoords='figure fraction', ha='center', va='bottom')
    ax.annotate('Occurrence', xy=(0, 0.5), xytext=(.02, 4 / 18 + 3 / 8),
                xycoords='figure fraction',
                textcoords='figure fraction', ha='left', va='center',
                rotation=90)
    ax.plot(xls, yls)
    return fig, ax




def main():
    print('This is a library.')


if __name__ == '__main__':
    main()
