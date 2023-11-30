import datetime
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import sys
import src.eqa_takuyakawanishi.eqa as eqa
#
# Springer, figure size: 119 mm x 195 mm
#


def main():
    big_quakes = pd.read_csv("../../intermediates/intensity_D.csv")
    big_quakes = big_quakes.reset_index(drop=True)
    dir_data = "../../data/stationwise/"
    meta2read = "../../intermediates/organized_codes_pre_02.csv"
    meta = pd.read_csv(meta2read)
    print(meta.head(3))
    conf = eqa.Settings()
    #
    # TODO Screen duration until the day before the quake day.
    #
    big_quakes["date_time"] = pd.to_datetime(
        big_quakes[["year", "month", "day", "hour", "minute", "second"]])

    for i_quake in range(len(big_quakes)):
        code_prime = big_quakes.at[i_quake, "code_prime"]
        set_to = datetime.datetime.strftime(
            big_quakes.at[i_quake, "date_time"], "%Y-%m-%d %H:%M:%S"
        )
        set_dict = {"set_from": conf.datetime_beginning, "set_to": set_to}
        try:
            _, _, summary = \
                eqa.find_intensity_frequency_regression_summarize_ts(
                    meta, code_prime, set_dict, dir_data=dir_data)
        except Exception as ex:
            print(ex)
            continue
        big_quakes.at[i_quake, "duration_0"] = summary["duration"]
    print(big_quakes["duration_0"])
    big_quakes = big_quakes[big_quakes["duration_0"] >= 10 * 365.2425]

    df_res = pd.DataFrame(columns=["code_prime", "duration_0"])

    for i_quake in big_quakes.index:
        try:
            code_prime = big_quakes.at[i_quake, "code_prime"]
        except Exception as ex:
            print(ex)
            continue
        df_res.at[i_quake, "code_prime"] = code_prime
        #
        # TODO Consider use pd.to_datetime()
        datetime_big = big_quakes.at[i_quake, "date_time"]
        dates = [
            datetime_big + datetime.timedelta(seconds=-1),
            datetime_big + datetime.timedelta(days=1),
            datetime_big + datetime.timedelta(days=7),
            datetime_big + datetime.timedelta(days=70),
            datetime_big + datetime.timedelta(days=700)
        ]
        fig = plt.figure(figsize=(2.3, 2.3), dpi=144)
        ax = fig.add_axes([9/50, 8/50, 4/5, 4/5])
        ax.tick_params(which="both", axis="both", direction="in")
        ax.set_yscale("log")

        set_to_s = []
        for date in dates:
            set_to_s.append(
                datetime.datetime.strftime(date, "%Y-%m-%d %H:%M:%S"))
        # print(set_to_s)
        markers = ["o", "s", "<", ">", "o", "o"]
        colors = ["#666666", "#888888", "#aaaaaa", "#cccccc", "#222222",
                  "#222222"]
        lws = [.3, .3, .3, .3, .3]
        sizes = [24, 22, 22, 22, 12]
        duration_0 = 0
        for i_set_to, set_to in enumerate(set_to_s):

            set_dict = {"set_from": conf.datetime_beginning, "set_to": set_to}
            # print(set_dict)
            frequency = None
            regression = None
            summary = None
            try:
                frequency, regression, summary = \
                    eqa.find_intensity_frequency_regression_summarize_ts(
                        meta, code_prime, set_dict, dir_data=dir_data)

            except Exception as ex:
                print(ex)
            if i_set_to == 0:
                df_res.at[i_quake, "duration_0"] = summary["duration"]
                df_res.at[i_quake, "est6p5_0"] = summary["est6p5"]
                df_res.at[i_quake, "slope_0"] = summary["slope"]
                df_res.at[i_quake, "intercept_0"] = summary["intercept"]
                duration_0 = summary["duration"]

            elif i_set_to == 4:
                df_res.at[i_quake, "duration_700"] = summary["duration"]
                df_res.at[i_quake, "est6p5_700"] = summary["est6p5"]
                df_res.at[i_quake, "slope_700"] = summary["slope"]
                df_res.at[i_quake, "intercept_700"] = summary["intercept"]
            n = len(frequency)
            intensities = np.arange(n) + 1
            ax.scatter(
                intensities, frequency, marker=markers[i_set_to],
                c=colors[i_set_to], edgecolors="k", lw=lws[i_set_to],
                s=sizes[i_set_to]
            )
            if i_set_to == 0:
                ints = np.linspace(2, 7)
                fits = 10 ** (summary["intercept"] + summary["slope"] * ints)
                ax.plot(ints, fits, lw=.5, c="k", ls="--")
            if i_set_to == len(set_to_s) - 1:
                ints = np.linspace(2, 7)
                fits = 10 ** (summary["intercept"] + summary["slope"] * ints)
                ax.plot(ints, fits, lw=.5, c="k")

        # ax.plot(ints, fits, lw=.5, c="#333333")
        print(duration_0)
        if duration_0 < 3652.425:
            continue
        else:
            pass

        for tick in ax.get_xticklabels():
            tick.set_fontname("Futura")
            tick.set_fontsize(7)
        for tick in ax.get_yticklabels():
            tick.set_fontname("Futura")  # "Arial")  #  "Helvetica Neue")
            tick.set_fontsize(7)
        ax.annotate(
            "Frequencies", xy=(0, 0.5), xytext=(0.01, 7/32 + 3/8),
            xycoords="figure fraction", textcoords="figure fraction",
            ha="left", va="center", rotation=90,
            font="Helvetica Neue", size=8
        )
        ax.annotate(
            "Intensities", xy=(0.5, 0), xytext=(7/32 + 3/8, 0.01),
            xycoords="figure fraction", textcoords="figure fraction",
            ha="center", va="bottom",
            font="Helvetica Neue", size=8
        )
    df_res.to_csv("temp.csv", index=False)
    # plt.show()


if __name__ == "__main__":
    main()
