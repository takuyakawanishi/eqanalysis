import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def main():

    df = pd.read_csv('temp.csv')

    print(df['intmax'])

    for i in range(len(df)):
        intmax = int(df.at[i, 'intmax'])
        if intmax <= 3:
            est = np.nan
            print("intmax is <= 3.")
        if intmax == 4:
            est = df.at[i, 'est5']
        elif intmax == 5:
            est = df.at[i, 'est6']
        elif intmax == 6:
            est = df.at[i, 'est7']
        df.at[i, 'est'] = est

    df['p_no_eq_Mp1'] = np.exp(- df['est'] * df['duration'])
    df['p_no_eq_Mp1'].describe()

    dfs = df.sort_values(by='p_no_eq_Mp1')
    dfss = dfs[['code', 'address', 'intmax', 'est', 'slope', 'duration', 'est7', 'p_no_eq_Mp1']]
    print(dfss.head(15))
    print(dfss['p_no_eq_Mp1'].describe())
    fig = plt.figure(figsize=(4.5, 3))
    ax = fig.add_axes([4/25, 4/25, 4/5, 4/5])
    ax.tick_params(which='both', axis='both', direction='in')
    ax.hist(dfss['p_no_eq_Mp1'], bins=[0, 0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45,
                                      0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95,
                                      1.0], alpha=.8)
    ax.set_xlabel("$\\mathrm{\\mathbb{P}}$", fontsize=14)
    ax.annotate("Counts", xy=(0, 0.5), xytext=(0.02, 4/25+2/5),
                xycoords='figure fraction', textcoords='figure fraction',
                va='center', ha='left', rotation=90, fontsize=14)
    ax.plot([0.05, 0.05], [-1, 10], lw=.5, c='k')
    ax.annotate("$\\mathbb{P} < 0.05$ for five stations.",
                xy=(0, 0), xytext=(.05, .33), textcoords='axes fraction',
                va='bottom', ha='left')

    ax.set_ylim(bottom=0)
    fig.savefig('../../results/figures/validation_b1994.svg')
    plt.show()


if __name__ == '__main__':
    main()