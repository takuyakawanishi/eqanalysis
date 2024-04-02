import datetime
import numpy as np
import pandas as pd
import sys
sys.path.append("./")
import eqanalysis.src.eqa_takuyakawanishi.eqa as eqa


def main():
    fn_p = "eqanalysis/data_2024/code_p_20231205_df.csv"
    df_code_p = pd.read_csv(fn_p)
    df_combine = df_code_p.groupby(by=['lat', 'lon'])
    for key, item in df_combine:
        print(df_combine.get_group(key), "\n\n")


if __name__ == '__main__':
    main()
