Tutorial collection
===================

On launching the Pytch IDE, the user has a choice of tutorials.  To
know what tutorials are available, the IDE loads the file
``tutorials-index.html`` and uses it to populate the *List of
tutorials* pane.

The ``pytchbuild-gather-tutorials`` utility builds this
``tutorials-index.html`` file and includes it in the resulting
zipfile.  To know what tutorials belong in the collection, it reads
the file ``index.yaml`` in the root of the ``pytch-tutorials`` repo's
working directory.  See below for the workflow for changing this file.
The utility can also, if requested, create a new *release* of the
tutorial collection.


Creating a zipfile of all tutorials
-----------------------------------

Running the command::

    pytchbuild-gather-tutorials -o /tmp/tutorials.zip

will read the current working copy of the``index.yaml`` file, and use
it to create the zipfile given by the ``-o`` argument.


Structure of tutorial list HTML
-------------------------------

The ``tutorial-index.html`` file has the following structure::

    <div class="tutorial-index" data-collection-oid="...SHA1...">
      <div class="tutorial-summary" data-tutorial-name="bunner">
        <p class="image-container">
          <img alt="Screenshot" src="summary-screenshot.png"/></p>
        <h1>Bunner — a Frogger-like game</h1>
        <p>In this tutorial we'll ...</p>
      </div>
      <div class="tutorial-summary" data-tutorial-name="boing">
        <p class="image-container">
          <img alt="Screenshot" src="summary-screenshot.png"/></p>
        <h1>Boing — a Pong-like game</h1>
        <p>This tutorial shows you ...</p>
      </div>
    </div>

The ``SHA1`` is the git oid of the commit, at the tip of the
``release-recipes`` branch, from which the collection was created.
See `Releasing a new version of the tutorial collection`_ for more
details.


Archive of releases
-------------------

Each tutorial is developed in its own branch, allowing history to be
re-written while the tutorial is being developed.

We would like to ensure reproducibility for the tutorials, in that we
would like to be able to:

- go back to a particular history of some individual tutorial;

- remember what tutorials, and with what histories, were in the
  collection at different times.

Both needs are met by having a ``releases`` branch, *which authors do
not directly commit to*.  Instead, the workflow for releasing a new
version of the tutorial collection is as follows.


Releasing a new version of the tutorial collection
--------------------------------------------------

The maintainer checks out the branch ``release-recipes``, which
contains just the ``index.yaml`` file.  The maintainer might be
releasing a new version of the tutorial collection because:

- one of the individual tutorials has been revised — perhaps its
  author has edited the wording of the tutorial text, or re-arranged
  the history of the commits developing the ``code.py`` file;

- the collection itself has been revised — perhaps we have added a new
  tutorial, or removed an old one, or changed the order of the
  tutorials in the collection.

In the first case, the ``index.yaml`` file does not need to change.
(Unless the author renamed the branch containing the tutorial in
question.)

In the second case, it does, and so the maintainer edits
``index.yaml`` and commits that change to the ``release-recipes``
branch.

Either way, the maintainer runs, from somewhere in the tutorials
repo::

    pytchbuild-gather-tutorials --make-release -o /tmp/tutorials.zip

This will produce the tutorials bundle zipfile as usual, but then also
make a commit to the ``releases`` branch.  The commit to ``releases``
has a hard-coded generic commit message.  Ideally, the maintainer will
check out the ``releases`` branch and reword its tip commit's message
to something more meaningful.  This can be done with::

    git commit --amend --only

on the command line, or ``cw`` (Commit reWord) if using `Magit
<https://magit.vc/>`_.  Rewording the commit's message must be done
*before* pushing upstream, to avoiding rewriting upstream history.

If the working copy of the ``index.yaml`` file differs from the
version stored at the tip of ``release-recipes``, an error will be
thrown.  This is to guard against creating an inconsistent release.


Details: Commits on ``releases``
--------------------------------

A commit to the ``release`` branch has many parents.  Its first parent
is the previous state of the ``release`` branch, as usual.  Its other
parents are, first, the then-current tip of the ``release-recipes``
branch, followed by the then-current tips of the tutorials' branches,
i.e., as they were when they were used to build the tutorial
collection.  In this way, tutorials' individual historical commit
histories are preserved.
