import geopy.distance
import datetime
import numpy as np
import pandas as pd
import src.eqa_takuyakawanishi.eqa as eqa
import sys
import time


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
        idx = meta.index[meta["code"] == ordered_code].values[0]
        lat = meta.at[idx, "lat"]
        lon = meta.at[idx, "lon"]
        # print(lat, lon)
        latrons.append([lon, lat])
    for latron in latrons:
        latron_values.append(calc_latron(*latron))
    n = len(latron_values)
    distances = []
    for i in range(n):
        for j in range(i + 1, n):
            distance = calc_distance(latron_values[i], latron_values[j])
            distance = np.round(distance, 2)
            distances.append(distance)
    return distances


def add_address_only_column_to_df(df):
    codes = list(df["code"])
    for i_code, code in enumerate(codes):
        i_code_g = df.loc[df["code"] == code].index[0]
        s = df[df['code'] == code]['address'].values[0]
        if "（臨" in s:
            df.at[i_code_g, "address_only"] = s[:s.index("（")] + "（臨時）"
        elif "（" in s:
            df.at[i_code_g, "address_only"] = s[:s.index("（")]
        elif "＊" in s:
            df.at[i_code_g, "address_only"] = s[:s.index("＊")]
        else:
            df.at[i_code_g, "address_only"] = s
    return df


def find_kyu_index_and_combine_them(df_sll, cfg, dir_data):
    df_sll_g = df_sll.groupby(by="address_only")
    keys = df_sll_g.groups.keys()
    dfs = []
    for i, key in enumerate(keys):
        df = df_sll_g.get_group(key)
        df = df.reset_index(drop=True)
        df["kyu"] = df["address"].str.extract("(\uff08.+)")
        n = len(df)
        codes_g = list(df["code"])
        for i_code_g, code_g in enumerate(codes_g):
            s = df.at[i_code_g, "kyu"]
            if type(s) != str:
                df.at[i_code_g, "order"] = n - 1
            elif s[2] == "）":
                df.at[i_code_g, "order"] = 0
            elif s[2] == "２":
                df.at[i_code_g, "order"] = 1
            elif s[2] == "３":
                df.at[i_code_g, "order"] = 2
            elif s[2] == "４":
                df.at[i_code_g, "order"] = 3
            elif s[2] == "５":
                df.at[i_code_g, "order"] = 4
        try:
            df = df.sort_values("order")
        except Exception as ex:
            print(df)
            print(ex)
        df = df.reset_index(drop=True)
        # print(df["from"])
        # df = eqa.calc_date_b_date_e_duration(
        #     df, cfg.date_beginning, cfg.date_end, dir_data=dir_data)
        df = eqa.calc_datetime_b_datetime_e_duration(
            df, cfg.datetime_beginning, cfg.datetime_end, dir_data=dir_data)
        df["date_b"] = df["datetime_b"].dt.date
        df["date_e"] = df["datetime_e"].dt.date
        # print(df["date_b"].head(4))
        # print(type(df.at[0, "date_b"]))
        df["date_b_str"] = pd.to_datetime(df["date_b"]).dt.strftime("%Y-%m-%d")
        df["date_e_str"] = pd.to_datetime(df["date_e"]).dt.strftime("%Y-%m-%d")
        df["datetime_b_str"] = df["datetime_b"].dt.strftime("%Y-%m-%d %H:%M:%S")
        df["datetime_e_str"] = df["datetime_e"].dt.strftime("%Y-%m-%d %H:%M:%S")
        dfs.append(df)
    return dfs


def create_organized_meta_file(meta, dfs):
    dfg = pd.DataFrame(columns=[
        "code_prime", "lon", "lat", "address", "codes_ordered", "gaps",
        "distances", "grand_date_b", "grand_date_e", "date_b_s", "date_e_s",
        "lats", "lons", "datetime_b_s", "datetime_e_s",
        "date_b_s_old", "date_e_s_old"
    ])
    dfg["codes_ordered"] = dfg["codes_ordered"].astype('object')
    dfg["gaps"] = dfg["gaps"].astype('object')
    dfg["date_b_s"] = dfg["date_b_s"].astype('object')
    dfg["date_e_s"] = dfg["date_e_s"].astype('object')
    dfg["date_b_s_old"] = dfg["date_b_s_old"].astype('object')
    dfg["date_e_s_old"] = dfg["date_e_s_old"].astype('object')
    dfg["lats"] = dfg["lats"].astype('object')
    dfg["lons"] = dfg["lons"].astype('object')
    dfg["datetime_b_s"] = dfg["datetime_b_s"].astype('object')
    dfg["datetime_e_s"] = dfg["datetime_e_s"].astype('object')
    dfg["distances"] = dfg["distances"].astype('object')
    for i_df, df in enumerate(dfs):
        n = len(df)
        codes = list(df["code"])
        dfg.at[i_df, "code_prime"] = codes[0]
        dfg.at[i_df, "lon"] = df[df["code"] == codes[0]]["lon"].values[0]
        dfg.at[i_df, "lat"] = df[df["code"] == codes[0]]["lat"].values[0]
        dfg.at[i_df, "address"] = \
            df[df["code"] == codes[0]]["address_only"].values[0]
        dfg.at[i_df, "codes_ordered"] = codes
        dfg.at[i_df, "date_b_s"] = list(df["date_b_str"])
        dfg.at[i_df, "date_e_s"] = list(df["date_e_str"])
        dfg.at[i_df, "datetime_b_s"] = list(df["datetime_b_str"])
        dfg.at[i_df, "datetime_e_s"] = list(df["datetime_e_str"])
        dfg.at[i_df, "grand_date_b"] = df.at[0, "date_b_str"]
        dfg.at[i_df, "grand_date_e"] = df.at[n-1, "date_e_str"]
        dfg.at[i_df, "lats"] = list(df["lat"])
        dfg.at[i_df, "lons"] = list(df["lon"])
        gaps = []
        distances = []
        if n > 1:
            distances = calc_distances_in_group(meta, codes)
            for i in range(n - 1):
                dlt_t = df.at[i + 1, "datetime_b"] - df.at[i, "datetime_e"]
                gaps.append(np.round(dlt_t.days, 2))
        dfg.at[i_df, "gaps"] = gaps
        dfg.at[i_df, "distances"] = distances
    dfg = dfg.sort_values("code_prime")
    dfg = dfg.reset_index(drop=True)
    return dfg


