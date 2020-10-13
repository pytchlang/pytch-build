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

Comes from the ``pytch-ide`` repo.  TODO: Rename to ``pytch-vm``?
Produces files in::

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
(``REACT_APP_SKULPT_BASE``).  The files from the webapp end up in::

  app/...

Informational content
^^^^^^^^^^^^^^^^^^^^^

When this exists, will come from ``pytch-web`` repo, and go to::

  info/...


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
  ( cd /tmp/local-pytch-deployment; unzip $zipfilename )

See also next section for serving this content in the manner required
for React apps.


Local testing of deployment zipfile
-----------------------------------

Can be done via a Docker container running Apache2 with mod-rewrite
enabled.  There is a script which launches a Docker container serving
the contents of a deployment zipfile, which can be used as in:

.. code-block:: bash

  cd makesite/local-server
  ./serve-zipfile.sh "$zipfilename"

where the shell variable ``zipfilename`` has been set as in the
previous section.

See the contents of ``serve-zipfile.sh`` for details of what happens.

   makesite/local-server

which can be built with, e.g.,

.. code-block:: bash

   cd makesite/local-server
   docker build --tag pytch-local-server .

and then run with

.. code-block:: bash

    docker run -dit \
      --name pytch-beta \
      -p 5888:80 \
      -v /tmp/local-pytch-deployment/:/usr/local/apache2/htdocs/ \
      pytch-local-server


TODOs
-----

- Include commit SHA1s in build somewhere.

- Create a build identifier automatically and store build info and
  contributing SHA1s somewhere central.
