import datetime
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import scipy.stats
import scipy.ndimage as ndimage
import time
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
        # self.duration_min = 5
        # self.remiflt = {
        #     '1': 7, '2': 10, '3': 32, '4': 46, '5': 46, '6': 46, '7': 46
        # }
        self.range_exp_fit_low = [20, 20, 50, 50, 50, 50, 50]
        self.range_exp_fit_upp = [100, 100, 1000, 1000, 1000, 1000, 1000]
        # self.intensities = [1, 2, 3, 4, 5, 6, 7]
        # self.n_int3_min = 1
        # self.n_int4_min = 1
        # self.n_int5_min = 0
        # self.n_int6_min = 0


class IROR():

    def __init__(self, ros):
        self.ros = ros

    def find_iror(self, li):
        self.li = li
        self.ros_trn = self.ros[self.ros > 0]
        self.ros_log10 = np.log10(self.ros_trn)
        n_fit = len(self.ros_trn[li - 1:])
        intensities = np.arange(n_fit) + li
        if n_fit == 1:
            print("Only one point for iror, no relation can be calculated.")
            return None
        elif n_fit == 2:
            print("Only two points for iror, use with care.")
            self.slope = self.ros_log10[li] - self.ros_log10[li - 1]
            self.intercept = self.ros_log10[li - 1] - self.slope * li
            self.rvalue = np.nan
            self.pvalue = np.nan
            self.stderr = np.nan
            self.intercept_stderr = np.nan
            return self
        elif n_fit > 2:
            res = scipy.stats.linregress(
                intensities, self.ros_log10[li - 1:]
            )
            return res

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
#  Intensity and ro
################################################################################


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
    df = df[df["duration"] > 0]
    df = df.reset_index(drop=True)
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


# def create_intensity_frequency_table_of_period_ts(actual, dir_data='./'):
#     return create_intensity_ro_table_of_period_ts(actual, dir_data=dir_data)

def create_intensity_ro_table_of_period_ts(actual, dir_data='./'):
    #print(actual)
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
    actual_res_sum["froms"] = list(actual["from"])
    actual_res_sum["tos"] = list(actual["to"])
    duration = actual_res_sum["duration"]
    actual_res_sum = actual_res_sum.drop(labels=['from', 'to'])
    ro = actual_res_sum[columns]
    ro = ro[ro > 0] / duration * 365.2425
    return ro, actual_res_sum

# def find_intensity_frequency_regression_summarize_ts(
#         meta, station, set_dict, dir_data='./'):
#     return find_intensity_ro_regression_summarize_ts(\
#         meta, station, set_dict, dir_data='./')

def find_intensity_ro_regression_summarize_ts(
        meta, station, set_dict, dir_data='./'):
    return find_intensity_ro_summarize_ts(
        meta, station, set_dict, dir_data='./')

def find_intensity_ro_summarize_ts(
        meta, station, set_dict, dir_data='./'):
    meta_1 = meta[meta["code_prime"] == station]
    meta_1 = meta_1.reset_index(drop=True)
    available = find_available_periods_meta_1_ts(meta_1)
    actual = calc_periods_durations_ts(available, set_dict)
    summary_pre = pd.Series()
    summary_pre["station"] = station
    summary_pre["latitude"] = calc_latitude(meta_1.at[0, "lat"])
    summary_pre["longitude"] = calc_longitude(meta_1.at[0, "lon"])
    summary_pre["address"] = meta_1.at[0, "address"]
    ro, summary = \
        create_intensity_ro_table_of_period_ts(actual, dir_data)
    summary = pd.concat([summary_pre, summary])
    return ro, summary


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
    available = find_available_periods_ts(meta, station)
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


###############################################################################
#   Intervals
################################################################################


def combine_if_no_gaps(gaps, diss):
    if diss is None:
        print("diss is None. This should not happen.")
        sys.exit()
    diss_new = []
    dis_new = [None, None, None, None, None, None, None]
    if type(gaps) is str:
        gaps = eval(gaps)
    for i_int in range(7):
        if diss[0][i_int].empty:
            continue
            print("empty dataframe at 0, i_int", i_int)
        else:
            dis_new[i_int] = diss[0][i_int]
    diss_new.append(dis_new)
    i_new = 0
    for i_st in range(len(diss) - 1):
        dis_new = [None, None, None, None, None, None, None]
        if gaps[i_st] == 0:
            for i_int in range(7):
                # print(diss_new)
                # print("i_st = {}, i_int = {}".format(i_st, i_int))
                if diss_new[i_new][i_int] is None:
                    dis_new[i_int] = diss[i_st + 1][i_int].copy()
                else:
                    diss_int = diss[i_st + 1][i_int].copy()
                    dis_new[i_int] = pd.concat([
                    diss_new[i_new][i_int], diss_int
                ])
            diss_new[i_new] = dis_new
        else:
            for i_int in range(7):
                if not diss[i_st + 1][i_int].empty:
                    dis_new[i_int] = diss[i_st + 1][i_int].copy()
            diss_new.append(dis_new)
            i_new +=1
    return diss_new


