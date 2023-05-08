import cartopy.crs as ccrs
import cartopy.feature as cfeature
import datetime
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.tri as tri
from mpl_toolkits.axes_grid1 import make_axes_locatable
import numpy as np
import pandas as pd
import scipy.stats
import scipy.ndimage as ndimage
import warnings
import sys


class Settings:

    def __init__(self):
        self.date_beginning = '1919-01-01'
        self.date_end = '2019-12-31'
        self.duration_min = 5
        self.remiflt = {
            '1': 7, '2': 10, '3': 32, '4': 46, '5': 46, '6': 46, '7': 46
        }
        self.range_exp_fit_low = [20, 20, 50, 50, 50, 50, 50]
        self.range_exp_fit_upp = [100, 100, 1000, 1000, 1000, 1000, 1000]
        self.intensities = [1, 2, 3, 4, 5, 6, 7]
        self.n_int3_min = 1
        self.n_int4_min = 1
        self.n_int5_min = 0
        self.n_int6_min = 0

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
        self.contour_colorbartitle = self.create_colorbar_title()

    def create_colorbar_title(self):
        #
        a = "("
        b = ")"
        if self.contour_log_scale:
            slog = '\\log_{10}'
        else:
            slog = ""
        if self.contour_to_draw[:3] == 'est':
            symb = '\\hat N'
            sint = self.contour_to_draw[3]
        elif self.contour_to_draw[:2] == 'rg':
            symb = 'N_{\\mathrm{a}}'
            sint = self.contour_to_draw[3]
        elif self.contour_to_draw[:2] == 'ge':
            symb = 'N_{\\mathrm{raw}}'
            sint = self.contour_to_draw[2]
        else:
            return ""
        return '$' + ' ' + slog + symb + a + sint + b + ' ' + '$'


################################################################################
#   Dates, Periods
################################################################################

# def organize_record_period_of_station(meta, code):
#     str_b = meta['from']
#     str_d = meta['to']
#     meta['date_b'] = calc_date_beginning(str_b)
#     meta['date_e'] = date_end_to_datetime(str_e)
#     return meta


def calc_date_b_date_e_duration(meta, date_beginning, date_end):
    meta = calc_date_beginning(meta)
    meta = calc_date_end(meta)
    meta.loc[:, 'beginning'] = datetime.datetime.strptime(
        date_beginning, "%Y-%m-%d")
    meta.loc[:, 'end'] = datetime.datetime.strptime(date_end, "%Y-%m-%d")
    meta['date_b_sub'] = meta[['date_b', 'beginning']].max(axis=1)
    meta['date_e_sub'] = meta[['date_e', 'end']].min(axis=1)
    meta['duration'] = (meta['date_e_sub'] - meta['date_b_sub']) / \
                       np.timedelta64(1, 'Y')
    return meta


def datetime_from_to(meta):
    meta = calc_date_beginning(meta)
    meta = calc_date_end(meta)
    return meta


def calc_date_beginning(df):
    dt_earliest = datetime.datetime(1919, 1, 1)
    codes = list(df['code'])
    for i_code, code in enumerate(codes):
        # print(i_code)
        # print(df.at[i_code, 'from'])
        strdt = str(df.at[i_code, 'from'])[:8]
        # print(strdt)
        dt_beginning = date_beginning_to_datetime(strdt)
        try:
            if dt_beginning < dt_earliest:
                dt_beginning = dt_earliest
                # print(i_code, 'dt_b < dt_e')
            df.at[i_code, 'date_b'] = dt_beginning
            # print(i_code, dt_beginning)
        except:
            df.at[i_code, 'date_b'] = pd.NaT
            # print(i_code, df.at[i_code, 'date_b'])
    return df


def calc_date_end(df):
    codes = list(df['code'])
    for i_code, code in enumerate(codes):
        if np.isnan(df.at[i_code, 'to']):
            df.at[i_code, 'date_e'] = datetime.datetime(2019, 12, 31)
        else:
            dt_end = date_end_to_datetime(str(df.at[i_code, 'to']))
            df.at[i_code, 'date_e'] = dt_end
    return df


def date_beginning_to_datetime(strdt):
    year = strdt[:4]
    month = strdt[4:6]
    day = strdt[6:8]
    # time = strdt[8:12]
    if year == '9999':
        return np.nan
    else:
        if month == '99':
            month = '01'
        if day == '99':
            day = '01'
        # if time == '9999':
        #     time = '0000'
        dt = datetime.datetime.strptime(year + month + day, '%Y%m%d')
        return dt


def date_end_to_datetime(strdt):
    year = strdt[:4]
    month = strdt[4:6]
    day = strdt[6:8]
    # time = strdt[8:12]
    if year == '9999':
        return np.nan
    else:
        if month == '99':
            month = '12'
        if day == '99':
            day = '28'
        # if time == '9999':
        #     time = '2359'
        dt = datetime.datetime.strptime(year + month + day, '%Y%m%d')
        return dt


