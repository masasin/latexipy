'''
Automatically change Matplotlib figures to LaTeX figures.

'''
from contextlib import contextmanager
import errno
import logging
import math
from pathlib import Path
import warnings

import matplotlib.pyplot as plt


logger = logging.getLogger('latexipy')


INCH_PER_POINT = 1/72.27
GOLDEN_RATIO = (math.sqrt(5) - 1) / 2

MAX_HEIGHT_INCH = 8
FONT_SIZE = 8

PARAMS = {
    'pgf.texsystem': 'xelatex',  # pdflatex, xelatex, lualatex
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

_ORIGINAL_PARAMS = dict(plt.rcParams)
_ORIGINAL_BACKEND = plt.get_backend()


def latexify(params=PARAMS, new_backend='pgf'):
    '''
    Set up Matplotlib's RC params for LaTeX plotting.

    Call this function before plotting the first figure.

    Parameters
    ----------
    params : Optional[dict]
        A dictionary containing the RC params that need to be updated. Default
        is ``PARAMS``. The defaults should be okay for most cases, but
        ``PARAMS`` can be updated via ``.update()`` as well.

    new_backend : Optional[str|None]
        The backend to switch too. Default is PGF, which allows a nicer PDF
        output too.

    Raises
    ------
    ValueError
        If the new backend is not supported.

    Example
    -------
    >>> params = PARAMS.copy()
    >>> params.update({'font.family': 'sans-serif'})
    >>> latexify(params)

    '''
    plt.rcParams.update(params)
    if new_backend is not None:
        try:
            plt.switch_backend(new_backend)
        except ValueError:
            logger.error(f'Backend not supported: {new_backend!r}')
            raise


def revert():
    '''
    Return to the settings before running ``latexify()`` and updating params.

    '''
    plt.rcParams.update(_ORIGINAL_PARAMS)
    plt.switch_backend(_ORIGINAL_BACKEND)


@contextmanager
def temp_params(font_size=None, font_family=None, font_serif=None,
                font_sans_serif=None, font_monospace=None, params_dict=None):
    '''
    Temporarily set Matplotlib's RC params.

    Parameters
    ----------
    font_size : Optional[int]
        The font size to use. It changes all the components that are normally
        updated with ``latexify()``. If you want to change something
        individually, do so from within ``params_dict``.
    font_family : Optional[str]
        The font family to use.
    font_serif : Optional[List[str]]
        A list of serif fonts to use.
    font_sans_serif : Optional[List[str]]
        A list of sans-serif fonts to use.
    font_monospace : Optional[List[str]]
        A list of monospace fonts to use.
    params_dict : Optional[Dict[str, Any]]
        The dictionary of parameters to update, and the updated values. This is
        only applied after going through the rest of the arguments.

    '''
    old_params = plt.rcParams
    new_params = old_params.copy()

    mapping = {
        'font.size': font_size,
        'axes.labelsize': font_size,
        'axes.titlesize': font_size,
        'legend.fontsize': font_size,
        'xtick.labelsize': font_size,
        'ytick.labelsize': font_size,
        'font.family': font_family,
        'font.serif': font_serif,
        'font.sans-serif': font_sans_serif,
        'font.monospace': font_monospace,
    }

    new_params.update({k: v
                       for k, v in mapping.items()
                       if v is not None})

    if params_dict is not None:
        new_params.update(params_dict)

    plt.rcParams.update(new_params)
    try:
        yield
    finally:
        plt.rcParams.update(old_params)


def figure_size(width_tw=0.9, *, ratio=None, height=None, n_columns=1,
                max_height=MAX_HEIGHT_INCH, doc_width_pt=345):
    r'''
    Get the necessary figure size.

    Parameters
    ----------
    width_tw : Optional[float]
        The width of the figure, as a proportion of the text width, between 0
        and 1. Default is 0.9.
    ratio: Optional[float]
        The ratio of the figure height to figure width. If ``height`` is
        specified, ``ratio`` is calculated from that and ``width``. Default is
        the golden ratio.
    height : Optional[float]
        The height of the figure in inches. If ``ratio`` is specified,
        ``height`` is ignored. Default is the golden ratio of the width.
    n_columns : Optional[int]
        The number of equally sized columns in the document. The figure will
        never be larger than the width of one column.  Default is 1.
    max_height : Optional[float]
        The maximum height of the figure, in inches. Default is
        ``MAX_HEIGHT_INCH``.
    doc_width_pt : float
        The text width of the document, in points. It can be obtained by typing
        ``\the\textwidth`` in the LaTeX document. Default is 345.

    Returns
    -------
    width : float
        The figure width, in inches.
    height : float
        The figure height in inches.

    '''
    doc_width_in = doc_width_pt * INCH_PER_POINT
    width = doc_width_in * width_tw / n_columns

    if ratio is None:
        if height is None:
            ratio = GOLDEN_RATIO
        else:
            ratio = height / width

    height = width * ratio

    if height > max_height:
        warnings.warn(f'height too large at {height} inches; '
                      f'will automatically reduce to {max_height} inches.')
        height = max_height
    return width, height


def save_figure(filename, directory, exts, mkdir=True,
                from_context_manager=False):
    '''
    Save the figure in each of the extensions.

    Parameters
    ----------
    filename : str
        The base name of the file, without extensions.
    directory : str
        The name of the directory in which to store the saved files.
    exts : Sequence
        A list of all the extensions to be saved, without the dot.
    mkdir : Optional[bool]
        Whether the directory should be created automatically if it does not
        exist.  Default is True.
    from_context_manager : Optional[bool]
        Whether the function is being called from the ``figure`` context
        manager.  This only affects the logging output. Default is False.

    Raises
    ------
    FileNotFoundError
        If the target directory does not exist and cannot be created.
    NotADirectoryError
        If the target directory is actually a file.
    PermissionError
        If there is no permission to write to the target directory.
    ValueError
        If the format is not supported.

    Notes
    -----
    When integrating with LaTeX, the recommended format is PGF. PNG can be used
    externally, such as in blog posts or as embedded images, while PDF can be
    standalone, or inserted into LaTeX documents. A full list of supported
    formats can be found by calling
    ``plt.gcf().canvas.get_supported_filetypes_grouped()``

    '''
    directory = Path(directory)

    if not from_context_manager:
        logger.info(f'Saving {filename}...  ')

    try:
        plt.tight_layout(0)
    except ValueError as e:
        warnings.warn('No figures to save.')

    if mkdir:
        if directory.is_file():
            msg = 'A file exists at directory location'
            e = NotADirectoryError(errno.ENOTDIR, msg, str(directory))
            logger.error(f'Directory set to file: {str(directory)}')
            raise e
        try:
            directory.mkdir(parents=True, exist_ok=True)
        except PermissionError as e:
            logger.error('Permission denied for directory: '
                         f'{str(directory)!r}')
            raise

    for ext in exts:
        if from_context_manager:
            logger.info(f'  Saving {ext}...')
        full_filename = f'{filename}.{ext}'
        try:
            plt.savefig(str(directory/full_filename))
        except FileNotFoundError as e:
            logger.error(f'Directory does not exist: {str(directory)!r}.'
                         'Please create it or set mkdir to True.')
            raise
        except PermissionError as e:
            logger.error(f'Permission denied for file ({full_filename!r}) in'
                         f'directory: {str(directory)!r}')
            raise
        except ValueError as e:
            logger.error(f'Unsupported file format: {ext}')
            raise


@contextmanager
def figure(filename, *, directory='img', exts=['pgf', 'png'], size=None,
           mkdir=True):
    '''
    The primary interface for creating figures.

    Any Matplotlib-derived code in the scope of this context manager is valid,
    and should output as expected.

    Parameters
    ----------
    filename : str
        The base name of the file, without extensions.
    directory : Optional[str]
        The name of the directory in which to store the saved files. Default is
        'img'.
    exts : Sequence
        A list of all the extensions to be saved, without the dot. Default is
        ['pgf', 'png'].
    size : Optional[Sequence[float, float]]
        The width and height of the figure, in inches. Default is
        ``figure_size()``.
    mkdir : Optional[bool]
        Whether the directory should be created automatically if it does not
        exist.  Default is True.

    Raises
    ------
    FileNotFoundError
        If the target directory does not exist and cannot be created.
    NotADirectoryError
        If the target directory is actually a file.
    PermissionError
        If there is no permission to write to the target directory.
    ValueError
        If the format is not supported.

    Notes
    -----
    When integrating with LaTeX, the recommended format is PGF. PNG can be used
    externally, such as in blog posts or as embedded images, while PDF can be
    standalone, or inserted into LaTeX documents. A full list of supported
    formats can be found by calling
    ``plt.gcf().canvas.get_supported_filetypes_grouped()``

    '''
    if size is None:
        size = figure_size()
    logger.info(f'{filename}:')
    logger.info('  Plotting...')
    yield
    plt.gcf().set_size_inches(*size)
    save_figure(filename=filename, directory=directory, exts=exts, mkdir=mkdir,
                from_context_manager=True)
    plt.close()
