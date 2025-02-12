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

At the moment, the only tags used are:

* ``difficulty`` — what level of challenge the tutorial presents;
  currently one of the strings ``"getting started"``, ``"beginner"``,
  ``"medium"``, and ``"advanced"``;

* ``programKind`` — what representation of a Pytch program does the
  tutorial work with; currently one of the strings ``"flat"`` and
  ``"per-method"``; can be omitted, in which case ``"flat"`` is
  assumed; the strings here match the values of the type
  ``PytchProgram["kind"]`` in the TypeScript front end.

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

* ``orderedProjectAssets`` (optional) — only relevant to "flat"
  tutorials, in which case it determines the order in which the
  project assets are added when creating a tutorial-following project
  or a demo.  If not present, the assets are added in order of the
  most recent commit affecting (adding or modifying) them, with
  most-recently affected assets first.  If present, must be an array
  containing a complete list of the pathnames (within
  ``project-assets``) of all assets.

The property :py:attr:`metadata_text` of the
:py:class:`ProjectHistory` reads the content of the ``metadata.json``
file, from the last tip-commit or from the working directory.  Then
the property :py:attr:`summary_div_from_project_history` adds an HTML
attribute called ``data-metadata-json`` to the ``summary_div``
object. The content of that attribute will be the
:py:attr:`metadata_text` property.  This is an example of what can be
found in the ``summary.html`` file:

.. code-block:: html

  <div class="tutorial-summary" data-metadata-json='{"difficulty": "advanced"}'>
  <!-- tutorial content -->
  </div>

Each individual tutorial's metadata is also provided as the attribute
``data-metadata-json`` in the top-level `div`.


Representation in the output
----------------------------

In the front end, the work of processing the HTML of each tutorial's
``summary_div`` is done in the ``<TutorialSummaryDisplay>`` component.
The parsed metadata object is stored in a slot ``metadata: any``
within the type ``ITutorialSummary``.  The function
``allTutorialSummaries()`` in ``src/database/tutorials.ts`` pulls out
the JSON metadata from the attribute, parses it, and uses the result
as the value of the metadata slot.  Finally, in the
``<TutorialSummaryDisplay>``, we use ``tutorial.metadata`` to look for
a "difficulty" property, and insert a suitable ``<div>`` to show it on
screen.





