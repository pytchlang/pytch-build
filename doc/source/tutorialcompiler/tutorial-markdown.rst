Markdown processing within tutorials
====================================

The tutorial system uses Markdown as the source representation of
various pieces of a tutorial:

* The main tutorial content (in a tutorial's ``tutorial.md`` file)

* The tutorial summary (in a tutorial's ``summary.md`` file)

* The credits / acknowledgement / licence text for third-party assets
  (in commit messages adding those assets)

All of these pieces of Markdown are processed by the
``soup_from_markdown_text()`` function in::

  pytchbuild/tutorialcompiler/fromgitrepo/tutorial_markdown.py

and returned as a ``BeautifulSoup`` object.  This is a two-step
process:

* The ``markdown`` library turns the Markdown source text into HTML.

* The ``BeautifulSoup`` library parses that HTML into a Python object
  representation.


Shortcode processing
--------------------

The ``markdown`` library allows extensions.  The Pytch
tutorial-compiler installs a ``BlockProcessor`` extension to handle
our custom shortcodes.
