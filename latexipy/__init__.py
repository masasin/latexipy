'''
Top-level package for LaTeXiPy.

'''
from latexipy.latexipy import (
    latexify,
    figure_size,
    save_figure,
    figure,
    INCH_PER_POINT,
    GOLDEN_RATIO,
    MAX_HEIGHT_INCH,
    FONT_SIZE,
    PARAMS,
)

INCH_PER_POINT, GOLDEN_RATIO, MAX_HEIGHT_INCH, FONT_SIZE, PARAMS  # for flake8

__all__ = ['latexify', 'figure_size', 'save_figure', 'figure']

__author__ = '''Jean Nassar'''
__email__ = 'jn.masasin@gmail.com'
__version__ = '0.1.0'
