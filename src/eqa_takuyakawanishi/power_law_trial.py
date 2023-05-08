import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import scipy.stats
import eqanalysis.src.eqa_takuyakawanishi.eqa as eqa


def find_power_low_exp(dfi):
    dfis = dfi[dfi['suvf'] < 0.05]

    if len(dfis) == 0:
        print("Not enough data for calculating tail exponent.")
        return None
    else:
        dfis = dfis.reset_index(drop=True)
        ly = dfis['suvf'].apply(np.log)
        lx = dfis['interval'].apply(np.log)
        res = scipy.stats.linregress((lx, ly))
        return res


def main():
    station = 3000000
    df = pd.read_csv('../../data/stationwise_fine/st_' + str(station) + '.txt')
    print(df.head(3))
    dfis = eqa.calc_intervals('../../data/stationwise_fine/', station)
    print(dfis[2].head(3))
    for i in range(4):
        dfi = dfis[i]
        res = find_power_low_exp(dfi)
        if res is not None:
            print(res.slope)


    x = dfi.interval
    y = dfi.suvf

    fig = plt.figure(figsize=(4.5, 3))
    ax = fig.add_axes([4/18, 4/18, 3/4, 3/4])
    ax.set_yscale('log')
    ax.set_xscale('log')
    xls = np.logspace(0, 2)

    yls = 1 - scipy.stats.levy_stable.cdf(xls, 1.9, 0, loc=0, scale=3)
    yls2 = 1 - scipy.stats.lognorm.cdf(xls, .8, loc=0, scale=5)
    ax.scatter(x, y)
    ax.plot(xls, yls, c='r')
    ax.plot(xls, yls2, c='k')
    plt.show()



if __name__ == '__main__':
    main()