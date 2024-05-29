import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import scipy.stats


def main():
    x = [1, 2, 3, 4]
    y1 = np.array([75, 26, 5, 2])
    y2 = np.array([.55 * 75, .71 * 26, .8 * 5, 2])
    ly1 = np.log10(y1)
    ly2 = np.log10(y2)
    reg1 = scipy.stats.linregress(x, ly1)
    reg2 = scipy.stats.linregress(x, ly2)
    print(reg1)
    print(reg2)
    xrs = np.linspace(.8, 7.2)
    fig, ax = plt.subplots(figsize=(3.3, 3.3))
    ax.set_yscale('log')
    ax.scatter(x, y1)
    ax.scatter(x, y2)
    y1rs = 10 ** (reg1.intercept + reg1.slope * xrs)
    y2rs = 10 ** (reg2.intercept + reg2.slope * xrs)
    ax.plot(xrs, y1rs)
    ax.plot(xrs, y2rs)
    plt.show()


if __name__ == '__main__':
    main()