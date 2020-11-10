Querying status of all repos
============================

A script

.. code-block:: text

  makesite/pytch-git-status.sh

emits a summary of the status of all repos parallel to the one it is
found in.  For a typical development setup, which has the various
Pytch repos as sibling directories, this allows the developer to check
that their local state is clean before making a deployment build.
