import matplotlib.pyplot as plt
import numpy as np

PAGE_WIDTH = 5.08
PAGE_HEIGHT = 9.21

def four_in_line(n_figures):
    gap = .04
    n = 4
    s = n + (n - 1) * gap
    fig_width = np.round(PAGE_WIDTH / n, 2)
    print(fig_width)





def main():
    # 129 mm in width and 234 mm in height
    page_width = np.round(129 / 25.4, 2)
    page_height = np.round(234 / 25.4, 2)
    fig_width = page_width / 4.15
    print(fig_width)
    print(page_width, page_height)
    page = plt.figure(figsize=(page_width, page_height))  # A4: 8.3 x 11.7 inch
    res = four_in_line(1)



if __name__ == "__main__":
    main()