###############################################################################
#   Intervals
################################################################################

def calc_intervals(dir_data, code, beginning='1919-01-01', end='2019-12-31'):
    print(dir_data, code, beginning, end)
    try:
        d7, d6, d5, d4, d3, d2, d1 = create_subdfs_by_intensities(
            code, beginning=beginning, end=end,
            dir=dir_data)
        # print(d4)
    except ValueError as ve:
        print(code, 'cannot be read.', ve)
        # st.dfoc['rawc'] = np.nan
        # st.dfoc['aasc'] = np.nan
    except TypeError as te:
        print(code, 'cannot be read.', te)
        # st.dfoc['rawc'] = np.nan
        # st.dfoc['aasc'] = np.nan
    dfis = []
    for i in range(5):
        intensity = i + 1
        # print(intensity)
        df = eval('d' + str(intensity))
        df['date'] = pd.to_datetime(df[['year', 'month', 'day']])
        df['diff'] = df['date'].diff() / np.timedelta64(1, "D")
        intervals = (np.array(df['diff']).astype(np.float64))[1:]
        intervals = np.sort(intervals)
        n = len(intervals)
        suvf = 1 - (np.arange(n) + 1) / (n + 1)
        counts = n - np.arange(n)
        dfi = pd.DataFrame()
        dfi['interval'] = intervals
        dfi['suvf'] = suvf
        dfi['counts'] = counts
        dfis.append(dfi)
    return dfis


def calc_intervals_n_raw_counts(
        dir_data, code, beginning='1919-01-01', end='2019-12-31'):
    # print(dir_data, code, beginning, end)
    try:
        d7, d6, d5, d4, d3, d2, d1 = create_subdfs_by_intensities(
            code, beginning=beginning, end=end,
            dir=dir_data)
        # print(d4)
    except ValueError as ve:
        print(code, 'cannot be read.', ve)
        # st.dfoc['rawc'] = np.nan
        # st.dfoc['aasc'] = np.nan
    except TypeError as te:
        print(code, 'cannot be read.', te)
        # st.dfoc['rawc'] = np.nan
        # st.dfoc['aasc'] = np.nan
    dfis = []
    n_raws = []
    for i in range(7):
        intensity = i + 1
        # print(intensity)
        df = eval('d' + str(intensity))
        if df is not None:
            n_raws.append(len(df))
            df['date'] = pd.to_datetime(df[['year', 'month', 'day']])
            df['diff'] = df['date'].diff() / np.timedelta64(1, "D")
            intervals = (np.array(df['diff']).astype(np.float64))[1:]
            intervals = np.sort(intervals)
            n = len(intervals)
            suv_f = 1 - (np.arange(n) + 1) / (n + 1)
            counts = n - np.arange(n)
            dfi = pd.DataFrame()
            dfi['interval'] = intervals
            dfi['suvf'] = suv_f
            dfi['counts'] = counts
            dfis.append(dfi)
        else:
            n_raws.append(0)
            dfis.append(None)
    return dfis, n_raws


def calc_regression_intervals(dfis, reg_thres, upto=5):
    results = []
    for i in range(upto):
        dfi = dfis[i]
        reg_l = int(reg_thres[i, 0])
        reg_u = int(reg_thres[i, 1])
        dfi['interval'].astype(int)
        dfisel = dfi[dfi['interval'] >= reg_l]
        dfisel = dfisel[dfisel['interval'] <= reg_u]
        n_reg = len(dfisel)
        if n_reg < 3:
            print('Counts are not enough for linear regression.')
            results.append(None)
        else:
            log10suvf = np.log10(np.array(dfisel['suvf']).astype(np.float64))
            results.append(
                scipy.stats.linregress(dfisel['interval'], log10suvf))
    return results


###############################################################################
#   Longitude, Latitude
################################################################################

def calc_latlon(meta):
    temp = meta.loc[:, ['lat', 'lon']]
    temp['lats'] = temp['lat'].apply(str)
    temp.loc[:, 'lat0'] = temp.loc[:, 'lats'].str[:2]
    temp['lat1'] = temp['lats'].str[2:4]
    temp['lon0'] = temp['lon'].astype(str).str[:3]
    temp['lon1'] = temp['lon'].astype(str).str[3:5]
    meta['latitude'] = pd.to_numeric(temp['lat0'], errors='coerce') + \
                       pd.to_numeric(temp['lat1'], errors='coerce') / 60
    meta['longitude'] = pd.to_numeric(temp['lon0'], errors='coerce') + \
                        pd.to_numeric(temp['lon1'], errors='coerce') / 60
    return meta


