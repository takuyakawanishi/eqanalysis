import datetime
import matplotlib.pyplot as plt
from matplotlib import ticker
import numpy as np
import pandas as pd
import statsmodels.api as sm
import sys
sys.path.append("./")

import eqanalysis.src.eqa_takuyakawanishi.eqa as eqa
# import dashfiles.layouts.fig_template as fig_template

DATE_B_MACHINE = "1996-04-01"
DATE_LAST_RECORDED = "2021-12-31"
LWTST = .36
LWREG = .5
FSLEG = 8
cud_orange = (0.9, 0.6, 0)
cud_skyblue = (.35, .7, .9)
cud_blue = (0, .45, .7)


class Hokkaido_1460600():
    # 1460600,7,2018,9,6,3,8,5.0,65,9673,1460600
    def __init__(self):
        self.code_prime = 1460600
        self.name = "atsumacho-shikanuma"
        self.max_int = 7
        self.max_date = "2018-09-06 03:08:05"
        self.mechanical_intensity = 6.5
        self.acceleration = 9673
        self.day_before = "2018-09-05 03:08:05"
        self.day_after = "2018-09-07 03:08:05"
        self.year_after = "2019-09-05 03:08:05"
        self.list_anlysis_end_days = [
            self.day_before, self.day_after, self.year_after]
        self.labels = ["24 hours before", "24 hours after", "one year after"]
        self.proxy = 1460600



def find_dates_of_occurrence(intensity, df):
    df = eqa.add_datetime_column_to_dataframe(df)
    idxs = df.index[df["intensity"] == intensity]
    dates = []
    for idx in idxs:
        date = datetime.datetime.strftime(df.loc[idx, "date"], "%Y-%m-%d")
        dates.append(date)
    return dates


