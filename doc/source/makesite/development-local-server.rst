.. _local_development_server:

Testing while developing
========================

A script

.. code-block:: text

  makesite/local-server/dev-server.sh

is provided which launches a five-way ``tmux`` session.  The panes
contain individual shell scripts for the following pieces:

* ``dev-server-webapp.sh`` — An ``npm``-based server for the React
  webapp itself.  Uses various environment variables (including some
  loaded from a ``.env`` file) to configure the webapp's behaviour.
* ``dev-server-live-reload-watch.sh`` — A websocket server for
  live-reload of code and tutorial content.  See
  :doc:`../live-reload/index` for details of this mechanism.  This
  piece only does anything if the environment variable
  ``PYTCH_IN_PROGRESS_TUTORIAL`` is set.
* ``dev-server-skulpt.sh`` — A Python-based web server for the
  Skulpt-based VM.
* ``dev-server-tutorials.sh`` — A Python-based web server for the
  tutorial bundle and components.
* ``dev-server-medialib.sh`` — Builds the media library and serves it
  over HTTP.

For example,

.. code-block:: shell

  cd makesite/local-server
  PYTCH_IN_PROGRESS_TUTORIAL=space-invaders ./dev-server.sh

will launch the required servers for working on a tutorial in a
subdirectory ``space-invaders`` of the ``pytch-tutorials`` repo.

Everything is tied together with a bundle of environment variables.
See the individual scripts for details.


Serving demo zips
-----------------

Experimental: The local development server specifies that demo zips
can be found at ``localhost:8126`` but does not launch a server at
that port.  The companion repo ``pytch-demos`` has its own development
server for this.  In live deployments, the demos are maintained
separately from the release / beta process.  This arrangement might
evolve as we gain experience with the mechanism for providing
non-tutorial demos.
