.. _deploying_to_hosting:

Deployment to hosting provider
==============================

The resulting zipfile can be ``scp``\ ’d to the hosting provider and
unzipped there.

Redirecting to latest beta
----------------------------

For cleaner links, we have a redirect in place from ``latest`` to the
current beta deployment.  Currently this is done manually.  There is
an ``.htaccess`` file in the hosted ``beta/`` directory::

  RewriteEngine   on
  RewriteBase     "/beta/"
  RewriteRule     "^latest/?$"  "build-gSHA/app/"  [R,L]

which can be updated after unzipping the deployment bundle.  In future
this mechanism will be automated or superseded.

Redirecting to current release
------------------------------

A release zipfile contains a file

.. code-block:: text

  releases/X.Y.Z/toplevel-dot-htaccess

ready to be used as a top-level ``.htaccess`` file.  This is copied
manually on the host, to keep a human in the loop for final
deployment.  This mechanism also allows rolling back to a previous
release by re-copying an earlier release's htaccess file.
