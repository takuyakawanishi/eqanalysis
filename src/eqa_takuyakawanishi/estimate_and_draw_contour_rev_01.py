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
    dir_data = '../../data/stationwise/'
    file2read_meta = '../../intermediates/organized_codes_pre_02.csv'
    conf = eqa.Settings()
    # Dates and duration
    # conf.date_beginning = '1996-04-01'
    conf.date_beginning = '1919-01-01'
    conf.date_end = "2020-12-31"
    conf.works_at_date_end = True
    conf.reg_start = 2
    conf.reg_end = 4
    conf.highest_available = True
    conf.n_int2_min = 0
    conf.n_int3_min = 1
    conf.n_int4_min = 1
    conf.n_int5_min = 0
    conf.duration_min = 10
    conf.draw = 'contour'
    # contour_to_draw = (est7, est6, est6p5)    #
    conf.contour_to_draw = 'est6p5'
    conf.minus = False
    conf.contour_plot_int_7 = True
    conf.contour_plot_int_6 = False
    conf.contour_log_scale = True
    # conf.contour_cmap = "coolwarm"
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
    meta = pd.read_csv(file2read_meta)
    meta = eqa.calc_latlon(meta)  # Add "latitude" and "longitude" to meta
    lal, lau, lol, lou = eqa.calc_range_latlon(
        meta, conf.map_include_all_japan_lands)
    set_dict = {"set_from": conf.date_beginning, "set_to": conf.date_end}
    df_est = pd.DataFrame()
    for idx in meta.index:
        station = meta.at[idx, "code_prime"]
        frequency, regression, summary = \
            eqa.find_intensity_frequency_regression_summarize(
                meta, station, set_dict, dir_data=dir_data
            )
        summary["latitude"] = meta.at[idx, "latitude"]
        summary["longitude"] = meta.at[idx, "longitude"]
        df_est = pd.concat([df_est, summary], axis=1)
    df_est = df_est.transpose()
    # print(df_est)
    # print(len(df_est))
    if conf.works_at_date_end:
        df_est = df_est[df_est["to"] == conf.date_end]
    df_est = df_est[df_est["int2"] >= conf.n_int2_min]
    df_est = df_est[df_est["int3"] >= conf.n_int3_min]
    df_est = df_est[df_est["int4"] >= conf.n_int4_min]
    df_est = df_est[df_est["int5"] >= conf.n_int5_min]
    df_est = df_est[df_est["duration"] >= conf.duration_min * 365.2425]
    print("Number of relevant stations = {}".format(len(df_est)))

    if conf.works_at_date_end:
        wade = 1
    else:
        wade = 0
    filename = "est_" + str(wade) + str(conf.n_int2_min) + \
               str(conf.n_int3_min) + str(conf.n_int4_min) + \
               str(conf.n_int5_min) + "_" + str(conf.duration_min) + "_" +\
               str(conf.date_beginning) + "_" + str(conf.date_end) + ".csv"
    filename = "../../intermediates/" + filename

    df_est.to_csv(filename, index=None)
    if conf.draw == 'contour':
        fig, ax = eqa.draw_contour(
            df_est, conf.contour_to_draw, minus=conf.minus,
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
    # longitude = latlons7['longitude']
    # print(latlons7)
    # latitude = latlons7['latitude']
    # if conf.contour_plot_int_7:
    #     ax.scatter(
    #         latlons7['longitude'], latlons7['latitude'],
    #         transform=ccrs.PlateCarree(), marker='x', c='k', s=50,
    #         linewidth=1, zorder=1000)
    #     lat = 34 + 41 / 60
    #     lon = 135 + 11 / 60
    #     ax.scatter(
    #         lon, lat, transform=ccrs.PlateCarree(), c='k', s=50,
    #         marker='x', linewidth=1,
    #         zorder=1000)
    # if conf.contour_plot_int_6:
    #     ax.scatter(latlons6['longitude'], latlons6['latitude'],
    #                transform=ccrs.PlateCarree(), c='k', marker='s',
    #                linewidth=.2,
    #                alpha=1, zorder=-2000, s=4, lw=.5)
    # fig.savefig('../../results/test.png')
    # filename = '../../results/figures/Contour_' + conf.contour_to_draw + \
    #     '_yge' + str(conf.duration_min) + '_ige' + str(conf.reg_start) + \
    #     '_' + conf.date_beginning + '_' + conf.date_end + '.svg'
    # fig.savefig(filename)
    plt.show()


if __name__ == '__main__':
    main()
