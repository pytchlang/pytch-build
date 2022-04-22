Data-flow of tutorial text
==========================

This section gives a summary of how a tutorial's text content gets
from the ``pytch-tutorials`` git repo through to the webapp.


Source
------

The tutorial text for a particular tutorial is in the file
``tutorial.md`` at top-level in that tutorial's directory.


Representation in code: ``ProjectHistory``
------------------------------------------

An instance of the class ``ProjectHistory`` is built from a particular
commit of a repo.  That commit should be the tip of the tutorial's
branch.

The ``ProjectHistory`` instance has a cached-property
``tutorial_text``, whose value is the contents of the ``tutorial.md``
file (as a string).

(There is a detail here allowing the ``ProjectHistory`` to read the
committed contents of the ``tutorial.md`` file, or the contents of
that file as it is in the working directory of the repo.  This latter
option allows for more rapid development while writing tutorial text.)


Representation in HTML
----------------------

The function ``tutorial_div_from_project_history`` takes a
``ProjectHistory`` instance, and returns the top-level ``DIV``
representing the tutorial (as a ``BeautifulSoup`` element).  This is
done in two stages:

* Conversion of Markdown to a ``BeautifulSoup`` element — done by the
  function ``soup_from_markdown_text()``, which handles the custom
  shortcodes;

* Re-organisation of that HTML element into ``DIV``\ s representing
  the front matter, chapters, extra information for the code patches
  to be shown to the learner, etc.  This is the bulk of the work of
  ``tutorial_div_from_project_history()``.


Representation in code: ``TutorialBundle``
------------------------------------------

An instance of ``TutorialBundle`` contains all the information needed
to write files, for one particular tutorial, to a zipfile.  The HTML
which came from the ``tutorial.md`` file is held in the
``TutorialBundle`` instance's ``tutorial_html`` attribute.

A ``TutorialBundle`` is constructed from a ``ProjectHistory``.


Storage of one tutorial into zipfile
------------------------------------

The ``TutorialBundle.write_to_zipfile()`` method writes the files into
a given already-opened zipfile.  For a tutorial ``catch-the-rabbit``,
the files written are (using made-up examples for the project assets):

* ``catch-the-rabbit/tutorial.html`` — the ``tutorial_html`` as
  described above;

* ``catch-the-rabbit/summary.html`` — HTML for the tutorial summary,
  derived from the ``summary.md`` file using a very similar process to
  how the ``tutorial.md`` file is processed.

* ``catch-the-rabbit/project-assets.json`` — a manifest describing the
  assets the project itself needs (e.g., graphics or sounds).

* ``catch-the-rabbit/project-assets/rabbit.png``,
  ``catch-the-rabbit/project-assets/carrot.png``, etc. — project
  assets.


Storage of all tutorials into zipfile
-------------------------------------

The Pytch site has a collection of tutorials.  This is represented by
the ``TutorialCollection`` class, which is a wrapper round a
dictionary mapping tutorial name to ``TutorialInfo`` instance.  (TODO:
Looks like the names aren't used; could replace just with list of
``TutorialInfo``?)

A ``TutorialInfo`` instance gathers a tutorial's name, branch-name,
and a ``ProjectHistory`` instance representing that tutorial.

The ``TutorialCollection`` instance can write one big zipfile.  Within
that zipfile, each tutorial's data is stored in a directory (such as
the ``catch-the-rabbit`` example above).  At top-level in the zipfile
is the ``tutorial-index.html`` file, which has content taken from each
tutorial's ``summary.md`` file.  The structure of
``tutorial-index.html`` is described :ref:`elsewhere
<tutorial-index-html-structure>`.


Serving from site
-----------------

The contents of that big zipfile are served from a common prefix on
the site.  The prefix is of the form
``tutorials/1234abcd1234abcd1234``, where the hex string is a
'deployment ID', which is the shortened SHA1 for the commit of the
``pytch-releases`` repo from which the deployment was created.


Consumption by webapp
---------------------

A summary of how the tutorial data is consumed by the webapp is
available in :doc:`its developer documentation
<../../webapp/developer/tutorials>`.
