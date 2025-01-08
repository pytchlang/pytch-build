=================
Pytch Build Tools
=================

Tools to assemble website from content, IDE, and tutorials.


Development setup
-----------------

This project uses `poetry <https://python-poetry.org/>`_.

To set up a virtualenv for development and testing::

  poetry install

which will cause *poetry* to create a virtual environment in a
``.venv`` folder.

Then one of::

  poetry run pytest tests

and/or::

  poetry run tox

(which will also build the docs and run ``flake8``), and/or::

  poetry run tox -p

to run ``tox`` tasks in parallel.

For live reload while editing docs, use::

  cd doc
  poetry run sphinx-autobuild --re-ignore '/\.#' source build/html

and then visit the URL mentioned in the output.  (The ``--re-ignore
'/\.#'`` avoids Emacs auto-save files; other editors might require
something analogous.)
