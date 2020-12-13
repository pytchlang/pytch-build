.. _testing_deployment_zipfile:

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

This local copy of Pytch can be explored interactively by going to
``http://localhost:5888/``, or :ref:`tested via
Cypress<testing_zipfile_with_Cypress>`.

A *release* zipfile will have in place the redirect from the root to
the app, but for a *beta* release, you will have to manually navigate
to the required subdirectory.
