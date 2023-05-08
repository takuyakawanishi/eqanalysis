import datetime
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import scipy.stats
import src.eqa_takuyakawanishi.eqa as eqa


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
    dir_data = '../../data/stationwise_fine/'
    file2read_meta = '../../data/code_p_df.csv'
    conf = eqa.Settings()
    # Dates and duration
    # conf.date_beginning = '1996-04-01-00-00'
    # conf.date_beginning = '2012-01-01-00-00'
    # conf.date_end = '1994-12-31'
    # contour_to_draw = (est7, est6, est5, rge4_ras_py, rge3_ras_py,
    #                    ge3_raw_py, ge4_raw_py, slope)    #
    conf.reg_start = 3
    conf.reg_end = 5

    conf.contour_to_draw = 'est7'
    conf.contour_log_scale = True
    conf.contour_colorbartitle = conf.create_colorbar_title()
    conf.contour_plot_stations = True
    # conf.contour_lmin = -3
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
        meta, conf.date_beginning, conf.date_end)
    meta = meta[meta['duration'] >= conf.duration_min]
    #
    conf.n_int3_min = 0
    conf.n_int4_min = 2
    conf.n_int5_min = 1
    conf.duration_min = 10
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

        try:
            d7, d6, d5, d4, d3, d2, d1 = eqa.create_subdfs_by_intensities(
                code, beginning=conf.date_beginning, end=conf.date_end,
                dir=dir_data)
        except ValueError as ve:
            print(code, 'cannot be read.', ve)
            continue
        except TypeError as te:
            print(code, 'cannot be read.', te)
            continue
        duration = meta.at[i_code, 'duration']
        if len(d3) >= conf.n_int3_min and \
                len(d4) >= conf.n_int4_min and \
                len(d5) >= conf.n_int5_min and \
                len(d6) >= conf.n_int6_min and \
                duration >= conf.duration_min:
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

            meta.at[i_code, 'est7'] = np.nan
            meta.at[i_code, 'est6'] = np.nan
            meta.at[i_code, 'est5'] = np.nan
            meta.at[i_code, 'slope'] = np.nan
            meta.at[i_code, 'intercept'] = np.nan
            res = eqa.find_regression_intensity_occurrence(
                meta, i_code, 'ras', conf.reg_start,
                conf.reg_end)
            if res is None:
                continue
            if res is not None:
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

    meta.to_csv('temp.csv', index=None)
    meta = meta[meta[conf.contour_to_draw].notna()]
    meta = meta.reset_index(drop=True)
    print("Number of station analysed = ", len(meta))
    meta.to_csv('../../results/temp.csv', index=None)
    # draw_scatter(meta, conf.coutour_to_draw)
    fig, ax = eqa.draw_contour(
        meta, conf.contour_to_draw, log_scale=conf.contour_log_scale,
        cmap=conf.contour_cmap,
        lmin=conf.contour_lmin, lmax=conf.contour_lmax,
        lstep=conf.contour_lstep,
        colorbartitle=conf.contour_colorbartitle,
        lon_min=lol - .1, lon_max=lou + .1,
        lat_min=lal - .1, lat_max=lau + .1,
        plot_stations=conf.contour_plot_stations,
        station_size=conf.contour_station_size,
        station_alpha=conf.contour_station_alpha
    )
    fig.savefig('../../results/test.png')
    plt.show()


if __name__ == '__main__':
    main()
