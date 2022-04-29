Tools for writing a tutorial
============================

A 'tutorial', as presented by the IDE, consists of text divided into
*chapters*.  Each chapter consists of text interspersed with headings
and other HTML-style structure, as well as *patches* showing the
learner how to change the code at that point in the tutorial.

The project being developed in the tutorial will also need various
*assets*, i.e., images or sounds.

Although in general such a collection of tutorial material might be
generated in different ways, currently we are experimenting with a
workflow based on the *git* version control system.

.. toctree::
   :maxdepth: 1

   tutorial-structure
   fromgitrepo
   tutorial-collection
   tutorial-text-dataflow
   unit-testing

And see also :doc:`../live-reload/index`.
