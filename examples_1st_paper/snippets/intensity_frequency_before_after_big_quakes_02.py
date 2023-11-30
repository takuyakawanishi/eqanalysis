import datetime
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import src.eqa_takuyakawanishi.eqa as eqa
#
# Springer, figure size: 119 mm x 195 mm
#
# plt.rc('text', usetex=True)
# # plt.rc('font', **{'family': 'sans-serif', 'sans-serif': ['Helvetica']})
# plt.rc('mathtext', fontset='stixsans')
# plt.rc('text.latex', preamble=r'\usepackage{Areal}')

def main():
    big_quakes = [
        [1460600, "2018-09-06"], [2205220, "2011-03-11"],
        [3710044, "2004-10-23"], [7413630, "2016-04-16"],
        [7413930, "2016-04-14"], [1460630, "2018-09-06"],
        [1460920, "2018-09-06"], [1460921, "2018-09-06"],
        [1461020, "2018-09-06"], [1461021, "2018-09-06"],
        [2132733, "2008-06-14"], [2201600, "2011-03-11"],
        [2205220, "2011-04-07"], [2205230, "2011-03-11"],
        [2205230, "2011-04-07"], [2205231, "2011-03-11"],
        [2205232, "2011-03-11"], 
    ]
    station = 1460600
    dir_data = "../../data/stationwise/"
    meta2read = "../../intermediates/organized_codes_pre_02.csv"
    meta = pd.read_csv(meta2read)
    conf = eqa.Settings()

    for big_quake in big_quakes:
        station = big_quake[0]
        fig = plt.figure(figsize=(2.3, 2.3), dpi=144)
        # ax = fig.add_axes([7/32, 7/32, .75, .75])
        # ax = fig.add_axes([9/50, 9/50, 4/5, 4/5])
        # ax = fig.add_axes([16/81, 15/81, 7/9, 7/9])
        ax = fig.add_axes([9/50, 8/50, 4/5, 4/5])

        ax.tick_params(which="both", axis="both", direction="in")
        ax.set_yscale("log")
        # print(frequency)
        # print(summary)
        # slope = summary["slope"]
        # intcpt = summary["intercept"]
        # ints = np.linspace(2, 7)
        # fits = 10 ** (intcpt + slope * ints)
        date_big = datetime.datetime.strptime(big_quake[1], "%Y-%m-%d")
        #
        # ToDo: datetime.timedelta(days=-1), etc should be 24 hours, etc.
        # It requires some changes in eqa.
        #
        dates = [
            date_big + datetime.timedelta(days=-1),
            date_big,
            date_big + datetime.timedelta(days=5),
            date_big + datetime.timedelta(days=30),
            datetime.datetime.strptime(conf.date_end, "%Y-%m-%d")
        ]
        set_to_s = []
        for date in dates:
            set_to_s.append(datetime.datetime.strftime(date, "%Y-%m-%d"))
        # set_to_s = [
        #     "2018-09-05", "2018-09-06", "2018-09-11", "2018-10-06", "2020-12-31"
        # ]
        markers = ["o", "s", "<", ">", "o", "o"]
        colors = ["#666666", "#888888", "#aaaaaa", "#cccccc", "#222222", "#222222", "#222222"]
        lws = [.3, .3, .3, .3, .3]
        sizes = [24, 22, 22, 22, 12]
        for i_set_to, set_to in enumerate(set_to_s):
            set_dict = {"set_from": conf.date_beginning, "set_to": set_to}
            frequency, regression, summary = \
                eqa.find_intensity_frequency_regression_summarize(
                    meta, station, set_dict, dir_data=dir_data)
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
    plt.show()



if __name__ == "__main__":
    main()
