=================
Pytch Build Tools
=================

Tools to assemble website from content, IDE, and tutorials.


Development setup
-----------------

To set up a virtualenv for development and testing::

  virtualenv -p python3 venv
  source venv/bin/activate
  pip install tox

Then one or both of::

  python setup.py develop
  pip install -r requirements_dev.txt
  pytest tests

and/or::

  tox
