import datetime
from dateutil.relativedelta import relativedelta
from dash import Dash, dcc, dash_table, html, Input, Output, State
from collections import OrderedDict
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import pandas as pd
import scipy.stats
import eqa
import sys
sys.path.append("./")
import eqanalysis.dashfiles.layouts.fig_template as fig_template


################################################################################
#  Global Constants and Variables
################################################################################

DATABASE_START_DATE = '19190101'
DATABASE_END_DATE = '20211231'
# DIR_DATA = '../../data/stationwise_fine_old_until_2019/'
# FILE2READ_META = '../../data/code_p_df.csv'
DIR_DATA = 'eqanalysis/data_2024/stationwise_2021/'
FILE2READ_META = 'eqanalysis/data_2024/code_p_20231205_df.csv'
FILE2READ_ORG = "eqanalysis/data_2024/intermediates/organized_code_2024_04.csv"
cud_orange = "#e69900"  # (0.9, 0.6, 0)
cud_skyblue = "#59b3e6"  # (.35, .7, .9)
cud_green = "#009980"  # (0, .6, .5)
cud_blue = "#0073b3"  # (0, .45, .7)
cudr_base_pink_ap3 = (255/255, 202/255, 191/255, .3)
cudr_base_cream_ap3 = (255/255, 255/255, 128/255, .3)
cudr_base_beige = (255/255, 202/255, 128/255)
cudr_base_yellowgreen_ap3 = (216/255, 242/255, 85/255, .3)
curd_base_brightblue_ap3 = (191/255, 228/255, 255/255, .3)


def main():
    station_prime = 3100000
    df_org = pd.read_csv(FILE2READ_ORG)
    dir_data = DIR_DATA
    set_dict = {"set_from": "1996-04-01 12:00:00",
                "set_to": "2121-12-31 23:59:59"}
    frequency, regression, summary = \
        eqa.find_intensity_ro_regression_summarize_ts(
            df_org, station_prime, set_dict, dir_data=dir_data)
    print(summary)


if __name__ == '__main__':
    main()

