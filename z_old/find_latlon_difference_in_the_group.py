import geopy.distance
import numpy as np
import pandas as pd
import sys


def calc_latron(lon, lat):
    lat = str(lat)
    lat0 = lat[:2]
    lat1 = lat[2:4]
    lon = str(lon)
    lon0 = lon[:3]
    lon1 = lon[3:5]
    latitude = float(lat0) + float(lat1) / 60
    longitude = float(lon0) + float(lon1) / 60
    return latitude, longitude


def calc_distance(a, b):
    return geopy.distance.geodesic(a, b).km


def calc_distances_in_group(meta, codes_ordered):
    latrons = []
    latron_values = []
    for ordered_code in codes_ordered:
        idx = meta.index[meta["code"] == ordered_code]
        try:
            lat = meta.loc[idx, "lat"].values[0]
        except Exception as ex:
            print(ex)
        lon = meta.loc[idx, "lon"].values[0]
        latrons.append([lon, lat])
    for latron in latrons:
        latron_values.append(calc_latron(*latron))
    n = len(latron_values)
    distances = []
    for i in range(n):
        for j in range(i + 1, n):
            distance = calc_distance(latron_values[i], latron_values[j])
            distances.append(distance)
    distances = np.array(distances)
    return distances


def main():
    np.set_printoptions(precision=2)
    meta = pd.read_csv("../data/code_p_df_old.csv")
    org = pd.read_csv("../intermediates/organized_codes.csv")
    org = org.reset_index(drop=True)
    codes = list(org["code_prime"])
    count = 0
    for i_code, code in enumerate(codes):
        codes_ordered = eval(org.at[i_code, "codes_ordered"])
        if len(codes_ordered) > 1:
            count += 1
            distances = calc_distances_in_group(meta, codes_ordered)
            print(distances)
    print(count)

if __name__ == '__main__':
    main()