'''
Top-level package for LaTeXiPy.

'''
from ._latexipy import (
    latexify,
    temp_params,
    revert,
    figure_size,
    save_figure,
    figure,
    PARAMS,
)

__all__ = ['latexify', 'temp_params', 'revert', 'figure_size', 'save_figure',
           'figure', 'PARAMS']

__author__ = '''Jean Nassar'''
__email__ = 'jn.masasin@gmail.com'
__version__ = '0.1.0'