def main():
    #
    # TODO
    # Adjust the periods which overlaps.
    # This should be done in another program.
    #
    cfg = eqa.Settings()
    cfg.date_end = '2023-12-31'
    dir_data = '../../../data/stationwise/'
    meta = pd.read_csv(r"../../../data/code_p_df.csv")
    #
    # Correction to meta file
    #
    idx = meta.index[meta["code"] == 1010330]
    meta.loc[idx, "address"] = "札幌白石区本郷通札幌白石区北郷（修）"
    idx = meta.index[meta["code"] == 1010340]
    meta.loc[idx, "address"] = "札幌白石区本郷通札幌白石区北郷（修２）"
    idx = meta.index[meta["code"] == 1010341]
    meta.loc[idx, "address"] = "札幌白石区本郷通札幌白石区北郷"
    #
    idx = meta.index[meta["code"] == 1010540]
    meta.loc[idx, "address"] = "札幌南区真駒内札幌南区川沿（修）"
    idx = meta.index[meta["code"] == 1010542]
    meta.loc[idx, "address"] = "札幌南区真駒内札幌南区川沿"

    idx = meta.index[meta["code"] == 1010541]
    meta.loc[idx, "address"] = "札幌南区簾舞札幌南区石山（修）"
    idx = meta.index[meta["code"] == 1010543]
    meta.loc[idx, "address"] = "札幌南区簾舞札幌南区石山"

    # idx = meta.index[meta["code"] == 1050000]
    # meta.loc[idx, "address"] = "八雲町大新八雲町上の湯（修）"
    # idx = meta.index[meta["code"] == 1050001]
    # meta.loc[idx, "address"] = "八雲町大新八雲町上の湯"

    idx = meta.index[meta["code"] == 1061000]
    meta.loc[idx, "address"] = "渡島森町御幸町（修）"
    idx = meta.index[meta["code"] == 1061001]
    meta.loc[idx, "address"] = "渡島森町御幸町（修２）"
    idx = meta.index[meta["code"] == 1061002]
    meta.loc[idx, "address"] = "渡島森町御幸町（修３）"
    idx = meta.index[meta["code"] == 1061003]
    meta.loc[idx, "address"] = "渡島森町御幸町"

    idx = meta.index[meta["code"] == 1170500]
    meta.loc[idx, "address"] = "岩内町清住岩内町高台（修）"
    idx = meta.index[meta["code"] == 1170501]
    meta.loc[idx, "address"] = "岩内町清住岩内町高台"

    idx = meta.index[meta["code"] == 1190000]
    meta.loc[idx, "address"] = "奥尻町米岡奥尻町松江（修）"
    idx = meta.index[meta["code"] == 1190001]
    meta.loc[idx, "address"] = "奥尻町米岡奥尻町松江"

    idx = meta.index[meta["code"] == 1190070]
    meta.loc[idx, "address"] = "奥尻町奥尻（修）"
    idx = meta.index[meta["code"] == 1190030]
    meta.loc[idx, "address"] = "奥尻町奥尻（修２）"
    idx = meta.index[meta["code"] == 1190031]
    meta.loc[idx, "address"] = "奥尻町奥尻"

    idx = meta.index[meta["code"] == 1210330]
    meta.loc[idx, "address"] = "砂川市西６条７条（旧）"
    idx = meta.index[meta["code"] == 1210331]
    meta.loc[idx, "address"] = "砂川市西６条７条（修２）"
    idx = meta.index[meta["code"] == 1210332]
    meta.loc[idx, "address"] = "砂川市西６条７条"

    idx = meta.index[meta["code"] == 1220160]
    meta.loc[idx, "address"] = "北村赤川岩見沢市北村赤川（旧）"
    idx = meta.index[meta["code"] == 1220130]
    meta.loc[idx, "address"] = "北村赤川岩見沢市北村赤川（修２）"
    idx = meta.index[meta["code"] == 1220132]
    meta.loc[idx, "address"] = "北村赤川岩見沢市北村赤川"

    idx = meta.index[meta["code"] == 1220200]
    meta.loc[idx, "address"] = "美唄市西４条５条（修）"
    idx = meta.index[meta["code"] == 1220201]
    meta.loc[idx, "address"] = "美唄市西４条５条"

    idx = meta.index[meta["code"] == 1220330]
    meta.loc[idx, "address"] = "三笠市若松町幸町（修）"
    idx = meta.index[meta["code"] == 1220331]
    meta.loc[idx, "address"] = "三笠市若松町幸町"

    idx = meta.index[meta["code"] == 1260000]
    meta.loc[idx, "address"] = "旭川市８条通宮前１条（修）"
    idx = meta.index[meta["code"] == 1260001]
    meta.loc[idx, "address"] = "旭川市８条通宮前１条"

    # idx = meta.index[meta["code"] == 1260600]
    # meta.loc[idx, "address"] = "上川町白川上川地方越路（修）"
    # idx = meta.index[meta["code"] == 1260601]
    # meta.loc[idx, "address"] = "上川町白川上川地方越路"

    idx = meta.index[meta["code"] == 1270230]
    meta.loc[idx, "address"] = "中富良野町市街地本町（修）"
    idx = meta.index[meta["code"] == 1270231]
    meta.loc[idx, "address"] = "中富良野町市街地本町"

    idx = meta.index[meta["code"] == 1350120]
    meta.loc[idx, "address"] = "猿払村鬼志別浜鬼志別（修）"
    idx = meta.index[meta["code"] == 1350122]
    meta.loc[idx, "address"] = "猿払村鬼志別浜鬼志別"

    # idx = meta.index[meta["code"] == 1410002]
    # meta.loc[idx, "address"] = "北見市常呂町吉野北見市常呂町東浜（修）"
    # idx = meta.index[meta["code"] == 1410003]
    # meta.loc[idx, "address"] = "北見市常呂町吉野北見市常呂町東浜"

    idx = meta.index[meta["code"] == 1410060]
    meta.loc[idx, "address"] = "端野町端野北見市端野町二区（修）"
    idx = meta.index[meta["code"] == 1410030]
    meta.loc[idx, "address"] = "端野町端野北見市端野町二区（修２）"
    idx = meta.index[meta["code"] == 1410031]
    meta.loc[idx, "address"] = "端野町端野北見市端野町二区"

    idx = meta.index[meta["code"] == 1450510]
    meta.loc[idx, "address"] = "壮瞥町壮瞥温泉壮瞥町滝之町（修）"
    idx = meta.index[meta["code"] == 1450511]
    meta.loc[idx, "address"] = "壮瞥町壮瞥温泉壮瞥町滝之町（修２）"
    idx = meta.index[meta["code"] == 1450520]
    meta.loc[idx, "address"] = "壮瞥町壮瞥温泉壮瞥町滝之町"

    idx = meta.index[meta["code"] == 1450670]
    meta.loc[idx, "address"] = "虻田町栄町洞爺湖町栄町（修）"
    idx = meta.index[meta["code"] == 1450630]
    meta.loc[idx, "address"] = "虻田町栄町洞爺湖町栄町（修２）"
    idx = meta.index[meta["code"] == 1450632]
    meta.loc[idx, "address"] = "虻田町栄町洞爺湖町栄町"

    idx = meta.index[meta["code"] == 1460030]
    meta.loc[idx, "address"] = "室蘭市東町室蘭市寿町（修）"
    idx = meta.index[meta["code"] == 1460020]
    meta.loc[idx, "address"] = "室蘭市東町室蘭市寿町"

    idx = meta.index[meta["code"] == 1460100]
    meta.loc[idx, "address"] = "苫小牧市しらかば末広町（修）"
    idx = meta.index[meta["code"] == 1460101]
    meta.loc[idx, "address"] = "苫小牧市しらかば末広町"

    idx = meta.index[meta["code"] == 1510300]
    meta.loc[idx, "address"] = "新ひだか町静内ときわ町山手町（修）"
    idx = meta.index[meta["code"] == 1510301]
    meta.loc[idx, "address"] = "新ひだか町静内ときわ町山手町"

    idx = meta.index[meta["code"] == 1610000]
    meta.loc[idx, "address"] = "釧路市幣舞町幸町（修）"
    idx = meta.index[meta["code"] == 1610009]
    meta.loc[idx, "address"] = "釧路市幣舞町幸町（修２）"
    idx = meta.index[meta["code"] == 1610001]
    meta.loc[idx, "address"] = "釧路市幣舞町幸町"

    idx = meta.index[meta["code"] == 1610040]
    meta.loc[idx, "address"] = "釧路市音別町本町釧路市音別町中園（修）"
    idx = meta.index[meta["code"] == 1610041]
    meta.loc[idx, "address"] = "釧路市音別町本町釧路市音別町中園"

    # idx = meta.index[meta["code"] == 1610320]
    # meta.loc[idx, "address"] = "浜中町霧多布浜中町茶内（修）"
    # idx = meta.index[meta["code"] == 1610321]
    # meta.loc[idx, "address"] = "浜中町霧多布浜中町茶内"

    idx = meta.index[meta["code"] == 2010300]
    meta.loc[idx, "address"] = "深浦町深浦深浦町深浦岡町（修）"
    idx = meta.index[meta["code"] == 2010302]
    meta.loc[idx, "address"] = "深浦町深浦深浦町深浦岡町"

    idx = meta.index[meta["code"] == 2010200]
    meta.loc[idx, "address"] = "鯵ヶ沢町本町鯵ヶ沢町舞戸町鳴戸（修）"
    idx = meta.index[meta["code"] == 2010201]
    meta.loc[idx, "address"] = "鯵ヶ沢町本町鯵ヶ沢町舞戸町鳴戸"

    idx = meta.index[meta["code"] == 2011560]
    meta.loc[idx, "address"] = "尾上町猿賀平川市猿賀（修）"
    idx = meta.index[meta["code"] == 2011530]
    meta.loc[idx, "address"] = "尾上町猿賀平川市猿賀"

    idx = meta.index[meta["code"] == 2020030]
    meta.loc[idx, "address"] = "八戸市南郷南郷区（修）"
    idx = meta.index[meta["code"] == 2020031]
    meta.loc[idx, "address"] = "八戸市南郷南郷区"

    idx = meta.index[meta["code"] == 2021430]
    meta.loc[idx, "address"] = "三戸町在府小路小路町（修）"
    idx = meta.index[meta["code"] == 2021431]
    meta.loc[idx, "address"] = "三戸町在府小路小路町"

    idx = meta.index[meta["code"] == 2030060]
    meta.loc[idx, "address"] = "青森川内町川内むつ市川内町（修）"
    idx = meta.index[meta["code"] == 2030030]
    meta.loc[idx, "address"] = "青森川内町川内むつ市川内町"

    idx = meta.index[meta["code"] == 2030421]
    meta.loc[idx, "address"] = "東通村小田野沢白糠（修）"
    idx = meta.index[meta["code"] == 2030422]
    meta.loc[idx, "address"] = "東通村小田野沢白糠"

    idx = meta.index[meta["code"] == 2030430]
    meta.loc[idx, "address"] = "東通村砂小又砂子又沢内（修）"
    idx = meta.index[meta["code"] == 2030431]
    meta.loc[idx, "address"] = "東通村砂小又砂子又沢内"

    idx = meta.index[meta["code"] == 2110430]
    meta.loc[idx, "address"] = "大槌町新町大槌町上町大槌町小槌（修）"
    idx = meta.index[meta["code"] == 2110431]
    meta.loc[idx, "address"] = "大槌町新町大槌町上町大槌町小槌（修２）"
    idx = meta.index[meta["code"] == 2110432]
    meta.loc[idx, "address"] = "大槌町新町大槌町上町大槌町小槌"

    idx = meta.index[meta["code"] == 2121630]
    meta.loc[idx, "address"] = "紫波町日詰紫波町紫波中央駅前（修）"
    idx = meta.index[meta["code"] == 2121631]
    meta.loc[idx, "address"] = "紫波町日詰紫波町紫波中央駅前"

    idx = meta.index[meta["code"] == 2130160]
    meta.loc[idx, "address"] = "大迫町役場花巻市大迫総合支所（修）"
    idx = meta.index[meta["code"] == 2130131]
    meta.loc[idx, "address"] = "大迫町役場花巻市大迫総合支所"

    idx = meta.index[meta["code"] == 2130220]
    meta.loc[idx, "address"] = "北上市二子町北上市相去町（修）"
    idx = meta.index[meta["code"] == 2130221]
    meta.loc[idx, "address"] = "北上市二子町北上市相去町"

    idx = meta.index[meta["code"] == 2130320]
    meta.loc[idx, "address"] = "遠野市松崎町青笹町（修）"
    idx = meta.index[meta["code"] == 2130321]
    meta.loc[idx, "address"] = "遠野市松崎町青笹町"

    idx = meta.index[meta["code"] == 2130420]
    meta.loc[idx, "address"] = "一関市山目一関市竹山町（修）"
    idx = meta.index[meta["code"] == 2130421]
    meta.loc[idx, "address"] = "一関市山目一関市竹山町"

    idx = meta.index[meta["code"] == 2132732]
    meta.loc[idx, "address"] = "奥州市丹沢区奥州市丹沢（修）"
    idx = meta.index[meta["code"] == 2132735]
    meta.loc[idx, "address"] = "奥州市丹沢区奥州市丹沢"

    idx = meta.index[meta["code"] == 2132733]
    meta.loc[idx, "address"] = "奥州市衣川区奥州市衣川（修）"
    idx = meta.index[meta["code"] == 2132734]
    meta.loc[idx, "address"] = "奥州市衣川区奥州市衣川（修２）"
    idx = meta.index[meta["code"] == 2132736]
    meta.loc[idx, "address"] = "奥州市衣川区奥州市衣川"

    idx = meta.index[meta["code"] == 2205360]
    meta.loc[idx, "address"] = "南方町八の森登米市南方町（修）"
    idx = meta.index[meta["code"] == 2205334]
    meta.loc[idx, "address"] = "南方町八の森登米市南方町"

    idx = meta.index[meta["code"] == 2205520]
    meta.loc[idx, "address"] = "南三陸町歌津（修）"
    idx = meta.index[meta["code"] == 2205511]
    meta.loc[idx, "address"] = "南三陸町歌津（修２）"
    idx = meta.index[meta["code"] == 2205521]
    meta.loc[idx, "address"] = "南三陸町歌津"

    idx = meta.index[meta["code"] == 2205721]
    meta.loc[idx, "address"] = "大崎市古川北町大崎市古川旭（修）"
    idx = meta.index[meta["code"] == 2205724]
    meta.loc[idx, "address"] = "大崎市古川北町大崎市古川旭"

    idx = meta.index[meta["code"] == 2205720]
    meta.loc[idx, "address"] = "大崎市鳴子大崎市鳴子臨時（修）"
    idx = meta.index[meta["code"] == 2205710]
    meta.loc[idx, "address"] = "大崎市鳴子大崎市鳴子臨時（修２）"
    idx = meta.index[meta["code"] == 2205722]
    meta.loc[idx, "address"] = "大崎市鳴子大崎市鳴子臨時（修３）"
    idx = meta.index[meta["code"] == 2205723]
    meta.loc[idx, "address"] = "大崎市鳴子大崎市鳴子臨時"

    idx = meta.index[meta["code"] == 2205760]
    meta.loc[idx, "address"] = "鹿島台町平渡大崎市鹿島台（修）"
    idx = meta.index[meta["code"] == 2205770]
    meta.loc[idx, "address"] = "鹿島台町平渡大崎市鹿島台（修２）"
    idx = meta.index[meta["code"] == 2205761]
    meta.loc[idx, "address"] = "鹿島台町平渡大崎市鹿島台（修３）"
    idx = meta.index[meta["code"] == 2205732]
    meta.loc[idx, "address"] = "鹿島台町平渡大崎市鹿島台"

    idx = meta.index[meta["code"] == 2211830]
    meta.loc[idx, "address"] = "亘理町下小路悠里（修）"
    idx = meta.index[meta["code"] == 2211831]
    meta.loc[idx, "address"] = "亘理町下小路悠里"

    idx = meta.index[meta["code"] == 2220620]
    meta.loc[idx, "address"] = "塩竈市旭町塩竈市今宮町（修）"
    idx = meta.index[meta["code"] == 2220621]
    meta.loc[idx, "address"] = "塩竈市旭町塩竈市今宮町"

    idx = meta.index[meta["code"] == 2220860]
    meta.loc[idx, "address"] = "鳴瀬町小野東松島市小野（修）"
    idx = meta.index[meta["code"] == 2220831]
    meta.loc[idx, "address"] = "鳴瀬町小野東松島市小野"

    idx = meta.index[meta["code"] == 2220900]
    meta.loc[idx, "address"] = "松島町松島松島町高城（修）"
    idx = meta.index[meta["code"] == 2220910]
    meta.loc[idx, "address"] = "松島町松島松島町高城（修２）"
    idx = meta.index[meta["code"] == 2220901]
    meta.loc[idx, "address"] = "松島町松島松島町高城"

    idx = meta.index[meta["code"] == 2221632]
    meta.loc[idx, "address"] = "女川町女川浜（修３）"
    idx = meta.index[meta["code"] == 2221633]
    meta.loc[idx, "address"] = "女川町女川浜（修４）"
    idx = meta.index[meta["code"] == 2221634]
    meta.loc[idx, "address"] = "女川町女川浜"

    idx = meta.index[meta["code"] == 2221760]
    meta.loc[idx, "address"] = "富谷長富谷富谷市富谷（修）"
    idx = meta.index[meta["code"] == 2221730]
    meta.loc[idx, "address"] = "富谷長富谷富谷市富谷"

    idx = meta.index[meta["code"] == 2300160]
    meta.loc[idx, "address"] = "若美町角間崎男鹿市角間崎（修）"
    idx = meta.index[meta["code"] == 2300131]
    meta.loc[idx, "address"] = "若美町角間崎男鹿市角間崎（修２）"
    idx = meta.index[meta["code"] == 2300133]
    meta.loc[idx, "address"] = "若美町角間崎男鹿市角間崎"

    idx = meta.index[meta["code"] == 2301831]
    meta.loc[idx, "address"] = "三種町豊岡三種町森岳（修）"
    idx = meta.index[meta["code"] == 2301833]
    meta.loc[idx, "address"] = "三種町豊岡三種町森岳（修２）"
    idx = meta.index[meta["code"] == 2301835]
    meta.loc[idx, "address"] = "三種町豊岡三種町森岳"

    idx = meta.index[meta["code"] == 2301930]
    meta.loc[idx, "address"] = "八峰町八森中浜八峰町峰浜目名潟（修）"
    idx = meta.index[meta["code"] == 2301932]
    meta.loc[idx, "address"] = "八峰町八森中浜八峰町峰浜目名潟"

    idx = meta.index[meta["code"] == 2310032]
    meta.loc[idx, "address"] = "秋田市雄和妙法雄和新波（修）"
    idx = meta.index[meta["code"] == 2310033]
    meta.loc[idx, "address"] = "秋田市雄和妙法雄和新波（修２）"
    idx = meta.index[meta["code"] == 2310034]
    meta.loc[idx, "address"] = "秋田市雄和妙法雄和新波"

    idx = meta.index[meta["code"] == 2311360]
    meta.loc[idx, "address"] = "西目町沼田由利本荘市西目町沼田（修）"
    idx = meta.index[meta["code"] == 2311334]
    meta.loc[idx, "address"] = "西目町沼田由利本荘市西目町沼田"

    idx = meta.index[meta["code"] == 2311361]
    meta.loc[idx, "address"] = "東由利町老方由利本荘市東由利老方（修）"
    idx = meta.index[meta["code"] == 2311335]
    meta.loc[idx, "address"] = "東由利町老方由利本荘市東由利老方"

    idx = meta.index[meta["code"] == 2320230]
    meta.loc[idx, "address"] = "小坂町小坂鉱山小坂谷地（修）"
    idx = meta.index[meta["code"] == 2320231]
    meta.loc[idx, "address"] = "小坂町小坂鉱山小坂谷地"

    idx = meta.index[meta["code"] == 2333100]
    meta.loc[idx, "address"] = "仙北市角館町東勝楽丁仙北市各館町中菅沢（修）"
    idx = meta.index[meta["code"] == 2333101]
    meta.loc[idx, "address"] = "仙北市角館町東勝楽丁仙北市各館町中菅沢"

    idx = meta.index[meta["code"] == 2400100]
    meta.loc[idx, "address"] = "酒田市亀ヶ崎（修）"
    idx = meta.index[meta["code"] == 2400102]
    meta.loc[idx, "address"] = "酒田市亀ヶ崎"

    idx = meta.index[meta["code"] == 2410030]
    meta.loc[idx, "address"] = "新庄市沖の町住吉町（修）"
    idx = meta.index[meta["code"] == 2410031]
    meta.loc[idx, "address"] = "新庄市沖の町住吉町"

    idx = meta.index[meta["code"] == 2420630]
    meta.loc[idx, "address"] = "山辺町山辺緑ヶ丘（修）"
    idx = meta.index[meta["code"] == 2420631]
    meta.loc[idx, "address"] = "山辺町山辺緑ヶ丘（修２）"
    idx = meta.index[meta["code"] == 2420632]
    meta.loc[idx, "address"] = "山辺町山辺緑ヶ丘"

    idx = meta.index[meta["code"] == 2420730]
    meta.loc[idx, "address"] = "山形中山町長崎中山町長崎（修）"
    idx = meta.index[meta["code"] == 2420731]
    meta.loc[idx, "address"] = "山形中山町長崎中山町長崎"

    idx = meta.index[meta["code"] == 2430130]
    meta.loc[idx, "address"] = "長井市ままの上長井市本町（修）"
    idx = meta.index[meta["code"] == 2430131]
    meta.loc[idx, "address"] = "長井市ままの上長井市本町（修２）"
    idx = meta.index[meta["code"] == 2430132]
    meta.loc[idx, "address"] = "長井市ままの上長井市本町"

    idx = meta.index[meta["code"] == 2500330]
    meta.loc[idx, "address"] = "須賀川市八幡町須賀川市牛袋町（修）"
    idx = meta.index[meta["code"] == 2500333]
    meta.loc[idx, "address"] = "須賀川市八幡町須賀川市牛袋町（修２）"
    idx = meta.index[meta["code"] == 2500336]
    meta.loc[idx, "address"] = "須賀川市八幡町須賀川市牛袋町（修３）"
    idx = meta.index[meta["code"] == 2500337]
    meta.loc[idx, "address"] = "須賀川市八幡町須賀川市牛袋町"

    idx = meta.index[meta["code"] == 2500460]
    meta.loc[idx, "address"] = "安達町油井二本松市油井（修）"
    idx = meta.index[meta["code"] == 2500431]
    meta.loc[idx, "address"] = "安達町油井二本松市油井"

    idx = meta.index[meta["code"] == 2500530]
    meta.loc[idx, "address"] = "桑折町東大隅桑折町谷地（修）"
    idx = meta.index[meta["code"] == 2500531]
    meta.loc[idx, "address"] = "桑折町東大隅桑折町谷地"

    idx = meta.index[meta["code"] == 2501230]
    meta.loc[idx, "address"] = "川俣町五百田樋ノ口（修）"
    idx = meta.index[meta["code"] == 2501231]
    meta.loc[idx, "address"] = "川俣町五百田樋ノ口（修２）"
    idx = meta.index[meta["code"] == 2501232]
    meta.loc[idx, "address"] = "川俣町五百田樋ノ口"

    idx = meta.index[meta["code"] == 2501500]
    meta.loc[idx, "address"] = "大玉村曲藤大玉村南小屋（修）"
    idx = meta.index[meta["code"] == 2501501]
    meta.loc[idx, "address"] = "大玉村曲藤大玉村南小屋"

    idx = meta.index[meta["code"] == 2503220]
    meta.loc[idx, "address"] = "矢祭町東館下上野内矢祭村戸塚（修）"
    idx = meta.index[meta["code"] == 2503221]
    meta.loc[idx, "address"] = "矢祭町東館下上野内矢祭村戸塚"

    idx = meta.index[meta["code"] == 2503530]
    meta.loc[idx, "address"] = "石川町下泉石川町長久保（修）"
    idx = meta.index[meta["code"] == 2503531]
    meta.loc[idx, "address"] = "石川町下泉石川町長久保"

    idx = meta.index[meta["code"] == 2504760]
    meta.loc[idx, "address"] = "常葉町常葉田村市常葉町（修）"
    idx = meta.index[meta["code"] == 2504733]
    meta.loc[idx, "address"] = "常葉町常葉田村市常葉町"

    idx = meta.index[meta["code"] == 2504860]
    meta.loc[idx, "address"] = "保原町宮下福島伊達市保原（修）"
    idx = meta.index[meta["code"] == 2504832]
    meta.loc[idx, "address"] = "保原町宮下福島伊達市保原"

    idx = meta.index[meta["code"] == 2504931]
    meta.loc[idx, "address"] = "本宮市糠沢本宮市白岩（修）"
    idx = meta.index[meta["code"] == 2504932]
    meta.loc[idx, "address"] = "本宮市糠沢本宮市白岩"

    idx = meta.index[meta["code"] == 2510730]
    meta.loc[idx, "address"] = "大熊町下野上大熊町大川原（修）"
    idx = meta.index[meta["code"] == 2510731]
    meta.loc[idx, "address"] = "大熊町下野上大熊町大川原"

    idx = meta.index[meta["code"] == 2510830]
    meta.loc[idx, "address"] = "双葉町新山双葉町両竹（修）"
    idx = meta.index[meta["code"] == 2510831]
    meta.loc[idx, "address"] = "双葉町新山双葉町両竹（修２）"
    idx = meta.index[meta["code"] == 2510832]
    meta.loc[idx, "address"] = "双葉町新山双葉町両竹"

    idx = meta.index[meta["code"] == 2511531]
    meta.loc[idx, "address"] = "南相馬市鹿島区南相馬市鹿島区西町（修）"
    idx = meta.index[meta["code"] == 2511533]
    meta.loc[idx, "address"] = "南相馬市鹿島区南相馬市鹿島区西町"

    idx = meta.index[meta["code"] == 2521930]
    meta.loc[idx, "address"] = "湯川村笈川湯川村清水田（修）"
    idx = meta.index[meta["code"] == 2521931]
    meta.loc[idx, "address"] = "湯川村笈川湯川村清水田（修２）"
    idx = meta.index[meta["code"] == 2521932]
    meta.loc[idx, "address"] = "湯川村笈川湯川村清水田"

    idx = meta.index[meta["code"] == 3000330]
    meta.loc[idx, "address"] = "高萩市本町高萩市下手綱（修）"
    idx = meta.index[meta["code"] == 3000331]
    meta.loc[idx, "address"] = "高萩市本町高萩市下手綱（修２）"
    idx = meta.index[meta["code"] == 3000332]
    meta.loc[idx, "address"] = "高萩市本町高萩市下手綱"

    idx = meta.index[meta["code"] == 3001930]
    meta.loc[idx, "address"] = "東海村舟石川東海村東海（修）"
    idx = meta.index[meta["code"] == 3001931]
    meta.loc[idx, "address"] = "東海村舟石川東海村東海（修２）"
    idx = meta.index[meta["code"] == 3001932]
    meta.loc[idx, "address"] = "東海村舟石川東海村東海"

    idx = meta.index[meta["code"] == 3003120]
    meta.loc[idx, "address"] = "常陸大宮市上村田常陸大宮市北町（修）"
    idx = meta.index[meta["code"] == 3003121]
    meta.loc[idx, "address"] = "常陸大宮市上村田常陸大宮市北町"

    idx = meta.index[meta["code"] == 3003170]
    meta.loc[idx, "address"] = "茨城大宮町常陸大宮常陸大宮市中富町（修）"
    idx = meta.index[meta["code"] == 3003100]
    meta.loc[idx, "address"] = "茨城大宮町常陸大宮常陸大宮市中富町"

    idx = meta.index[meta["code"] == 3003332]
    meta.loc[idx, "address"] = "城里町徳蔵城里町小勝（修）"
    idx = meta.index[meta["code"] == 3003333]
    meta.loc[idx, "address"] = "城里町徳蔵城里町小勝（修２）"
    idx = meta.index[meta["code"] == 3003336]
    meta.loc[idx, "address"] = "城里町徳蔵城里町小勝"

    idx = meta.index[meta["code"] == 3010000]
    meta.loc[idx, "address"] = "土浦市大岩田土浦市常名（修）"
    idx = meta.index[meta["code"] == 3010001]
    meta.loc[idx, "address"] = "土浦市大岩田土浦市常名"

    idx = meta.index[meta["code"] == 3010030]
    meta.loc[idx, "address"] = "土浦市下高津土浦市田中（修）"
    idx = meta.index[meta["code"] == 3010032]
    meta.loc[idx, "address"] = "土浦市下高津土浦市田中"

    idx = meta.index[meta["code"] == 3010430]
    meta.loc[idx, "address"] = "結城市悠樹結城市中央町（修）"
    idx = meta.index[meta["code"] == 3010431]
    meta.loc[idx, "address"] = "結城市悠樹結城市中央町"

    idx = meta.index[meta["code"] == 3010530]
    meta.loc[idx, "address"] = "龍ケ崎市寺後龍ケ崎市役所（修）"
    idx = meta.index[meta["code"] == 3010531]
    meta.loc[idx, "address"] = "龍ケ崎市寺後龍ケ崎市役所"

    idx = meta.index[meta["code"] == 3011130]
    meta.loc[idx, "address"] = "つくば市谷田部つくば市研究学園（修）"
    idx = meta.index[meta["code"] == 3011132]
    meta.loc[idx, "address"] = "つくば市谷田部つくば市研究学園"

    idx = meta.index[meta["code"] == 3014330]
    meta.loc[idx, "address"] = "茨城八千代町菅谷八千代町菅谷（修）"
    idx = meta.index[meta["code"] == 3014331]
    meta.loc[idx, "address"] = "茨城八千代町菅谷八千代町菅谷"

    idx = meta.index[meta["code"] == 3015030]
    meta.loc[idx, "address"] = "茨城境町役場茨城旭町（修）"
    idx = meta.index[meta["code"] == 3015031]
    meta.loc[idx, "address"] = "茨城境町役場茨城旭町"

    idx = meta.index[meta["code"] == 3015531]
    meta.loc[idx, "address"] = "稲敷町柴崎稲敷町伊佐津（修）"
    idx = meta.index[meta["code"] == 3015535]
    meta.loc[idx, "address"] = "稲敷町柴崎稲敷町伊佐津"

    idx = meta.index[meta["code"] == 3015630]
    meta.loc[idx, "address"] = "筑西市下中山筑西市二木成（修）"
    idx = meta.index[meta["code"] == 3015635]
    meta.loc[idx, "address"] = "筑西市下中山筑西市二木成"

    idx = meta.index[meta["code"] == 3100030]
    meta.loc[idx, "address"] = "日光市中鉢石町日光市御幸町（修）"
    idx = meta.index[meta["code"] == 3100037]
    meta.loc[idx, "address"] = "日光市中鉢石町日光市御幸町"

    idx = meta.index[meta["code"] == 3100032]
    meta.loc[idx, "address"] = "日光市足尾町松原日光市足尾長通洞（修）"
    idx = meta.index[meta["code"] == 3100035]
    meta.loc[idx, "address"] = "日光市足尾町松原日光市足尾長通洞"

    idx = meta.index[meta["code"] == 3100033]
    meta.loc[idx, "address"] = "日光市日蔭日光市黒部（修）"
    idx = meta.index[meta["code"] == 3100038]
    meta.loc[idx, "address"] = "日光市日蔭日光市黒部"

    idx = meta.index[meta["code"] == 3100034]
    meta.loc[idx, "address"] = "日光市藤原日光市藤原庁舎（修）"
    idx = meta.index[meta["code"] == 3100036]
    meta.loc[idx, "address"] = "日光市藤原日光市藤原庁舎"

    idx = meta.index[meta["code"] == 3100070]
    meta.loc[idx, "address"] = "今市市瀬川日光市瀬川（修）"
    idx = meta.index[meta["code"] == 3100001]
    meta.loc[idx, "address"] = "今市市瀬川日光市瀬川"

    idx = meta.index[meta["code"] == 3100260]
    meta.loc[idx, "address"] = "湯津上村佐良土大田原市湯津上（修）"
    idx = meta.index[meta["code"] == 3100231]
    meta.loc[idx, "address"] = "湯津上村佐良土大田原市湯津上"

    idx = meta.index[meta["code"] == 3101432]
    meta.loc[idx, "address"] = "那須塩原市塩原那須塩原市塩原庁舎（修）"
    idx = meta.index[meta["code"] == 3101433]
    meta.loc[idx, "address"] = "那須塩原市塩原那須塩原市塩原庁舎"

    idx = meta.index[meta["code"] == 3110032]
    meta.loc[idx, "address"] = "宇都宮市白沢町宇都宮市中岡本町（修）"
    idx = meta.index[meta["code"] == 3110033]
    meta.loc[idx, "address"] = "宇都宮市白沢町宇都宮市中岡本町"

    idx = meta.index[meta["code"] == 3110230]
    meta.loc[idx, "address"] = "栃木市入舟町栃木市万町（修）"
    idx = meta.index[meta["code"] == 3110235]
    meta.loc[idx, "address"] = "栃木市入舟町栃木市万町"

    idx = meta.index[meta["code"] == 3110330]
    meta.loc[idx, "address"] = "佐野市高砂町佐野市亀井町（修）"
    idx = meta.index[meta["code"] == 3110333]
    meta.loc[idx, "address"] = "佐野市高砂町佐野市亀井町（修２）"
    idx = meta.index[meta["code"] == 3110335]
    meta.loc[idx, "address"] = "佐野市高砂町佐野市亀井町"

    idx = meta.index[meta["code"] == 3111520]
    meta.loc[idx, "address"] = "茂木町小井戸茂木町北高岡天矢場（修）"
    idx = meta.index[meta["code"] == 3111521]
    meta.loc[idx, "address"] = "茂木町小井戸茂木町北高岡天矢場"

    idx = meta.index[meta["code"] == 3113600]
    meta.loc[idx, "address"] = "那須烏山市中央那須烏山市神長（修）"
    idx = meta.index[meta["code"] == 3113601]
    meta.loc[idx, "address"] = "那須烏山市中央那須烏山市神長"

    idx = meta.index[meta["code"] == 3113831]
    meta.loc[idx, "address"] = "下野市石橋下野市大松山（修）"
    idx = meta.index[meta["code"] == 3113835]
    meta.loc[idx, "address"] = "下野市石橋下野市大松山"

    idx = meta.index[meta["code"] == 3113832]
    meta.loc[idx, "address"] = "下野市小金井下野市笹原（修）"
    idx = meta.index[meta["code"] == 3113834]
    meta.loc[idx, "address"] = "下野市小金井下野市笹原"

    idx = meta.index[meta["code"] == 3200000]
    meta.loc[idx, "address"] = "沼田市西倉内町沼田市東原新町（修）"
    idx = meta.index[meta["code"] == 3200010]
    meta.loc[idx, "address"] = "沼田市西倉内町沼田市東原新町（修２）"
    idx = meta.index[meta["code"] == 3200001]
    meta.loc[idx, "address"] = "沼田市西倉内町沼田市東原新町"

    idx = meta.index[meta["code"] == 3200131]
    meta.loc[idx, "address"] = "中之条町小雨中之条町入山（修）"
    idx = meta.index[meta["code"] == 3200132]
    meta.loc[idx, "address"] = "中之条町小雨中之条町入山"

    idx = meta.index[meta["code"] == 3201360]
    meta.loc[idx, "address"] = "吾妻郡東村五町田東吾妻町奥田（修）"
    idx = meta.index[meta["code"] == 3201330]
    meta.loc[idx, "address"] = "吾妻郡東村五町田東吾妻町奥田（修２）"
    idx = meta.index[meta["code"] == 3201331]
    meta.loc[idx, "address"] = "吾妻郡東村五町田東吾妻町奥田"

    idx = meta.index[meta["code"] == 3210160]
    meta.loc[idx, "address"] = "群馬吉井町吉井高崎市吉井町吉井川（修）"
    idx = meta.index[meta["code"] == 3210136]
    meta.loc[idx, "address"] = "群馬吉井町吉井高崎市吉井町吉井川"

    idx = meta.index[meta["code"] == 3210520]
    meta.loc[idx, "address"] = "館林市美園町館林市上三林町（修）"
    idx = meta.index[meta["code"] == 3210521]
    meta.loc[idx, "address"] = "館林市美園町館林市上三林町"

    idx = meta.index[meta["code"] == 3210620]
    meta.loc[idx, "address"] = "渋川市八木原渋川市有馬（修）"
    idx = meta.index[meta["code"] == 3210621]
    meta.loc[idx, "address"] = "渋川市八木原渋川市有馬"

    idx = meta.index[meta["code"] == 3210660]
    meta.loc[idx, "address"] = "北橘村真壁渋川市北橘町（修）"
    idx = meta.index[meta["code"] == 3210631]
    meta.loc[idx, "address"] = "北橘村真壁渋川市北橘町"

    idx = meta.index[meta["code"] == 3212630]
    meta.loc[idx, "address"] = "榛東村山子田榛東村村井（修）"
    idx = meta.index[meta["code"] == 3212631]
    meta.loc[idx, "address"] = "榛東村山子田榛東村村井"

    idx = meta.index[meta["code"] == 3213230]
    meta.loc[idx, "address"] = "神流町神ケ原（修）"
    idx = meta.index[meta["code"] == 3213231]
    meta.loc[idx, "address"] = "神流町神ケ原"

    idx = meta.index[meta["code"] == 3300731]
    meta.loc[idx, "address"] = "深谷市岡部深谷市普済寺（修）"
    idx = meta.index[meta["code"] == 3300735]
    meta.loc[idx, "address"] = "深谷市岡部深谷市普済寺"

    idx = meta.index[meta["code"] == 3302031]
    meta.loc[idx, "address"] = "神川町下阿久原埼玉神川町下阿久原（修）"
    idx = meta.index[meta["code"] == 3302032]
    meta.loc[idx, "address"] = "神川町下阿久原埼玉神川町下阿久原"

    idx = meta.index[meta["code"] == 3310130]
    meta.loc[idx, "address"] = "川口市青木川口市安行領家（修）"
    idx = meta.index[meta["code"] == 3310132]
    meta.loc[idx, "address"] = "川口市青木川口市安行領家"

    idx = meta.index[meta["code"] == 3310500]
    meta.loc[idx, "address"] = "飯能市苅生飯能市下直竹（修）"
    idx = meta.index[meta["code"] == 3310501]
    meta.loc[idx, "address"] = "飯能市苅生飯能市下直竹"

    idx = meta.index[meta["code"] == 3310720]
    meta.loc[idx, "address"] = "春日部市中央春日部市粕壁（修）"
    idx = meta.index[meta["code"] == 3310721]
    meta.loc[idx, "address"] = "春日部市中央春日部市粕壁"

    idx = meta.index[meta["code"] == 3311130]
    meta.loc[idx, "address"] = "草加市高砂草加市中央（修）"
    idx = meta.index[meta["code"] == 3311131]
    meta.loc[idx, "address"] = "草加市高砂草加市中央"

    idx = meta.index[meta["code"] == 3311830]
    meta.loc[idx, "address"] = "志木市中宗岡志木市本町（修）"
    idx = meta.index[meta["code"] == 3311831]
    meta.loc[idx, "address"] = "志木市中宗岡志木市本町"

    idx = meta.index[meta["code"] == 3312130]
    meta.loc[idx, "address"] = "桶川市泉桶川市上日出谷（修）"
    idx = meta.index[meta["code"] == 3312131]
    meta.loc[idx, "address"] = "桶川市泉桶川市上日出谷（修２）"
    idx = meta.index[meta["code"] == 3312132]
    meta.loc[idx, "address"] = "桶川市泉桶川市上日出谷"

    idx = meta.index[meta["code"] == 3312630]
    meta.loc[idx, "address"] = "三郷市幸房三郷市中央（修）"
    idx = meta.index[meta["code"] == 3312631]
    meta.loc[idx, "address"] = "三郷市幸房三郷市中央"

    idx = meta.index[meta["code"] == 3313230]
    meta.loc[idx, "address"] = "吉川市吉川吉川市きよみ野（修）"
    idx = meta.index[meta["code"] == 3313231]
    meta.loc[idx, "address"] = "吉川市吉川吉川市きよみ野"

    idx = meta.index[meta["code"] == 3313930]
    meta.loc[idx, "address"] = "川島町平沼川島町下八林（修）"
    idx = meta.index[meta["code"] == 3313931]
    meta.loc[idx, "address"] = "川島町平沼川島町下八林"

    idx = meta.index[meta["code"] == 3314030]
    meta.loc[idx, "address"] = "宮代町中央宮代町笠原（修）"
    idx = meta.index[meta["code"] == 3314031]
    meta.loc[idx, "address"] = "宮代町中央宮代町笠原"

    idx = meta.index[meta["code"] == 3315430]
    meta.loc[idx, "address"] = "さいたま岩槻区本町さいたま岩槻区本丸（修）"
    idx = meta.index[meta["code"] == 3315431]
    meta.loc[idx, "address"] = "さいたま岩槻区本町さいたま岩槻区本丸"

    idx = meta.index[meta["code"] == 3315531]
    meta.loc[idx, "address"] = "ふじみ野市大井中央ふじみ野市大井（修）"
    idx = meta.index[meta["code"] == 3315532]
    meta.loc[idx, "address"] = "ふじみ野市大井中央ふじみ野市大井"

    idx = meta.index[meta["code"] == 3320000]
    meta.loc[idx, "address"] = "秩父市近戸町秩父市上町（修）"
    idx = meta.index[meta["code"] == 3320001]
    meta.loc[idx, "address"] = "秩父市近戸町秩父市上町"

    idx = meta.index[meta["code"] == 3403531]
    meta.loc[idx, "address"] = "横芝光町横芝横芝光町栗山（修）"
    idx = meta.index[meta["code"] == 3403532]
    meta.loc[idx, "address"] = "横芝光町横芝横芝光町栗山"

    idx = meta.index[meta["code"] == 3400001]
    meta.loc[idx, "address"] = "銚子市天王台銚子市小畑新町（修）"
    idx = meta.index[meta["code"] == 3400002]
    meta.loc[idx, "address"] = "銚子市天王台銚子市小畑新町"

    idx = meta.index[meta["code"] == 3403100]
    meta.loc[idx, "address"] = "長柄町大津倉長柄町総合グラウンド（修）"
    idx = meta.index[meta["code"] == 3403200]
    meta.loc[idx, "address"] = "長柄町大津倉長柄町総合グラウンド"

    idx = meta.index[meta["code"] == 3403400]
    meta.loc[idx, "address"] = "香取市佐原下川岸香取市佐原八日市場香取市佐原平田（修）"
    idx = meta.index[meta["code"] == 3403401]
    meta.loc[idx, "address"] = "香取市佐原下川岸香取市佐原八日市場香取市佐原平田（修２）"
    idx = meta.index[meta["code"] == 3403402]
    meta.loc[idx, "address"] = "香取市佐原下川岸香取市佐原八日市場香取市佐原平田"

    idx = meta.index[meta["code"] == 3403633]
    meta.loc[idx, "address"] = "山武市松尾町松尾山武市松尾町五反田（修）"
    idx = meta.index[meta["code"] == 3403637]
    meta.loc[idx, "address"] = "山武市松尾町松尾山武市松尾町五反田"

    idx = meta.index[meta["code"] == 3410630]
    meta.loc[idx, "address"] = "市川市八幡市川市南八幡（修）"
    idx = meta.index[meta["code"] == 3410631]
    meta.loc[idx, "address"] = "市川市八幡市川市南八幡（修２）"
    idx = meta.index[meta["code"] == 3410632]
    meta.loc[idx, "address"] = "市川市八幡市川市南八幡"

    # idx = meta.index[meta["code"] == 3411000]
    # meta.loc[idx, "address"] = "成田市花崎町成田市名古屋（修）"
    # idx = meta.index[meta["code"] == 3411002]
    # meta.loc[idx, "address"] = "成田市花崎町成田市名古屋"

    idx = meta.index[meta["code"] == 3411300]
    meta.loc[idx, "address"] = "柏市千代田柏市旭町（修）"
    idx = meta.index[meta["code"] == 3411301]
    meta.loc[idx, "address"] = "柏市千代田柏市旭町"

    idx = meta.index[meta["code"] == 3413030]
    meta.loc[idx, "address"] = "千葉栄町安食台栄町安食台（修）"
    idx = meta.index[meta["code"] == 3413031]
    meta.loc[idx, "address"] = "千葉栄町安食台栄町安食台"

    idx = meta.index[meta["code"] == 3420100]
    meta.loc[idx, "address"] = "木更津市塩見木更津市太田（修）"
    idx = meta.index[meta["code"] == 3420101]
    meta.loc[idx, "address"] = "木更津市塩見木更津市太田"

    idx = meta.index[meta["code"] == 3420130]
    meta.loc[idx, "address"] = "木更津市役所木更津市富士見（修）"
    idx = meta.index[meta["code"] == 3420131]
    meta.loc[idx, "address"] = "木更津市役所木更津市富士見"

    idx = meta.index[meta["code"] == 3422236]
    meta.loc[idx, "address"] = "南房総市和田町仁我浦和田町上三原和田町（修）"
    idx = meta.index[meta["code"] == 3422237]
    meta.loc[idx, "address"] = "南房総市和田町仁我浦和田町上三原和田町（修２）"
    idx = meta.index[meta["code"] == 3422239]
    meta.loc[idx, "address"] = "南房総市和田町仁我浦和田町上三原和田町"

    idx = meta.index[meta["code"] == 3500032]
    meta.loc[idx, "address"] = "東京千代田区九段南東京千代田区富士見（修）"
    idx = meta.index[meta["code"] == 3500033]
    meta.loc[idx, "address"] = "東京千代田区九段南東京千代田区富士見（修２）"
    idx = meta.index[meta["code"] == 3500034]
    meta.loc[idx, "address"] = "東京千代田区九段南東京千代田区富士見"

    idx = meta.index[meta["code"] == 3500350]
    meta.loc[idx, "address"] = "東京新宿区北新宿百人町（修）"
    idx = meta.index[meta["code"] == 3500351]
    meta.loc[idx, "address"] = "東京新宿区北新宿百人町"

    idx = meta.index[meta["code"] == 3500751]
    meta.loc[idx, "address"] = "東京江東区枝川江東区塩浜（修）"
    idx = meta.index[meta["code"] == 3500753]
    meta.loc[idx, "address"] = "東京江東区枝川江東区塩浜（修２）"
    idx = meta.index[meta["code"] == 3500754]
    meta.loc[idx, "address"] = "東京江東区枝川江東区塩浜"

    idx = meta.index[meta["code"] == 3501530]
    meta.loc[idx, "address"] = "東京豊島区東池袋（修）"
    idx = meta.index[meta["code"] == 3501531]
    meta.loc[idx, "address"] = "東京豊島区東池袋"

    idx = meta.index[meta["code"] == 3501651]
    meta.loc[idx, "address"] = "東京北区赤羽南北区神谷（修）"
    idx = meta.index[meta["code"] == 3501652]
    meta.loc[idx, "address"] = "東京北区赤羽南北区神谷（修２）"
    idx = meta.index[meta["code"] == 3501653]
    meta.loc[idx, "address"] = "東京北区赤羽南北区神谷"

    idx = meta.index[meta["code"] == 3502050]
    meta.loc[idx, "address"] = "東京足立区千住足立区千住中居町（修）"
    idx = meta.index[meta["code"] == 3502053]
    meta.loc[idx, "address"] = "東京足立区千住足立区千住中居町"

    idx = meta.index[meta["code"] == 3510250]
    meta.loc[idx, "address"] = "武蔵野市吉祥寺東町吉祥寺南町（修）"
    idx = meta.index[meta["code"] == 3510251]
    meta.loc[idx, "address"] = "武蔵野市吉祥寺東町吉祥寺南町（修２）"
    idx = meta.index[meta["code"] == 3510252]
    meta.loc[idx, "address"] = "武蔵野市吉祥寺東町吉祥寺南町"

    idx = meta.index[meta["code"] == 3510430]
    meta.loc[idx, "address"] = "東京府中市本町府中市寿町（修）"
    idx = meta.index[meta["code"] == 3510431]
    meta.loc[idx, "address"] = "東京府中市本町府中市寿町"

    idx = meta.index[meta["code"] == 3510450]
    meta.loc[idx, "address"] = "東京府中市白糸台東京府中市朝日町（修）"
    idx = meta.index[meta["code"] == 3510451]
    meta.loc[idx, "address"] = "東京府中市白糸台東京府中市朝日町"

    idx = meta.index[meta["code"] == 3510730]
    meta.loc[idx, "address"] = "町田市役所町田市森野（修）"
    idx = meta.index[meta["code"] == 3510731]
    meta.loc[idx, "address"] = "町田市役所町田市森野（修２）"
    idx = meta.index[meta["code"] == 3510732]
    meta.loc[idx, "address"] = "町田市役所町田市森野"

    idx = meta.index[meta["code"] == 3510750]
    meta.loc[idx, "address"] = "町田市中町町田市本町田（修）"
    idx = meta.index[meta["code"] == 3510751]
    meta.loc[idx, "address"] = "町田市中町町田市本町田（修２）"
    idx = meta.index[meta["code"] == 3510752]
    meta.loc[idx, "address"] = "町田市中町町田市本町田"

    idx = meta.index[meta["code"] == 3511430]
    meta.loc[idx, "address"] = "西東京市南町西東京市中町（修）"
    idx = meta.index[meta["code"] == 3511440]
    meta.loc[idx, "address"] = "西東京市南町西東京市中町（修２）"
    idx = meta.index[meta["code"] == 3511441]
    meta.loc[idx, "address"] = "西東京市南町西東京市中町"

    idx = meta.index[meta["code"] == 3511650]
    meta.loc[idx, "address"] = "福生市福生福生市熊川（修）"
    idx = meta.index[meta["code"] == 3511651]
    meta.loc[idx, "address"] = "福生市福生福生市熊川"

    # idx = meta.index[meta["code"] == 3550001]
    # meta.loc[idx, "address"] = "伊豆大島町津倍付伊豆大島市差木地（修）"
    # idx = meta.index[meta["code"] == 3550002]
    # meta.loc[idx, "address"] = "伊豆大島町津倍付伊豆大島市差木地（修２）"
    # idx = meta.index[meta["code"] == 3550003]
    # meta.loc[idx, "address"] = "伊豆大島町津倍付伊豆大島市差木地"

    idx = meta.index[meta["code"] == 3550070]
    meta.loc[idx, "address"] = "伊豆大島支庁伊豆大島元町基地（修）"
    idx = meta.index[meta["code"] == 3550071]
    meta.loc[idx, "address"] = "伊豆大島支庁伊豆大島元町基地"

    idx = meta.index[meta["code"] == 3560010]
    meta.loc[idx, "address"] = "東京利島村東京利島村東山（修）"
    idx = meta.index[meta["code"] == 3560000]
    meta.loc[idx, "address"] = "東京利島村東京利島村東山"

    idx = meta.index[meta["code"] == 3560110]
    meta.loc[idx, "address"] = "新島村本村２新島村本村（修）"
    idx = meta.index[meta["code"] == 3560130]
    meta.loc[idx, "address"] = "新島村本村２新島村本村"

    idx = meta.index[meta["code"] == 3570010]
    meta.loc[idx, "address"] = "三宅村坪田（修）"
    # idx = meta.index[meta["code"] == 3570012]
    # meta.loc[idx, "address"] = "三宅村坪田三宅村役場臨時庁舎（修２）"
    idx = meta.index[meta["code"] == 3570004]
    meta.loc[idx, "address"] = "三宅村坪田"

    idx = meta.index[meta["code"] == 3570110]
    meta.loc[idx, "address"] = "御蔵島村御蔵島村西川（修）"
    idx = meta.index[meta["code"] == 3570100]
    meta.loc[idx, "address"] = "御蔵島村御蔵島村西川"

    idx = meta.index[meta["code"] == 3580000]
    meta.loc[idx, "address"] = "八丈町大賀郷八丈町大賀郷西見八丈町三根（修）"
    idx = meta.index[meta["code"] == 3580002]
    meta.loc[idx, "address"] = "八丈町大賀郷八丈町大賀郷西見八丈町三根（修）"
    idx = meta.index[meta["code"] == 3580004]
    meta.loc[idx, "address"] = "八丈町大賀郷八丈町大賀郷西見八丈町三根"

    idx = meta.index[meta["code"] == 3580071]
    meta.loc[idx, "address"] = "八丈町大賀郷２八丈町三根（修）"
    idx = meta.index[meta["code"] == 3580001]
    meta.loc[idx, "address"] = "八丈町大賀郷２八丈町三根（修２）"

    idx = meta.index[meta["code"] == 3580020]
    meta.loc[idx, "address"] = "八丈町大賀郷金土川八丈町富士グランド（修）"
    idx = meta.index[meta["code"] == 3580021]
    meta.loc[idx, "address"] = "八丈町大賀郷金土川八丈町富士グランド"

    idx = meta.index[meta["code"] == 3600040]
    meta.loc[idx, "address"] = "横浜鶴見区下末吉横浜鶴見区馬場（修）"
    idx = meta.index[meta["code"] == 3600042]
    meta.loc[idx, "address"] = "横浜鶴見区下末吉横浜鶴見区馬場"

    idx = meta.index[meta["code"] == 3600141]
    meta.loc[idx, "address"] = "横浜神奈川区白幡上町神奈川区広台大田町（修）"
    idx = meta.index[meta["code"] == 3600142]
    meta.loc[idx, "address"] = "横浜神奈川区白幡上町神奈川区広台大田町"

    idx = meta.index[meta["code"] == 3600440]
    meta.loc[idx, "address"] = "横浜南区別所横浜南区大岡（修）"
    idx = meta.index[meta["code"] == 3600442]
    meta.loc[idx, "address"] = "横浜南区別所横浜南区大岡"

    idx = meta.index[meta["code"] == 3601040]
    meta.loc[idx, "address"] = "横浜港南区丸山台東部横浜港南区野庭町（修）"
    idx = meta.index[meta["code"] == 3601042]
    meta.loc[idx, "address"] = "横浜港南区丸山台東部横浜港南区野庭町"

    idx = meta.index[meta["code"] == 3601240]
    meta.loc[idx, "address"] = "横浜緑区白山横浜緑区鴨居（修）"
    idx = meta.index[meta["code"] == 3601242]
    meta.loc[idx, "address"] = "横浜緑区白山横浜緑区鴨居"

    idx = meta.index[meta["code"] == 3601741]
    meta.loc[idx, "address"] = "横浜都筑区茅ヶ崎（修）"
    idx = meta.index[meta["code"] == 3601742]
    meta.loc[idx, "address"] = "横浜都筑区茅ヶ崎"

    idx = meta.index[meta["code"] == 3602843]
    meta.loc[idx, "address"] = "藤沢市辻堂東海岸藤沢市辻堂西海岸（修）"
    idx = meta.index[meta["code"] == 3602844]
    meta.loc[idx, "address"] = "藤沢市辻堂東海岸藤沢市辻堂西海岸"

    idx = meta.index[meta["code"] == 3603430]
    meta.loc[idx, "address"] = "座間市緑ヶ丘座間市相武台（修）"
    idx = meta.index[meta["code"] == 3603431]
    meta.loc[idx, "address"] = "座間市緑ヶ丘座間市相武台"

    idx = meta.index[meta["code"] == 3603530]
    meta.loc[idx, "address"] = "綾瀬市深谷綾瀬市深谷中（修）"
    idx = meta.index[meta["code"] == 3603531]
    meta.loc[idx, "address"] = "綾瀬市深谷綾瀬市深谷中"

    idx = meta.index[meta["code"] == 3603830]
    meta.loc[idx, "address"] = "大磯町東小磯大磯町月京（修）"
    idx = meta.index[meta["code"] == 3603831]
    meta.loc[idx, "address"] = "大磯町東小磯大磯町月京"

    idx = meta.index[meta["code"] == 3610430]
    meta.loc[idx, "address"] = "伊勢原市伊勢原伊勢原市下谷（修）"
    idx = meta.index[meta["code"] == 3610431]
    meta.loc[idx, "address"] = "伊勢原市伊勢原伊勢原市下谷（修２）"
    idx = meta.index[meta["code"] == 3610432]
    meta.loc[idx, "address"] = "伊勢原市伊勢原伊勢原市下谷"

    idx = meta.index[meta["code"] == 3611230]
    meta.loc[idx, "address"] = "真鶴町真鶴真鶴町岩（修）"
    idx = meta.index[meta["code"] == 3611231]
    meta.loc[idx, "address"] = "真鶴町真鶴真鶴町岩"

    idx = meta.index[meta["code"] == 3611300]
    meta.loc[idx, "address"] = "湯河原町宮上湯河原町中央（修）"
    idx = meta.index[meta["code"] == 3611301]
    meta.loc[idx, "address"] = "湯河原町宮上湯河原町中央"

    idx = meta.index[meta["code"] == 3611430]
    meta.loc[idx, "address"] = "神奈川愛川町角田愛川町角田（修）"
    idx = meta.index[meta["code"] == 3611431]
    meta.loc[idx, "address"] = "神奈川愛川町角田愛川町角田"

    idx = meta.index[meta["code"] == 3612040]
    meta.loc[idx, "address"] = "相模原市中央区水郷田名中央区田名（修）"
    idx = meta.index[meta["code"] == 3612042]
    meta.loc[idx, "address"] = "相模原市中央区水郷田名中央区田名（修２）"
    idx = meta.index[meta["code"] == 3612043]
    meta.loc[idx, "address"] = "相模原市中央区水郷田名中央区田名"

    idx = meta.index[meta["code"] == 3612240]
    meta.loc[idx, "address"] = "相模原緑区相原相模原緑区橋本（修）"
    idx = meta.index[meta["code"] == 3612241]
    meta.loc[idx, "address"] = "相模原緑区相原相模原緑区橋本"

    idx = meta.index[meta["code"] == 3700233]
    meta.loc[idx, "address"] = "上越市大島区上達大島区岡（修）"
    idx = meta.index[meta["code"] == 3700244]
    meta.loc[idx, "address"] = "上越市大島区上達大島区岡"

    idx = meta.index[meta["code"] == 3700260]
    meta.loc[idx, "address"] = "安塚町安塚上越市安塚区安塚（修）"
    idx = meta.index[meta["code"] == 3700231]
    meta.loc[idx, "address"] = "安塚町安塚上越市安塚区安塚"

    idx = meta.index[meta["code"] == 3700261]
    meta.loc[idx, "address"] = "新潟吉川町原之町上越市吉川町原之町（修）"
    idx = meta.index[meta["code"] == 3700238]
    meta.loc[idx, "address"] = "新潟吉川町原之町上越市吉川町原之町"

    idx = meta.index[meta["code"] == 3702270]
    meta.loc[idx, "address"] = "妙高市関川妙高市田口（修）"
    idx = meta.index[meta["code"] == 3702231]
    meta.loc[idx, "address"] = "妙高市関川妙高市田口（修２）"
    idx = meta.index[meta["code"] == 3702235]
    meta.loc[idx, "address"] = "妙高市関川妙高市田口"

    idx = meta.index[meta["code"] == 3710033]
    meta.loc[idx, "address"] = "長岡市古志竹沢長岡市山古志竹沢（修）"
    idx = meta.index[meta["code"] == 3710040]
    meta.loc[idx, "address"] = "長岡市古志竹沢長岡市山古志竹沢"

    idx = meta.index[meta["code"] == 3710035]
    meta.loc[idx, "address"] = "長岡市栃尾大町長岡市金町（修）"
    idx = meta.index[meta["code"] == 3710041]
    meta.loc[idx, "address"] = "長岡市栃尾大町長岡市金町"

    idx = meta.index[meta["code"] == 3710038]
    meta.loc[idx, "address"] = "長岡市寺泊上田町長岡市寺泊烏帽子平（修）"
    idx = meta.index[meta["code"] == 3710043]
    meta.loc[idx, "address"] = "長岡市寺泊上田町長岡市寺泊烏帽子平"

    idx = meta.index[meta["code"] == 3710130]
    meta.loc[idx, "address"] = "三条市興野三条市西裏館（修）"
    idx = meta.index[meta["code"] == 3710131]
    meta.loc[idx, "address"] = "三条市興野三条市西裏館"

    idx = meta.index[meta["code"] == 3710230]
    meta.loc[idx, "address"] = "柏崎市三和町柏崎市中央町柏崎市日石町（修）"
    idx = meta.index[meta["code"] == 3710231]
    meta.loc[idx, "address"] = "柏崎市三和町柏崎市中央町柏崎市日石町（修２）"
    idx = meta.index[meta["code"] == 3710235]
    meta.loc[idx, "address"] = "柏崎市三和町柏崎市中央町柏崎市日石町（修３）"
    idx = meta.index[meta["code"] == 3710237]
    meta.loc[idx, "address"] = "柏崎市三和町柏崎市中央町柏崎市日石町"

    idx = meta.index[meta["code"] == 3710320]
    meta.loc[idx, "address"] = "小千谷市土川小千谷市旭町（修）"
    idx = meta.index[meta["code"] == 3710321]
    meta.loc[idx, "address"] = "小千谷市土川小千谷市旭町"

    idx = meta.index[meta["code"] == 3710520]
    meta.loc[idx, "address"] = "十日市町高山十日市町下条（修）"
    idx = meta.index[meta["code"] == 3710521]
    meta.loc[idx, "address"] = "十日市町高山十日市町下条"

    idx = meta.index[meta["code"] == 3710530]
    meta.loc[idx, "address"] = "十日市町妻有町西十日市町千歳町（修）"
    idx = meta.index[meta["code"] == 3710531]
    meta.loc[idx, "address"] = "十日市町妻有町西十日市町千歳町"

    idx = meta.index[meta["code"] == 3713700]
    meta.loc[idx, "address"] = "魚沼市米沢魚沼市折立（修）"
    idx = meta.index[meta["code"] == 3713701]
    meta.loc[idx, "address"] = "魚沼市米沢魚沼市折立"

    idx = meta.index[meta["code"] == 3720130]
    meta.loc[idx, "address"] = "新発田市豊町新発田市中央町（修）"
    idx = meta.index[meta["code"] == 3720132]
    meta.loc[idx, "address"] = "新発田市豊町新発田市中央町（修２）"
    idx = meta.index[meta["code"] == 3720135]
    meta.loc[idx, "address"] = "新発田市豊町新発田市中央町"

    idx = meta.index[meta["code"] == 3720134]
    meta.loc[idx, "address"] = "新発田市稲荷岡新発田市真野原外（修）"
    idx = meta.index[meta["code"] == 3720136]
    meta.loc[idx, "address"] = "新発田市稲荷岡新発田市真野原外"

    idx = meta.index[meta["code"] == 3720330]
    meta.loc[idx, "address"] = "村上市田端町村上市三之町（修）"
    idx = meta.index[meta["code"] == 3720331]
    meta.loc[idx, "address"] = "村上市田端町村上市三之町"

    idx = meta.index[meta["code"] == 3720333]
    meta.loc[idx, "address"] = "村上市今宿村上市岩船駅前（修）"
    idx = meta.index[meta["code"] == 3720336]
    meta.loc[idx, "address"] = "村上市今宿村上市岩船駅前"

    idx = meta.index[meta["code"] == 3720430]
    meta.loc[idx, "address"] = "燕市秋葉町燕市白山町（修）"
    idx = meta.index[meta["code"] == 3720433]
    meta.loc[idx, "address"] = "燕市秋葉町燕市白山町（修２）"
    idx = meta.index[meta["code"] == 3720436]
    meta.loc[idx, "address"] = "燕市秋葉町燕市白山町"

    idx = meta.index[meta["code"] == 3720432]
    meta.loc[idx, "address"] = "燕市吉田日之出町燕市吉田西太田（修）"
    idx = meta.index[meta["code"] == 3720435]
    meta.loc[idx, "address"] = "燕市吉田日之出町燕市吉田西太田（修２）"
    idx = meta.index[meta["code"] == 3720438]
    meta.loc[idx, "address"] = "燕市吉田日之出町燕市吉田西太田"

    idx = meta.index[meta["code"] == 3724331]
    meta.loc[idx, "address"] = "阿賀野市保田阿賀野市かがやき（修）"
    idx = meta.index[meta["code"] == 3724334]
    meta.loc[idx, "address"] = "阿賀野市保田阿賀野市かがやき（修２）"
    idx = meta.index[meta["code"] == 3724336]
    meta.loc[idx, "address"] = "阿賀野市保田阿賀野市かがやき"

    idx = meta.index[meta["code"] == 3724460]
    meta.loc[idx, "address"] = "津川町津川阿賀野町津川（修）"
    idx = meta.index[meta["code"] == 3724430]
    meta.loc[idx, "address"] = "津川町津川阿賀野町津川（修２）"
    idx = meta.index[meta["code"] == 3724434]
    meta.loc[idx, "address"] = "津川町津川阿賀野町津川"

    idx = meta.index[meta["code"] == 3724630]
    meta.loc[idx, "address"] = "新潟北区葛塚新潟北区東栄町（修）"
    idx = meta.index[meta["code"] == 3724631]
    meta.loc[idx, "address"] = "新潟北区葛塚新潟北区東栄町"

    idx = meta.index[meta["code"] == 3724730]
    meta.loc[idx, "address"] = "新潟東区古川町新潟東区下木戸（修）"
    idx = meta.index[meta["code"] == 3724731]
    meta.loc[idx, "address"] = "新潟東区古川町新潟東区下木戸"

    idx = meta.index[meta["code"] == 3724800]
    meta.loc[idx, "address"] = "新潟中央区幸西新潟中央区美咲町（修）"
    idx = meta.index[meta["code"] == 3724801]
    meta.loc[idx, "address"] = "新潟中央区幸西新潟中央区美咲町"

    idx = meta.index[meta["code"] == 3724961]
    meta.loc[idx, "address"] = "新潟市船戸山新潟江南区泉町（修）"
    idx = meta.index[meta["code"] == 3724930]
    meta.loc[idx, "address"] = "新潟市船戸山新潟江南区泉町"

    idx = meta.index[meta["code"] == 3725162]
    meta.loc[idx, "address"] = "新潟市親和町新潟南区白根（修）"
    idx = meta.index[meta["code"] == 3725130]
    meta.loc[idx, "address"] = "新潟市親和町新潟南区白根"

    idx = meta.index[meta["code"] == 3725260]
    meta.loc[idx, "address"] = "新潟市大野町新潟西区寺尾上新潟西区寺尾東（修）"
    idx = meta.index[meta["code"] == 3725230]
    meta.loc[idx, "address"] = "新潟市大野町新潟西区寺尾上新潟西区寺尾東（修２）"
    idx = meta.index[meta["code"] == 3725231]
    meta.loc[idx, "address"] = "新潟市大野町新潟西区寺尾上新潟西区寺尾東"

    idx = meta.index[meta["code"] == 3751039]
    meta.loc[idx, "address"] = "佐渡市徳和佐渡市赤泊（修）"
    idx = meta.index[meta["code"] == 3751041]
    meta.loc[idx, "address"] = "佐渡市徳和佐渡市赤泊"

    idx = meta.index[meta["code"] == 3800330]
    meta.loc[idx, "address"] = "黒部市新天黒部市植木（修）"
    idx = meta.index[meta["code"] == 3800332]
    meta.loc[idx, "address"] = "黒部市新天黒部市植木"

    idx = meta.index[meta["code"] == 3810400]
    meta.loc[idx, "address"] = "小矢部市本町小矢部市泉町（修）"
    idx = meta.index[meta["code"] == 3810401]
    meta.loc[idx, "address"] = "小矢部市本町小矢部市泉町"

    idx = meta.index[meta["code"] == 3812300]
    meta.loc[idx, "address"] = "南砺市天神南砺市天池（修）"
    idx = meta.index[meta["code"] == 3812301]
    meta.loc[idx, "address"] = "南砺市天神南砺市天池"

    idx = meta.index[meta["code"] == 3812335]
    meta.loc[idx, "address"] = "南砺市蛇喰（修）"
    idx = meta.index[meta["code"] == 3812310]
    meta.loc[idx, "address"] = "南砺市蛇喰（修２）"
    idx = meta.index[meta["code"] == 3812337]
    meta.loc[idx, "address"] = "南砺市蛇喰"

    idx = meta.index[meta["code"] == 3812431]
    meta.loc[idx, "address"] = "射水市戸破射水市橋下条（修）"
    idx = meta.index[meta["code"] == 3812436]
    meta.loc[idx, "address"] = "射水市戸破射水市橋下条"

    idx = meta.index[meta["code"] == 3900030]
    meta.loc[idx, "address"] = "七尾市田鶴浜町七尾市垣吉町（修）"
    idx = meta.index[meta["code"] == 3900010]
    meta.loc[idx, "address"] = "七尾市田鶴浜町七尾市垣吉町（修２）"
    idx = meta.index[meta["code"] == 3900033]
    meta.loc[idx, "address"] = "七尾市田鶴浜町七尾市垣吉町（修３）"
    idx = meta.index[meta["code"] == 3900036]
    meta.loc[idx, "address"] = "七尾市田鶴浜町七尾市垣吉町"

    idx = meta.index[meta["code"] == 3901931]
    meta.loc[idx, "address"] = "宝達志水町小川宝達志水町今浜（修）"
    idx = meta.index[meta["code"] == 3901934]
    meta.loc[idx, "address"] = "宝達志水町小川宝達志水町今浜"

    idx = meta.index[meta["code"] == 3912130]
    meta.loc[idx, "address"] = "内灘町鶴ヶ丘内灘町大学（修）"
    idx = meta.index[meta["code"] == 3912131]
    meta.loc[idx, "address"] = "内灘町鶴ヶ丘内灘町大学"

    idx = meta.index[meta["code"] == 3912360]
    meta.loc[idx, "address"] = "松任市古城町白山市倉光（修）"
    idx = meta.index[meta["code"] == 3912330]
    meta.loc[idx, "address"] = "松任市古城町白山市倉光"

    idx = meta.index[meta["code"] == 3912361]
    meta.loc[idx, "address"] = "白峰村白峰白山市白峰（修）"
    idx = meta.index[meta["code"] == 3912321]
    meta.loc[idx, "address"] = "白峰村白峰白山市白峰"

    idx = meta.index[meta["code"] == 3912460]
    meta.loc[idx, "address"] = "辰口町倉重能美市来丸町（修）"
    idx = meta.index[meta["code"] == 3912432]
    meta.loc[idx, "address"] = "辰口町倉重能美市来丸町（修２）"
    idx = meta.index[meta["code"] == 3912435]
    meta.loc[idx, "address"] = "辰口町倉重能美市来丸町"

    idx = meta.index[meta["code"] == 3912560]
    meta.loc[idx, "address"] = "野々市町本町野々市市三納（修）"
    idx = meta.index[meta["code"] == 3912530]
    meta.loc[idx, "address"] = "野々市町本町野々市市三納"

    idx = meta.index[meta["code"] == 4000020]
    meta.loc[idx, "address"] = "福井市板垣福井市原目町（修）"
    idx = meta.index[meta["code"] == 4000022]
    meta.loc[idx, "address"] = "福井市板垣福井市原目町"

    idx = meta.index[meta["code"] == 4000220]
    meta.loc[idx, "address"] = "大野市川合大野市貝皿（修）"
    idx = meta.index[meta["code"] == 4000222]
    meta.loc[idx, "address"] = "大野市川合大野市貝皿"

    idx = meta.index[meta["code"] == 4000430]
    meta.loc[idx, "address"] = "鯖江市西山町鯖江市水落町（修）"
    idx = meta.index[meta["code"] == 4000431]
    meta.loc[idx, "address"] = "鯖江市西山町鯖江市水落町"

    idx = meta.index[meta["code"] == 4000732]
    meta.loc[idx, "address"] = "永平寺町栗住波永平寺町山王（修）"
    idx = meta.index[meta["code"] == 4000734]
    meta.loc[idx, "address"] = "永平寺町栗住波永平寺町山王"

    idx = meta.index[meta["code"] == 4110031]
    meta.loc[idx, "address"] = "甲府市下向山町甲府市下曽根町（修）"
    idx = meta.index[meta["code"] == 4110034]
    meta.loc[idx, "address"] = "甲府市下向山町甲府市下曽根町"

    idx = meta.index[meta["code"] == 4112430]
    meta.loc[idx, "address"] = "早川町高住早川町薬袋（修）"
    idx = meta.index[meta["code"] == 4112431]
    meta.loc[idx, "address"] = "早川町高住早川町薬袋"

    idx = meta.index[meta["code"] == 4113731]
    meta.loc[idx, "address"] = "南アルプス市野牛島南アルプス市榎原（修）"
    idx = meta.index[meta["code"] == 4113737]
    meta.loc[idx, "address"] = "南アルプス市野牛島南アルプス市榎原"

    idx = meta.index[meta["code"] == 4114930]
    meta.loc[idx, "address"] = "笛吹市御坂町栗合笛吹市御坂町夏目原（修）"
    idx = meta.index[meta["code"] == 4114936]
    meta.loc[idx, "address"] = "笛吹市御坂町栗合笛吹市御坂町夏目原"

    idx = meta.index[meta["code"] == 4115031]
    meta.loc[idx, "address"] = "山梨北杜市須玉支所山梨北杜市市役所（修）"
    idx = meta.index[meta["code"] == 4115041]
    meta.loc[idx, "address"] = "山梨北杜市須玉支所山梨北杜市市役所"

    idx = meta.index[meta["code"] == 4115060]
    meta.loc[idx, "address"] = "白洲町白須山梨北杜市白洲町（修）"
    idx = meta.index[meta["code"] == 4115035]
    meta.loc[idx, "address"] = "白洲町白須山梨北杜市白洲町（修２）"
    idx = meta.index[meta["code"] == 4115040]
    meta.loc[idx, "address"] = "白洲町白須山梨北杜市白洲町"

    idx = meta.index[meta["code"] == 4115120]
    meta.loc[idx, "address"] = "市川三郷町岩間市川山郷町六郷支所（修）"
    idx = meta.index[meta["code"] == 4115132]
    meta.loc[idx, "address"] = "市川三郷町岩間市川山郷町六郷支所"

    idx = meta.index[meta["code"] == 4115160]
    meta.loc[idx, "address"] = "市川大門町役場市川三郷町役場（修）"
    idx = meta.index[meta["code"] == 4115131]
    meta.loc[idx, "address"] = "市川大門町役場市川三郷町役場"

    idx = meta.index[meta["code"] == 4120300]
    meta.loc[idx, "address"] = "上野原市上野原上野原市四方津（修）"
    idx = meta.index[meta["code"] == 4120301]
    meta.loc[idx, "address"] = "上野原市上野原上野原市四方津"

    idx = meta.index[meta["code"] == 4120430]
    meta.loc[idx, "address"] = "道志村役場道志村釜之前（修）"
    idx = meta.index[meta["code"] == 4120431]
    meta.loc[idx, "address"] = "道志村役場道志村釜之前"

    idx = meta.index[meta["code"] == 4120960]
    meta.loc[idx, "address"] = "富士河口湖町湖南富士河口湖町役場（修）"
    idx = meta.index[meta["code"] == 4120932]
    meta.loc[idx, "address"] = "富士河口湖町湖南富士河口湖町役場"

    idx = meta.index[meta["code"] == 4121030]
    meta.loc[idx, "address"] = "小菅村役場小菅村小菅小学校（修）"
    idx = meta.index[meta["code"] == 4121031]
    meta.loc[idx, "address"] = "小菅村役場小菅村小菅小学校（修２）"
    idx = meta.index[meta["code"] == 4121032]
    meta.loc[idx, "address"] = "小菅村役場小菅村小菅小学校"

    idx = meta.index[meta["code"] == 4210100]
    meta.loc[idx, "address"] = "上田市大手上田市築地（修）"
    idx = meta.index[meta["code"] == 4210101]
    meta.loc[idx, "address"] = "上田市大手上田市築地"

    idx = meta.index[meta["code"] == 4210120]
    meta.loc[idx, "address"] = "上田市役所上田市大手（修）"
    idx = meta.index[meta["code"] == 4210121]
    meta.loc[idx, "address"] = "上田市役所上田市大手"

    idx = meta.index[meta["code"] == 4210131]
    meta.loc[idx, "address"] = "上田市上武石上田市下武石（修）"
    idx = meta.index[meta["code"] == 4210133]
    meta.loc[idx, "address"] = "上田市上武石上田市下武石"

    idx = meta.index[meta["code"] == 4210430]
    meta.loc[idx, "address"] = "小諸市相生町小諸市文化センター（修）"
    idx = meta.index[meta["code"] == 4210431]
    meta.loc[idx, "address"] = "小諸市相生町小諸市文化センター"

    idx = meta.index[meta["code"] == 4210530]
    meta.loc[idx, "address"] = "茅野市塚原茅野市葛井公園（修）"
    idx = meta.index[meta["code"] == 4210531]
    meta.loc[idx, "address"] = "茅野市塚原茅野市葛井公園"

    idx = meta.index[meta["code"] == 4211830]
    meta.loc[idx, "address"] = "御代田町御代田御代田町役場（修）"
    idx = meta.index[meta["code"] == 4211831]
    meta.loc[idx, "address"] = "御代田町御代田御代田町役場"

    idx = meta.index[meta["code"] == 4214130]
    meta.loc[idx, "address"] = "朝日村小野沢朝日村役場（修）"
    idx = meta.index[meta["code"] == 4214131]
    meta.loc[idx, "address"] = "朝日村小野沢朝日村役場"

    idx = meta.index[meta["code"] == 4220000]
    meta.loc[idx, "address"] = "飯田市馬場町飯田市高羽町（修）"
    idx = meta.index[meta["code"] == 4220001]
    meta.loc[idx, "address"] = "飯田市馬場町飯田市高羽町（修２）"
    idx = meta.index[meta["code"] == 4220010]
    meta.loc[idx, "address"] = "飯田市馬場町飯田市高羽町（修３）"
    idx = meta.index[meta["code"] == 4220002]
    meta.loc[idx, "address"] = "飯田市馬場町飯田市高羽町"

    idx = meta.index[meta["code"] == 4222120]
    meta.loc[idx, "address"] = "天龍村天龍小学校天龍村清水（修）"
    idx = meta.index[meta["code"] == 4222121]
    meta.loc[idx, "address"] = "天龍村天龍小学校天龍村清水"

    idx = meta.index[meta["code"] == 4222930]
    meta.loc[idx, "address"] = "上松町駅前通り上松町役場（修）"
    idx = meta.index[meta["code"] == 4222931]
    meta.loc[idx, "address"] = "上松町駅前通り上松町役場"

    idx = meta.index[meta["code"] == 4300060]
    meta.loc[idx, "address"] = "高根村上ケ洞高山市高根町（修）"
    idx = meta.index[meta["code"] == 4300036]
    meta.loc[idx, "address"] = "高根村上ケ洞高山市高根町（修２）"
    idx = meta.index[meta["code"] == 4300042]
    meta.loc[idx, "address"] = "高根村上ケ洞高山市高根町"

    idx = meta.index[meta["code"] == 4302000]
    meta.loc[idx, "address"] = "飛騨市神岡町飛騨市神岡町殿（修）"
    idx = meta.index[meta["code"] == 4302001]
    meta.loc[idx, "address"] = "飛騨市神岡町飛騨市神岡町殿"

    idx = meta.index[meta["code"] == 4300221]
    meta.loc[idx, "address"] = "飛騨市神岡町東町（修）"
    idx = meta.index[meta["code"] == 4302033]
    meta.loc[idx, "address"] = "飛騨市神岡町東町（修２）"
    idx = meta.index[meta["code"] == 4302036]
    meta.loc[idx, "address"] = "飛騨市神岡町東町"

    idx = meta.index[meta["code"] == 4310930]
    meta.loc[idx, "address"] = "岐阜川辺町中川辺川辺町中川辺（修）"
    idx = meta.index[meta["code"] == 4310931]
    meta.loc[idx, "address"] = "岐阜川辺町中川辺川辺町中川辺"

    idx = meta.index[meta["code"] == 4322100]
    meta.loc[idx, "address"] = "揖斐川町三輪揖斐川町南方揖斐川町三輪（修）"
    idx = meta.index[meta["code"] == 4322101]
    meta.loc[idx, "address"] = "揖斐川町三輪揖斐川町南方揖斐川町三輪（修２）"
    idx = meta.index[meta["code"] == 4322102]
    meta.loc[idx, "address"] = "揖斐川町三輪揖斐川町南方揖斐川町三輪"

    # idx = meta.index[meta["code"] == 4323600]
    # meta.loc[idx, "address"] = "岐阜山県市神崎岐阜山県市谷運動公園（修）"
    # idx = meta.index[meta["code"] == 4323601]
    # meta.loc[idx, "address"] = "岐阜山県市神崎岐阜山県市谷運動公園"

    idx = meta.index[meta["code"] == 4323630]
    meta.loc[idx, "address"] = "岐阜山県市高木岐阜山県市高富（修）"
    idx = meta.index[meta["code"] == 4323632]
    meta.loc[idx, "address"] = "岐阜山県市高木岐阜山県市高富"

    idx = meta.index[meta["code"] == 4400500]
    meta.loc[idx, "address"] = "南伊豆町石廊崎（修）"
    idx = meta.index[meta["code"] == 4400501]
    meta.loc[idx, "address"] = "南伊豆町石廊崎（修２）"
    idx = meta.index[meta["code"] == 4400502]
    meta.loc[idx, "address"] = "南伊豆町石廊崎"

    idx = meta.index[meta["code"] == 4401330]
    meta.loc[idx, "address"] = "函南町仁田函南町平井（修）"
    idx = meta.index[meta["code"] == 4401331]
    meta.loc[idx, "address"] = "函南町仁田函南町平井"

    idx = meta.index[meta["code"] == 4401860]
    meta.loc[idx, "address"] = "中伊豆町八幡伊豆市八幡（修）"
    idx = meta.index[meta["code"] == 4401832]
    meta.loc[idx, "address"] = "中伊豆町八幡伊豆市八幡"

    idx = meta.index[meta["code"] == 4401831]
    meta.loc[idx, "address"] = "伊豆市市山伊豆市湯ヶ島（修）"
    idx = meta.index[meta["code"] == 4401833]
    meta.loc[idx, "address"] = "伊豆市市山伊豆市湯ヶ島（修２）"
    idx = meta.index[meta["code"] == 4401834]
    meta.loc[idx, "address"] = "伊豆市市山伊豆市湯ヶ島"

    idx = meta.index[meta["code"] == 4410420]
    meta.loc[idx, "address"] = "御殿場市役所御殿場市茱萸沢（修）"
    idx = meta.index[meta["code"] == 4410421]
    meta.loc[idx, "address"] = "御殿場市役所御殿場市茱萸沢"

    idx = meta.index[meta["code"] == 4420200]
    meta.loc[idx, "address"] = "島田市中央町島田市旗指（修）"
    idx = meta.index[meta["code"] == 4420202]
    meta.loc[idx, "address"] = "島田市中央町島田市旗指"

    idx = meta.index[meta["code"] == 4420270]
    meta.loc[idx, "address"] = "川根町家山島田市川根町家山（修）"
    idx = meta.index[meta["code"] == 4420201]
    meta.loc[idx, "address"] = "川根町家山島田市川根町家山"

    idx = meta.index[meta["code"] == 4420330]
    meta.loc[idx, "address"] = "焼津市本町焼津市石津（修）"
    idx = meta.index[meta["code"] == 4420332]
    meta.loc[idx, "address"] = "焼津市本町焼津市石津（修２）"
    idx = meta.index[meta["code"] == 4420333]
    meta.loc[idx, "address"] = "焼津市本町焼津市石津"

    idx = meta.index[meta["code"] == 4422240]
    meta.loc[idx, "address"] = "牧之原市静波（修）"
    idx = meta.index[meta["code"] == 4422220]
    meta.loc[idx, "address"] = "牧之原市静波"

    idx = meta.index[meta["code"] == 4430160]
    meta.loc[idx, "address"] = "福田町福田磐田市福田（修）"
    idx = meta.index[meta["code"] == 4430132]
    meta.loc[idx, "address"] = "福田町福田磐田市福田"

    idx = meta.index[meta["code"] == 4432870]
    meta.loc[idx, "address"] = "浜岡町池新田御前崎市池新田（修）"
    idx = meta.index[meta["code"] == 4432830]
    meta.loc[idx, "address"] = "浜岡町池新田御前崎市池新田"

    idx = meta.index[meta["code"] == 4433000]
    meta.loc[idx, "address"] = "浜松中区三組町測候所浜松中区三組町（修）"
    idx = meta.index[meta["code"] == 4433020]
    meta.loc[idx, "address"] = "浜松中区三組町測候所浜松中区三組町"

    idx = meta.index[meta["code"] == 4433260]
    meta.loc[idx, "address"] = "浜松市雄踏町浜松西区雄踏（修）"
    idx = meta.index[meta["code"] == 4433231]
    meta.loc[idx, "address"] = "浜松市雄踏町浜松西区雄踏"

    idx = meta.index[meta["code"] == 4433640]
    meta.loc[idx, "address"] = "浜松天竜区佐久間町（旧）＊"
    idx = meta.index[meta["code"] == 4433622]
    meta.loc[idx, "address"] = "浜松天竜区佐久間町＊"

    idx = meta.index[meta["code"] == 4433660]
    meta.loc[idx, "address"] = "浜松市春野町浜松市西区春野町（修）"
    idx = meta.index[meta["code"] == 4433620]
    meta.loc[idx, "address"] = "浜松市春野町浜松市西区春野町"

    idx = meta.index[meta["code"] == 4500230]
    meta.loc[idx, "address"] = "蒲郡市神ノ郷町蒲郡市水竹町（修）"
    idx = meta.index[meta["code"] == 4500231]
    meta.loc[idx, "address"] = "蒲郡市神ノ郷町蒲郡市水竹町"

    idx = meta.index[meta["code"] == 4500860]
    meta.loc[idx, "address"] = "津具村見出原設楽町津具（修）"
    idx = meta.index[meta["code"] == 4500831]
    meta.loc[idx, "address"] = "津具村見出原設楽町津具"

    idx = meta.index[meta["code"] == 4511600]
    meta.loc[idx, "address"] = "岡崎市伝馬通岡崎市若宮町（修）"
    idx = meta.index[meta["code"] == 4511601]
    meta.loc[idx, "address"] = "岡崎市伝馬通岡崎市若宮町"

    idx = meta.index[meta["code"] == 4512230]
    meta.loc[idx, "address"] = "碧南市港本町碧南市松本町（修）"
    idx = meta.index[meta["code"] == 4512231]
    meta.loc[idx, "address"] = "碧南市港本町碧南市松本町"

    idx = meta.index[meta["code"] == 4512630]
    meta.loc[idx, "address"] = "西尾市寄住町西尾市矢曽根町（修）"
    idx = meta.index[meta["code"] == 4512631]
    meta.loc[idx, "address"] = "西尾市寄住町西尾市矢曽根町"

    idx = meta.index[meta["code"] == 4513330]
    meta.loc[idx, "address"] = "東海市中央町東海市加木屋町（修）"
    idx = meta.index[meta["code"] == 4513331]
    meta.loc[idx, "address"] = "東海市中央町東海市加木屋町"

    idx = meta.index[meta["code"] == 4514030]
    meta.loc[idx, "address"] = "豊明市新田町豊明市沓掛町（修）"
    idx = meta.index[meta["code"] == 4514031]
    meta.loc[idx, "address"] = "豊明市新田町豊明市沓掛町"

    idx = meta.index[meta["code"] == 4600000]
    meta.loc[idx, "address"] = "四日市市小古曽四日市市日永（修）"
    idx = meta.index[meta["code"] == 4600001]
    meta.loc[idx, "address"] = "四日市市小古曽四日市市日永"

    idx = meta.index[meta["code"] == 4601130]
    meta.loc[idx, "address"] = "菰野町菰野菰野町潤田（修）"
    idx = meta.index[meta["code"] == 4601131]
    meta.loc[idx, "address"] = "菰野町菰野菰野町潤田"

    idx = meta.index[meta["code"] == 4610060]
    meta.loc[idx, "address"] = "河芸町上野津市河芸町浜田（修）"
    idx = meta.index[meta["code"] == 4610032]
    meta.loc[idx, "address"] = "河芸町上野津市河芸町浜田"

    idx = meta.index[meta["code"] == 4610061]
    meta.loc[idx, "address"] = "芸濃町椋本津市芸濃町椋本（修）"
    idx = meta.index[meta["code"] == 4610033]
    meta.loc[idx, "address"] = "芸濃町椋本津市芸濃町椋本"

    idx = meta.index[meta["code"] == 4601532]
    meta.loc[idx, "address"] = "いなべ市大安町大井田いなべ市大安町丹生川久下（修）"
    idx = meta.index[meta["code"] == 4601536]
    meta.loc[idx, "address"] = "いなべ市大安町大井田いなべ市大安町丹生川久下"

    idx = meta.index[meta["code"] == 4601620]
    meta.loc[idx, "address"] = "亀山市西丸町亀山市椿世町（修）"
    idx = meta.index[meta["code"] == 4601621]
    meta.loc[idx, "address"] = "亀山市西丸町亀山市椿世町"

    idx = meta.index[meta["code"] == 4610031]
    meta.loc[idx, "address"] = "津市久居東鷹跡町津市久居明神町（修）"
    idx = meta.index[meta["code"] == 4610041]
    meta.loc[idx, "address"] = "津市久居東鷹跡町津市久居明神町（修２）"
    idx = meta.index[meta["code"] == 4610045]
    meta.loc[idx, "address"] = "津市久居東鷹跡町津市久居明神町"

    idx = meta.index[meta["code"] == 4610035]
    meta.loc[idx, "address"] = "津市安濃町川西津市安濃町東観音寺（修）"
    idx = meta.index[meta["code"] == 4610040]
    meta.loc[idx, "address"] = "津市安濃町川西津市安濃町東観音寺"

    idx = meta.index[meta["code"] == 4610200]
    meta.loc[idx, "address"] = "松坂市高町松坂市上川町（修）"
    idx = meta.index[meta["code"] == 4610201]
    meta.loc[idx, "address"] = "松坂市高町松坂市上川町"

    idx = meta.index[meta["code"] == 4614330]
    meta.loc[idx, "address"] = "伊賀市上野丸之内伊賀市四十九町（修）"
    idx = meta.index[meta["code"] == 4614337]
    meta.loc[idx, "address"] = "伊賀市上野丸之内伊賀市四十九町"

    idx = meta.index[meta["code"] == 4620830]
    meta.loc[idx, "address"] = "三重御浜町下市木三重御浜町阿田和（修）"
    idx = meta.index[meta["code"] == 4620831]
    meta.loc[idx, "address"] = "三重御浜町下市木三重御浜町阿田和"

    idx = meta.index[meta["code"] == 4620930]
    meta.loc[idx, "address"] = "紀宝町成川紀宝町神内（修）"
    idx = meta.index[meta["code"] == 4620932]
    meta.loc[idx, "address"] = "紀宝町成川紀宝町神内"

    idx = meta.index[meta["code"] == 4621360]
    meta.loc[idx, "address"] = "南島町神前浦南伊勢町神前浦（修）"
    idx = meta.index[meta["code"] == 4621331]
    meta.loc[idx, "address"] = "南島町神前浦南伊勢町神前浦"

    idx = meta.index[meta["code"] == 4621430]
    meta.loc[idx, "address"] = "三重紀北町長島三重紀北町東長島（修）"
    idx = meta.index[meta["code"] == 4621432]
    meta.loc[idx, "address"] = "三重紀北町長島三重紀北町東長島（修２）"
    idx = meta.index[meta["code"] == 4621433]
    meta.loc[idx, "address"] = "三重紀北町長島三重紀北町東長島"

    idx = meta.index[meta["code"] == 4621470]
    meta.loc[idx, "address"] = "紀伊長島町十須三重紀北町十須（修）"
    idx = meta.index[meta["code"] == 4621400]
    meta.loc[idx, "address"] = "紀伊長島町十須三重紀北町十須"

    idx = meta.index[meta["code"] == 5000130]
    meta.loc[idx, "address"] = "長浜市高田町長浜市八幡東町（修）"
    idx = meta.index[meta["code"] == 5000140]
    meta.loc[idx, "address"] = "長浜市高田町長浜市八幡東町"

    idx = meta.index[meta["code"] == 5000133]
    meta.loc[idx, "address"] = "長浜市五村長浜市宮部町（修）"
    idx = meta.index[meta["code"] == 5000141]
    meta.loc[idx, "address"] = "長浜市五村長浜市宮部町"

    idx = meta.index[meta["code"] == 5003032]
    meta.loc[idx, "address"] = "米原市下多良米原市米原（修）"
    idx = meta.index[meta["code"] == 5003035]
    meta.loc[idx, "address"] = "米原市下多良米原市米原"

    idx = meta.index[meta["code"] == 5010001]
    meta.loc[idx, "address"] = "大津市北消防署志賀分室大津市木戸市民センター大津市南小松（修）"
    idx = meta.index[meta["code"] == 5010002]
    meta.loc[idx, "address"] = "大津市北消防署志賀分室大津市木戸市民センター大津市南小松（修２）"
    idx = meta.index[meta["code"] == 5010003]
    meta.loc[idx, "address"] = "大津市北消防署志賀分室大津市木戸市民センター大津市南小松"

    idx = meta.index[meta["code"] == 5010130]
    meta.loc[idx, "address"] = "近江八幡市安土町小中近江八幡市安土町下豊浦（修）"
    idx = meta.index[meta["code"] == 5010131]
    meta.loc[idx, "address"] = "近江八幡市安土町小中近江八幡市安土町下豊浦"

    idx = meta.index[meta["code"] == 5010430]
    meta.loc[idx, "address"] = "守山市吉身守山市石田町（修）"
    idx = meta.index[meta["code"] == 5010431]
    meta.loc[idx, "address"] = "守山市吉身守山市石田町"

    idx = meta.index[meta["code"] == 5012160]
    meta.loc[idx, "address"] = "野洲市小篠原（修）"
    idx = meta.index[meta["code"] == 5012131]
    meta.loc[idx, "address"] = "野洲市小篠原（修２）"
    idx = meta.index[meta["code"] == 5012132]
    meta.loc[idx, "address"] = "野洲市小篠原"

    idx = meta.index[meta["code"] == 5012431]
    meta.loc[idx, "address"] = "東近江市五個荘竜田町東近江市五個荘小畑町（修）"
    idx = meta.index[meta["code"] == 5012440]
    meta.loc[idx, "address"] = "東近江市五個荘竜田町東近江市五個荘小畑町"

    idx = meta.index[meta["code"] == 5012433]
    meta.loc[idx, "address"] = "東近江市下中野町東近江市妹町（修）"
    idx = meta.index[meta["code"] == 5012438]
    meta.loc[idx, "address"] = "東近江市下中野町東近江市妹町"

    idx = meta.index[meta["code"] == 5101130]
    meta.loc[idx, "address"] = "伊根町平田伊根町日出（修）"
    idx = meta.index[meta["code"] == 5101131]
    meta.loc[idx, "address"] = "伊根町平田伊根町日出"

    idx = meta.index[meta["code"] == 5101960]
    meta.loc[idx, "address"] = "久美浜町役場京丹後久美浜町市民局（修）"
    idx = meta.index[meta["code"] == 5101935]
    meta.loc[idx, "address"] = "久美浜町役場京丹後久美浜町市民局"

    idx = meta.index[meta["code"] == 5102060]
    meta.loc[idx, "address"] = "加悦町加悦与謝野町加悦（修）"
    idx = meta.index[meta["code"] == 5102030]
    meta.loc[idx, "address"] = "加悦町加悦与謝野町加悦"

    idx = meta.index[meta["code"] == 5110040]
    meta.loc[idx, "address"] = "京都北区紫竹京都北区大宮西脇台町（修）"
    idx = meta.index[meta["code"] == 5110042]
    meta.loc[idx, "address"] = "京都北区紫竹京都北区大宮西脇台町"

    idx = meta.index[meta["code"] == 5110220]
    meta.loc[idx, "address"] = "京都左京区花背大布施町京都左京区広河原能見町（修）"
    idx = meta.index[meta["code"] == 5110221]
    meta.loc[idx, "address"] = "京都左京区花背大布施町京都左京区広河原能見町"

    idx = meta.index[meta["code"] == 5112130]
    meta.loc[idx, "address"] = "宇治田原町荒木宇治田原町立川（修）"
    idx = meta.index[meta["code"] == 5112131]
    meta.loc[idx, "address"] = "宇治田原町荒木宇治田原町立川"

    idx = meta.index[meta["code"] == 5112730]
    meta.loc[idx, "address"] = "精華町北稲八間精華町南稲八間（修）"
    idx = meta.index[meta["code"] == 5112731]
    meta.loc[idx, "address"] = "精華町北稲八間精華町南稲八間"

    idx = meta.index[meta["code"] == 5113660]
    meta.loc[idx, "address"] = "園部町上本町南丹市園部町小桜町（修）"
    idx = meta.index[meta["code"] == 5113631]
    meta.loc[idx, "address"] = "園部町上本町南丹市園部町小桜町"

    idx = meta.index[meta["code"] == 5200830]
    meta.loc[idx, "address"] = "大阪東淀川区千船大阪東淀川区千舟（修）"
    idx = meta.index[meta["code"] == 5200831]
    meta.loc[idx, "address"] = "大阪東淀川区千船大阪東淀川区千舟"

    idx = meta.index[meta["code"] == 5203830]
    meta.loc[idx, "address"] = "東大阪市稲葉東大阪市荒本北（修）"
    idx = meta.index[meta["code"] == 5203831]
    meta.loc[idx, "address"] = "東大阪市稲葉東大阪市荒本北"

    idx = meta.index[meta["code"] == 5204320]
    meta.loc[idx, "address"] = "能勢町今西能勢町森上（修）"
    idx = meta.index[meta["code"] == 5204321]
    meta.loc[idx, "address"] = "能勢町今西能勢町森上"

    idx = meta.index[meta["code"] == 5210120]
    meta.loc[idx, "address"] = "岸和田市土生町岸和田市畑町（修）"
    idx = meta.index[meta["code"] == 5210121]
    meta.loc[idx, "address"] = "岸和田市土生町岸和田市畑町"

    idx = meta.index[meta["code"] == 5211530]
    meta.loc[idx, "address"] = "忠岡町忠岡忠岡町忠岡東（修）"
    idx = meta.index[meta["code"] == 5211531]
    meta.loc[idx, "address"] = "忠岡町忠岡忠岡町忠岡東（修２）"
    idx = meta.index[meta["code"] == 5211532]
    meta.loc[idx, "address"] = "忠岡町忠岡忠岡町忠岡東"

    idx = meta.index[meta["code"] == 5212460]
    meta.loc[idx, "address"] = "堺市南瓦町大阪堺市堺区市役所（修）"
    idx = meta.index[meta["code"] == 5212431]
    meta.loc[idx, "address"] = "堺市南瓦町大阪堺市堺区市役所"

    idx = meta.index[meta["code"] == 5212760]
    meta.loc[idx, "address"] = "堺市石津西町大阪堺市堺区大浜南町（修）"
    idx = meta.index[meta["code"] == 5212430]
    meta.loc[idx, "address"] = "堺市石津西町大阪堺市堺区大浜南町"

    idx = meta.index[meta["code"] == 5300060]
    meta.loc[idx, "address"] = "城崎町湯島豊岡市城崎町（修）"
    idx = meta.index[meta["code"] == 5300031]
    meta.loc[idx, "address"] = "城崎町湯島豊岡市城崎町（修２）"
    idx = meta.index[meta["code"] == 5300035]
    meta.loc[idx, "address"] = "城崎町湯島豊岡市城崎町"

    idx = meta.index[meta["code"] == 5300061]
    meta.loc[idx, "address"] = "竹野町竹野豊岡市竹野町（修）"
    idx = meta.index[meta["code"] == 5300032]
    meta.loc[idx, "address"] = "竹野町竹野豊岡市竹野町（修２）"
    idx = meta.index[meta["code"] == 5300037]
    meta.loc[idx, "address"] = "竹野町竹野豊岡市竹野町"

    idx = meta.index[meta["code"] == 5302070]
    meta.loc[idx, "address"] = "村岡町川会香美町村岡区川会（修）"
    idx = meta.index[meta["code"] == 5302011]
    meta.loc[idx, "address"] = "村岡町川会香美町村岡区川会"

    idx = meta.index[meta["code"] == 5302071]
    meta.loc[idx, "address"] = "兵庫美方町忠宮兵庫香美町小代区（修）"
    idx = meta.index[meta["code"] == 5302030]
    meta.loc[idx, "address"] = "兵庫美方町忠宮兵庫香美町小代区（修２）"
    idx = meta.index[meta["code"] == 5302031]
    meta.loc[idx, "address"] = "兵庫美方町忠宮兵庫香美町小代区（修３）"
    idx = meta.index[meta["code"] == 5302032]
    meta.loc[idx, "address"] = "兵庫美方町忠宮兵庫香美町小代区"

    idx = meta.index[meta["code"] == 5310010]
    meta.loc[idx, "address"] = "神戸東灘区魚崎北町神戸東灘区住吉東町（修）"
    idx = meta.index[meta["code"] == 5310030]
    meta.loc[idx, "address"] = "神戸東灘区魚崎北町神戸東灘区住吉東町"

    idx = meta.index[meta["code"] == 5310110]
    meta.loc[idx, "address"] = "神戸灘区神ノ木神戸灘区八幡町（修）"
    idx = meta.index[meta["code"] == 5310130]
    meta.loc[idx, "address"] = "神戸灘区神ノ木神戸灘区八幡町"

    idx = meta.index[meta["code"] == 5310210]
    meta.loc[idx, "address"] = "神戸兵庫区荒田町神戸兵庫区上沢通（修）"
    idx = meta.index[meta["code"] == 5310230]
    meta.loc[idx, "address"] = "神戸兵庫区荒田町神戸兵庫区上沢通"

    idx = meta.index[meta["code"] == 5310310]
    meta.loc[idx, "address"] = "神戸長田区細田町神戸長田区神楽町（修）"
    idx = meta.index[meta["code"] == 5310311]
    meta.loc[idx, "address"] = "神戸長田区細田町神戸長田区神楽町（修２）"
    idx = meta.index[meta["code"] == 5310330]
    meta.loc[idx, "address"] = "神戸長田区細田町神戸長田区神楽町"

    idx = meta.index[meta["code"] == 5310410]
    meta.loc[idx, "address"] = "神戸須磨区緑ヶ丘神戸須磨区若草町（修）"
    idx = meta.index[meta["code"] == 5310430]
    meta.loc[idx, "address"] = "神戸須磨区緑ヶ丘神戸須磨区若草町"

    idx = meta.index[meta["code"] == 5310510]
    meta.loc[idx, "address"] = "神戸垂水区日向神戸垂水区王居殿（修）"
    idx = meta.index[meta["code"] == 5310530]
    meta.loc[idx, "address"] = "神戸垂水区日向神戸垂水区王居殿（修２）"
    idx = meta.index[meta["code"] == 5310531]
    meta.loc[idx, "address"] = "神戸垂水区日向神戸垂水区王居殿"

    idx = meta.index[meta["code"] == 5310610]
    meta.loc[idx, "address"] = "神戸北区南五葉町神戸北区南五葉（修）"
    idx = meta.index[meta["code"] == 5310630]
    meta.loc[idx, "address"] = "神戸北区南五葉町神戸北区南五葉"

    idx = meta.index[meta["code"] == 5310810]
    meta.loc[idx, "address"] = "神戸西区神出町神戸西区竹の台（修）"
    idx = meta.index[meta["code"] == 5310830]
    meta.loc[idx, "address"] = "神戸西区神出町神戸西区竹の台"

    idx = meta.index[meta["code"] == 5310910]
    meta.loc[idx, "address"] = "尼崎市上ノ島町尼崎市昭和通（修）"
    idx = meta.index[meta["code"] == 5310930]
    meta.loc[idx, "address"] = "尼崎市上ノ島町尼崎市昭和通"

    idx = meta.index[meta["code"] == 5311210]
    meta.loc[idx, "address"] = "芦屋市精道町２芦屋市精道町（修）"
    idx = meta.index[meta["code"] == 5311230]
    meta.loc[idx, "address"] = "芦屋市精道町２芦屋市精道町（修２）"
    idx = meta.index[meta["code"] == 5311231]
    meta.loc[idx, "address"] = "芦屋市精道町２芦屋市精道町"

    idx = meta.index[meta["code"] == 5311310]
    meta.loc[idx, "address"] = "伊丹市昆陽伊丹市千僧（修）"
    idx = meta.index[meta["code"] == 5311330]
    meta.loc[idx, "address"] = "伊丹市昆陽伊丹市千僧"

    idx = meta.index[meta["code"] == 5311530]
    meta.loc[idx, "address"] = "西脇市黒田庄町喜多西脇市黒田庄町前坂（修）"
    idx = meta.index[meta["code"] == 5311531]
    meta.loc[idx, "address"] = "西脇市黒田庄町喜多西脇市黒田庄町前坂"

    idx = meta.index[meta["code"] == 5311610]
    meta.loc[idx, "address"] = "宝塚市武庫川町宝塚市東洋町（修）"
    idx = meta.index[meta["code"] == 5311630]
    meta.loc[idx, "address"] = "宝塚市武庫川町宝塚市東洋町（修２）"
    idx = meta.index[meta["code"] == 5311631]
    meta.loc[idx, "address"] = "宝塚市武庫川町宝塚市東洋町"

    idx = meta.index[meta["code"] == 5311910]
    meta.loc[idx, "address"] = "川西市火打川西市中央町（修）"
    idx = meta.index[meta["code"] == 5311930]
    meta.loc[idx, "address"] = "川西市火打川西市中央町"

    idx = meta.index[meta["code"] == 5312310]
    meta.loc[idx, "address"] = "猪名川町紫合２猪名川町紫合（修）"
    idx = meta.index[meta["code"] == 5312330]
    meta.loc[idx, "address"] = "猪名川町紫合２猪名川町紫合"

    idx = meta.index[meta["code"] == 5314630]
    meta.loc[idx, "address"] = "加東市下滝野加東市河高（修）"
    idx = meta.index[meta["code"] == 5314632]
    meta.loc[idx, "address"] = "加東市下滝野加東市河高"

    idx = meta.index[meta["code"] == 5320710]
    meta.loc[idx, "address"] = "市川町西川辺（修）"
    idx = meta.index[meta["code"] == 5320720]
    meta.loc[idx, "address"] = "市川町西川辺"

    idx = meta.index[meta["code"] == 5322500]
    meta.loc[idx, "address"] = "宍粟市山崎町鹿沢宍粟市山崎町中広瀬（修）"
    idx = meta.index[meta["code"] == 5322501]
    meta.loc[idx, "address"] = "宍粟市山崎町鹿沢宍粟市山崎町中広瀬"

    idx = meta.index[meta["code"] == 5322660]
    meta.loc[idx, "address"] = "兵庫新宮町新宮たつの市新宮町（修）"
    idx = meta.index[meta["code"] == 5322630]
    meta.loc[idx, "address"] = "兵庫新宮町新宮たつの市新宮町"

    idx = meta.index[meta["code"] == 5350000]
    meta.loc[idx, "address"] = "洲本市小路谷洲本市物部（修）"
    idx = meta.index[meta["code"] == 5350001]
    meta.loc[idx, "address"] = "洲本市小路谷洲本市物部"

    idx = meta.index[meta["code"] == 5351200]
    meta.loc[idx, "address"] = "淡路市中田淡路市長澤（修）"
    idx = meta.index[meta["code"] == 5351202]
    meta.loc[idx, "address"] = "淡路市中田淡路市長澤"

    idx = meta.index[meta["code"] == 5351270]
    meta.loc[idx, "address"] = "淡路町岩屋淡路市岩屋（修）"
    idx = meta.index[meta["code"] == 5351231]
    meta.loc[idx, "address"] = "淡路町岩屋淡路市岩屋（修２）"
    idx = meta.index[meta["code"] == 5351234]
    meta.loc[idx, "address"] = "淡路町岩屋淡路市岩屋"

    idx = meta.index[meta["code"] == 5351271]
    meta.loc[idx, "address"] = "津名郡一宮町郡家２淡路市郡家（修）"
    idx = meta.index[meta["code"] == 5351232]
    meta.loc[idx, "address"] = "津名郡一宮町郡家２淡路市郡家"

    idx = meta.index[meta["code"] == 5351272]
    meta.loc[idx, "address"] = "兵庫東浦町久留麻淡路市久留麻（修）"
    idx = meta.index[meta["code"] == 5351220]
    meta.loc[idx, "address"] = "兵庫東浦町久留麻淡路市久留麻"

    idx = meta.index[meta["code"] == 5400000]
    meta.loc[idx, "address"] = "奈良市半田開町奈良市西紀寺町（修）"
    idx = meta.index[meta["code"] == 5400001]
    meta.loc[idx, "address"] = "奈良市半田開町奈良市西紀寺町（修２）"
    idx = meta.index[meta["code"] == 5400002]
    meta.loc[idx, "address"] = "奈良市半田開町奈良市西紀寺町"

    idx = meta.index[meta["code"] == 5400032]
    meta.loc[idx, "address"] = "奈良市針町奈良市都祁白石町（修）"
    idx = meta.index[meta["code"] == 5400034]
    meta.loc[idx, "address"] = "奈良市針町奈良市都祁白石町"

    idx = meta.index[meta["code"] == 5400630]
    meta.loc[idx, "address"] = "五條市本町五條市岡口（修）"
    idx = meta.index[meta["code"] == 5400634]
    meta.loc[idx, "address"] = "五條市本町五條市岡口"

    idx = meta.index[meta["code"] == 5403430]
    meta.loc[idx, "address"] = "奈良吉野町上市吉野町上市（修）"
    idx = meta.index[meta["code"] == 5403431]
    meta.loc[idx, "address"] = "奈良吉野町上市吉野町上市"

    idx = meta.index[meta["code"] == 5403500]
    meta.loc[idx, "address"] = "大淀町土田大淀町桧柿本（修）"
    idx = meta.index[meta["code"] == 5403501]
    meta.loc[idx, "address"] = "大淀町土田大淀町桧柿本"

    idx = meta.index[meta["code"] == 5404830]
    meta.loc[idx, "address"] = "宇陀市大宇陀区迫間宇陀市大宇陀迫間（修）"
    idx = meta.index[meta["code"] == 5404834]
    meta.loc[idx, "address"] = "宇陀市大宇陀区迫間宇陀市大宇陀迫間"

    idx = meta.index[meta["code"] == 5404860]
    meta.loc[idx, "address"] = "奈良榛原町萩原宇陀市榛原下井足（修）"
    idx = meta.index[meta["code"] == 5404832]
    meta.loc[idx, "address"] = "奈良榛原町萩原宇陀市榛原下井足"

    idx = meta.index[meta["code"] == 5500130]
    meta.loc[idx, "address"] = "海南市日方海南市南赤坂（修）"
    idx = meta.index[meta["code"] == 5500132]
    meta.loc[idx, "address"] = "海南市日方海南市南赤坂（修２）"
    idx = meta.index[meta["code"] == 5500133]
    meta.loc[idx, "address"] = "海南市日方海南市南赤坂"

    idx = meta.index[meta["code"] == 5501930]
    meta.loc[idx, "address"] = "湯浅町湯浅湯浅町青木（修）"
    idx = meta.index[meta["code"] == 5501931]
    meta.loc[idx, "address"] = "湯浅町湯浅湯浅町青木"

    idx = meta.index[meta["code"] == 5503660]
    meta.loc[idx, "address"] = "桃山町元紀の川市桃山町元（修）"
    idx = meta.index[meta["code"] == 5503632]
    meta.loc[idx, "address"] = "桃山町元紀の川市桃山町元（修２）"
    idx = meta.index[meta["code"] == 5503636]
    meta.loc[idx, "address"] = "桃山町元紀の川市桃山町元"

    idx = meta.index[meta["code"] == 5503831]
    meta.loc[idx, "address"] = "有田川町金屋有田川町中井原（修）"
    idx = meta.index[meta["code"] == 5503833]
    meta.loc[idx, "address"] = "有田川町金屋有田川町中井原"

    idx = meta.index[meta["code"] == 5510070]
    meta.loc[idx, "address"] = "龍神村西田辺市龍神村西（修）"
    idx = meta.index[meta["code"] == 5510035]
    meta.loc[idx, "address"] = "龍神村西田辺市龍神村西"

    idx = meta.index[meta["code"] == 5510100]
    meta.loc[idx, "address"] = "新宮市新宮新宮市春日（修）"
    idx = meta.index[meta["code"] == 5510110]
    meta.loc[idx, "address"] = "新宮市新宮新宮市春日（修２）"
    idx = meta.index[meta["code"] == 5510101]
    meta.loc[idx, "address"] = "新宮市新宮新宮市春日（修３）"
    idx = meta.index[meta["code"] == 5510102]
    meta.loc[idx, "address"] = "新宮市新宮新宮市春日"

    idx = meta.index[meta["code"] == 5510160]
    meta.loc[idx, "address"] = "熊野川町日足新宮市熊野川町日足（修）"
    idx = meta.index[meta["code"] == 5510130]
    meta.loc[idx, "address"] = "熊野川町日足新宮市熊野川町日足"

    idx = meta.index[meta["code"] == 5510200]
    meta.loc[idx, "address"] = "白浜町湯崎白浜町消防本部（修）"
    idx = meta.index[meta["code"] == 5510202]
    meta.loc[idx, "address"] = "白浜町湯崎白浜町消防本部"

    idx = meta.index[meta["code"] == 5510930]
    meta.loc[idx, "address"] = "那智勝浦町朝日那智勝浦町天満（修）"
    idx = meta.index[meta["code"] == 5510931]
    meta.loc[idx, "address"] = "那智勝浦町朝日那智勝浦町天満（修２）"
    idx = meta.index[meta["code"] == 5510932]
    meta.loc[idx, "address"] = "那智勝浦町朝日那智勝浦町天満"

    idx = meta.index[meta["code"] == 5600030]
    meta.loc[idx, "address"] = "鳥取市国分町町屋鳥取市国分町宮下（修）"
    idx = meta.index[meta["code"] == 5600038]
    meta.loc[idx, "address"] = "鳥取市国分町町屋鳥取市国分町宮下"

    idx = meta.index[meta["code"] == 5630730]
    meta.loc[idx, "address"] = "大山町国信大山町末長（修）"
    idx = meta.index[meta["code"] == 5630733]
    meta.loc[idx, "address"] = "大山町国信大山町末長"

    idx = meta.index[meta["code"] == 5700021]
    meta.loc[idx, "address"] = "松江市美穂関町下宇部尾松江市美穂関総合運動公園（修）"
    idx = meta.index[meta["code"] == 5700022]
    meta.loc[idx, "address"] = "松江市美穂関町下宇部尾松江市美穂関総合運動公園"

    idx = meta.index[meta["code"] == 5700036]
    meta.loc[idx, "address"] = "松江市宍道町昭和松江市宍道町宍道（修）"
    idx = meta.index[meta["code"] == 5700039]
    meta.loc[idx, "address"] = "松江市宍道町昭和松江市宍道町宍道（修２）"
    idx = meta.index[meta["code"] == 5700043]
    meta.loc[idx, "address"] = "松江市宍道町昭和松江市宍道町宍道"

    idx = meta.index[meta["code"] == 5700060]
    meta.loc[idx, "address"] = "八雲村西岩坂松江市八雲町西岩坂（修）"
    idx = meta.index[meta["code"] == 5700034]
    meta.loc[idx, "address"] = "八雲村西岩坂松江市八雲町西岩坂（修２）"
    idx = meta.index[meta["code"] == 5700042]
    meta.loc[idx, "address"] = "八雲村西岩坂松江市八雲町西岩坂"

    idx = meta.index[meta["code"] == 5700160]
    meta.loc[idx, "address"] = "島根斐川町荘原町出雲市斐川町荘原（修）"
    idx = meta.index[meta["code"] == 5700139]
    meta.loc[idx, "address"] = "島根斐川町荘原町出雲市斐川町荘原"

    idx = meta.index[meta["code"] == 5700260]
    meta.loc[idx, "address"] = "伯太町母里安来市伯太町東母里（修）"
    idx = meta.index[meta["code"] == 5700232]
    meta.loc[idx, "address"] = "伯太町母里安来市伯太町東母里（修２）"
    idx = meta.index[meta["code"] == 5700233]
    meta.loc[idx, "address"] = "伯太町母里安来市伯太町東母里"

    idx = meta.index[meta["code"] == 5702931]
    meta.loc[idx, "address"] = "雲南市木次町木次雲南市木次町里方（修）"
    idx = meta.index[meta["code"] == 5702938]
    meta.loc[idx, "address"] = "雲南市木次町木次雲南市木次町里方"

    idx = meta.index[meta["code"] == 5703060]
    meta.loc[idx, "address"] = "頓原町頓原飯南町頓原（修）"
    idx = meta.index[meta["code"] == 5703030]
    meta.loc[idx, "address"] = "頓原町頓原飯南町頓原（修２）"
    idx = meta.index[meta["code"] == 5703033]
    meta.loc[idx, "address"] = "頓原町頓原飯南町頓原"

    idx = meta.index[meta["code"] == 5710260]
    meta.loc[idx, "address"] = "仁摩町仁万大田市仁摩町仁万（修）"
    idx = meta.index[meta["code"] == 5710232]
    meta.loc[idx, "address"] = "仁摩町仁万大田市仁摩町仁万"

    idx = meta.index[meta["code"] == 5712431]
    meta.loc[idx, "address"] = "邑南町三日市邑南町瑞穂支所（修）"
    idx = meta.index[meta["code"] == 5712433]
    meta.loc[idx, "address"] = "邑南町三日市邑南町瑞穂支所"

    idx = meta.index[meta["code"] == 5750730]
    meta.loc[idx, "address"] = "隠岐の島町城北町沖の島町島西（修）"
    idx = meta.index[meta["code"] == 5750735]
    meta.loc[idx, "address"] = "隠岐の島町城北町沖の島町島西"

    idx = meta.index[meta["code"] == 5800160]
    meta.loc[idx, "address"] = "神郷町下神代新見市神郷下神代（修）"
    idx = meta.index[meta["code"] == 5800132]
    meta.loc[idx, "address"] = "神郷町下神代新見市神郷下神代"

    idx = meta.index[meta["code"] == 5800161]
    meta.loc[idx, "address"] = "哲西町矢田新見市哲西町矢田（修）"
    idx = meta.index[meta["code"] == 5800134]
    meta.loc[idx, "address"] = "哲西町矢田新見市哲西町矢田"

    idx = meta.index[meta["code"] == 5803737]
    meta.loc[idx, "address"] = "真庭市蒜山上長田真庭市蒜山下福田（修）"
    idx = meta.index[meta["code"] == 5803739]
    meta.loc[idx, "address"] = "真庭市蒜山上長田真庭市蒜山下福田"

    idx = meta.index[meta["code"] == 5814260]
    meta.loc[idx, "address"] = "賀陽町豊野吉備中央町豊野（修）"
    idx = meta.index[meta["code"] == 5814231]
    meta.loc[idx, "address"] = "賀陽町豊野吉備中央町豊野"

    idx = meta.index[meta["code"] == 5814831]
    meta.loc[idx, "address"] = "岡山東区西大寺上岡山東区西大寺南（修）"
    idx = meta.index[meta["code"] == 5814832]
    meta.loc[idx, "address"] = "岡山東区西大寺上岡山東区西大寺南"

    idx = meta.index[meta["code"] == 5903620]
    meta.loc[idx, "address"] = "安芸高田市向原郵便局安芸高田市向原町長田（修）"
    idx = meta.index[meta["code"] == 5903621]
    meta.loc[idx, "address"] = "安芸高田市向原郵便局安芸高田市向原町長田"

    idx = meta.index[meta["code"] == 5912860]
    meta.loc[idx, "address"] = "世羅西町小国世羅町小国（修）"
    idx = meta.index[meta["code"] == 5912832]
    meta.loc[idx, "address"] = "世羅西町小国世羅町小国"

    idx = meta.index[meta["code"] == 5920430]
    meta.loc[idx, "address"] = "広島安佐南区緑井広島安佐南区祇園（修）"
    idx = meta.index[meta["code"] == 5920431]
    meta.loc[idx, "address"] = "広島安佐南区緑井広島安佐南区祇園"

    idx = meta.index[meta["code"] == 5920833]
    meta.loc[idx, "address"] = "呉市中央呉市二河町（修）"
    idx = meta.index[meta["code"] == 5920820]
    meta.loc[idx, "address"] = "呉市中央呉市二河町（修２）"
    idx = meta.index[meta["code"] == 5920821]
    meta.loc[idx, "address"] = "呉市中央呉市二河町"

    idx = meta.index[meta["code"] == 5920860]
    meta.loc[idx, "address"] = "広島豊浜町豊島呉市豊浜町（修）"
    idx = meta.index[meta["code"] == 5920840]
    meta.loc[idx, "address"] = "広島豊浜町豊島呉市豊浜町"

    idx = meta.index[meta["code"] == 5920861]
    meta.loc[idx, "address"] = "音戸町鰯浜呉市音戸町（修）"
    idx = meta.index[meta["code"] == 5920836]
    meta.loc[idx, "address"] = "音戸町鰯浜呉市音戸町（修２）"
    idx = meta.index[meta["code"] == 5920844]
    meta.loc[idx, "address"] = "音戸町鰯浜呉市音戸町"

    idx = meta.index[meta["code"] == 5920862]
    meta.loc[idx, "address"] = "下蒲刈町三之瀬呉市下蒲刈町（修）"
    idx = meta.index[meta["code"] == 5920834]
    meta.loc[idx, "address"] = "下蒲刈町三之瀬呉市下蒲刈町"

    idx = meta.index[meta["code"] == 5921060]
    meta.loc[idx, "address"] = "広島福富町久芳東広島市福富町（修）"
    idx = meta.index[meta["code"] == 5921031]
    meta.loc[idx, "address"] = "広島福富町久芳東広島市福富町（修２）"
    idx = meta.index[meta["code"] == 5921035]
    meta.loc[idx, "address"] = "広島福富町久芳東広島市福富町"

    idx = meta.index[meta["code"] == 6003620]
    meta.loc[idx, "address"] = "つるぎ町貞光宮下つるぎ町貞光（修）"
    idx = meta.index[meta["code"] == 6003621]
    meta.loc[idx, "address"] = "つるぎ町貞光宮下つるぎ町貞光"

    idx = meta.index[meta["code"] == 6003630]
    meta.loc[idx, "address"] = "つるぎ町半田木ノ内つるぎ町半田（修）"
    idx = meta.index[meta["code"] == 6003632]
    meta.loc[idx, "address"] = "つるぎ町半田木ノ内つるぎ町半田"

    idx = meta.index[meta["code"] == 6003631]
    meta.loc[idx, "address"] = "つるぎ町一宇赤松つるぎ町一宇（修）"
    idx = meta.index[meta["code"] == 6003633]
    meta.loc[idx, "address"] = "つるぎ町一宇赤松つるぎ町一宇"

    idx = meta.index[meta["code"] == 6003720]
    meta.loc[idx, "address"] = "阿波市市場町市場阿波市市場町（修）"
    idx = meta.index[meta["code"] == 6003721]
    meta.loc[idx, "address"] = "阿波市市場町市場阿波市市場町"

    idx = meta.index[meta["code"] == 6003730]
    meta.loc[idx, "address"] = "阿波市吉野町西条阿波市吉野町（修）"
    idx = meta.index[meta["code"] == 6003733]
    meta.loc[idx, "address"] = "阿波市吉野町西条阿波市吉野町（修２）"
    idx = meta.index[meta["code"] == 6003736]
    meta.loc[idx, "address"] = "阿波市吉野町西条阿波市吉野町"

    idx = meta.index[meta["code"] == 6003731]
    meta.loc[idx, "address"] = "阿波市土成町土成阿波市土成町（修）"
    idx = meta.index[meta["code"] == 6003734]
    meta.loc[idx, "address"] = "阿波市土成町土成阿波市土成町"

    idx = meta.index[meta["code"] == 6003732]
    meta.loc[idx, "address"] = "阿波市阿波町東原阿波市阿波町（修）"
    idx = meta.index[meta["code"] == 6003735]
    meta.loc[idx, "address"] = "阿波市阿波町東原阿波市阿波町"

    idx = meta.index[meta["code"] == 6003800]
    meta.loc[idx, "address"] = "徳島三好市池田町ウエノ池田総合体育館池田町サラダ（修）"
    idx = meta.index[meta["code"] == 6003801]
    meta.loc[idx, "address"] = "徳島三好市池田町ウエノ池田総合体育館池田町サラダ（修２）"
    idx = meta.index[meta["code"] == 6003802]
    meta.loc[idx, "address"] = "徳島三好市池田町ウエノ池田総合体育館池田町サラダ"

    idx = meta.index[meta["code"] == 6003821]
    meta.loc[idx, "address"] = "徳島三好市東祖谷下瀬徳島三好市東祖谷（修）"
    idx = meta.index[meta["code"] == 6003822]
    meta.loc[idx, "address"] = "徳島三好市東祖谷下瀬徳島三好市東祖谷"

    idx = meta.index[meta["code"] == 6003830]
    meta.loc[idx, "address"] = "徳島三好市三野町芝生徳島三好市三野町（修）"
    idx = meta.index[meta["code"] == 6003834]
    meta.loc[idx, "address"] = "徳島三好市三野町芝生徳島三好市三野町"

    idx = meta.index[meta["code"] == 6003831]
    meta.loc[idx, "address"] = "徳島三好市山城町大川持徳島三好市山城町（修）"
    idx = meta.index[meta["code"] == 6003835]
    meta.loc[idx, "address"] = "徳島三好市山城町大川持徳島三好市山城町"

    idx = meta.index[meta["code"] == 6003832]
    meta.loc[idx, "address"] = "徳島三好市井川町辻徳島三好市井川町（修）"
    idx = meta.index[meta["code"] == 6003836]
    meta.loc[idx, "address"] = "徳島三好市井川町辻徳島三好市井川町"

    idx = meta.index[meta["code"] == 6003833]
    meta.loc[idx, "address"] = "徳島三好市西祖谷山村一宇徳島三好市西祖谷山村（修）"
    idx = meta.index[meta["code"] == 6003837]
    meta.loc[idx, "address"] = "徳島三好市西祖谷山村一宇徳島三好市西祖谷山村"

    idx = meta.index[meta["code"] == 6010030]
    meta.loc[idx, "address"] = "阿南市那賀川町苅谷阿南市那賀川町（修）"
    idx = meta.index[meta["code"] == 6010032]
    meta.loc[idx, "address"] = "阿南市那賀川町苅谷阿南市那賀川町"

    idx = meta.index[meta["code"] == 6010031]
    meta.loc[idx, "address"] = "阿南市羽ノ浦町中庄阿南市羽ノ浦町（修）"
    idx = meta.index[meta["code"] == 6010033]
    meta.loc[idx, "address"] = "阿南市羽ノ浦町中庄阿南市羽ノ浦町"

    idx = meta.index[meta["code"] == 6011832]
    meta.loc[idx, "address"] = "海陽町久保海陽町宍喰浦（修）"
    idx = meta.index[meta["code"] == 6011835]
    meta.loc[idx, "address"] = "海陽町久保海陽町宍喰浦（修２）"
    idx = meta.index[meta["code"] == 6011836]
    meta.loc[idx, "address"] = "海陽町久保海陽町宍喰浦"

    idx = meta.index[meta["code"] == 6100200]
    meta.loc[idx, "address"] = "東かがわ市三本松東かがわ市西村（修）"
    idx = meta.index[meta["code"] == 6100201]
    meta.loc[idx, "address"] = "東かがわ市三本松東かがわ市西村"

    idx = meta.index[meta["code"] == 6101000]
    meta.loc[idx, "address"] = "土庄町甲土庄町渕崎（修）"
    idx = meta.index[meta["code"] == 6101001]
    meta.loc[idx, "address"] = "土庄町甲土庄町渕崎"

    idx = meta.index[meta["code"] == 6102030]
    meta.loc[idx, "address"] = "小豆島町安田小豆島町片城（修）"
    idx = meta.index[meta["code"] == 6102034]
    meta.loc[idx, "address"] = "小豆島町安田小豆島町片城"

    idx = meta.index[meta["code"] == 6110130]
    meta.loc[idx, "address"] = "坂出市室町坂出市久米町（修）"
    idx = meta.index[meta["code"] == 6110131]
    meta.loc[idx, "address"] = "坂出市室町坂出市久米町（修２）"
    idx = meta.index[meta["code"] == 6110132]
    meta.loc[idx, "address"] = "坂出市室町坂出市久米町"

    idx = meta.index[meta["code"] == 6112460]
    meta.loc[idx, "address"] = "豊中町本山三豊市豊中町（修）"
    idx = meta.index[meta["code"] == 6112433]
    meta.loc[idx, "address"] = "豊中町本山三豊市豊中町"

    idx = meta.index[meta["code"] == 6112461]
    meta.loc[idx, "address"] = "仁尾町仁尾三豊市仁尾町（修）"
    idx = meta.index[meta["code"] == 6112435]
    meta.loc[idx, "address"] = "仁尾町仁尾三豊市仁尾町"

    idx = meta.index[meta["code"] == 6202620]
    meta.loc[idx, "address"] = "四国中央市三島宮川四国中央市中曽根町（修）"
    idx = meta.index[meta["code"] == 6202621]
    meta.loc[idx, "address"] = "四国中央市三島宮川四国中央市中曽根町"

    idx = meta.index[meta["code"] == 6211760]
    meta.loc[idx, "address"] = "重信町志津川東温市見奈良（修）"
    idx = meta.index[meta["code"] == 6211730]
    meta.loc[idx, "address"] = "重信町志津川東温市見奈良"

    idx = meta.index[meta["code"] == 6220060]
    meta.loc[idx, "address"] = "愛媛吉田町東小路宇和島市吉田町（修）"
    idx = meta.index[meta["code"] == 6220030]
    meta.loc[idx, "address"] = "愛媛吉田町東小路宇和島市吉田町（修２）"
    idx = meta.index[meta["code"] == 6220033]
    meta.loc[idx, "address"] = "愛媛吉田町東小路宇和島市吉田町"

    idx = meta.index[meta["code"] == 6311320]
    meta.loc[idx, "address"] = "大豊町川口大豊町黒石（修）"
    idx = meta.index[meta["code"] == 6311321]
    meta.loc[idx, "address"] = "大豊町川口大豊町黒石"

    idx = meta.index[meta["code"] == 6320220]
    meta.loc[idx, "address"] = "土佐清水市中浜土佐清水市松尾（修）"
    idx = meta.index[meta["code"] == 6320221]
    meta.loc[idx, "address"] = "土佐清水市中浜土佐清水市松尾"

    idx = meta.index[meta["code"] == 6321530]
    meta.loc[idx, "address"] = "四万十市中村大橋通四万十市古津賀（修）"
    idx = meta.index[meta["code"] == 6321532]
    meta.loc[idx, "address"] = "四万十市中村大橋通四万十市古津賀"

    idx = meta.index[meta["code"] == 6321630]
    meta.loc[idx, "address"] = "四万十町茂串町四万十町琴平町（修）"
    idx = meta.index[meta["code"] == 6321632]
    meta.loc[idx, "address"] = "四万十町茂串町四万十町琴平町（修２）"
    idx = meta.index[meta["code"] == 6321634]
    meta.loc[idx, "address"] = "四万十町茂串町四万十町琴平町"

    idx = meta.index[meta["code"] == 7000000]
    meta.loc[idx, "address"] = "萩市堀内萩市土原（修）"
    idx = meta.index[meta["code"] == 7000001]
    meta.loc[idx, "address"] = "萩市堀内萩市土原"

    idx = meta.index[meta["code"] == 7000030]
    meta.loc[idx, "address"] = "萩市見島萩市見島本村（修）"
    idx = meta.index[meta["code"] == 7000043]
    meta.loc[idx, "address"] = "萩市見島萩市見島本村"

    idx = meta.index[meta["code"] == 7000060]
    meta.loc[idx, "address"] = "山口川上村役場萩市川上（修）"
    idx = meta.index[meta["code"] == 7000032]
    meta.loc[idx, "address"] = "山口川上村役場萩市川上"

    idx = meta.index[meta["code"] == 7020031]
    meta.loc[idx, "address"] = "下関市菊川町田部下関市菊川町下岡枝（修）"
    idx = meta.index[meta["code"] == 7020036]
    meta.loc[idx, "address"] = "下関市菊川町田部下関市菊川町下岡枝（修２）"
    idx = meta.index[meta["code"] == 7020045]
    meta.loc[idx, "address"] = "下関市菊川町田部下関市菊川町下岡枝"

    idx = meta.index[meta["code"] == 7020100]
    meta.loc[idx, "address"] = "宇部市沖宇部宇部市野中（修）"
    idx = meta.index[meta["code"] == 7020101]
    meta.loc[idx, "address"] = "宇部市沖宇部宇部市野中"

    idx = meta.index[meta["code"] == 7030060]
    meta.loc[idx, "address"] = "岩国市玖珂総合支所岩国市玖珂支所（修）"
    idx = meta.index[meta["code"] == 7030034]
    meta.loc[idx, "address"] = "岩国市玖珂総合支所岩国市玖珂支所（修２）"
    idx = meta.index[meta["code"] == 7030041]
    meta.loc[idx, "address"] = "岩国市玖珂総合支所岩国市玖珂支所"

    idx = meta.index[meta["code"] == 7030060]
    meta.loc[idx, "address"] = "岩国市玖珂総合支所岩国市玖珂支所（修）"
    idx = meta.index[meta["code"] == 7030034]
    meta.loc[idx, "address"] = "岩国市玖珂総合支所岩国市玖珂支所（修２）"
    idx = meta.index[meta["code"] == 7030041]
    meta.loc[idx, "address"] = "岩国市玖珂総合支所岩国市玖珂支所"

    idx = meta.index[meta["code"] == 7030070]
    meta.loc[idx, "address"] = "岩国市今津（修）"
    idx = meta.index[meta["code"] == 7030071]
    meta.loc[idx, "address"] = "岩国市今津（修２）"

    idx = meta.index[meta["code"] == 7030161]
    meta.loc[idx, "address"] = "光市岩田（修）"
    idx = meta.index[meta["code"] == 7030131]
    meta.loc[idx, "address"] = "光市岩田（修２）"
    idx = meta.index[meta["code"] == 7030132]
    meta.loc[idx, "address"] = "光市岩田"

    idx = meta.index[meta["code"] == 7030761]
    meta.loc[idx, "address"] = "周防大島町森周防大島町東和総合支所（修）"
    idx = meta.index[meta["code"] == 7030732]
    meta.loc[idx, "address"] = "周防大島町森周防大島町東和総合支所（修２）"
    idx = meta.index[meta["code"] == 7030734]
    meta.loc[idx, "address"] = "周防大島町森周防大島町東和総合支所"

    idx = meta.index[meta["code"] == 7040000]
    meta.loc[idx, "address"] = "山口市周布山口市前町（修）"
    idx = meta.index[meta["code"] == 7040001]
    meta.loc[idx, "address"] = "山口市周布山口市前町"

    idx = meta.index[meta["code"] == 7040064]
    meta.loc[idx, "address"] = "阿東町徳佐山口市阿東徳佐（修）"
    idx = meta.index[meta["code"] == 7040060]
    meta.loc[idx, "address"] = "阿東町徳佐山口市阿東徳佐（修２）"
    idx = meta.index[meta["code"] == 7040035]
    meta.loc[idx, "address"] = "阿東町徳佐山口市阿東徳佐（修３）"
    idx = meta.index[meta["code"] == 7040036]
    meta.loc[idx, "address"] = "阿東町徳佐山口市阿東徳佐"

    idx = meta.index[meta["code"] == 7040161]
    meta.loc[idx, "address"] = "熊毛町呼坂周南市熊毛中央町（修）"
    idx = meta.index[meta["code"] == 7040131]
    meta.loc[idx, "address"] = "熊毛町呼坂周南市熊毛中央町"

    idx = meta.index[meta["code"] == 7100030]
    meta.loc[idx, "address"] = "福岡東区東浜福岡東区千早（修）"
    idx = meta.index[meta["code"] == 7100031]
    meta.loc[idx, "address"] = "福岡東区東浜福岡東区千早"

    idx = meta.index[meta["code"] == 7100130]
    meta.loc[idx, "address"] = "福岡博多区住吉福岡博多区博多駅前（修）"
    idx = meta.index[meta["code"] == 7100131]
    meta.loc[idx, "address"] = "福岡博多区住吉福岡博多区博多駅前"

    idx = meta.index[meta["code"] == 7100730]
    meta.loc[idx, "address"] = "筑紫野市二日市西筑紫野市石崎（修）"
    idx = meta.index[meta["code"] == 7100731]
    meta.loc[idx, "address"] = "筑紫野市二日市西筑紫野市石崎"

    idx = meta.index[meta["code"] == 7101031]
    meta.loc[idx, "address"] = "宗像市江口宗像市江口神原（修）"
    idx = meta.index[meta["code"] == 7101020]
    meta.loc[idx, "address"] = "宗像市江口宗像市江口神原"

    idx = meta.index[meta["code"] == 7110030]
    meta.loc[idx, "address"] = "北九州門司区大里門司区不老町門司区大里東（修）"
    idx = meta.index[meta["code"] == 7110031]
    meta.loc[idx, "address"] = "北九州門司区大里門司区不老町門司区大里東（修２）"
    idx = meta.index[meta["code"] == 7110032]
    meta.loc[idx, "address"] = "北九州門司区大里門司区不老町門司区大里東"

    idx = meta.index[meta["code"] == 7110230]
    meta.loc[idx, "address"] = "北九州戸畑区千防北九州戸畑区新池（修）"
    idx = meta.index[meta["code"] == 7110231]
    meta.loc[idx, "address"] = "北九州戸畑区千防北九州戸畑区新池"

    idx = meta.index[meta["code"] == 7110530]
    meta.loc[idx, "address"] = "北九州八幡東区春の町北九州八幡東区大谷（修）"
    idx = meta.index[meta["code"] == 7110531]
    meta.loc[idx, "address"] = "北九州八幡東区春の町北九州八幡東区大谷"

    idx = meta.index[meta["code"] == 7111030]
    meta.loc[idx, "address"] = "芦屋町幸町芦屋町中ノ浜（修）"
    idx = meta.index[meta["code"] == 7111031]
    meta.loc[idx, "address"] = "芦屋町幸町芦屋町中ノ浜（修２）"
    idx = meta.index[meta["code"] == 7111032]
    meta.loc[idx, "address"] = "芦屋町幸町芦屋町中ノ浜"

    idx = meta.index[meta["code"] == 7112460]
    meta.loc[idx, "address"] = "築城町築城築上町築城（修）"
    idx = meta.index[meta["code"] == 7112431]
    meta.loc[idx, "address"] = "築城町築城築上町築城"

    idx = meta.index[meta["code"] == 7120134]
    meta.loc[idx, "address"] = "飯塚市勢田飯塚市鹿毛馬（修）"
    idx = meta.index[meta["code"] == 7120137]
    meta.loc[idx, "address"] = "飯塚市勢田飯塚市鹿毛馬"

    idx = meta.index[meta["code"] == 7120160]
    meta.loc[idx, "address"] = "筑穂町長尾飯塚市長尾（修）"
    idx = meta.index[meta["code"] == 7120131]
    meta.loc[idx, "address"] = "筑穂町長尾飯塚市長尾"

    idx = meta.index[meta["code"] == 7130460]
    meta.loc[idx, "address"] = "八女市黒木町桑原八女市黒木町今（修）"
    idx = meta.index[meta["code"] == 7130432]
    meta.loc[idx, "address"] = "八女市黒木町桑原八女市黒木町今"

    idx = meta.index[meta["code"] == 7133660]
    meta.loc[idx, "address"] = "杷木町池田朝倉市杷木池田（修）"
    idx = meta.index[meta["code"] == 7133631]
    meta.loc[idx, "address"] = "杷木町池田朝倉市杷木池田"
