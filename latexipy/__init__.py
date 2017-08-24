'''
LaTeXiPy
========

Provides
  1. An easy way of generating plots in multiple formats.
  2. Sensible defaults that fit perfectly with most LaTeX documents.
  3. Compatibility with Matplotlib-based packages.
  4. Easy restyling.

This documentation assumes that ``latexipy`` has been imported as ``lp``::

  >>> import latexipy as lp

You will probably use ``lp.figure()`` the most (once for each block)::

  >>> with lp.figure('filename'):
  ...     draw_the_plot()

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
__version__ = '1.0.1'
