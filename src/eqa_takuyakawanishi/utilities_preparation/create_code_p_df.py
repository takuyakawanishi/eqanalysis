import numpy as np
import pandas as pd


def main():
    df = pd.read_csv(
        "eqanalysis/data_2024/code_p.dat", encoding="shift_jis", sep="\t",
        header=None
    )
    df.columns = ["code", "address", "lat", "lon", "from", "to"]
    print(df)
    df.to_csv("eqanalysis/data_2024/code_p_20231205_df.csv", index=None)


if __name__ == "__main__":
    main()