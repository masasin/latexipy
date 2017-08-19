#!/usr/bin/env python
import matplotlib.pyplot as plt
import numpy as np

from latexipy import latexipy as lp


if __name__ == '__main__':
    lp.latexify()

    with lp.figure('fun'):
        x = np.linspace(-np.pi, np.pi)
        y1 = np.sin(x)
        y2 = np.cos(x)
        plt.plot(x, y1, label='sine')
        plt.plot(x, y2, label='cosine')
        plt.title('Sine and cosine')
        plt.xlabel(r'$\theta$')
        plt.ylabel('Value')
        plt.legend()
