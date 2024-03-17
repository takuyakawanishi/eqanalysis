import cartopy.crs as ccrs
import cartopy.feature as cfeature
import datetime
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.tri as tri
from mpl_toolkits.axes_grid1 import make_axes_locatable
import numpy as np
import pandas as pd
# import scipy.stats
import scipy.ndimage as ndimage

import sys
sys.path.append("./")
import eqanalysis.src.eqa_takuyakawanishi.eqa as eqa


class Settings:

    def __init__(self):
        self.draw_stationwise_figures = False
        self.regs = pd.DataFrame(columns=['x-ax', 'y-ax', 'minint', 'maxint'])
        self.reg_raw_show = False
        self.reg_raw_start = 2
        self.reg_raw_end = 4
        self.reg_aas_show = True
        self.reg_aas_start = 2
        self.reg_aas_end = 4
        self.map_include_all_japan_lands = False
        self.contour_to_draw = 'est7'
        self.contour_log_scale = True
        self.contour_cmap = 'Reds'
        self.contour_lstep = .5
        self.contour_lmin = None
        self.contour_lmax = None
        self.contour_plot_stations = False
        self.contour_station_size = 1
        self.contour_station_alpha = 1.


def draw_scatter(meta, col, minus=True, log_scale=True, cmap='Reds',
                 lmax= None, lmin=None, lstep=.5, colorbartitle=None,
                 lon_min=122, lon_max=154, lat_min=20, lat_max=46,
                 contour_alpha=1,
                 plot_stations=True, station_size=5, station_alpha=.5):
    fig = plt.figure(figsize=(10.8, 10.8), facecolor=None)
    ax = fig.add_axes(
        [0.025, 0.08, .9, .9],
        projection=ccrs.PlateCarree(central_longitude=180))
    fig.patch.set_alpha(0)
    ax.tick_params(axis='both', which='both', direction='in')
    ax.coastlines(resolution='10m', lw=.5)
    ax.set_extent([lon_min, lon_max, lat_min, lat_max])
    latitude = meta['latitude']
    longitude = meta['longitude']
    val = meta[col]
    if minus:
        val = - val
    if log_scale:
        val = meta[col].apply(np.log10)
    if lmax is not None:
        val_max = lmax
    else:
        val_max = val.max()
    if lmin is not None:
        val_min = lmin
    else:
        val_min = val.min()
    val_range = val_max - val_min
    print(val_max, val_min, val_range)
    floor = int(val_min / lstep) * lstep
    ceiling = (int(val_max / lstep) + 1) * lstep
    levels = np.arange(floor, ceiling, lstep)
    n_gridlon = 2000
    n_gridlat = 2000
    lon_i = np.linspace(lon_min, lon_max, n_gridlon)
    lat_i = np.linspace(lat_min, lat_max, n_gridlat)
    triang = tri.Triangulation(longitude, latitude)
    interpolator = tri.LinearTriInterpolator(triang, val)
    mesh_lon_i, mesh_lat_i = np.meshgrid(lon_i, lat_i)
    val_i = interpolator(mesh_lon_i, mesh_lat_i)
    val_i2 = ndimage.gaussian_filter(val_i, sigma=0, order=0)
    ax.add_feature(cfeature.OCEAN, zorder=100, edgecolor='k', lw=0.5,
                   facecolor='#eeeeee')
    scatter = ax.scatter(
        longitude, latitude, c=val, transform=ccrs.PlateCarree(),
        cmap=cmap, alpha=contour_alpha, zorder=200, clip_on=False,
        edgecolor='k', linewidth=.5
    )
    divider = make_axes_locatable(ax)
    ax_cb = divider.new_horizontal(size="5%", pad=0.05, axes_class=plt.Axes)

    fig.add_axes(ax_cb)
    cb = plt.colorbar(scatter, cax=ax_cb)
    cb.ax.set_title(colorbartitle)

    return fig, ax


