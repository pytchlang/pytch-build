Tutorial metadata
===================

At the moment, the tutorials are represented as a list. However, this
configuration will get difficult to navigate once the number of
provided tutorials will grow.  Therefore, we want to include the
possibility to filter the tutorials thanks to tags, such as the
difficulty level of the tutorial for example. This will allow an
easier navigation for the user.


Representation in the code
--------------------------

The data is saved in the file ``metadata.json``. Such files can be
found in each tutorial directory.  The top-level representation is a
dictionary, whose syntax is as follows:

.. code-block:: text

  {"name_of_tag": "value_of_tag"}

At the moment, the only tag created is the difficulty level associated
to each tutorial.

The property ``metadata_text()`` of the ``ProjectHistory class`` reads
the content of the ``metadata.json`` files, from the last tip-commit
or from the working directory.  Then the property
``summary_div_from_project_history()`` adds an HTML attribute called
``data-metadata-json`` to the ``summary_div`` object. The content of
that attribute will be the ``metadata_text`` property.  This is an
example of what can be found in the ``summary.html`` file:

.. code-block:: html

  <div class="tutorial-summary" data-metadata-json='{"difficulty": "advance"}'>
  <!-- tutorial content -->
  </div>


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





