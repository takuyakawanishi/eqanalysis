import numpy as np
import wget


pref = "https://www.data.jma.go.jp/eqev/data/bulletin/data/shindo/i"

year_begin = 1919
year_end = 2021 + 1
years = np.arange(year_begin, year_end)

for year in years:
    url = pref + str(year) + ".zip"
    wget.download(url, out="eqanalysis/data_2024/data_downloaded")