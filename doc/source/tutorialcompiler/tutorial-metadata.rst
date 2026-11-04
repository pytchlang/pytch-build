.. _tutorial-metadata:

Tutorial metadata
=================

At the moment, the tutorials are represented as a list. However, this
configuration will get difficult to navigate once the number of
provided tutorials will grow.  Therefore, we want to include the
possibility to filter the tutorials thanks to tags, such as the
difficulty level of the tutorial for example. This will allow an
easier navigation for the user.


Representation in the code
--------------------------

The data is saved in the file ``metadata.json``. Such files can be
found in each tutorial directory.  The top-level entity is an object,
whose JSON representation is as follows:

.. code-block:: text

  {"name_of_tag": "value_of_tag"}

The tags used are:

* ``difficulty`` (required) — what level of challenge the tutorial
  presents; one of the strings ``"getting-started"``,
  ``"beginner"``, ``"medium"``, and ``"advanced"``;

* ``programKind`` (optional) — what representation of a Pytch program
  does the tutorial work with; one of the strings ``"flat"`` and
  ``"per-method"``; can be omitted, in which case ``"flat"`` is
  assumed; the strings here match the values of the type
  ``PytchProgram["kind"]`` in the TypeScript front end.

* ``language`` (optional) — the language the tutorial is written in;
  one of the strings ``"en"``, ``"de"``, and ``"ga"``; can be
  omitted, in which case ``"en"`` is assumed.  This list is kept in
  sync by hand with ``kLanguagePreferenceOrder`` in the front end's
  ``src/model/languages.ts``.

* ``tutorialId`` (optional) — identifies "the same" tutorial across
  its translations; all translations of a tutorial should have the
  same ``tutorialId``.  Must be a non-empty string.  Can be omitted,
  in which case the tutorial's top-level directory name is used.  No
  two tutorials in a collection may have the same ``tutorialId`` and
  ``language``.

  A translation is otherwise an ordinary tutorial, with its own branch
  and its own top-level directory, conventionally the original's
  directory name with a ``--<language>`` suffix, e.g.,
  ``boing--ga``.  The directory name identifies one tutorial in one
  language, so a tutorial directory must never be renamed or reused.

* ``groupedProjectAssets`` (optional) — which project assets should be
  grouped into "entries" for the purposes of the media library.
  Should be an array of objects, each of which has properties:

  * ``name`` — the name of the media library entry to create;
  * ``assets`` — an array of asset paths (within ``project-assets``)
    to be gathered into that entry.

  For each asset not mentioned in a ``groupedProjectAssets``, a
  singleton entry is created with the same name as the (only) asset
  within it.  If ``groupedProjectAssets`` does not appear in the
  metadata, all assets are created as singleton media library entries.

* ``orderedProjectAssets`` (optional) — determines the order in which
  the project assets are added when creating a tutorial-following
  project or a demo, whatever the ``programKind``.  (Currently only
  "flat" tutorials use it.)  If not present, the assets are added in
  order of the most recent commit affecting (adding or modifying)
  them, with most-recently affected assets first.  If present, must
  be an array containing a complete list of the pathnames (within
  ``project-assets``) of all assets.

* ``intentionallyUnusedAssets`` (optional) — only relevant to
  "per-method" tutorials.  An array of the pathnames (within
  ``project-assets``) of assets which are part of the project but are
  not used in its code.  Without this, the build fails if an asset
  added in the commit history is not used by any ``Costume`` or
  ``Backdrop`` in the code.

The tag ``displayName`` must *not* appear in ``metadata.json``; it is
derived by the build (see below).  Nor may any tag not listed above
appear; this catches misspellings of the optional tags, which would
otherwise be silently ignored.

The ``groupedProjectAssets``, ``orderedProjectAssets``, and
``intentionallyUnusedAssets`` tags are used only by the build.  A
translation needs its own values of these, because they are checked
against that translation's own assets.


Validation and defaults
-----------------------

The property :py:attr:`metadata_text` of the
:py:class:`ProjectHistory` reads the content of the ``metadata.json``
file, from the last tip-commit or from the working directory.  The
property :py:attr:`completed_metadata` parses this, checks the values
of ``difficulty``, ``programKind``, ``language``, and ``tutorialId``
as described above, and fills in defaults for any of ``programKind``,
``language``, and ``tutorialId`` which are absent.  It also adds the
derived ``displayName``: the text of the sole ``<h1>`` of the
tutorial's ``summary.md``.  The build fails if the summary does not
have exactly one ``<h1>``, or if that ``<h1>``'s text is empty.

The ``summary.md`` title is the tutorial's canonical display name,
because it is the title shown in the front end's list of tutorials.
The ``tutorial.md`` file must also have exactly one ``<h1>``, before
its first ``<h2>``; the front end shows this as the title of the
tutorial's front matter.  The two titles need not match.


Representation in the output
----------------------------

The build writes the property :py:attr:`emitted_metadata` of the
:py:class:`ProjectHistory` as the HTML attribute
``data-metadata-json`` of:

* each tutorial's summary ``<div>``, in ``tutorial-index.html`` and in
  ``<tutorial-directory>/summary.html``;

* each tutorial's top-level ``<div>`` in
  ``<tutorial-directory>/tutorial.html``.  This includes the output of
  the live-reload server.

The emitted metadata has exactly the slots ``programKind``,
``difficulty``, ``language``, ``tutorialId``, and ``displayName``, all
always present (see ``EMITTED_METADATA_SLOTS``).  The build-only slots
are not emitted.  All defaulting happens in the build; the front end
never applies a default.  For example:

.. code-block:: html

  <div class="tutorial-summary" data-metadata-json='{"programKind":
    "flat", "difficulty": "advanced", "language": "en", "tutorialId":
    "boing", "displayName": "Boing — a Pong-like game"}'>
  <!-- tutorial content -->
  </div>

The front end parses this metadata with a strict schema, which
requires all the above slots and rejects any others.  Therefore,
adding a slot to the emitted metadata is a two-step change: first
deploy a front end which accepts the new slot (as optional), then
deploy tutorials built to emit it.  The opposite order would make
cached front-end bundles reject the tutorial index.
