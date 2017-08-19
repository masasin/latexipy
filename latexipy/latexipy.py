'''
Automatically change matplotlib figures to LaTeX figures.

'''
from contextlib import contextmanager
import errno
import logging
import math
from pathlib import Path
import sys
from typing import Sequence
import warnings

import matplotlib.pyplot as plt


logger = logging.getLogger('latexipy')


INCH_PER_POINT = 1/72.27
MAX_HEIGHT_INCH = 8

FONT_SIZE = 8

PARAMS = {
    'pgf.texsystem': 'xelatex',  # change this if using xetex or luatex
    'text.usetex': True,
    'font.family': 'serif',
    'font.serif': [],
    'font.sans-serif': [],
    'font.monospace': [],
    'pgf.preamble': [
      r'\usepackage[utf8x]{inputenc}',
      r'\usepackage[T1]{fontenc}',
      ],
    'font.size': FONT_SIZE,
    'axes.labelsize': FONT_SIZE,
    'axes.titlesize': FONT_SIZE,
    'legend.fontsize': FONT_SIZE,
    'xtick.labelsize': FONT_SIZE,
    'ytick.labelsize': FONT_SIZE,
}


def latexify(params=PARAMS):
    '''
    Set up matplotlib's RC params for LaTeX plotting.

    Call this function before plotting the first figure.

    Parameters
    ----------
    params : Optional[dict]
        A dictionary containing the RC params that need to be updated. Default
        is `PARAMS`. The defaults should be okay for most cases, but `PARAMS`
        can be updated via `.update()` as well.

    Example
    -------
    >>> params = PARAMS.copy()
    >>> params.update({'font.family': 'sans-serif'})
    >>> latexify(params)

    '''
    plt.rcParams.update(params)
    plt.switch_backend('pgf')


def fig_size(fig_width_tw=0.9, *, fig_ratio=None, fig_height=None, n_columns=1,
             max_height=MAX_HEIGHT_INCH, doc_width_pt=345):
    r'''
    Get the necessary figure size.

    Parameters
    ----------
    fig_width_tw : Optional[float]
        The width of the figure, as a proportion of the text width, between 0
        and 1. Default is 0.9.
    fig_ratio: Optional[float]
        The ratio of the figure height to figure width. If `fig_height` is
        specified, `fig_ratio` is calculated from that and `fig_width`. Default
        is the golden ratio.
    fig_height : Optional[float]
        The height of the figure in inches. Default is the golden ratio of the
        figure width.
    n_columns : Optional[int]
        The number of equally sized columns in the document. The figure will
        never be larger than the width of one column.  Default is 1.
    max_height : Optional[float]
        The maximum height of the figure, in inches. Default is
        `MAX_HEIGHT_INCH`.
    doc_width_pt : float
        The text width of the document, in points. Can be obtained by typing
        `\the\textwidth` in the LaTeX document. Default is 345.

    Returns
    -------
    fig_width : float
        The figure width, in inches.
    fig_height : float
        The figure height in inches.

    '''
    doc_width_in = doc_width_pt * INCH_PER_POINT
    fig_width = doc_width_in * fig_width_tw / n_columns

    if fig_ratio is None:
        if fig_height is None:
            golden_mean = (math.sqrt(5)-1.0)/2.0
            fig_ratio = golden_mean
        else:
            fig_ratio = fig_height / fig_width

    fig_height = fig_width * fig_ratio

    if fig_height > max_height:
        warnings.warn(f'fig_height too large at {fig_height} inches; '
                      'will automatically reduce to {max_height} inches.')
        fig_height = max_height
    return fig_width, fig_height


def save_fig(filename, folder, exts, from_context=False, mkdir=True):
    '''
    Save the figure in each of the extensions.

    Parameters
    ----------
    filename : str
        The base name of the file, without extensions.
    folder : str
        The name of the directory in which to store the saved files.
    exts : Sequence
        A list of all the extensions to be saved, without the dot.
    from_context : Optional[bool]
        Whether the function is being called from the context manager. This only
        affects the logging output. Default is False.
    mkdir : Optional[bool]
        Whether the folder should be created automatically if it does not exist.
        Default is True.

    '''
    folder = Path(folder)

    if not from_context:
        logger.info(f'Saving {filename}...  ')
    plt.tight_layout(0)

    if mkdir:
        if folder.is_file():
            msg = 'A file exists at directory location'
            e = NotADirectoryError(errno.ENOTDIR, msg, str(folder))
            logger.error(e)
            return
        folder.mkdir(parents=True, exist_ok=True)

    for ext in exts:
        if from_context:
            logger.info(f'  Saving {ext}...')
        try:
            plt.savefig(str(folder/f'{filename}.{ext}'))
        except (FileNotFoundError, PermissionError) as e:
            logger.error(e)
            break


@contextmanager
def figure(filename, *, folder='img', exts=['pgf', 'png'], size=fig_size(),
           mkdir=True):
    '''
    The primary interface for creating figures.

    Any matplotlib-derived code in the scope of this context manager is valid,
    and should output as expected.

    Parameters
    ----------
    filename : str
        The base name of the file, without extensions.
    folder : Optional[str]
        The name of the directory in which to store the saved files. Default is
        'img'.
    exts : Sequence
        A list of all the extensions to be saved, without the dot. Default is
        ['pgf', 'png'].
    mkdir : Optional[bool]
        Whether the folder should be created automatically if it does not exist.
        Default is True.

    Notes
    -----
    When integrating with LaTeX, the recommended format is PGF. PNG can be used
    externally, such as in blog posts or as embedded images, while PDF can be
    standalone, or inserted into LaTeX documents. A full list of supported
    formats can be found by calling
    `plt.gcf().canvas.get_supported_filetypes_grouped()`

    '''
    logger.info(f'{filename}:')
    logger.info('  Plotting...')
    yield
    plt.gcf().set_size_inches(*size)
    save_fig(filename, folder=folder, exts=exts, from_context=True, mkdir=mkdir)
    plt.close()
