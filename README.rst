========
LaTeXiPy
========


.. image:: https://img.shields.io/pypi/v/latexipy.svg
        :target: https://pypi.python.org/pypi/latexipy
        :alt: PyPI version

.. image:: https://img.shields.io/travis/masasin/latexipy.svg
        :target: https://travis-ci.org/masasin/latexipy
        :alt: Test status

.. image:: https://readthedocs.org/projects/latexipy/badge/?version=latest
        :target: https://latexipy.readthedocs.io/en/latest/?badge=latest
        :alt: Documentation Status

.. image:: https://pyup.io/repos/github/masasin/latexipy/shield.svg
        :target: https://pyup.io/repos/github/masasin/latexipy/
        :alt: Updates

.. image:: https://img.shields.io/badge/license-MIT-blue.svg
        :target: https://github.com/masasin/latexipy
        :alt: MIT License


Generate beautiful plots for LaTeX using your existing Matplotlib-based code.

You can also use this package to generate plots without using LaTeX. Just don't run ``lp.latexify()``.

* Free software: MIT license
* Documentation: https://latexipy.readthedocs.io.


Usage
-----

.. code-block:: python
    :caption: myfile.py

    import latexipy as lp

    lp.latexify()  # Change to a serif font that fits with most LaTeX.

    with lp.figure('filename'):  # saves in img/ by default.
        draw_the_plot()

.. image:: https://github.com/masasin/latexipy/raw/master/examples/img/sincos_defaults.png

.. code-block:: latex
    :caption: mydoc.tex

    \usepackage{pgf}
    \input{filename.pgf}


See the examples_ directory for some example code, their resulting images, as well as an example LaTeX file and its output PDF_.

.. _examples: https://github.com/masasin/latexipy/tree/master/examples
.. _PDF: https://github.com/masasin/latexipy/raw/master/examples/example.pdf


Features
--------

* Automatically generate multiple plot types, such as PDF, PNG, and PGF for LaTeX.
* Works with all Matplotlib-based packages, including Seaborn and Pandas.
* Allows for easily changing the style temporarily.


Credits
---------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage

