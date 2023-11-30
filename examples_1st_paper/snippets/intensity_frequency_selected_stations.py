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
    stations = [3500000]
    dir_data = "../../data/stationwise/"
    meta2read = "../../intermediates/organized_codes_pre_02.csv"
    meta = pd.read_csv(meta2read)
    conf = eqa.Settings()
    set_dict = {"set_from": conf.date_beginning, "set_to": conf.date_end}
    for station in stations:
        frequency, regression, summary = \
            eqa.find_intensity_frequency_regression_summarize(
                meta, station, set_dict, dir_data=dir_data)
        fig = plt.figure(figsize=(2.3, 2.3), dpi=144)
        ax = fig.add_axes([7/32, 7/32, .75, .75])
        ax.tick_params(which="both", axis="both", direction="in")
        ax.set_yscale("log")
        print(frequency)
        print(summary)
        slope = summary["slope"]
        intcpt = summary["intercept"]
        ints = np.linspace(2, 7)
        fits = 10 ** (intcpt + slope * ints)

        n = len(frequency)
        intensities = np.arange(n) + 1
        ax.scatter(intensities, frequency, s=20, c="#888888")
        ax.plot(ints, fits, lw=.5, c="#333333")
        for tick in ax.get_xticklabels():
            tick.set_fontname("Furura")
            tick.set_fontsize(9)
        for tick in ax.get_yticklabels():
            tick.set_fontname("Futura")  # "Arial")  #  "Helvetica Neue")
            tick.set_fontsize(8)
        ax.annotate(
            "Frequencies", xy=(0, 0.5), xytext=(0.02, 7/32 + 3/8),
            xycoords="figure fraction", textcoords="figure fraction",
            ha="left", va="center", rotation=90,
            font="Helvetica Neue", size=11
        )
        ax.annotate(
            "Intensities", xy=(0.5, 0), xytext=(7/32 + 3/8, 0.02),
            xycoords="figure fraction", textcoords="figure fraction",
            ha="center", va="bottom",
            font="Helvetica Neue", size=11
        )
        plt.show()



if __name__ == "__main__":
    main()
