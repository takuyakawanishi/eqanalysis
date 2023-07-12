import numpy as np
import pandas as pd


def main():
    filename = "../../../intermediates/organized_codes_pre_02.csv"
    dfg = pd.read_csv(filename)
    dfg = dfg.reset_index(drop=True)
    dfg["grand_date_b"] = pd.to_datetime(dfg["grand_date_b"], format="%Y-%m-%d")
    dfg["grand_date_e"] = pd.to_datetime(dfg["grand_date_e"], format="%Y-%m-%d")
    dfg["gross_duration"] = dfg["grand_date_e"] - dfg["grand_date_b"]
    dfg["gross_duration"] = dfg["gross_duration"] / np.timedelta64(1, "D")
    codes = dfg["code_prime"]
    for i_code, code in enumerate(codes):
        gaps = eval(dfg.loc[i_code, "gaps"])
        if len(gaps) == 0:
            gapdays = 0
        else:
            gaps = np.array(gaps)
            gapdays = gaps.sum()
        dfg.at[i_code, "gap_days"] = gapdays
    dfg["net_duration"] = dfg["gross_duration"] - dfg["gap_days"]
    print(dfg[["gross_duration", "gap_days", "net_duration"]])


if __name__ == '__main__':
    main()