def calc_range_latlon(meta, include_all_japan_lands):
    #
    # Consider put this in the Settings class
    #
    if include_all_japan_lands:
        lal = 20 + 25 / 60 + 31 / 3600
        lau = 45 + 33 / 60 + 26 / 3600
        lol = 122 + 55 / 60 + 57 / 3600
        lou = 153 + 59 / 60 + 12 / 3600
    else:
        lal = meta['latitude'].min()
        lau = meta['latitude'].max()
        lol = meta['longitude'].min()
        lou = meta['longitude'].max()
    return lal, lau, lol, lou


################################################################################
#   Analyse counts at intensities, with or without considering the aftershocks
################################################################################

def create_subdfs_by_intensities(
        station, beginning='1919-01-01', end='2019-12-31', dir='./'
):
    file2read = dir + 'st_' + str(station) + '.txt'
    try:
        df = pd.read_csv(file2read)
    except:
        print('Empty data at ', station)
        return None
    df.loc[df['day'] == '//', 'day'] = '15'
    df = df.drop(df[df.day == '00'].index)
    df['date'] = pd.to_datetime(df[['year', 'month', 'day']])
    beginning_dt = datetime.datetime.strptime(beginning, "%Y-%m-%d")
    end_dt = datetime.datetime.strptime(end, "%Y-%m-%d")
    df = df[df['date'] > beginning_dt]
    df = df[df['date'] < end_dt]
    df['intensity'] = df['intensity'].astype(str)
    df = df.reset_index(drop=True)
    l7 = ['7']
    l6 = ['6', '7', 'C', 'D']
    l5 = ['5', '6', '7', 'A', 'B', 'C', 'D']
    l4 = ['4', '5', '6', '7', 'A', 'B', 'C', 'D']
    l3 = ['3', '4', '5', '6', '7', 'A', 'B', 'C', 'D']
    l2 = ['2', '3', '4', '5', '6', '7', 'A', 'B', 'C', 'D']
    l1 = ['1', '2', '3', '4', '5', '6', '7', 'A', 'B', 'C', 'D']
    d7 = df[df['intensity'].isin(l7)]
    d6 = df[df['intensity'].isin(l6)]
    d5 = df[df['intensity'].isin(l5)]
    d4 = df[df['intensity'].isin(l4)]
    d3 = df[df['intensity'].isin(l3)]
    d2 = df[df['intensity'].isin(l2)]
    d1 = df[df['intensity'].isin(l1)]
    return d7, d6, d5, d4, d3, d2, d1


def count_considering_aftershocks(df, intensity, remiflt):
    n_raw_count = len(df)
    df.loc[df['day'] == '//', 'day'] = '15'
    # df.loc[df['day'] == '00', 'day'] = '15'
    df['diff'] = df['date'].diff() / np.timedelta64(1, "D")
    dfrem = df[df['diff'] < remiflt[str(intensity)]]
    n_to_rem = len(dfrem)
    n_rem_aftsk = n_raw_count - n_to_rem
    return n_raw_count, n_rem_aftsk


def find_regression_intensity_occurrence(
        meta, i_code, reg_for_which, reg_start, reg_end):
    ints = np.arange(reg_start, reg_end + 1)
    cols = []
    for i in ints:
        if reg_for_which == 'ras':
            cols.append('rge' + str(i) + '_ras')
        elif reg_for_which == 'raw':
            cols.append('ge' + str(i) + 'raw')
    res = None
    if meta.at[i_code, 'rge4_ras'] > 0:
        ys = meta.loc[i_code, cols]
        ys = np.array(ys)
        ys = ys.astype(np.float64)
        lys = np.log10(ys)
        try:
            res = scipy.stats.linregress(ints, lys)
        except ValueError as ve:
            print(i_code, 'regression failed.', ve)
    return res


def find_days_cros_the_intercept(x, suvf, intercept):
    df = pd.DataFrame({'x': x, 'suvf': suvf})
    # print(df)
    dfupp = df[df['suvf'] > intercept]
    dflow = df[df['suvf'] <= intercept]
    d1 = dfupp['x'].max()
    d2 = dflow['x'].min()
    return d1, d2


################################################################################
#   Utilities
################################################################################

