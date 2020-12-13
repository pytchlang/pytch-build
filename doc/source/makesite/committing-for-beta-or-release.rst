Making a beta or release commit
===============================

Releases are managed via the git superproject ``pytch-releases``.


Committing a new beta/development version
-----------------------------------------

The process of gathering together the required versions of
contributing subprojects into a beta release is as follows.

The individual subprojects should be brought up to date with their
origin repos, via, for example

.. code-block:: bash

  cd pytch-vm
  git pull origin

At this point, the ``pytch-releases`` superproject will show changes
in the submodule commits.  Commit those changes onto ``develop``.  At
this point, ``make.sh`` will produce a new beta zipfile.


Committing a new release version
--------------------------------

A release is made as a non-fast-forward merge in to ``releases`` from
``develop``.  That commit on ``releases`` is then given a tag of the
form ``vX.Y.Z``.

Running ``make.sh`` inside ``pytch-releases`` when it is checked out
at a tagged commit on the ``releases`` branch will produce a release
zipfile.
