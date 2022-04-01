=================
Pytch Build Tools
=================

Tools to assemble website from content, IDE, and tutorials.


Development setup
-----------------

To set up a virtualenv for development and testing::

  python3 -m venv venv
  source venv/bin/activate
  pip install --upgrade pip
  pip install tox

Then one or both of::

  python setup.py develop
  pip install -r requirements_dev.txt
  pytest tests

and/or::

  tox

(Using ``tox`` will also build the docs and run ``flake8``.)
