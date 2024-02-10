import datetime
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import sys
sys.path.append("./")

import eqanalysis.src.eqa_takuyakawanishi.eqa as eqa
# import dashfiles.layouts.fig_template as fig_template

DATE_B_MACHINE = "1996-04-01"
DATE_LAST_RECORDED = "2019-12-31"


def find_dates_of_occurrence(intensity, df):
    df = eqa.add_date_column_to_dataframe(df)
    idxs = df.index[df["intensity"] == intensity]
    dates = []
    for idx in idxs:
        date = datetime.datetime.strftime(df.loc[idx, "date"], "%Y-%m-%d")
        dates.append(date)
    return dates


def main():
    dir_data = 'eqanalysis/data/stationwise_fine_old_until_2019/'
    file2read = 'eqanalysis/intermediates/organized_codes_pre_02.csv'
    meta = pd.read_csv(file2read)
    having_Ds = [2502330, 3110032, 2510430, 3000330, 3000131]
    # having_Ds = [1460630, 1460920, 1460921, 1461020, 1461021, 2132733, 2201600,
    #              2205220, 2205230, 2205231, 2205232, 2205332, 2205360, 2205631,
    #              2205700, 2205721, 2205734, 2205760, 2210730, 2211130, 2211630,
    #              2211930, 2220120, 2220560, 2220620, 2220830, 2220860, 2221530,
    #              2500220, 2500330, 2500730, 2502130, 2502330, 2510430, 2510530,
    #              2510730, 2510830, 2510900, 2511130, 3000120, 3000131, 3000330,
    #              3000531, 3003120, 3003231, 3003432, 3015600, 3016120, 3100260,
    #              3110032, 3110631, 3111630, 3112730, 3710033, 3710034, 3710044,
    #              3710230, 3710233, 3710300, 3710530, 3713530, 3720335, 3900030,
    #              3900100, 3900130, 3901420, 4203130, 4203331, 4410200, 4410221,
    #              5630100, 5631130, 7400430, 7401232, 7410532, 7410630, 7413130,
    #              7413830, 7413930, 7414800, 7414831, 7414832, 7415130, 7415330,
    #              7415370, 7415420]

    ints = np.linspace(2, 7)
    ratios = []
    station_idxs = []
    for station_prime in having_Ds:
        try:
            available = eqa.find_available_periods(meta, station_prime)
        except Exception as ex:
            print(ex)
            continue
        # print(available)
        available_dict = available.to_dict("records")

        idx = meta.index[meta["code_prime"] == station_prime]
        # print(type(meta.loc[idx, "codes_ordered"].values))
        stations = meta.loc[idx, "codes_ordered"].values[0]
        stations = eval(stations)
        for station in stations:
            try:
                df = pd.read_csv(dir_data + "st_" + str(station) + ".txt")
            except Exception as ex:
                print("For station {}, {}".format(station, ex))
                continue
            dates = find_dates_of_occurrence("D", df)
            # print(dates)
            for date in dates:
                date_e_b = datetime.datetime.strptime(date, "%Y-%m-%d") - \
                    datetime.timedelta(days=1)
                date_e_b_str = datetime.datetime.strftime(date_e_b, "%Y-%m-%d")
                date_b_a = date_e_b + datetime.timedelta(days=2)
                date_b_a_str = datetime.datetime.strftime(date_b_a, "%Y-%m-%d")
                date_b_a_2 = date_e_b + datetime.timedelta(days=366)
                date_b_a_2_str = datetime.datetime.strftime(
                    date_b_a_2, "%Y-%m-%d")
                date_b_a_3 = date_e_b + datetime.timedelta(days=365 * 5 + 1)
                date_b_a_3_str = datetime.datetime.strftime(
                    date_b_a_3, "%Y-%m-%d")
                set_dict_b = {
                    "set_from": DATE_B_MACHINE, "set_to": date_e_b_str}
                set_dict_a = {
                    "set_from": date_b_a_str, "set_to": DATE_LAST_RECORDED}
                set_dict_a_2 = {
                    "set_from": date_b_a_2_str, "set_to": DATE_LAST_RECORDED}
                set_dict_a_3 = {
                    "set_from": date_b_a_3_str, "set_to": DATE_LAST_RECORDED}

                try:
                    frequency, res, summary = \
                        eqa.find_intensity_frequency_regression_summarize(
                            meta, station_prime, set_dict_b, dir_data=dir_data)
                except Exception as ex:
                    print(ex)
                try:
                    frequency_a, res_a, summary_a = \
                        eqa.find_intensity_frequency_regression_summarize(
                            meta, station_prime, set_dict_a, dir_data=dir_data)
                except Exception as ex:
                    print(ex)
                    continue
                try:
                    frequency_a_2, res_a_2, summary_a_2 = \
                        eqa.find_intensity_frequency_regression_summarize(
                            meta, station_prime,  set_dict_a_2,
                            dir_data=dir_data)
                except Exception as ex:
                    print(ex)
                try:
                    frequency_a_3, res_a_3, summary_a_3 = \
                        eqa.find_intensity_frequency_regression_summarize(
                            meta, station_prime, set_dict_a_3,
                            dir_data=dir_data)
                    intensities_a_3 = np.arange(len(frequency_a_3)) + 1
                except Exception as ex:
                    print(ex)
                    continue

                intensities = np.arange(len(frequency)) + 1
                intensities_a = np.arange(len(frequency_a)) + 1
                intensities_a_2 = np.arange(len(frequency_a_2)) + 1
                length = np.round(summary["duration"] / 365.2425, 2)
                length_a = np.round(summary_a["duration"] / 365.2425, 2)
                length_a_2 = np.round(summary_a_2["duration"] / 365.2425, 2)
                length_a_3 = np.round(summary_a_3["duration"] / 365.2425, 2)
                ratio = summary_a["est7"] / summary["est7"]
                print(ratio)
                station_idxs.append(station_prime)
                ratios.append(ratio)
                draw_intensity_frequency = True

                if draw_intensity_frequency:
                    if length > 1 and length_a > 1:
                        fig = plt.figure(figsize=(3.6, 3.6))
                        ax = fig.add_axes([4/25, 4/25, 4/5, 4/5])
                        ax.tick_params(
                            which="both", axis="both", direction="in")
                        ax.annotate(
                            "Intensities", xy=(0.5, 0),
                            xytext=(4/25 + 2/5, 0.02),
                            xycoords="figure fraction",
                            textcoords="figure fraction",
                            ha="center", va="center", fontsize=12
                        )
                        ax.annotate(
                            "Frequency [1/year]", xy=(0, 0.5),
                            xytext=(0.01, 4/25 + 2/5),
                            xycoords="figure fraction",
                            textcoords="figure fraction",
                            ha="left", va="center", rotation=90, fontsize=12
                        )
                        ax.annotate(
                            str(stations), xy=(0, 1), xytext=(0.95, 0.90),
                            xycoords="axes fraction",
                            textcoords="axes fraction",
                            ha="right", va="bottom"
                        )
                        # print(summary["duration"], summary_a["duration"])
                        ax.annotate(
                            str([length, length_a, length_a_2, length_a_3]),
                            xy=(0, 1), xytext=(0.95, 0.85),
                            xycoords="axes fraction",
                            textcoords="axes fraction",
                            ha="right", va="center"
                        )
                        ax.scatter(intensities, frequency)
                        try:
                            reg_freqs = 10 ** (res.intercept + res.slope * ints)
                            ax.plot(ints, reg_freqs, lw=.5, ls="--", c="k")
                        except Exception as ex:
                            print(ex)
                        try:
                            ax.scatter(intensities_a, frequency_a)
                            reg_freqs_a = 10 ** (res_a.intercept +
                                                 res_a.slope * ints)
                        except Exception as ex:
                            print(ex)

                        try:
                            ax.scatter(
                                intensities_a_2, frequency_a_2, marker="x")
                            reg_freqs_a_2 = 10 ** (
                                    res_a_2.intercept + res_a_2.slope * ints)
                        except Exception as ex:
                            print(ex)
                        try:
                            ax.scatter(intensities_a_3, frequency_a_3, marker="+")
                            reg_freqs_a_3 = 10 ** (
                                    res_a_3.intercept + res_a_3.slope * ints)
                        except Exception as ex:
                            print(ex)
                        ax.plot(ints, reg_freqs_a, lw=.5, ls=":", c="k")
                        # ax.plot(ints, reg_freqs_a_2, lw=.5, ls="-.", c="k")

                        ax.set_yscale("log")
    print(ratios)
    ser = pd.Series(ratios, index=station_idxs)
    ser = ser.sort_values()
    print(ser)

    # ser.hist()
    plt.show()


if __name__ == '__main__':
    main()
