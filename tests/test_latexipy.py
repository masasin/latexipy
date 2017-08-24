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
import matplotlib.pyplot as plt
import pytest

import latexipy as lp
from latexipy._latexipy import INCH_PER_POINT, GOLDEN_RATIO, MAX_HEIGHT_INCH


class TestLatexify:
    def test_defaults(self):
        with patch('matplotlib.rcParams.update') as mock_update, \
                patch('matplotlib.pyplot.switch_backend') as mock_switch:
            lp.latexify()

            mock_update.assert_called_once_with(lp.PARAMS)
            mock_switch.assert_called_once_with('pgf')

    def test_custom_params(self):
        with patch('matplotlib.rcParams.update') as mock_update, \
                patch('matplotlib.pyplot.switch_backend') as mock_switch:
            params = {'param_a': 1, 'param_b': 2}
            lp.latexify(params)

            mock_update.assert_called_once_with(params)
            mock_switch.assert_called_once_with('pgf')

    def test_custom_backend(self):
        with patch('matplotlib.rcParams.update') as mock_update, \
                patch('matplotlib.pyplot.switch_backend') as mock_switch:
            lp.latexify(new_backend='QtAgg')

            mock_update.assert_called_once_with(lp.PARAMS)
            mock_switch.assert_called_once_with('QtAgg')

    def test_raises_error_on_bad_backend(self):
        with patch('matplotlib.rcParams.update') as mock_update:
            with pytest.raises(ValueError):
                lp.latexify(new_backend='foo')

            mock_update.assert_called_once_with(lp.PARAMS)


def test_revert():
    with patch('matplotlib.rcParams.update') as mock_update, \
            patch('matplotlib.pyplot.switch_backend') as mock_switch:
        lp.latexify()
        lp.revert()
        mock_update.assert_called_with(dict(plt.rcParams))
        mock_switch.assert_called_with(plt.get_backend())


class TestTempParams:
    def test_defaults(self):
        with patch('matplotlib.rcParams.update') as mock_update, \
                patch('matplotlib.pyplot.switch_backend') as mock_switch:
            old_params = dict(plt.rcParams)
            with lp.temp_params():
                mock_update.assert_called_with(old_params)
            mock_update.assert_called_with(old_params)

    def test_font_size(self):
        with patch('matplotlib.rcParams.update') as mock_update, \
                patch('matplotlib.pyplot.switch_backend') as mock_switch:
            old_params = dict(plt.rcParams)
            with lp.temp_params(font_size=10):
                called_with = mock_update.call_args[0][0]
                print(called_with)
                assert all(called_with[k] == 10
                           for k in lp.PARAMS if 'size' in k)
            mock_update.assert_called_with(old_params)

    def test_params_dict(self):
        with patch('matplotlib.rcParams.update') as mock_update, \
                patch('matplotlib.pyplot.switch_backend') as mock_switch:
            old_params = dict(plt.rcParams)
            with lp.temp_params(params_dict={'font.family': 'sans-serif'}):
                called_with = mock_update.call_args[0][0]
                assert called_with['font.family'] == 'sans-serif'
            mock_update.assert_called_with(old_params)

    def test_params_dict_after_font_size(self):
        with patch('matplotlib.rcParams.update') as mock_update, \
                patch('matplotlib.pyplot.switch_backend') as mock_switch:
            old_params = dict(plt.rcParams)
            with lp.temp_params(font_size=10, params_dict={
                    'axes.labelsize': 12,
                    'legend.fontsize': 12,
                    }):
                called_with = mock_update.call_args[0][0]
                assert called_with['font.size'] == 10
                assert called_with['axes.labelsize'] == 12
                assert called_with['axes.titlesize'] == 10
                assert called_with['legend.fontsize'] == 12
                assert called_with['xtick.labelsize'] == 10
                assert called_with['ytick.labelsize'] == 10

            mock_update.assert_called_with(old_params)


class TestFigureSize:
    def setup(self):
        self.width = 345 * 0.9 * INCH_PER_POINT

    def test_defaults(self):
        height = GOLDEN_RATIO * self.width
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
            height = MAX_HEIGHT_INCH + 1
            assert lp.figure_size(height=height) == (self.width,
                                                     MAX_HEIGHT_INCH)

    def test_columns(self):
        width = self.width / 2
        height = GOLDEN_RATIO * width
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
                patch('latexipy._latexipy.save_figure'):
            with lp.figure('filename'):
                pass

            mock_set.assert_called_once_with(*default_size)

    def test_figure_size_is_kwarg_size(self):
        size = (6, 6)
        with patch('matplotlib.figure.Figure.set_size_inches') as mock_set, \
                patch('latexipy._latexipy.save_figure'):
            with lp.figure('filename', size=size):
                pass

            mock_set.assert_called_once_with(*size)

    def test_parameters_passed_all_kwargs_default(self):
        params = inspect.signature(lp.figure).parameters

        with patch('matplotlib.figure.Figure.set_size_inches'), \
                patch('latexipy._latexipy.save_figure') as mock_save_figure:
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
                patch('latexipy._latexipy.save_figure') as mock_save_figure:
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