def create_stationwise_dataframe(actual, dir_data):
    beginning = actual.at[0, "from"]
    end = actual.at[len(actual) - 1, "to"]
    stations = list(actual["station"])
    dfsts = []
    for station in stations:
        dfsts.append(pd.read_csv(dir_data + "st_" + str(station) + ".txt"))
    diss = []
    for i_st, station in enumerate(stations):
        d7, d6, d5, d4, d3, d2, d1 = create_subdfs_by_intensities_essentials(
            dfsts[i_st], beginning, end)
        dis = [d1, d2, d3, d4, d5, d6, d7]
        # print("type d7 in crate_stationwise_dataframe", type(d7))
        diss.append(dis)
        # print(diss)
    return diss


def create_interval_dataframe_ts(diss):
    dfis = []
    for i_int in range(7):
        intervalss = []
        for dis in diss:
            if dis[i_int] is not None:
                df = dis[i_int]
                df['diff'] = df['date_time'].diff() / np.timedelta64(1, "D")
                intervals = (np.array(df['diff']).astype(np.float64))[1:]
                intervalss.append(intervals)
        if intervalss == []:
            dfi = None
        else:
            intervals_this_int = np.concatenate(intervalss)
            n = len(intervals_this_int)
            suvf = 1 - np.arange(n) / n
            counts = n - np.arange(n)
            dfi = pd.DataFrame()
            dfi['interval'] = np.sort(intervals_this_int)
            dfi['suvf'] = suvf
            dfi['counts'] = counts
        dfis.append(dfi)
    return dfis


def create_interval_datasets_ts(df_org, code_prime, set_dict, dir_data):
    df_org_1 = df_org[df_org["code_prime"] == code_prime]
    df_org_1 = df_org_1.reset_index(drop=True)
    gaps = df_org_1.at[0, "gaps"]
    if type(gaps) is str:
        gaps = eval(gaps)
    available = find_available_periods_meta_1_ts(df_org_1)
    actual = calc_periods_durations_ts(available, set_dict)
    # print("calculating diss")
    diss = create_stationwise_dataframe(actual, dir_data)
    # print("calculating diss2")
    if len(gaps) > 1:
        diss = combine_if_no_gaps(gaps, diss)
    dfis = create_interval_dataframe_ts(diss)
    return dfis


def create_subdfs_by_intensities_essentials(df_st, beginning, end_t):
    df = add_datetime_column_to_dataframe(df_st)
    if type(beginning) is str:
        # print(beginning)
        beginning = datetime.datetime.strptime(beginning, "%Y-%m-%d %H:%M:%S")
    if type(end_t) is str:
        # print(end_t, type(end_t))
        end_t = datetime.datetime.strptime(end_t, "%Y-%m-%d %H:%M:%S")
    df = df[df['date_time'] >= beginning]
    df = df[df['date_time'] <= end_t]
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


###############################################################################
#
# Foreshock-aftershock-swarm correction
#
###############################################################################


def fit_to_first_linear_part(ints_ot, suvf_ot):
    n_ot = len(ints_ot)
    if n_ot < 6:
        return reg_min, factor
    sums = np.zeros(len(ints_ot) - 6)
    reg_0s = []
    count = 0
    x_seps = []
    for i_sep in range(n_ot - 6):
        n_sep = i_sep + 3
        count += 1
        x_seps.append(ints_ot[n_sep])
        reg_0 = scipy.stats.linregress(ints_ot[:n_sep], np.log10(suvf_ot[:n_sep]))
        reg_1 = scipy.stats.linregress(ints_ot[n_sep:], np.log10(suvf_ot[n_sep:]))
        sum_0 = ((np.log10(suvf_ot[:n_sep]) - \
                    (reg_0.intercept + reg_0.slope * ints_ot[:n_sep])) ** 2).sum()
        sum_1 = ((np.log10(suvf_ot[n_sep:]) - \
                    (reg_1.intercept + reg_1.slope * ints_ot[n_sep:])) ** 2).sum()
        sums[i_sep] = sum_0 + sum_1
        reg_0s.append(reg_0)
    sums = np.array(sums)
    x_seps = np.array(x_seps)
    i_min = np.argmin(sums)
    reg_min = reg_0s[i_min]
    x_sep = x_seps[i_min]
    factor = 10 ** reg_min.intercept
    return reg_min, factor, x_sep