#
    idx = meta.index[meta["code"] == 7201130]
    meta.loc[idx, "address"] = "有田町岩谷川内有田町本町（修）"
    idx = meta.index[meta["code"] == 7201132]
    meta.loc[idx, "address"] = "有田町岩谷川内有田町本町"

    idx = meta.index[meta["code"] == 7210330]
    meta.loc[idx, "address"] = "武雄市武雄町武雄市武雄町昭和（修）"
    idx = meta.index[meta["code"] == 7210331]
    meta.loc[idx, "address"] = "武雄市武雄町武雄市武雄町昭和（修２）"
    idx = meta.index[meta["code"] == 7210334]
    meta.loc[idx, "address"] = "武雄市武雄町武雄市武雄町昭和（修３）"
    idx = meta.index[meta["code"] == 7210337]
    meta.loc[idx, "address"] = "武雄市武雄町武雄市武雄町昭和"

    idx = meta.index[meta["code"] == 7300000]
    meta.loc[idx, "address"] = "佐世保市大黒町佐世保市千尽町（修）"
    idx = meta.index[meta["code"] == 7300001]
    meta.loc[idx, "address"] = "佐世保市大黒町佐世保市千尽町"

    idx = meta.index[meta["code"] == 7310034]
    meta.loc[idx, "address"] = "長崎市神浦夏井町長崎市神浦江川町（修）"
    idx = meta.index[meta["code"] == 7310037]
    meta.loc[idx, "address"] = "長崎市神浦夏井町長崎市神浦江川町"

    idx = meta.index[meta["code"] == 7310060]
    meta.loc[idx, "address"] = "長崎三和町為石長崎布巻町（修）"
    idx = meta.index[meta["code"] == 7310033]
    meta.loc[idx, "address"] = "長崎三和町為石長崎布巻町（修２）"
    idx = meta.index[meta["code"] == 7310038]
    meta.loc[idx, "address"] = "長崎三和町為石長崎布巻町"

    idx = meta.index[meta["code"] == 7321770]
    meta.loc[idx, "address"] = "長崎国見町土黒甲雲仙市国見町（修）"
    idx = meta.index[meta["code"] == 7321700]
    meta.loc[idx, "address"] = "長崎国見町土黒甲雲仙市国見町"

    idx = meta.index[meta["code"] == 7350630]
    meta.loc[idx, "address"] = "長崎対馬市美津島町長崎対馬市美津島町鶏知（修）"
    idx = meta.index[meta["code"] == 7350634]
    meta.loc[idx, "address"] = "長崎対馬市美津島町長崎対馬市美津島町鶏知"

    idx = meta.index[meta["code"] == 7371431]
    meta.loc[idx, "address"] = "新上五島町榎津新上五島町立串（修）"
    idx = meta.index[meta["code"] == 7371435]
    meta.loc[idx, "address"] = "新上五島町榎津新上五島町立串"

    idx = meta.index[meta["code"] == 7410101]
    meta.loc[idx, "address"] = "八代市泉町（修）"
    idx = meta.index[meta["code"] == 7410110]
    meta.loc[idx, "address"] = "八代市泉町（修２）"
    idx = meta.index[meta["code"] == 7410102]
    meta.loc[idx, "address"] = "八代市泉町"

    idx = meta.index[meta["code"] == 7410120]
    meta.loc[idx, "address"] = "八代市松江城町八代市新地町（修）"
    idx = meta.index[meta["code"] == 7410121]
    meta.loc[idx, "address"] = "八代市松江城町八代市新地町"

    idx = meta.index[meta["code"] == 7410160]
    meta.loc[idx, "address"] = "坂本村坂本八千代市坂本町（修）"
    idx = meta.index[meta["code"] == 7410132]
    meta.loc[idx, "address"] = "坂本村坂本八千代市坂本町（修２）"
    idx = meta.index[meta["code"] == 7410135]
    meta.loc[idx, "address"] = "坂本村坂本八千代市坂本町（修３）"
    idx = meta.index[meta["code"] == 7410136]
    meta.loc[idx, "address"] = "坂本村坂本八千代市坂本町"

    idx = meta.index[meta["code"] == 7414030]
    meta.loc[idx, "address"] = "甲佐町岩下甲佐町豊内（修）"
    idx = meta.index[meta["code"] == 7414031]
    meta.loc[idx, "address"] = "甲佐町岩下甲佐町豊内"

    idx = meta.index[meta["code"] == 7414920]
    meta.loc[idx, "address"] = "山都町浜町山都町下馬尾（修）"
    idx = meta.index[meta["code"] == 7414921]
    meta.loc[idx, "address"] = "山都町浜町山都町下馬尾（修２）"
    idx = meta.index[meta["code"] == 7414922]
    meta.loc[idx, "address"] = "山都町浜町山都町下馬尾"

    idx = meta.index[meta["code"] == 7415370]
    meta.loc[idx, "address"] = "熊本市京町熊本市西区春日（修）"
    idx = meta.index[meta["code"] == 7415371]
    meta.loc[idx, "address"] = "熊本市京町熊本市西区春日（修２）"
    idx = meta.index[meta["code"] == 7415500]
    meta.loc[idx, "address"] = "熊本市京町熊本市西区春日"

    idx = meta.index[meta["code"] == 7415420]
    meta.loc[idx, "address"] = "熊本東区東町熊本東区佐土原（修）"
    idx = meta.index[meta["code"] == 7415421]
    meta.loc[idx, "address"] = "熊本東区東町熊本東区佐土原"

    idx = meta.index[meta["code"] == 7415660]
    meta.loc[idx, "address"] = "熊本市富合町熊本南区富合町（修）"
    idx = meta.index[meta["code"] == 7415631]
    meta.loc[idx, "address"] = "熊本市富合町熊本南区富合町"

    idx = meta.index[meta["code"] == 7420000]
    meta.loc[idx, "address"] = "人吉町城本町人吉町西間下町（修）"
    idx = meta.index[meta["code"] == 7420010]
    meta.loc[idx, "address"] = "人吉町城本町人吉町西間下町（修２）"
    idx = meta.index[meta["code"] == 7420001]
    meta.loc[idx, "address"] = "人吉町城本町人吉町西間下町"

    idx = meta.index[meta["code"] == 7432020]
    meta.loc[idx, "address"] = "天草市東浜町天草市本渡町本渡（修）"
    idx = meta.index[meta["code"] == 7432024]
    meta.loc[idx, "address"] = "天草市東浜町天草市本渡町本渡"

    idx = meta.index[meta["code"] == 7432060]
    meta.loc[idx, "address"] = "河浦町河浦天草市河浦町（修）"
    idx = meta.index[meta["code"] == 7432035]
    meta.loc[idx, "address"] = "河浦町河浦天草市河浦町"

    idx = meta.index[meta["code"] == 7501631]
    meta.loc[idx, "address"] = "国東市武蔵町（修）"
    idx = meta.index[meta["code"] == 7501633]
    meta.loc[idx, "address"] = "国東市武蔵町（修２）"
    idx = meta.index[meta["code"] == 7501635]
    meta.loc[idx, "address"] = "国東市武蔵町"

    idx = meta.index[meta["code"] == 7510000]
    meta.loc[idx, "address"] = "大分市長浜大分市明野北（修）"
    idx = meta.index[meta["code"] == 7510001]
    meta.loc[idx, "address"] = "大分市長浜大分市明野北（修２）"
    idx = meta.index[meta["code"] == 7510002]
    meta.loc[idx, "address"] = "大分市長浜大分市明野北"

    idx = meta.index[meta["code"] == 7510020]
    meta.loc[idx, "address"] = "大分市碩田町大分市新春日町（修）"
    idx = meta.index[meta["code"] == 7510022]
    meta.loc[idx, "address"] = "大分市碩田町大分市新春日町"

    idx = meta.index[meta["code"] == 7530160]
    meta.loc[idx, "address"] = "久住町久住竹田市久住町（修）"
    idx = meta.index[meta["code"] == 7530132]
    meta.loc[idx, "address"] = "久住町久住竹田市久住町"

    idx = meta.index[meta["code"] == 7530161]
    meta.loc[idx, "address"] = "直入町長湯竹田市直入町（修）"
    idx = meta.index[meta["code"] == 7530133]
    meta.loc[idx, "address"] = "直入町長湯竹田市直入町"

    idx = meta.index[meta["code"] == 7620000]
    meta.loc[idx, "address"] = "宮崎市和知川原宮崎市霧島（修）"
    idx = meta.index[meta["code"] == 7620001]
    meta.loc[idx, "address"] = "宮崎市和知川原宮崎市霧島"

    # idx = meta.index[meta["code"] == 7620200]
    # meta.loc[idx, "address"] = "串間市本城串間市西方臨時串間市奈留（修）"
    # idx = meta.index[meta["code"] == 7620210]
    # meta.loc[idx, "address"] = "串間市本城串間市西方臨時串間市奈留（修２）"
    # idx = meta.index[meta["code"] == 7620201]
    # meta.loc[idx, "address"] = "串間市本城串間市西方臨時串間市奈留"

    idx = meta.index[meta["code"] == 7700060]
    meta.loc[idx, "address"] = "桜島町新島鹿児島市桜島赤水新島（修）"
    idx = meta.index[meta["code"] == 7700032]
    meta.loc[idx, "address"] = "桜島町新島鹿児島市桜島赤水新島"

    idx = meta.index[meta["code"] == 7705270]
    meta.loc[idx, "address"] = "鹿児島東郷町斧淵薩摩川内市東郷町（修）"
    idx = meta.index[meta["code"] == 7705232]
    meta.loc[idx, "address"] = "鹿児島東郷町斧淵薩摩川内市東郷町（修２）"
    idx = meta.index[meta["code"] == 7705235]
    meta.loc[idx, "address"] = "鹿児島東郷町斧淵薩摩川内市東郷町"

    idx = meta.index[meta["code"] == 7705370]
    meta.loc[idx, "address"] = "鹿児島鶴田町神子薩摩町神子（修）"
    idx = meta.index[meta["code"] == 7705330]
    meta.loc[idx, "address"] = "鹿児島鶴田町神子薩摩町神子"

    idx = meta.index[meta["code"] == 7705610]
    meta.loc[idx, "address"] = "いちき串木野市昭和通いちき串木野市緑町（修）"
    idx = meta.index[meta["code"] == 7705620]
    meta.loc[idx, "address"] = "いちき串木野市昭和通いちき串木野市緑町"

    idx = meta.index[meta["code"] == 7705833]
    meta.loc[idx, "address"] = "霧島市福山町福山霧島市福山町牧之原（修）"
    idx = meta.index[meta["code"] == 7705837]
    meta.loc[idx, "address"] = "霧島市福山町福山霧島市福山町牧之原"

    idx = meta.index[meta["code"] == 7711970]
    meta.loc[idx, "address"] = "鹿児島田代町麓錦江町田代麓（修）"
    idx = meta.index[meta["code"] == 7711900]
    meta.loc[idx, "address"] = "鹿児島田代町麓錦江町田代麓"

    idx = meta.index[meta["code"] == 7740070]
    meta.loc[idx, "address"] = "小宝島鹿児島十島村小宝島（修）"
    idx = meta.index[meta["code"] == 7740035]
    meta.loc[idx, "address"] = "小宝島鹿児島十島村小宝島（修２）"
    idx = meta.index[meta["code"] == 7740041]
    meta.loc[idx, "address"] = "小宝島鹿児島十島村小宝島"

    idx = meta.index[meta["code"] == 7780920]
    meta.loc[idx, "address"] = "奄美市笠利町里（修）"
    idx = meta.index[meta["code"] == 7780970]
    meta.loc[idx, "address"] = "奄美市笠利町里（修２）"
    idx = meta.index[meta["code"] == 7780921]
    meta.loc[idx, "address"] = "奄美市笠利町里"

    idx = meta.index[meta["code"] == 8010630]
    meta.loc[idx, "address"] = "沖縄市仲宗根町沖縄市美里（修）"
    idx = meta.index[meta["code"] == 8010631]
    meta.loc[idx, "address"] = "沖縄市仲宗根町沖縄市美里"

    idx = meta.index[meta["code"] == 8010900]
    meta.loc[idx, "address"] = "読谷村波平読谷村座喜味（修）"
    idx = meta.index[meta["code"] == 8010901]
    meta.loc[idx, "address"] = "読谷村波平読谷村座喜味"

    idx = meta.index[meta["code"] == 8011430]
    meta.loc[idx, "address"] = "西原町嘉手苅西原町与那城（修）"
    idx = meta.index[meta["code"] == 8011431]
    meta.loc[idx, "address"] = "西原町嘉手苅西原町与那城"

    idx = meta.index[meta["code"] == 8011530]
    meta.loc[idx, "address"] = "豊見城市上田豊見城市翁長豊見城市宜保（修）"
    idx = meta.index[meta["code"] == 8011531]
    meta.loc[idx, "address"] = "豊見城市上田豊見城市翁長豊見城市宜保（修２）"
    idx = meta.index[meta["code"] == 8011532]
    meta.loc[idx, "address"] = "豊見城市上田豊見城市翁長豊見城市宜保（修３）"
    idx = meta.index[meta["code"] == 8011533]
    meta.loc[idx, "address"] = "豊見城市上田豊見城市翁長豊見城市宜保"

    idx = meta.index[meta["code"] == 8012510]
    meta.loc[idx, "address"] = "座間味村座間味（修２）"
    idx = meta.index[meta["code"] == 8012531]
    meta.loc[idx, "address"] = "座間味村座間味（修３）"
    idx = meta.index[meta["code"] == 8012532]
    meta.loc[idx, "address"] = "座間味村座間味（修４）"

    idx = meta.index[meta["code"] == 8012731]
    meta.loc[idx, "address"] = "うるま市与那城中央うるま市与那城饒辺うるま市勝連平安名（修）"
    idx = meta.index[meta["code"] == 8012735]
    meta.loc[idx, "address"] = "うるま市与那城中央うるま市与那城饒辺うるま市勝連平安名（修２）"
    idx = meta.index[meta["code"] == 8012736]
    meta.loc[idx, "address"] = "うるま市与那城中央うるま市与那城饒辺うるま市勝連平安名"

    idx = meta.index[meta["code"] == 8012900]
    meta.loc[idx, "address"] = "南城市玉城前川南城市玉城字玉城（修）"
    idx = meta.index[meta["code"] == 8012901]
    meta.loc[idx, "address"] = "南城市玉城前川南城市玉城字玉城"

    idx = meta.index[meta["code"] == 8012930]
    meta.loc[idx, "address"] = "南城市玉城富里南城市佐敷字新里（修）"
    idx = meta.index[meta["code"] == 8012935]
    meta.loc[idx, "address"] = "南城市玉城富里南城市佐敷字新里"

    idx = meta.index[meta["code"] == 8012931]
    meta.loc[idx, "address"] = "南城市佐敷南城市佐敷字佐敷（修）"
    idx = meta.index[meta["code"] == 8012933]
    meta.loc[idx, "address"] = "南城市佐敷南城市佐敷字佐敷"

    idx = meta.index[meta["code"] == 8040604]
    meta.loc[idx, "address"] = "宮古島市伊良部国仲宮古島市伊良部前里添（修）"
    idx = meta.index[meta["code"] == 8040606]
    meta.loc[idx, "address"] = "宮古島市伊良部国仲宮古島市伊良部前里添"

    idx = meta.index[meta["code"] == 8040632]
    meta.loc[idx, "address"] = "宮古島市上野宮古島市上野支所（修）"
    idx = meta.index[meta["code"] == 8040637]
    meta.loc[idx, "address"] = "宮古島市上野宮古島市上野支所"

    idx = meta.index[meta["code"] == 8040633]
    meta.loc[idx, "address"] = "宮古島市伊良部宮古島市伊良部長浜宮古島市下地島空港（修）"
    idx = meta.index[meta["code"] == 8040637]
    meta.loc[idx, "address"] = "宮古島市伊良部宮古島市伊良部長浜宮古島市下地島空港（修２）"
    idx = meta.index[meta["code"] == 8040639]
    meta.loc[idx, "address"] = "宮古島市伊良部宮古島市伊良部長浜宮古島市下地島空港"

    idx = meta.index[meta["code"] == 8070070]
    meta.loc[idx, "address"] = "竹富町西表竹富町西表東祖納竹富町上原青年会館（修）"
    idx = meta.index[meta["code"] == 8070030]
    meta.loc[idx, "address"] = "竹富町西表竹富町西表東祖納竹富町上原青年会館（修２）"
    idx = meta.index[meta["code"] == 8070020]
    meta.loc[idx, "address"] = "竹富町西表竹富町西表東祖納竹富町上原青年会館"

    # idx = meta.index[meta["code"] == 8070003]
    # meta.loc[idx, "address"] = "竹富町船浮竹富町上原小学校（修）"
    # idx = meta.index[meta["code"] == 8070005]
    # meta.loc[idx, "address"] = "竹富町船浮竹富町上原小学校"

    # idx = meta.index[meta["code"] == 3110333]
    # meta.loc[idx, "address"] = "佐野市高砂町（修２）"
    #
    # idx = meta.index[meta["code"] == 3200010]
    # meta.loc[idx, "address"] = "沼田市西倉内町（修２）"

    # idx = meta.index[meta["code"] == 3312131]
    # meta.loc[idx, "address"] = "桶川市泉（修２）"
    # idx = meta.index[meta["code"] == 3410631]
    # meta.loc[idx, "address"] = "市川市八幡（修２）"
    # idx = meta.index[meta["code"] == 3500753]
    # meta.loc[idx, "address"] = "東京江東区枝川（修２）"
    # idx = meta.index[meta["code"] == 3501652]
    # meta.loc[idx, "address"] = "東京北区赤羽南（修２）"
    # idx = meta.index[meta["code"] == 3510251]
    # meta.loc[idx, "address"] = "武蔵野市吉祥寺東町（修２）"
    # idx = meta.index[meta["code"] == 3610431]
    # meta.loc[idx, "address"] = "伊勢原市伊勢原（修２）"
    # idx = meta.index[meta["code"] == 3612042]
    # meta.loc[idx, "address"] = "相模原中央区水郷田名（修２）"
    # idx = meta.index[meta["code"] == 3720433]
    # meta.loc[idx, "address"] = "燕市秋葉町（修２）"

    # idx = meta.index[meta["code"] == 4210100]
    # meta.loc[idx, "address"] = "上田市築地（旧）"
    # idx = meta.index[meta["code"] == 4210120]
    # meta.loc[idx, "address"] = "上田市大手（旧）"
    # # idx = meta.index[meta["code"] == 4322101]
    # # meta.loc[idx, "address"] = "揖斐川町三輪（旧３）"
    # idx = meta.index[meta["code"] == 4400501]
    # meta.loc[idx, "address"] = "南伊豆町石廊崎（修２）"
    # idx = meta.index[meta["code"] == 5510110]
    # meta.loc[idx, "address"] = "新宮市新宮（修２）"
    # idx = meta.index[meta["code"] == 5510101]
    # meta.loc[idx, "address"] = "新宮市新宮（修３）"
    # idx = meta.index[meta["code"] == 5510931]
    # meta.loc[idx, "address"] = "那智勝浦町朝日（修３）"
    # idx = meta.index[meta["code"] == 5511200]
    # meta.loc[idx, "address"] = "古座川町峯・高池（修）"
    # idx = meta.index[meta["code"] == 5511201]
    # meta.loc[idx, "address"] = "古座川町峯・高池"
    # idx = meta.index[meta["code"] == 7111031]
    # meta.loc[idx, "address"] = "芦屋町幸町（修２）"
    #
    # codes = [3500330, 3500331, 3500332, 3500350, 3500351]
    # codes = [2500730, 2500731, 2500732, 2500733, 2500734]
    # codes = [3713510, 3713530, 3713531, 3713532, 3713533]
    # codes = [7020000, 7020030, 7020035, 7020042, 7020044]
    # codes = [8012510, 8012530, 8012531, 8012532, 8012533]
    # codes = [7520000, 7520020, 7520030, 7520042, 7520043]
    # codes = [1000000, 1000001, 1000230, 1000231, 4220001, 4220002, 4220010,
    #          4220032, 4220033]
    #
    # df_sll = meta[meta['code'].isin(codes)]
    #
    #
    df_sll = meta
    df_sll = add_address_only_column_to_df(df_sll)
    dfs = find_kyu_index_and_combine_them(df_sll, cfg, dir_data)
    dfg = create_organized_meta_file(meta, dfs)
    dfg.to_csv("../../../intermediates/organized_codes_pre_01.csv", index=None)
    print(dfg)


if __name__ == '__main__':
    main()
