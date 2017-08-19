#!/usr/bin/env python
'''Tests for `latexipy` package.'''
import math
from unittest.mock import patch

import matplotlib
import matplotlib.pyplot
import pytest

from latexipy import latexipy as lp


class TestFigSize:
    def setup(self):
        self.width = 345 * 0.9 * lp.INCH_PER_POINT

    def test_defaults(self):
        height = lp.GOLDEN_RATIO * self.width
        assert lp.fig_size() == (self.width, height)

    def test_ratio_no_height(self):
        assert lp.fig_size(fig_ratio=1) == (self.width, self.width)
        assert lp.fig_size(fig_ratio=0.5) == (self.width, self.width/2)

    def test_ratio_height(self):
        dimensions = (self.width, self.width)
        assert lp.fig_size(fig_ratio=1, fig_height=5) == dimensions

    def test_height_no_ratio(self):
        assert lp.fig_size(fig_height=5) == (self.width, 5)

    def test_height_too_high(self):
        with pytest.warns(UserWarning):
            height = lp.MAX_HEIGHT_INCH + 1
            assert lp.fig_size(fig_height=height) == (self.width,
                                                      lp.MAX_HEIGHT_INCH)

    def test_columns(self):
        width = self.width / 2
        height = lp.GOLDEN_RATIO * width
        assert lp.fig_size(n_columns=2) == (width, height)
