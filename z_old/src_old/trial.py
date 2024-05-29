import numpy as np
import scipy.stats
import sys
sys.path.append("./")
import eqanalysis.src.eqa_takuyakawanishi.eqa as eqa

def main():

    ints = np.array([1, 2, 3, 4])
    bs = 10 ** (.9 * - .25 * ints + scipy.stats.norm.rvs(scale=.1, size= 4))
    b_s = []
    for b in bs:
        b = eqa.round_to_k(b, 2)
        b_s.append(b)
    b_s = np.array(b_s)
    print(repr(b_s))
    b_log10_s = np.log10(b_s)
    res = scipy.stats.linregress(ints, b_log10_s)
    print(res)


if __name__ == "__main__":
    main()