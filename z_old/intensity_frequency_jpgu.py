import datetime
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import scipy.stats
import src.eqa_takuyakawanishi.eqa as eqa


def calc_duration(meta):
    meta = meta.reset_index(drop=True)
    datefrom = str(meta.at[0, 'from'])[:8]
    datefrom = datetime.datetime.strptime(datefrom, "%Y%m%d")
    dateto = None
    try:
        dateto = str(meta.at[0, 'to'])[:8]
        dateto = datetime.datetime.strptime(dateto, "%Y%m%d")
    except Exception as ex:
        print(ex)
        dateto = datetime.datetime(2019, 12, 31)
    duration = (dateto - datefrom) / datetime.timedelta(days=1) / 365.2425
    print(datefrom, dateto, duration)
    return duration


def main():
    station = 3500000  # Tokyo, Otemachi, Chiyoda-ku,
    station = 2220100  # Sendai,
    station = 3724800  # Niigata
    station = 4320000  # Gifu
    station = 2500000  # Fukushima
    station = 2500170  # Koriyama

    station = 2500200  # Shirakawa
    station = 2521770  # Inawashiro sokkosyo
    station = 4300000  # Takayama
    station = 4210300  # Suwa
    station = 4210170  # 上田通報所
    station = 4211600  # 軽井沢町追分
    station = 2510000  # Iwaki
    station = 3710070  # Nagaoka tuhoujyo
    station = 2421270  # 尾花沢通報所
    station = 3560170  # Niijima
    station = 4410070  # Numazu
    # station = 2510000  # Iwaki
    station = 2132770  # Mizusawa
    station = 5710170  # Masuda
    station = 5310700  # Kobe, Nakayamate, Chuo-ku,
    station = 3500000  # Tokyo, Otemachi, Chiyoda-ku,
    station = 7415370  # Kumamoto
    station = 2220500  # Miyagi, Izumicho, Ishinomaki
    station = 1500070  # Hidaka-Monbetsu
    station = 5710000  # Hamada, Shimane

    place = "Hamada"


    # station = 3724800
    ilow = 2
    iupp = 4
    dir_data = '../../data/stationwise_fine_old_until_2019/'
    file2read_meta = '../../data/code_p_df_old.csv'
    conf = eqa.Settings()
    meta = pd.read_csv(file2read_meta)
    meta_sel = meta[meta['code'] == station]
    meta_sel = meta_sel.reset_index(drop=True)
    date_beginning = '1919-01-01'
    # date_end = '2019-12-31'
    date_end = '1994-12-31'
    res = eqa.calc_date_b_date_e_duration(
        meta_sel, date_beginning, date_end, dir_data=dir_data)
    date_b = res.at[0, 'date_b']
    date_e = res.at[0, 'date_e']
    duration = res.at[0, 'duration']
    # date_bs = datetime.datetime.strftime(date_b, "%Y-%m-%d")
    # date_es = datetime.datetime.strftime(date_e, "%Y-%m-%d")
    # print(date_bs, type(date_bs))
    # print(duration)
    d7, d6, d5, d4, d3, d2, d1 = None, None, None, None, None, None, None
    try:
        d7, d6, d5, d4, d3, d2, d1 = \
            eqa.create_subdfs_by_intensities_new(
                station, date_b, date_e, dir=dir_data)
    except Exception as ex:
        print(ex)
    intensities = [1, 2, 3, 4, 5, 6, 7]
    counts = []
    for i in intensities:
        df = eval('d' + str(i))
        if df is None:
            counts.append(0)
        else:
            counts.append(len(df))
    print(counts)
    print("Date from : ", res.at[0, 'date_b'])
    print("Data to : ", res.at[0, 'date_e'])
    print("Duration : ", res.at[0, 'duration'])

    fig = plt.figure(figsize=(4.5, 4.5))
    fig.patch.set_alpha(0)
    # ax = fig.add_axes([4/18, 4/18, 3/4, 3/4])
    ax = fig.add_axes([4/25, 4/25, 4/5, 4/5])
    ax.tick_params(which='both', axis='both', direction='in', labelsize=12)
    ax.set_yscale('log')
    ax.scatter(intensities, counts, s=60)
    ints_reg = intensities[ilow - 1:iupp]
    cnts_reg = counts[ilow - 1: iupp]
    print(ints_reg)
    res = scipy.stats.linregress(ints_reg, np.log10(cnts_reg))
    slope = res.slope
    intercept = res.intercept
    print("slope = {:.2f}".format(slope))
    est_7 = 10 ** (intercept + slope * 7)
    ax.plot([ilow, 7.2],
            [10 ** (intercept + slope * ilow), 10 ** (intercept + slope * 7.2)],
            c='k')
    ax.set_xlim(.5, 7.5)
    # ylow, yupp = ax.get_ylim()
    # xlow, xupp = ax.get_xlim()
    # ax.plot([7, 7], [ylow, est_7], lw=.5, c='k')
    # ax.plot([xlow, 7], [est_7, est_7], lw=.5, c='k')

    markerline, stemlines, baseline = \
        ax.stem(est_7, 7, orientation='horizontal', markerfmt="")
    plt.setp(stemlines, color='k', linewidth=.5)
    markerline, stemlines, baseline = ax.stem(7, est_7, markerfmt=" ")
    plt.setp(stemlines, color='k', linewidth=.5)
    est_7_100year = est_7 / duration * 100
    print(est_7_100year)
    fs = 16

    ax.annotate(
        place, xy=(0, .9), xytext=(.05, .95),
        xycoords='axes fraction', textcoords='axes fraction',
        va='top', ha='left', fontsize= fs
    )
    ax.annotate(
        "Intensities $I$", xy=(.5, 0), xytext=(4/25 + 2/5, 0.02),
        xycoords='figure fraction', textcoords='figure fraction',
        va='bottom', ha='center', fontsize=18
    )
    ax.annotate(
        "Counts $N$", xy=(0, 0.5), xytext=(0.02, 4/18 + 3/8),
        xycoords='figure fraction', textcoords='figure fraction',
        va='center', ha='left', fontsize=18, rotation=90
    )
    ax.annotate(
        "St. " + str(station), xy=(.95, .95),
        xytext=(.95, .95), textcoords='axes fraction', va='top', ha='right',
        fontsize=fs
    )
    ax.annotate(
        "Duration/years =" + str(np.round(duration, 1)), xy=(.95, .87),
        xytext=(.95, .87), textcoords='axes fraction', va='top', ha='right',
        fontsize=fs
    )
    ax.annotate(
        "Fitted to range", xy=(.95, .79),
        xytext=(.95, .79), textcoords='axes fraction', va='top', ha='right',
        fontsize=fs,
    )
    ax.annotate(
        "(" + str(ilow) + ", " + str(iupp) + ")", xy=(.95, .71),
        xytext=(.95, .71), textcoords='axes fraction', va='top', ha='right',
        fontsize=fs
    )
    ax.annotate(
        "Slope =" + str(np.round(slope, 2)), xy=(.95, .63),
        xytext=(.95, .63), textcoords='axes fraction', va='top', ha='right',
        fontsize=fs,
    )

    ax.annotate(
        "Predicted occurrence", xy=(.05, .3),
        xytext=(.05, .32), xycoords='axes fraction',
        textcoords='axes fraction', va='top', ha='left', fontsize=fs,
    )
    ax.annotate(
        "of intensity 7 /100yrs.", xy=(.95, .16),
        xytext=(.05, .26), xycoords='axes fraction',
        textcoords='axes fraction', va='top', ha='left', fontsize=fs,
    )
    ax.annotate(
        "=" + str(np.round(est_7_100year, 3)), xy=(.95, .08),
        xytext=(.05, .18), xycoords='axes fraction',
        textcoords='axes fraction', va='top', ha='left', fontsize=fs
    )
    ax.set_ylim(1e-2, 1e4)
    filename = "../../results/figures/IntFreq_" + str(station) + '_' + place + ".svg"
    plt.savefig(filename)
    plt.show()


if __name__ == '__main__':
    main()