.. _making_deployment_zipfile:

Making a deployment zipfile
===========================

We want to be able to host different beta versions of the site at, e.g.,::

  beta.pytch.org/SOME-BUILD-IDENTIFIER



Layout
------

The various components of the site each contribute a 'layer', which is
unzipped under a particular subdirectory.

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
created inside ``webapp-layer.sh``.


Informational content
^^^^^^^^^^^^^^^^^^^^^

Comes from the ``pytch-website`` repo, and produces content in::

  doc/...


Assembly method
---------------

One script for each layer, which emits a zipfile suitable for
unzipping inside the deployment directory.  The top-level script then
merges these zipfiles into one.

If you have the various repos in sibling directories, for
example::

  /home/somebody/dev/pytch-build
  /home/somebody/dev/pytch-vm
  /home/somebody/dev/pytch-webapp
  /home/somebody/dev/pytch-tutorials

then you can use

.. code-block:: bash

  cd /home/somebody/dev/pytch-build/makesite
  ./make-develop.sh SOURCE-BRANCHNAME DEPLOY-BASE-URL

to build a zipfile.  Internally this script sets up some environment
variables then ``exec``\ ’s ``make.sh``.

TODO: Deployment from production (GitHub) repo.

Arguments to this script are:

``SOURCE-BRANCHNAME``
  The branch to check out for ``pytch-vm`` and ``pytch-webapp``
  layers.  The tutorials layer is handled differently because of the
  way it uses branches to represent the content.  TODO: More detail.

``DEPLOY-BASE-URL``
  The path component of the URL from which the site will be served.
  Should start with a slash, to be an absolute path.

for example:

.. code-block:: bash

  ./make-develop.sh develop /beta/1234

The name of the zipfile is emitted to stdout, allowing usage like

.. code-block:: bash

  zipfilename=$(./make-develop.sh develop /beta/1234)

See also:

* :ref:`Local testing of the deployment-ready
  zipfile<testing_deployment_zipfile>` — before deploying, you can
  serve the content exactly as it is in the zipfile.

* :ref:`How to deploy the content to hosting<deploying_to_hosting>` —
  there are some details regarding serving the content in a manner
  required for React apps.