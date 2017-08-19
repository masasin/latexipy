#!/usr/bin/env python
from functools import partial

import matplotlib.pyplot as plt
import numpy as np

from latexipy import latexipy as lp


if __name__ == '__main__':
    lp.latexify()

    figure = partial(lp.figure, folder='some_images', exts=['png'])

    x = np.linspace(-np.pi, np.pi)
    y1 = np.sin(x)
    y2 = np.cos(x)

    with figure('sin'):
        plt.plot(x, y1, label='sine')
        plt.title('Sine')
        plt.xlabel(r'$\theta$')
        plt.ylabel('Value')
        plt.legend()

    with figure('cos'):
        plt.plot(x, y2, label='cosine', c='C1')
        plt.title('Cosine')
        plt.xlabel(r'$\theta$')
        plt.ylabel('Value')
        plt.legend()

    with figure('both'):
        plt.plot(x, y1, label='sine')
        plt.plot(x, y2, label='cosine')
        plt.title('Sine and cosine')
        plt.xlabel(r'$\theta$')
        plt.ylabel('Value')
        plt.legend()