def draw_contour(meta, col, minus=True, log_scale=True, cmap='Reds',
                 lmax=None, lmin=None, lstep=.5, colorbartitle=None,
                 lon_min=122, lon_max=154, lat_min=20, lat_max=46,
                 contour_alpha=1,
                 plot_stations=True, station_size=5, station_alpha=.5
                 ):

    # mloc= plt.MultipleLocator(5)
    fig = plt.figure(figsize=(10, 8.8), facecolor=None)
    # ax = fig.add_subplot(
    #     1, 1, 1, projection=ccrs.PlateCarree(central_longitude=180))
    ax = fig.add_axes(
        [0.02, 0.02, .9, .94],
        projection=ccrs.PlateCarree())
    # ax.set_facecolor(color=None)
    fig.patch.set_alpha(0)

    ax.tick_params(axis='both', which='both', direction='in')
    ax.coastlines(resolution='10m', lw=.5)
    # ax.gridlines(draw_labels=True, xlocs=mloc, ylocs=mloc, dms=True,
    #              zorder=-100)
    ax.set_extent([lon_min, lon_max, lat_min, lat_max])
    latitude = meta['latitude']
    longitude = meta['longitude']
    values_col = np.array(meta[col])
    if minus:
        vala = - values_col[values_col < 0]
        vala = vala.astype(np.float64)
    else:
        # meta = meta[meta[col] > 0]
        vala = values_col[values_col > 0]
        vala = vala.astype(np.float64)
    # print(vala)
    # for i in range(len(vala)):
    #     if vala[i] <= 0:
    #         print("val is zero at {}".format(i))
    # print("type of vala", type(vala))
    if log_scale:
        val = np.log10(vala)
    if lmax is not None:
        val_max = lmax
    else:
        val_max = val.max()
    if lmin is not None:
        val_min = lmin
    else:
        val_min = val.min()
    val_range = val_max - val_min
    print(val_max, val_min, val_range)
    floor = int(val_min / lstep) * lstep
    ceiling = (int(val_max / lstep) + 1) * lstep
    levels = np.arange(floor, ceiling, lstep)
    n_gridlon = 2000
    n_gridlat = 2000
    lon_i = np.linspace(lon_min, lon_max, n_gridlon)
    lat_i = np.linspace(lat_min, lat_max, n_gridlat)
    triang = tri.Triangulation(longitude, latitude)
    interpolator = tri.LinearTriInterpolator(triang, val)
    mesh_lon_i, mesh_lat_i = np.meshgrid(lon_i, lat_i)
    val_i = interpolator(mesh_lon_i, mesh_lat_i)
    val_i2 = ndimage.gaussian_filter(val_i, sigma=0, order=0)
    ax.add_feature(cfeature.OCEAN, zorder=100, edgecolor='k', lw=0.5,
                   facecolor='#cccccc')
    contourf = ax.contourf(
        lon_i, lat_i, val_i2, transform=ccrs.PlateCarree(), levels=levels,
        cmap=cmap, alpha=contour_alpha
    )
    ax.contour(
        lon_i, lat_i, val_i2, transform=ccrs.PlateCarree(), levels=levels,
        linewidths=.5, colors='k', linestyles='-'
    )
    divider = make_axes_locatable(ax)
    ax_cb = divider.new_horizontal(size="5%", pad=0.05, axes_class=plt.Axes)

    fig.add_axes(ax_cb)
    cb = plt.colorbar(contourf, cax=ax_cb)

    # cb = plt.colorbar(contourf, shrink=0.75)
    cb.ax.set_title(colorbartitle)
    if plot_stations:
        ax.scatter(
            longitude, latitude, c='k', transform=ccrs.PlateCarree(),
            s=station_size, alpha=station_alpha, zorder=2000
        )

    return fig, ax


def create_colorbar_title(contour_to_draw):
    if contour_to_draw == 'slope':
        return "$\\mathrm{slope}$"
    elif contour_to_draw == 'est7':
        return "$\\log_{10}(\\hat{N}(7)/T)$"
    elif contour_to_draw == 'est6':
        return "$\\log_{10}(\\hat{N}(6)/T)$"
    elif contour_to_draw == "est6p5":
        return "$\\log_{10}(\\hat{N}(6.5)/T)$"
    elif contour_to_draw == 'freq3':
        return "$\\log_{10}(N(3)/T)$"
    elif contour_to_draw == 'freq2':
        return "$\\log_{10}(N(2)/T)$"
    else:
        return ""


