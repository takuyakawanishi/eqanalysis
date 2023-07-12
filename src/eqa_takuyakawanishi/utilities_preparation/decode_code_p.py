import numpy as np
import pandas as pd


def main():
    df = pd.read_csv(
        "../../../data/code_p.txt", encoding="shift_jis", sep="\t",
        header=None
    )
    df.columns = ["code", "address", "lat", "lon", "from", "to"]
    print(df)
    df.to_csv("../../../data/code_p_df.csv", index=None)


if __name__ == "__main__":
    main()