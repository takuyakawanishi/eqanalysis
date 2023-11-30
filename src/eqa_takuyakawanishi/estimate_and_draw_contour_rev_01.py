import cartopy.crs as ccrs
import cartopy.feature as cfeature
import datetime
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import scipy.stats
import sys
import src.eqa_takuyakawanishi.eqa as eqa


def get_lat_lon_intensity_7(meta):
    stations = [1460600, 2205220, 3710044, 7413631, 7413931]
    meta_sel = meta[meta['code'].isin(stations)]
    meta_latlon = eqa.calc_latlon(meta_sel)
    latlons = meta_latlon.loc[:, ['latitude', 'longitude']]
    return latlons


def main():
    # TO DO
    # abstract the content in loops and make them functions.
    # make in Settings the range of intensities for regression line.
    # create a function to check if all settings are consistent.
    #     For example minimum rge4
    #
    ############################################################################
    # Settings
    ############################################################################
    #
    dir_data = '../../data/stationwise_fine_old_until_2019/'
    file2read_meta = '../../data/code_p_df_old.csv'
    conf = eqa.Settings()
    # Dates and duration
    conf.date_beginning = '1996-04-01'
    # conf.date_beginning = '2012-01-01'
    # conf.date_end = '1994-12-31'
    # contour_to_draw = (est7, est6, est5, rge4_ras_py, rge3_ras_py,
    #                    ge3_raw_py, ge4_raw_py, slope)    #
    conf.reg_start = 2
    conf.reg_end = 4
    conf.highest_available = True
    conf.n_int2_min = 0
    conf.n_int3_min = 1
    conf.n_int4_min = 1
    conf.n_int5_min = 0
    conf.duration_min = 10

    conf.draw = 'contour'
    conf.contour_to_draw = 'est7'
    conf.minus = False
    conf.contour_plot_int_7 = True
    conf.contour_plot_int_6 = False
    conf.contour_log_scale = True
    conf.contour_cmap = "coolwarm"
    # conf.contour_cmap = "Blues"
    conf.contour_cmap = "seismic"
    conf.contour_colorbartitle = conf.create_colorbar_title()
    conf.contour_alpha = 1
    conf.contour_plot_stations = False
    # conf.contour_lmax = - 2
    conf.contour_lmin = - 5
    conf.contour_lstep = .5
    if conf.contour_to_draw == 'freq2':
        conf.contour_lmin = - 0.5
    elif conf.contour_to_draw == 'freq3':
        conf.contour_lmin = - 1
    elif conf.contour_to_draw == 'est6':
        conf.contour_lmin = - 4
    elif conf.contour_to_draw == 'slope':
        conf.contour_log_scale = False
        conf.contour_lstep = 0.1
        conf.contour_lmin = - 1

    conf.contour_station_size = 1.
    conf.contour_station_alpha = .3

    #
    ############################################################################
    # Processing
    ############################################################################
    #
    # Read data
    #
    meta = pd.read_csv(file2read_meta)
    #
    having_int_7 = eqa.find_having_int_7(meta, dir_data)
    meta_sel_7 = meta[meta['code'].isin(having_int_7)]
    latlons7 = eqa.calc_latlon(meta_sel_7)
    # print(latlons7)
    having_int_6 = eqa.find_having_int_6(meta, dir_data)
    meta_sel_6 = meta[meta['code'].isin(having_int_6)]
    latlons6 = eqa.calc_latlon(meta_sel_6)
    # sys.exit()
    # Area settings
    # meta['sel'] = meta.code.astype(str).str[:2]
    # meta = meta.query('sel == "37" or sel == "38" or sel == "39" or '
    #                  'sel == "22" or sel == "23" or sel == "24"')
    # meta = meta.query('sel == "52" or sel == "53"')
    # meta = meta.reset_index(drop=True)
    meta = eqa.calc_latlon(meta)
    lal, lau, lol, lou = eqa.calc_range_latlon(
        meta, conf.map_include_all_japan_lands)
    #
    # Screening by the minimum period, minimum counts.
    #
    meta = eqa.calc_date_b_date_e_duration(
        meta, conf.date_beginning, conf.date_end, dir_data=dir_data)
    meta = meta[meta['duration'] >= conf.duration_min]
    #
    #
    # Stationwise values
    #
    meta = meta.reset_index(drop=True)
    print("Number of relevant stations = ", len(meta))
    codes = list(meta['code'])
    meta.to_csv('../../results/intermediate_meta.csv')
    for i_code, code in enumerate(codes):
        # print('Now processing {}'.format(code))
        #
        # Bring the following into a function, which enables us
        # 1) calculate the station-wise counts and regressions,
        #    by passing an one-row dataframe of meta.
        # Avoid i_code but use code by making code index.
        date_b = meta.at[i_code, 'date_b']
        date_e = meta.at[i_code, 'date_e']
        try:
            d7, d6, d5, d4, d3, d2, d1 = \
                eqa.create_subdfs_by_intensities_new(
                    code, date_b, date_e, dir=dir_data)
        except ValueError as ve:
            print(code, 'cannot be read.', ve)
            continue
        except TypeError as te:
            print(code, 'cannot be read.', te)
            continue
        duration = meta.at[i_code, 'duration']
        if len(d2) >= conf.n_int2_min and \
                len(d3) >= conf.n_int3_min and \
                len(d4) >= conf.n_int4_min and \
                len(d5) >= conf.n_int5_min and \
                len(d6) >= conf.n_int6_min:
            for intensity in conf.intensities:
                #
                strraw = 'ge' + str(intensity) + '_raw'
                strras = 'rge' + str(intensity) + '_ras'
                df = eval('d' + str(intensity))
                n_raw_count, n_rem_aftsk = \
                    eqa.count_considering_aftershocks(
                        df, intensity, conf.remiflt)
                meta.at[i_code, strraw] = n_raw_count
                meta.at[i_code, strras] = n_rem_aftsk
                meta.at[i_code, strraw + '_py'] = n_raw_count / duration
                meta.at[i_code, strras + '_py'] = n_raw_count / duration
            meta.at[i_code, 'freq2'] = len(d2) / duration
            meta.at[i_code, 'freq3'] = len(d3) / duration
            meta.at[i_code, 'freq4'] = len(d4) / duration

            meta.at[i_code, 'est7'] = np.nan
            meta.at[i_code, 'est6'] = np.nan
            meta.at[i_code, 'est5'] = np.nan
            meta.at[i_code, 'slope'] = np.nan
            meta.at[i_code, 'intmax'] = np.nan

            if conf.highest_available:
                frqs = np.array(
                    [len(d1), len(d2), len(d3), len(d4), len(d5), len(d6),
                     len(d7)])
                ints = [1, 2, 3, 4, 5, 6, 7]
                if len(d6) > 0:
                    intmax = 6
                elif len(d5) > 0:
                    intmax = 5
                elif len(d4) > 0:
                    intmax = 4
                try:
                    frqs = frqs[1:intmax]
                    lfrqs = np.log10(frqs)
                    meta.at[i_code, 'intmax'] = intmax
                    res = scipy.stats.linregress(ints[1:intmax], lfrqs)
                except Exception as ex:
                    print(ex)
                # print(code, res.slope, res.intercept)
            else:
                res = eqa.find_regression_intensity_occurrence(
                    meta, i_code, 'ras', conf.reg_start,
                    conf.reg_end)
            if res is None:
                continue
            else:
                intercept = res.intercept
                slope = res.slope
                rvalue = res.rvalue
                meta.at[i_code, 'est5'] = \
                    10 ** (intercept + slope * 5) / duration
                meta.at[i_code, 'est6'] = \
                    10 ** (intercept + slope * 6) / duration
                meta.at[i_code, 'est7'] = \
                    10 ** (intercept + slope * 7) / duration
                meta.at[i_code, 'slope'] = slope
                meta.at[i_code, 'intercept'] = 10 ** intercept / duration
                meta.at[i_code, 'rvalue'] = rvalue
                # if conf.draw_stationwise_figures:
                #     eqa.create_figure_intensity_vs_occurrence(
                #         meta.loc[i_code, :], code, intercept, slope,
                #         conf.intensities)

    meta = meta[meta[conf.contour_to_draw].notna()]
    meta = meta.reset_index(drop=True)
    meta.to_csv('temp.csv', index=None)

    meta_zero = meta[meta[conf.contour_to_draw] == 0]
    print(meta_zero.loc[:, 'code'])
    print("Number of station analysed = ", len(meta))
    meta.to_csv('../../results/temp.csv', index=None)
    if conf.draw == 'contour':
        fig, ax = eqa.draw_contour(
            meta, conf.contour_to_draw, minus=conf.minus,
            log_scale=conf.contour_log_scale,
            cmap=conf.contour_cmap,
            lmin=conf.contour_lmin, lmax=conf.contour_lmax,
            lstep=conf.contour_lstep,
            colorbartitle=conf.contour_colorbartitle,
            lon_min=lol - .1, lon_max=lou + .1,
            lat_min=lal - .1, lat_max=lau + .1,
            contour_alpha=conf.contour_alpha,
            plot_stations=conf.contour_plot_stations,
            station_size=conf.contour_station_size,
            station_alpha=conf.contour_station_alpha
        )
    elif conf.draw == 'scatter':
        fig, ax = eqa.draw_scatter(
            meta, conf.contour_to_draw, minus=conf.minus,
            log_scale=conf.contour_log_scale,
            cmap=conf.contour_cmap,
            lmin=conf.contour_lmin, lmax=conf.contour_lmax,
            lstep=conf.contour_lstep,
            colorbartitle=conf.contour_colorbartitle,
            lon_min=lol - .1, lon_max=lou + .1,
            lat_min=lal - .1, lat_max=lau + .1,
            contour_alpha=conf.contour_alpha,
            plot_stations=conf.contour_plot_stations,
            station_size=conf.contour_station_size,
            station_alpha=conf.contour_station_alpha
        )
    longitude = latlons7['longitude']
    print(latlons7)
    latitude = latlons7['latitude']
    if conf.contour_plot_int_7:
        ax.scatter(
            latlons7['longitude'], latlons7['latitude'],
            transform=ccrs.PlateCarree(), marker='x', c='k', s=50,
            linewidth=1, zorder=1000)
        lat = 34 + 41 / 60
        lon = 135 + 11 / 60
        ax.scatter(
            lon, lat, transform=ccrs.PlateCarree(), c='k', s=50,
            marker='x', linewidth=1,
            zorder=1000)
    if conf.contour_plot_int_6:
        ax.scatter(latlons6['longitude'], latlons6['latitude'],
                   transform=ccrs.PlateCarree(), c='k', marker='s',
                   linewidth=.2,
                   alpha=1, zorder=-2000, s=4, lw=.5)
    fig.savefig('../../results/test.png')
    filename = '../../results/figures/Contour_' + conf.contour_to_draw + \
        '_yge' + str(conf.duration_min) + '_ige' + str(conf.reg_start) + \
        '_' + conf.date_beginning + '_' + conf.date_end + '.svg'
    fig.savefig(filename)
    plt.show()


if __name__ == '__main__':
    main()
