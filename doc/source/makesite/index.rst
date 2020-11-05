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