def find_highest_occurrence_of_intensity_5(meta, dir_data, conf):
    dfoc_raw = pd.DataFrame()
    codes = list(meta['code'])
    for i_code, code in enumerate(codes):
        dfoc_raw.at[i_code, 'code'] = code
        dfoc_raw.at[i_code, 'ge7'] = np.nan
        dfoc_raw.at[i_code, 'ge6'] = np.nan
        dfoc_raw.at[i_code, 'ge5'] = np.nan
        dfoc_raw.at[i_code, 'ge4'] = np.nan
        dfoc_raw.at[i_code, 'ge3'] = np.nan
        dfoc_raw.at[i_code, 'ge2'] = np.nan
        dfoc_raw.at[i_code, 'ge1'] = np.nan
        try:
            d7, d6, d5, d4, d3, d2, d1 = create_subdfs_by_intensities(
                code, beginning=conf.date_beginning, end=conf.date_end,
                dir=dir_data)
        except ValueError as ve:
            print(code, 'cannot be read.', ve)
            continue
        except TypeError as te:
            print(code, 'cannot be read.', te)
            continue
        dfoc_raw.at[i_code, 'ge7'] = len(d7)
        dfoc_raw.at[i_code, 'ge6'] = len(d6)
        dfoc_raw.at[i_code, 'ge5'] = len(d5)
        dfoc_raw.at[i_code, 'ge4'] = len(d4)
        dfoc_raw.at[i_code, 'ge3'] = len(d3)
        dfoc_raw.at[i_code, 'ge2'] = len(d2)
        dfoc_raw.at[i_code, 'ge1'] = len(d1)
    dfoc_raw = dfoc_raw.sort_values(by='ge5', ascending=False)
    return dfoc_raw


def find_largest_files(dir_data):
    dfsize = pd.DataFrame(columns=['code', 'filesize'])
    with os.scandir(dir_data) as it:
        i_code = 0
        for entry in it:
            dfsize.at[i_code, 'code'] = entry.path[-11:-4]
            dfsize.at[i_code, 'filesize'] = entry.stat().st_size
            i_code += 1
    dfsize = dfsize.sort_values(by='filesize', ascending=False)
    return dfsize.head(10)


################################################################################
#   Figures
################################################################################

def create_figure_intensity_vs_occurrence(
        ser, code, intercept, slope, intensities):
    strraws = ['ge1_raw', 'ge2_raw', 'ge3_raw', 'ge4_raw', 'ge5_raw',
               'ge6_raw', 'ge7_raw']
    strrass = ['rge1_ras', 'rge2_ras', 'rge3_ras', 'rge4_ras', 'rge5_ras',
               'rge6_ras', 'rge7_ras']
    xls = np.linspace(1, 7)
    yls = 10 ** (intercept + slope * xls)
    fig = plt.figure(figsize=(2.7, 2.7))
    ax = fig.add_axes([4 / 18, 4 / 18, 3 / 4, 3 / 4])
    ax.set_yscale('log')
    ax.scatter(intensities, ser[strraws])
    ax.scatter(intensities, ser[strrass])
    ax.annotate(str(code), xy=(.9, .9), xytext=(.9, .9),
                xycoords='axes fraction',
                textcoords='axes fraction', ha='right',
                va='top')
    ax.annotate('Intensity', xy=(0.5, 0), xytext=(4 / 18 + 3 / 8, .02),
                xycoords='figure fraction',
                textcoords='figure fraction', ha='center', va='bottom')
    ax.annotate('Occurrence', xy=(0, 0.5), xytext=(.02, 4 / 18 + 3 / 8),
                xycoords='figure fraction',
                textcoords='figure fraction', ha='left', va='center',
                rotation=90)
    ax.plot(xls, yls)
    return fig, ax


def draw_contour(meta, col, log_scale=True, cmap='Reds',
                 lmax=None, lmin=None, lstep=.5, colorbartitle=None,
                 lon_min=122, lon_max=154, lat_min=20, lat_max=46,
                 plot_stations=True, station_size=5, station_alpha=.5):

    # mloc= plt.MultipleLocator(5)
    fig = plt.figure(figsize=(10.8, 10.8), facecolor='w')
    ax = fig.add_subplot(
        1, 1, 1, projection=ccrs.PlateCarree(central_longitude=180))
    ax.coastlines(resolution='10m', lw=.5)
    # ax.gridlines(draw_labels=True, xlocs=mloc, ylocs=mloc, dms=True,
    #              zorder=-100)
    ax.set_extent([lon_min, lon_max, lat_min, lat_max])
    latitude = meta['latitude']
    longitude = meta['longitude']
    val = meta[col]
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
    val_i2 = ndimage.gaussian_filter(val_i, sigma=2, order=0)
    ax.add_feature(cfeature.OCEAN, zorder=1000, edgecolor='k', lw=0.5,
                   facecolor='#cccccc')
    contourf = ax.contourf(
        lon_i, lat_i, val_i2, transform=ccrs.PlateCarree(), levels=levels,
        cmap=cmap
    )
    ax.contour(
        lon_i, lat_i, val_i2, transform=ccrs.PlateCarree(), levels=levels,
        linewidths=.5, colors='k', linestyles='-'
    )
    divider = make_axes_locatable(ax)
    ax_cb = divider.new_horizontal(size="5%", pad=0.1, axes_class=plt.Axes)

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


def main():
    print('This is a library.')


if __name__ == '__main__':
    main()