def get_lat_lon_intensity_7(meta):
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
    dir_data = 'eqanalysis/data_2024/stationwise_2021/'
    file2read_code_p = "eqanalysis/data_2024/code_p_20231205_df.csv"
    df_code = pd.read_csv(file2read_code_p)
    file2read_meta = \
        'eqanalysis/data_2024/intermediates/organized_code_2024_04.csv'
    conf = Settings()
    conf.date_beginning = '1919-01-01 00:00:00'
    conf.date_end = "2011-03-10 23:59:59"
    print("Date beginning: ", conf.date_beginning)
    print("Date end:       ", conf.date_end)
    conf.works_at_date_end = False
    conf.reg_start = 2
    conf.reg_end = 4
    conf.highest_available = True
    #
    # Screening
    #
    # conf.n_int3_min = 0
    # conf.n_int4_min = 1
    # conf.n_int5_min = 0

    # conf.duration_min = 5
    conf.draw = 'contour'
    # contour_to_draw = ('est7', 'est6', 'st6p5') 
    conf.contour_to_draw = 'ero6p'
    conf.minus = False
    conf.contour_plot_int_7 = True
    conf.int7_station_size = 50
    conf.int7_station_alpha = 1
    conf.contour_plot_int_6 = False
    conf.contour_log_scale = True
    conf.contour_cmap = "seismic"
    conf.contour_colorbartitle = create_colorbar_title(conf.contour_to_draw)
    conf.contour_alpha = 1
    conf.contour_plot_stations = False
    conf.contour_lmax = -1
    # conf.contour_lmin = - 4
    conf.contour_lstep = .5
    conf.contour_station_size = 1.
    conf.contour_station_alpha = .3
    conf.int7_stations = [5310700, 1460600, 2205220, 3710044, 7413631, 
                          7413931, 3900131, 3900620]
    conf.int7_dates = [
        "1995 Jan 17", "2018 Sep 6", "2011 Mar 11", "2004 Oct 23",
        "2016 Apr 16", "2016 Apr 14", "2024 Jan 1", "2024 Jan 1"
    ]
    # if conf.contour_to_draw == 'freq2':
    #     conf.contour_lmin = - 0.5
    # elif conf.contour_to_draw == 'freq3':
    #     conf.contour_lmin = - 1
    # elif conf.contour_to_draw == 'est6':
    #     conf.contour_lmin = - 4
    # elif conf.contour_to_draw == 'slope':
    #     conf.contour_log_scale = False
    #     conf.contour_lstep = 0.1
    #     conf.contour_lmin = - 1
    
    file2read_meta = \
        'eqanalysis/data_2024/intermediates/organized_code_2024_04.csv'
    df_org = pd.read_csv(file2read_meta)
    df_org = eqa.calc_latlon(df_org)
    df_est = pd.read_csv("peps/results/japan_cor_ge2.csv")
    # df_est = pd.read_csv(
    #     "peps/results/japan_cor_ge2_form_1996-04-01_to_2011-03-10.csv")
    df_est = df_est[df_est["ero6p"] > 0]
    df_est = df_est[df_est["duration"] > 5 * 365.2425]
    df_est = df_est[df_est["pvalue"] > 0]
    df_est["est6p5"] = df_est["ero6p"]

    idxs = df_est.index
    for i_idx, idx in enumerate(idxs):
        station_prime = df_est.at[idx, "station_prime"]
        df_sel = df_org[df_org["code_prime"] == station_prime]
        df_sel = df_sel.reset_index(drop=True)

        df_est.at[idx, "latitude"] = df_sel.at[0, "latitude"]
        df_est.at[idx, "longitude"] = df_sel.at[0, "longitude"]

    print(df_est.head(5))
    n_relevant_stations = len(df_est)
    print("Number of relevant stations = {}".format(n_relevant_stations))
    lal, lau, lol, lou = eqa.calc_range_latlon(
        df_est, conf.map_include_all_japan_lands)
    
    print("df_est")
    print(df_est.head(3))
    print("conf.contour_to_draw = ", conf.contour_to_draw)
    if conf.draw == 'contour':
        fig, ax = draw_contour(
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
        fig, ax = draw_scatter(
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
    # if conf.contour_plot_int_7:
    int7s = conf.int7_stations
    # print(int7s)

    transform = ccrs.PlateCarree()._as_mpl_transform(ax)
    lonlat7s = []
    for i_int7, int7 in enumerate(int7s):
        # print(int7)
        lonlat7 = eqa.find_lonlat_for_station(int7, df_code)
        lonlat7s.append(lonlat7)
        movedown = 0
        if i_int7 == 5:
            movedown = 1.6
        elif i_int7 == 7:
            movedown = .8
        elif i_int7 == 6:
            movedown = -.4
        # https://stackoverflow.com/questions/25416600/why-the-annotate-worked-unexpected-here-in-cartopy
        ax.annotate(
            conf.int7_dates[i_int7], xy=lonlat7, 
            xytext=(lonlat7[0] - 1.6, lonlat7[1] + 2.5 - movedown),
            xycoords=transform,
            arrowprops=dict(arrowstyle="-", linewidth=1, shrinkA=0, shrinkB=0,
                            color=(0.9, 1, 0.7)), 
            va="bottom", ha="right", zorder=5000)
        # print(lonlat7)
        # ax.scatter(
        #     lonlat7[0], lonlat7[1], color=(0.6, 1, 0.4), 
        #     transform=ccrs.PlateCarree(), edgecolors="k",
        #     linewidths=0.5,
        #     s=6, alpha=1, zorder=3000, marker="o"
        # )
    # output_filename = "eqanalysis/results/figures/test_contour_02"
    # fig.savefig(output_filename + ".svg")
    # fig.savefig(output_filename + ".png", dpi=300)
    # fig.savefig(output_filename + ".pdf")
    # print(output_filename)
    plt.show()


if __name__ == '__main__':
    main()
