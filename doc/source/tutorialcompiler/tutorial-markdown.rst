Markdown processing within tutorials
====================================

The tutorial system uses Markdown as the source representation of
various pieces of a tutorial:

* The main tutorial content

* The tutorial summary

* The credits / acknowledgement / licence text for third-party assets

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
the custom shortcodes.
