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

Then one or both of::

  poetry run pytest tests

and/or::

  poetry run tox

(which will also build the docs and run ``flake8``).

  poetry run tox -p

will run ``tox`` tasks in parallel.

For live reload while editing docs, first enter a shell which has the
poetry virtualenv activated by doing::

  poetry shell

then within that shell, run::

  cd doc
  sphinx-autobuild --re-ignore '/\.#' source build/html

and then visit the URL mentioned in the output.  (The ``--re-ignore
'/\.#'`` avoids Emacs auto-save files; other editors might require
something analogous.)
