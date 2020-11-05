Local testing of deployment zipfile
===================================

Can be done via a Docker container running Apache2 with mod-rewrite
enabled.  There is a script which launches a Docker container serving
the contents of a deployment zipfile, which can be used as in:

.. code-block:: bash

  cd makesite/local-server
  ./serve-zipfile.sh "$zipfilename"

where the shell variable ``zipfilename`` has been set as in the
previous section.

See the contents of ``serve-zipfile.sh`` for details of what happens.


Deployment to hosting provider
==============================

The resulting zipfile can be ``scp``\ ’d to the hosting provider and
unzipped there.

Redirecting from ‘latest’
-------------------------

For cleaner links, we have a redirect in place from ``latest`` to the
current beta deployment.  Currently this is done manually.  There is
an ``.htaccess`` file in the hosted ``beta/`` directory::

  RewriteEngine   on
  RewriteBase     "/beta/"
  RewriteRule     "^latest/?$"  "build-YYYYMMDDhhmmssZ/app/"  [R,L]

which can be updated after unzipping the deployment bundle.  In future
this mechanism will be automated or superseded.


TODOs
-----

- Include commit SHA1s in build somewhere.

- Create a build identifier automatically and store build info and
  contributing SHA1s somewhere central.