def find_correction_factor_internsity(intervals, suvf, thres):
    ser = pd.Series()
    intervals = np.array(intervals)
    suvf = np.array(suvf)
    overthres = intervals[intervals > thres]
    n_intervals = len(intervals)
    n_overthres = len(overthres)
    oversuvf = suvf[-n_overthres:]
    ser["factor"] = 0
    ser["intercept"] = np.nan
    ser["slope"] = np.nan
    ser["rvalue"] = np.nan
    if n_intervals == 0:
        return ser
    if n_overthres > 10:
        reg, factor, interval_1st_fit_upp = fit_to_first_linear_part(
            overthres, oversuvf)
        ser["intercept"] = reg.intercept
        ser["slope"] = reg.slope
        ser["rvalue"] = reg.rvalue
        ser['interval_1st_fit_upp'] = interval_1st_fit_upp
        if factor < 1:
            ser["factor"] = factor
        elif factor > 1:
            ser["factor"] = 1
    elif n_overthres > 11:  # Disabled if > 10 or more
        reg = scipy.stats.linregress(overthres, np.log10(oversuvf))
        factor = 10 ** reg.intercept
        if factor < 1:
            ser["factor"] = factor
            ser["intercept"] = reg.intercept
            ser["slope"] = reg.slope
            ser["rvalue"] = reg.rvalue
        elif factor >= 1:
            if n_intervals > 1:
                factor = (n_overthres + 1) / (n_intervals + 1) 
                ser["factor"] = factor
    else:
        factor = (n_overthres + 1) / (n_intervals + 1)
        ser["factor"] = factor
    return ser


def find_correction_factor(dfs_intervals, thres_int=[4,8,16,32,64,128]):
    series = []
    for i_int, intensity in enumerate([1, 2, 3, 4, 5]):
        df_intervals = dfs_intervals[intensity - 1]
        intervals = df_intervals["interval"]
        suvf = df_intervals["suvf"]
        thres = thres_int[i_int]
        ser = find_correction_factor_internsity(intervals, suvf, thres)
        series.append(ser)
    df = pd.concat(series, axis=1).transpose()
    return df


def calc_corrected_ro(df_factor, ro):
    df_int = pd.DataFrame()
    df_int["intensity"] = np.arange(7) + 1
    df_r = df_factor[df_factor["factor"] > 0]
    factor = df_r["factor"].values
    n = min(len(df_r), len(ro))
    a = np.empty((7, 2))
    a[:] = np.nan
    df_freq = pd.DataFrame(a, columns=["ro", "corrected"])
    n_freq = len(ro)
    df_freq["ro"][:n_freq] = ro
    df_freq["corrected"][:n] = factor[:n] * ro[:n] 
    df_factor = pd.concat([df_int, df_factor, df_freq], axis=1)
    return df_factor


def add_corrected_results_to_summary(summary, df_corrected):
    for intensity in [1, 2, 3, 4, 5, 6, 7]:
        idx = "int" + str(intensity) + "_roc"
        summary[idx] = df_corrected.at[intensity-1, "corrected"]
    # df_sel = df_corrected[df_corrected["corrected"] > 0]
    # corrected = df_sel["corrected"].values
    # n = len(corrected)
    # summary["slope_cor"] = np.nan
    # summary["intercept_cor"] = np.nan
    # summary["rvalue_cor"] = np.nan
    # summary["pvalue_cor"] = np.nan
    # summary["est7_cor"] = np.nan
    # summary["est6p5_cor"] = np.nan
    # summary["est6_cor"] = np.nan
    # iror = IROR(corrected)
    # res = iror.find_iror(1)
    # if res is not None:
    #     summary["slope_cor"] = res.slope
    #     summary["intercept_cor"] = res.intercept
    #     summary["rvalue_cor"] = res.rvalue
    #     summary["pvalue_cor"] = res.pvalue
    #     summary["est7_cor"] = 10 ** (res.intercept + res.slope * 7)
    #     summary["est6p5_cor"] = 10 ** (res.intercept + res.slope * 6.5)
    #     summary["est6_cor"] = 10 ** (res.intercept + res.slope * 6)
    return summary


def do_aftershock_correction(df_org, station_prime, set_dict, dir_data):
    dfs_intervals = create_interval_datasets_ts(
        df_org, station_prime, set_dict, dir_data)
    ro, summary = \
        find_intensity_ro_summarize_ts(
            df_org, station_prime, set_dict, dir_data=dir_data)
    ro = np.array(ro.astype(np.float64))
    df_factor = find_correction_factor(dfs_intervals)  #thres_int=[5, 10, 20, 40]
    df_corrected = calc_corrected_ro(df_factor, ro)
    summary_corrected = add_corrected_results_to_summary(summary, df_corrected)
    return dfs_intervals, df_corrected, summary_corrected


def main():
    print('This is a library.')


if __name__ == '__main__':
    main()
