"Per-method" tutorials
======================

We support tutorials for program represented in the "per-method" style
(also known internally as "structured" or "Pytch junior").  The
underlying source of truth for such a tutorial remains a linear git
history for a single file of flat Python code, coupled with a markdown
file for the tutorial text.  For these tutorials, we also bring in the
idea of progressive revelation of help for the user, and a different
presentation of changes to the code.


Writing a per-method tutorial
-----------------------------

The learner will work with the program using the per-method
representation and interface.  However, the source of truth for the
tutorial is a normal flat Pytch program, obeying some constraints to
ensure that it has a direct equivalent per-method representation.

Each well-defined change to the user's program should be a commit in
the git history.  Such commits can be as short as only one or two
lines long for introductory tutorials.  Every commit must be of a
known and well-defined semantic kind, described below.

Each commit is presented as part of a "learner task" in the front end.
The learner tasks are marked up in the tutorial source by means of
begin and end shortcodes:

* ``{{< learner-task >}}`` to mark the beginning of a learner task

* ``{{< /learner-task >}}`` to mark the end of a learner task

In between these two shortcode markers, the learner task consists of
*introductory text* and a sequence of one or more *learner-task help*
sections.  The introductory text starts at the start of the learner
task, and ends just before the first ``{{< learner-task-help >}}``
marker shortcode.  The text should describe in fairly broad,
high-level terms the goal of the change.

Each ``{{< learner-task-help }}`` shortcode indicates the start of a
learner help section.  The help sections should provide more and more
detail about how to achieve the goal.  The last learner help section
should include "the answer", i.e., tell the learner exactly what
change to their program is needed.  This is done by referring to a
tagged commit using a shortcode like

* ``{{< jr-commit COMMIT-SLUG COMMIT-KIND OPTIONAL-COMMIT-ARGS >}}``

where:

* *COMMIT-SLUG* is the label identifying this commit, as found in its
  special tag commit message (e.g., ``{#increment-score}``);

* *COMMIT-KIND* identifies the kind of commit this is, for example one
  which adds a new script to a sprite; see below for details of the
  different kinds of commit;

* *OPTIONAL-COMMIT-ARGS* are any arguments the particular commit-kind
  requires; see below for details.

Kinds of commit
~~~~~~~~~~~~~~~

Currently the tutorial author must indicate what kind of change is
being made by each commit, by supplying one of the following
commit-kinds.  The ``add-medialib-appearance`` kind takes one
argument; the other kinds take no arguments.

``add-sprite``

    Add a new sprite to the project.  Such a commit should add code
    text for a new Sprite-derived class whose body is the assignment
    statement ``Costumes = []``

``add-medialib-appearance`` *DISPLAY-IDENTIFIER*

    Add an entry to the list of Costumes (for a Sprite) or Backdrops
    (for the Stage).  Such a commit should add a string literal to the
    appropriate class variable.  The *DISPLAY-IDENTIFIER* is a string
    shown to the learner to help them find the correct appearance in
    the media library.

``add-script``

    Add a script (decorated method) to a sprite.  The code added
    should include the decorator, the method ``def`` line, and a body.
    If the body is just ``pass``, this is treated as empty; otherwise,
    the displayed help will include the given body code.

``edit-script``

    Change exactly one script (decorated method) body in exactly one
    Sprite or the Stage.

``change-hat-block``

    Change exactly one script's decorator in exactly one Sprite or the
    Stage.


Summary theory of operation for compiler
----------------------------------------

An instance of the class ``StructuredPytchProgram`` wraps a
well-formed Pytch program, and provides access to the program's list
of actors, methods, appearances, etc.  An instance of the class
``StructuredPytchDiff`` can provide a "rich commit" instance
representing the change from an "old" state of the program to a "new"
state.  There are different rich-commit classes, one for each kind of
commit (e.g., ``JrCommitAddSprite`` for the ``"add-sprite"``
commit-kind).  These form the interface between the compiler and the
front end.

There are fairly extensive assertions when generating these commits
that the code has undergone the right kind of change.  (E.g., an
"edit-script" commit must change exactly one method-body.)  If any of
these assertions fails, an exception is raised.

A learner task's flat sequence of ``div`` elements, as produced by the
markdown processor, is converted into a nested form before being
written to the final tutorial output.  Each learner-task ``div`` will
contain a "commit ``div``" with the JSON of the rich commit object as
a data attribute.


Future work
-----------

It should be possible to determine the commit-kind automatically.  One
approach would be to just try asking the ``StructuredPytchDiff``
object for every kind of rich-commit kind.  Exactly one such request
should succeed, with all others raising an exception.

As we write more tutorials, other kinds of commit might be needed.
For example, one which adds all the images in a group (e.g., all four
directions of the player's character in Qbert).

It would be good to include costume thumbnails in the "task cards";
this might be made easier with help from the compiler.
