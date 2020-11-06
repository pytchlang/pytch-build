Using an external editor
========================

The ``pytch-build`` repo includes a websocket server
``pytchbuild-watch``, which watches a tutorial's ``code.py`` and
``tutorial.md`` files.  If the appropriate environment variable is set,
the webapp attempts to connect to this server.  If successful, the
webapp listens for updates from the server, and live-reloads either the
code or the tutorial content.


Launching the watcher
---------------------

The watcher websocket server can be launched with, for example,

.. code-block:: bash

  cd pytch-tutorials-repo-directory
  pytchbuild-watch qbert

where ``qbert`` here is a directory name within the ``pytch-tutorials``
repo, saying which tutorial to monitor.


Live-reload of code
-------------------

You can then edit ``code.py`` with your editor or development
environment of choice.  Whenever the on-disk file changes, the watcher
will send it to the webapp, which will build and green-flag the project.
This makes it easy for developers with experience of other IDEs or
editors to use their existing workflows with Pytch.  We are not
imagining that it will be the primary method that most users in the
intended audience will use to write Pytch programs, though.


Live-reload of tutorial content
-------------------------------

Once the git history is in a reasonable form for explaining the
development of the project which is the subject of the tutorial, the
author then typically switches to working on the actual tutorial
content.  This is done by working on the ``tutorial.md`` file.  Again,
this can be done in the author's editor of choice.  Whenever the
``tutorial.md`` file changes, the watcher sends the tutorial content to
the webapp, which updates its *Tutorial* tab.

TODO: Currently, getting set up to develop a brand new tutorial is
quite clunky.  We should make this workflow smoother.


Marking the work-in-progress chapter
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

When working on a tutorial, you can include the shortcode

.. code-block:: text

  {{< work-in-progress >}}

in a chapter body to indicate that this is the chapter you're working
on.  The effect of this is that the webapp will navigate to this
chapter on live-reload, with the code in the state it would be had the
student followed carefully up to the end of the *previous* chapter.

TODO: Warn if this is left in for a production build of the tutorials.
