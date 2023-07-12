import numpy as np
import pandas as pd


def main():
    file = "../../../intermediates/olds/organized_codes_pre_01.csv"
    df = pd.read_csv(file)
    df = df.reset_index(drop=True)
    codes = list(df["code_prime"])
    for i_code, code in enumerate(codes):
        distances = eval(df.at[i_code, "distances"])
        if len(distances) > 0:
            df.at[i_code, "max_dist_group"] = max(distances)
    dfs = df.sort_values(by="max_dist_group", ascending=False)
    print(dfs.head(40))


if __name__ == '__main__':
    main()