def main():
    dir_data = 'eqanalysis/data_2024/stationwise_2021/'
    file2read = 'eqanalysis/data_2024/intermediates/organized_code_2024_04.csv'
    meta = pd.read_csv(file2read)
    ints = np.linspace(2, 7)
    eq = Hokkaido_1460600()
    station_prime = eq.code_prime
    try:
        available = eqa.find_available_periods_ts(meta, station_prime)
    except Exception as ex:
        print(ex)
    print(available)
    #
    # Prepare figure data on raw counts.
    #
    set_tos = eq.list_anlysis_end_days
    df_raw = pd.DataFrame(columns=["intensities", "frequency"])
    df_raw["intensities"].astype(object)
    df_raw["frequency"].astype(object)
    for i_set, set_to in enumerate(set_tos):
        set_dict = {"set_from": "1919-01-01 00:00:00",
                    "set_to": set_to}
        frequency, res, summary = \
            eqa.find_intensity_frequency_regression_summarize_ts(
                meta, station_prime, set_dict, dir_data=dir_data)
        frequency = np.array(frequency.astype(np.float64))  
        intensities = np.arange(len(frequency)) + 1
        df_raw.at[i_set, "intensities"] = list(intensities)
        df_raw.at[i_set, "frequency"] = list(frequency)
    print(df_raw)
    #
    # Prepare figure data on reduced counts considering aftershocks.
    #
    fn = "eqanalysis/results/temp/atumacho-shikanuma_reduction.csv"
    factor_reduction = pd.read_csv(fn)
    print(factor_reduction)
    df_red = pd.DataFrame(columns=["intensities", "reduced_freq"])
    df_red["intensities"].astype(object)
    df_red["reduced_freq"].astype(object)
    print("len(set_tos) = ", len(set_tos))
    for i_set in range(3):
        frequency = df_raw.at[i_set, "frequency"]
        if type(frequency) is str:
            frequency = eval(frequency)
        #print(frequency)
        freq_1_4 = frequency[:4]
        factor = np.array(factor_reduction.loc[i_set, :].astype(np.float64))
        # print("freq_1_4", freq_1_4)
        # print("factor", factor)
        freq_red = freq_1_4 * factor
        # print(freq_red)
        df_red.at[i_set, "intensities"] = [1, 2, 3, 4]
        df_red.at[i_set, "reduced_freq"] = freq_red
    print(df_red)


    sys.exit()
    #
    # For Hokkaido_1060600
    #
    fn = "eqanalysis/results/temp/atumacho-shikanuma_reduction.csv"
    dfred = pd.read_csv(fn)


    freq_2_4 = frequency[1:4]
    freq_2_4_red = freq_2_4 * a
    int_2_4 = np.array([2., 3., 4.])
    if i_set == 1 or i_set == 2:
        ax.scatter(int_2_4, freq_2_4_red,
                    marker=symbols[i_set],
                    color=colors[i_set], zorder=10000)

    fig = plt.figure(figsize=(3.3, 3.3 * 12/13))
    # Square plot area
    ax = fig.add_axes([.2246, 4/25, 4/5 * 12/13, 4/5])
    ax.tick_params(which="both", axis="both", direction="in")
    ax.xaxis.set_major_locator(ticker.MaxNLocator(integer=True))
    ax.set_yscale("log")
    x_min = .8
    x_max = 7.2
    x_reg_min = 1.8
    est6p5s = []
    frequency_max_s = []
    durations = []
    symbols = ["s", "D", "o"]
    colors = [cud_blue, cud_orange, "k"]
    labels = eq.labels
    set_tos = eq.list_anlysis_end_days
    # sys.exit()

    xrs = np.linspace(x_reg_min, x_max)
    yrs = 10 ** (res.intercept + res.slope * xrs)
    ax.plot(xrs, yrs, lw=LWREG, c="k")
    durations.append(summary["duration"])
    est6p5s.append(summary["est6p5"])
    frequency_max_s.append(frequency.max())
    frequency_max_s = np.array(frequency_max_s)
    frequency_grand_max = frequency_max_s.max()
    est6p5s = np.array(est6p5s)
    min_est6p5 = est6p5s.min()
    lower = np.floor(np.log10(min_est6p5))
    upper = np.ceil(np.log10(frequency_grand_max))
    ax.set_ylim(10 ** lower, 10 ** upper)
    ax.set_xlim(x_min, x_max)
    ax.annotate("Intensities",
        xy=(0, 0.5), xytext=(.2246 + 2/5 * 10/11, 0.02),
        xycoords="figure fraction", textcoords="figure fraction",
        ha="center", va="bottom", fontsize=12, font="Arial")
    ax.annotate("Rates of occurrence [1/year]",
        xy=(0., 0.5), xytext=(0.02, 4/25 + 2/5),
        xycoords="figure fraction", textcoords="figure fraction",
        ha="left", va="center", 
        rotation=90,
        fontsize=12, font="Arial")

    est6p5_max = est6p5s.max()
    ax.plot([6.5, 6.5], [10 ** lower, est6p5_max], lw=LWTST, c="k")
    for est6p5 in est6p5s:
        ax.plot([x_min, 6.5], [est6p5, est6p5], lw=LWTST, c= "k")
    print(est6p5s)
    print(durations)
    ax.legend(loc="upper right", fontsize=FSLEG)
    
    set_dict = {"set_from": eq.year_after, "set_to":"2022-01-01 00:00:00"}
    frequency, res, summary = \
        eqa.find_intensity_frequency_regression_summarize_ts(
            meta, eq.proxy, set_dict, dir_data=dir_data)
    # print(frequency)
    # print(res)
    # print(summary)
    frequency = np.array(frequency.astype(np.float64))
    intensities = np.arange(len(frequency)) + 1
    # print(eq.year_after)
    # print(intensities)
    # print(frequency)
    # ax.scatter(intensities, frequency, marker="x", c="k", zorder=5000)
    dir = "eqanalysis/results/figures/"
    fn = "st_" + str(eq.code_prime) + "_" + eq.name + ".pdf"
    fn_png = "st_" + str(eq.code_prime) + "_" + eq.name + ".png"
    plt.savefig(dir + fn)
    plt.savefig(dir + fn_png)


    plt.show()        


    #     # print(available)
    #     available_dict = available.to_dict("records")

    #     idx = meta.index[meta["code_prime"] == station_prime]
    #     # print(type(meta.loc[idx, "codes_ordered"].values))
    #     stations = meta.loc[idx, "codes_ordered"].values[0]
    #     stations = eval(stations)
    #     for station in stations:
    #         try:
    #             df = pd.read_csv(dir_data + "st_" + str(station) + ".txt")
    #         except Exception as ex:
    #             print("For station {}, {}".format(station, ex))
    #             continue
    #         dates = find_dates_of_occurrence("D", df)
    #         # print(dates)
    #         for date in dates:
    #             date_e_b = datetime.datetime.strptime(date, "%Y-%m-%d") - \
    #                 datetime.timedelta(days=1)
    #             date_e_b_str = datetime.datetime.strftime(date_e_b, "%Y-%m-%d")
    #             date_b_a = date_e_b + datetime.timedelta(days=2)
    #             date_b_a_str = datetime.datetime.strftime(date_b_a, "%Y-%m-%d")
    #             date_b_a_2 = date_e_b + datetime.timedelta(days=366)
    #             date_b_a_2_str = datetime.datetime.strftime(
    #                 date_b_a_2, "%Y-%m-%d")
    #             date_b_a_3 = date_e_b + datetime.timedelta(days=365 * 5 + 1)
    #             date_b_a_3_str = datetime.datetime.strftime(
    #                 date_b_a_3, "%Y-%m-%d")
    #             set_dict_b = {
    #                 "set_from": DATE_B_MACHINE, "set_to": date_e_b_str}
    #             set_dict_a = {
    #                 "set_from": date_b_a_str, "set_to": DATE_LAST_RECORDED}
    #             set_dict_a_2 = {
    #                 "set_from": date_b_a_2_str, "set_to": DATE_LAST_RECORDED}
    #             set_dict_a_3 = {
    #                 "set_from": date_b_a_3_str, "set_to": DATE_LAST_RECORDED}

    #             try:
    #                 frequency, res, summary = \
    #                     eqa.find_intensity_frequency_regression_summarize(
    #                         meta, station_prime, set_dict_b, dir_data=dir_data)
    #             except Exception as ex:
    #                 print(ex)
    #             try:
    #                 frequency_a, res_a, summary_a = \
    #                     eqa.find_intensity_frequency_regression_summarize(
    #                         meta, station_prime, set_dict_a, dir_data=dir_data)
    #             except Exception as ex:
    #                 print(ex)
    #                 continue
    #             try:
    #                 frequency_a_2, res_a_2, summary_a_2 = \
    #                     eqa.find_intensity_frequency_regression_summarize(
    #                         meta, station_prime,  set_dict_a_2,
    #                         dir_data=dir_data)
    #             except Exception as ex:
    #                 print(ex)
    #             try:
    #                 frequency_a_3, res_a_3, summary_a_3 = \
    #                     eqa.find_intensity_frequency_regression_summarize(
    #                         meta, station_prime, set_dict_a_3,
    #                         dir_data=dir_data)
    #                 intensities_a_3 = np.arange(len(frequency_a_3)) + 1
    #             except Exception as ex:
    #                 print(ex)
    #                 continue

    #             intensities = np.arange(len(frequency)) + 1
    #             intensities_a = np.arange(len(frequency_a)) + 1
    #             intensities_a_2 = np.arange(len(frequency_a_2)) + 1
    #             length = np.round(summary["duration"] / 365.2425, 2)
    #             length_a = np.round(summary_a["duration"] / 365.2425, 2)
    #             length_a_2 = np.round(summary_a_2["duration"] / 365.2425, 2)
    #             length_a_3 = np.round(summary_a_3["duration"] / 365.2425, 2)
    #             ratio = summary_a["est7"] / summary["est7"]
    #             print(ratio)
    #             station_idxs.append(station_prime)
    #             ratios.append(ratio)
    #             draw_intensity_frequency = True

    #             if draw_intensity_frequency:
    #                 if length > 1 and length_a > 1:
    #                     fig = plt.figure(figsize=(3.6, 3.6))
    #                     ax = fig.add_axes([4/25, 4/25, 4/5, 4/5])
    #                     ax.tick_params(
    #                         which="both", axis="both", direction="in")
    #                     ax.annotate(
    #                         "Intensities", xy=(0.5, 0),
    #                         xytext=(4/25 + 2/5, 0.02),
    #                         xycoords="figure fraction",
    #                         textcoords="figure fraction",
    #                         ha="center", va="center", fontsize=12
    #                     )
    #                     ax.annotate(
    #                         "Frequency [1/year]", xy=(0, 0.5),
    #                         xytext=(0.01, 4/25 + 2/5),
    #                         xycoords="figure fraction",
    #                         textcoords="figure fraction",
    #                         ha="left", va="center", rotation=90, fontsize=12
    #                     )
    #                     ax.annotate(
    #                         str(stations), xy=(0, 1), xytext=(0.95, 0.90),
    #                         xycoords="axes fraction",
    #                         textcoords="axes fraction",
    #                         ha="right", va="bottom"
    #                     )
    #                     # print(summary["duration"], summary_a["duration"])
    #                     ax.annotate(
    #                         str([length, length_a, length_a_2, length_a_3]),
    #                         xy=(0, 1), xytext=(0.95, 0.85),
    #                         xycoords="axes fraction",
    #                         textcoords="axes fraction",
    #                         ha="right", va="center"
    #                     )
    #                     ax.scatter(intensities, frequency)
    #                     try:
    #                         reg_freqs = 10 ** (res.intercept + res.slope * ints)
    #                         ax.plot(ints, reg_freqs, lw=.5, ls="--", c="k")
    #                     except Exception as ex:
    #                         print(ex)
    #                     try:
    #                         ax.scatter(intensities_a, frequency_a)
    #                         reg_freqs_a = 10 ** (res_a.intercept +
    #                                              res_a.slope * ints)
    #                     except Exception as ex:
    #                         print(ex)

    #                     try:
    #                         ax.scatter(
    #                             intensities_a_2, frequency_a_2, marker="x")
    #                         reg_freqs_a_2 = 10 ** (
    #                                 res_a_2.intercept + res_a_2.slope * ints)
    #                     except Exception as ex:
    #                         print(ex)
    #                     try:
    #                         ax.scatter(intensities_a_3, frequency_a_3, marker="+")
    #                         reg_freqs_a_3 = 10 ** (
    #                                 res_a_3.intercept + res_a_3.slope * ints)
    #                     except Exception as ex:
    #                         print(ex)
    #                     ax.plot(ints, reg_freqs_a, lw=.5, ls=":", c="k")
    #                     # ax.plot(ints, reg_freqs_a_2, lw=.5, ls="-.", c="k")

    #                     ax.set_yscale("log")
    # print(ratios)
    # ser = pd.Series(ratios, index=station_idxs)
    # ser = ser.sort_values()
    # print(ser)

    # # ser.hist()
    # plt.show()


if __name__ == '__main__':
    main()
