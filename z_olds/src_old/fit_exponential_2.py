import datetime
import json
import matplotlib.pyplot as plt
from dateutil.relativedelta import relativedelta
from dash import Dash, dcc, dash_table, html, Input, Output, State
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import pandas as pd
import scipy.stats
import sys
sys.path.append("./")
import eqanalysis.src.eqa_takuyakawanishi.eqa as eqa


################################################################################
#  Global Constants
################################################################################

DATABASE_START_DATE = '19190101'
DATABASE_END_DATE = '20201231'
# DIR_DATA = '../../data/stationwise_fine_old_until_2019/'
# FILE2READ_META = '../../data/code_p_df.csv'
DIR_DATA = 'eqanalysis/data/stationwise/'
FILE2READ_META = 'eqanalysis/data/code_p_df.csv'


################################################################################
#  Utility
################################################################################

def round_to_k(x, k):
    try:
        return round(x, -int(np.floor(np.log10(abs(x)))) - 1 + k)
    except Exception as ex:
        print(ex)
        return np.nan


def fit_intervals_to_exponential(df, d_low, d_upp):
    df_sel = df[df['interval'] >= d_low]
    df_sel = df_sel[df_sel['interval'] <= d_upp]
    x = df_sel['interval']
    log10y = df_sel['counts'].apply(np.log10)
    res = scipy.stats.linregress(x, log10y)
    return res


def get_subdfs_by_intensities(
        df, beginning='1919-01-01', end='2020-12-31'):
    
    df.loc[df['month'] == '//', 'month'] = 6
    df.loc[df['day'] == '//', 'day'] = 15
    df.loc[df['hour'] == '//', 'hour'] = 12
    df.loc[df['minute'] == '//', 'minute'] = 30
    df.loc[df['second'] == '//', 'second'] = 30
    df = df.drop(df[df.day == '00'].index)
    try:
        df['date'] = pd.to_datetime(df[['year', 'month', 'day']])
    except Exception as ex:
        print(ex)
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


def check_if_gaps_are_zeros(meta_st):
    gaps = meta_st.at[0, "gaps"]
    # print(gaps)
    gaps = eval(gaps)
    for gap in gaps:
        # print(gap, type(gap))
        if gap != 0:
            return False
    return True


def read_data_into_dataframe(stations):
    df = pd.DataFrame()
    for station in stations:
        filename = DIR_DATA + "st_" + str(station) + ".txt"
        dfa = pd.read_csv(filename)
        df = pd.concat([df, dfa])
    return df


def create_datetime_column(df):
    df = df.reset_index(drop=True)
    try:
        df["datetime"] = pd.to_datetime(
            dict(year=df.year, month=df.month, day=df.day,
                hour=df.hour, minute=df.minute, second=df.second))
    except Exception as ex:
        print(ex)
        return pd.DataFrame()
    df["timedelta"] = df["datetime"].diff()
    return df


def main():
    meta_org2 = pd.read_csv(
        "eqanalysis/intermediates/organized_codes_pre_02.csv")
    print(meta_org2.head(3))
    station_prime = 1460630
    file_ps = "eqanalysis/intermediates/intensity_D_prime.txt"

    primary_stations = []
    with open(file_ps, "r") as f:
        for line in f:
            primary_stations.append(int(line.strip()))
    print(primary_stations)
    for station_prime in primary_stations:
        print(station_prime)
        meta_st = meta_org2[meta_org2["code_prime"] == station_prime]
        # print(type(meta_st))
        meta_st = meta_st.reset_index(drop=True)
        res = check_if_gaps_are_zeros(meta_st)
        if res == False:
            print("A gap is not zero, avoid interval analysis.")
            continue
        stations = meta_st.at[0, "codes_ordered"]
        stations = eval(stations)
        df = read_data_into_dataframe(stations)
        d7, d6, d5, d4, d3, d2, d1 = get_subdfs_by_intensities(df)
        intensity = 4
        if intensity == 1:
            di = d1
        elif intensity == 2:
            di = d2
        elif intensity == 3:
            di = d3
        elif intensity == 4:
            di = d4
        di = create_datetime_column(di)
        if di.empty:
            continue

        intervals = di.loc[1:, "timedelta"] / np.timedelta64(1, "D")
        intervals = np.sort(intervals)
        suvf = 1 - (np.arange(len(intervals)) + 1) / (len(intervals) + 1)
        fig = plt.figure(figsize=(3, 2))
        ax = fig.add_axes([4/25, 4/25, 4/5, 4/5])
        ax.tick_params(which="both", axis="both", direction="in",
                    labelsize=8)
        ax.set_yscale("log")
        # ax.scatter(intervals, suvf, color=(86/256, 180/256, 233/256))
        # ax.scatter(intervals, suvf, color=(0/256, 114/256, 178/256))
        ax.scatter(intervals, suvf, color="#111111", s=20)
        #
        # Regression line
        #
        log10suvf = np.log10(suvf)
        dfi = pd.DataFrame()
        dfi["intvl"] = intervals
        dfi["log10suvf"] = log10suvf
        intvl_min = 10
        intvl_max = dfi["intvl"].max()
        # print(intvl_max)
        dfi = dfi[dfi["intvl"] > intvl_min]
        res = scipy.stats.linregress(dfi["intvl"], dfi["log10suvf"])
        # print(res)
        intvls = np.linspace(0, intvl_max)
        svfs = 10 ** (res.slope * intvls + res.intercept)
        ax.plot(intvls, svfs, c=(213/256, 94/256, 0), lw=2)
        # ax.plot(intvls, svfs, c=(86/256, 180/256, 233/256))
        # ax.plot(intvls, svfs, c=(0/256, 114/256, 178/256), lw=3)
        # ax.plot(intvls, svfs, c="k", lw=2)

        ax.annotate(
            "Intervals [days]", xy=(0.5, 0), xytext=(4/25 + 2/5, .01),
            xycoords="figure fraction", textcoords="figure fraction",
            ha="center", va="bottom", math_fontfamily="stix", fontsize=9)
        ax.annotate(
            "$1 - F$", xy=(0, .5), xytext=(.01, 4/25 + 2/5),
            xycoords="figure fraction", textcoords="figure fraction",
            ha="left", va="center", math_fontfamily="stix", fontsize=9,
            rotation=90)
        filename = "eqanalysis/results/figures/if_poisson_processes/" \
            + "suvf_" + str(station_prime) + "_int_" + str(intensity) + ".png"
        # plt.savefig(filename)
    plt.show()


if __name__ == '__main__':
    main()