.. _making_deployment_zipfile:

Making a deployment zipfile
===========================

We want to be able to host different beta versions of the site at, e.g.,::

  pytch.org/beta/SOME-BUILD-IDENTIFIER

with the latest beta available at::

  pytch.org/beta/latest/

We also want to make real versioned releases, such that the latest is
available at::

  pytch.org/

This is achieved via a git 'superproject' ``pytch-releases`` which has
the contributing repos as git submodules.



Layout
------

The various components of the site each contribute a 'layer', which is
unzipped under a particular subdirectory.  Most repos are responsible
for making their own layer, via a script

.. code-block:: text

  REPO-ROOT/website-layer/make.sh

However, the tutorials layer is produced differently; see below.


Virtual Machine
^^^^^^^^^^^^^^^

Comes from the ``pytch-vm`` repo.  Produces files in::

  skulpt/...

Tutorials
^^^^^^^^^

Comes from the ``pytch-tutorials`` repo.  The files are not meant for
direct presentation by the user's browser, although no harm will come
if the user does look directly at the files.  The files are intended
to be ``fetch()``\ ’d by the webapp.  Files end up in::

  tutorials/tutorials-index.html
  tutorials/bunner/...
  tutorials/boing/...

This layer is unusual in that it is built by a script in the
``pytch-build`` repo:

.. code-block:: text

  pytch-build/makesite/tutorials-layer.sh

WebApp / IDE
^^^^^^^^^^^^

Comes from ``pytch-webapp`` repo.  This is a React app and so needs to
be built with knowledge of where it will be deployed (via
``PUBLIC_URL``).  The Pytch app in particular also needs to be built
knowing where it will get its Skulpt files from
(``REACT_APP_SKULPT_BASE``), and where it will get tutorial
information from (``REACT_APP_TUTORIALS_BASE``).  The files from the
webapp end up in::

  app/...

To allow a user to directly visit a URL within the app (for example,
``/ide/3``), the web server must be directed to serve ``index.html``
for all non-existent files.  This is done by a ``.htaccess`` file
created inside

.. code-block:: text

  pytch-webapp/website-layer/make.sh


Informational content
^^^^^^^^^^^^^^^^^^^^^

Comes from the ``pytch-website`` repo, and produces content in::

  doc/...


Assembly method
---------------

One script for each layer, which emits a zipfile suitable for
unzipping inside the deployment directory.  A top-level ``make.sh``
script within ``pytch-releases`` calls those scripts, and then merges
the resulting zipfiles into one.

With the superproject ``pytch-releases`` cleanly checked out at either
a particular tagged release, or some other branch,

.. code-block:: bash

  cd /home/somebody/dev/pytch-releases
  ./make.sh

will build the deployment zipfile.  If the repo is currently checked
out at ``releases``, there must also be a tag on that commit, and a
release zipfile is made.  Otherwise a beta zipfile is made.

Note that if the ``pytch-releases`` repo is checked out at the
``releases`` branch, then the contained submodule ``pytch-tutorials``
must also be checked out at its ``releases`` branch.

The name of the zipfile is emitted to stdout, allowing usage like

.. code-block:: bash

  zipfilename=$(./make.sh)

See also:

* :ref:`Local testing of the deployment-ready
  zipfile<testing_deployment_zipfile>` — before deploying, you can
  serve the content exactly as it is in the zipfile.

* :ref:`How to deploy the content to hosting<deploying_to_hosting>` —
  there are some details regarding serving the content in a manner
  required for React apps.

TODO: Explain how to get started with checkout out superproject.
