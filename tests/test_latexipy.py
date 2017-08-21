#!/usr/bin/env python
'''
Tests for `latexipy` package.

'''
from functools import partial
import inspect
import math
from unittest.mock import patch

import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot
import pytest

import latexipy as lp


def test_latexify():
    with patch('matplotlib.rcParams.update') as mock_update, \
            patch('matplotlib.pyplot.switch_backend') as mock_switch:
        lp.latexify(lp.PARAMS)

        mock_update.assert_called_once_with(lp.PARAMS)
        mock_switch.assert_called_once_with('pgf')


class TestFigureSize:
    def setup(self):
        self.width = 345 * 0.9 * lp.INCH_PER_POINT

    def test_defaults(self):
        height = lp.GOLDEN_RATIO * self.width
        assert lp.figure_size() == (self.width, height)

    def test_ratio_no_height(self):
        assert lp.figure_size(ratio=1) == (self.width, self.width)
        assert lp.figure_size(ratio=0.5) == (self.width, self.width/2)

    def test_ratio_height(self):
        dimensions = (self.width, self.width)
        assert lp.figure_size(ratio=1, height=5) == dimensions

    def test_height_no_ratio(self):
        assert lp.figure_size(height=5) == (self.width, 5)

    def test_height_too_high(self):
        with pytest.warns(UserWarning):
            height = lp.MAX_HEIGHT_INCH + 1
            assert lp.figure_size(height=height) == (self.width,
                                                     lp.MAX_HEIGHT_INCH)

    def test_columns(self):
        width = self.width / 2
        height = lp.GOLDEN_RATIO * width
        assert lp.figure_size(n_columns=2) == (width, height)


class TestSaveFigure:
    def setup(self):
        self.f = partial(lp.save_figure, 'filename', 'directory', ['png'])

    def test_raises_error_if_directory_does_not_exist(self):
        with patch('matplotlib.pyplot.tight_layout'), \
                patch('matplotlib.pyplot.savefig',
                      side_effect=FileNotFoundError):
            with pytest.raises(FileNotFoundError):
                self.f(mkdir=False)

    def test_raises_error_if_directory_is_file(self):
        with patch('matplotlib.pyplot.tight_layout'), \
                patch('pathlib.Path.is_file', return_value=True):
            with pytest.raises(NotADirectoryError):
                self.f()

    def test_raises_error_if_no_permission_directory_does_not_exist(self):
        with patch('matplotlib.pyplot.tight_layout'), \
                patch('pathlib.Path.mkdir', side_effect=PermissionError), \
                patch('matplotlib.pyplot.savefig'):
            with pytest.raises(PermissionError):
                self.f()

    def test_raises_error_if_no_permission_directory_exists(self):
        with patch('matplotlib.pyplot.tight_layout'), \
                patch('pathlib.Path.mkdir'), \
                patch('matplotlib.pyplot.savefig',
                      side_effect=PermissionError):
            with pytest.raises(PermissionError):
                self.f()

    def test_raises_error_if_file_format_not_supported(self):
        with patch('matplotlib.pyplot.tight_layout'), \
                patch('pathlib.Path.mkdir'):
            with pytest.raises(ValueError):
                lp.save_figure('filename', 'directory', exts=['nonexistent'])


    def test_warns_if_no_figures(self):
        with patch('pathlib.Path.mkdir'), \
                patch('matplotlib.pyplot.savefig'):
            with pytest.warns(UserWarning):
                self.f()

    def test_saves_if_all_good(self):
        with patch('matplotlib.pyplot.tight_layout'), \
                patch('pathlib.Path.mkdir'), \
                patch('matplotlib.pyplot.savefig') as mock_savefig:
            self.f()
            assert mock_savefig.called_once()

    def test_saves_if_from_context_manager(self):
        with patch('matplotlib.pyplot.tight_layout'), \
                patch('pathlib.Path.mkdir'), \
                patch('matplotlib.pyplot.savefig') as mock_savefig:
            self.f(from_context_manager=True)
            assert mock_savefig.called_once()


class TestFigure:
    def test_default_size_is_figure_size(self):
        default_size = lp.figure_size()

        with patch('matplotlib.figure.Figure.set_size_inches') as mock_set, \
                patch('latexipy.latexipy.save_figure'):
            with lp.figure('filename'):
                pass

            mock_set.assert_called_once_with(*default_size)

    def test_figure_size_is_kwarg_size(self):
        size = (6, 6)
        with patch('matplotlib.figure.Figure.set_size_inches') as mock_set, \
                patch('latexipy.latexipy.save_figure'):
            with lp.figure('filename', size=size):
                pass

            mock_set.assert_called_once_with(*size)

    def test_parameters_passed_all_kwargs_default(self):
        params = inspect.signature(lp.figure).parameters

        with patch('matplotlib.figure.Figure.set_size_inches'), \
                patch('latexipy.latexipy.save_figure') as mock_save_figure:
            with lp.figure('filename'):
                pass

            mock_save_figure.assert_called_once_with(
                filename='filename',
                directory=params['directory'].default,
                exts=params['exts'].default,
                mkdir=params['mkdir'].default,
                from_context_manager=True,
            )

    def test_parameters_passed_custom_kwargs(self):
        params = inspect.signature(lp.figure).parameters

        with patch('matplotlib.figure.Figure.set_size_inches'), \
                patch('latexipy.latexipy.save_figure') as mock_save_figure:
            with lp.figure('filename', directory='directory', exts='exts',
                           mkdir='mkdir'):
                pass

            mock_save_figure.assert_called_once_with(
                filename='filename',
                directory='directory',
                exts='exts',
                mkdir='mkdir',
                from_context_manager=True,
            )
