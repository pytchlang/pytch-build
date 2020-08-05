Compiling a tutorial from a Git repository
==========================================

Usage
-----

Create a ``git`` repo with a particular structure.  TODO: Move
description from Google doc into here.  Run the command-line tool to
produce a zipfile of the tutorial html bundle and the project assets.
Unzip into the web content directory.


Internals
---------

The following is cut/paste from an earlier version of the tool and
needs revising:

We collect the tutorial into chapters; each chapter is a list of
elements.  An 'interactive patch' element gets turned into a DIV with
the relevant patch as a table, as well as extra metadata.  Each
chapter starts with an H2 and continues until either the next H2 or
the end of the whole document.


Outline design
--------------

Major pieces are:

.. py:class:: ProjectAsset

    Graphics or sound asset belonging to project

    Distinction is (or will be) against *tutorial* asset, e.g., a
    screenshot to be included in the presentation.

    Contains path (QN: relative to what?) and data-bytes.  Relative to
    git root?

.. py:class:: ProjectCommit

    Individual commit from history

    Construct from repo and commit-OID.

    Different types of commit:

    - Identified commit belonging to project being developed: Expect
      this to be used in tutorial.
    - Addition of asset/s: E.g., adding a graphics file.
    - The unique base commit: How much code should there be in this?
      Just the ``import`` stuff at the top?
    - Updates just to the raw markdown of the tutorial text: Ignored
      when generating tutorial.
    - TODO: Addition of tutorial assets, e.g., screenshots.

    .. py:attribute:: added_assets

        A list of :py:class:`ProjectAsset` instances.

        QN: A given ProjectCommit might add more than one asset.  We
        also have an explicit (but possibly redundant) tag in the
        commit message to flag a commit as adding assets.  What if the
        tag and the actual commit disagree?  Should it be possible to
        do :py:attr:`added_assets` on any :py:class:`ProjectCommit`?
        Should this return an empty list if there are no added assets?
        Emit a warning if it adds assets but doesn't include the
        ``add-project-assets`` tag (or vice versa)?

    .. py:attribute:: maybe_identifying_slug

        The text of the identifying slug, if one present, otherwise None.

    .. py:attribute:: is_base: bool

        Whether the commit message contains the magic 'this is the base' tag.

    .. py:attribute:: modified_tutorial_text

        Whether the commit updates just the
        :samp:`{TOP-LEVEL-DIRECTORY}/tutorial.md` file, and is not
        otherwise tagged.


.. py:class:: ProjectHistory

    Chain of git commits developing project from scratch.

    Read in repo, starting at some commit and tracing back through
    first parent until a given end commit.  Really just a list of
    `ProjectCommit` objects.

    Ctor inputs:

    - Repo directory.  Branch name with latest commit in history to
      process.  (QN: Might one day want to support more than one
      'final' branch, to support 'now you try this', or 'alternatively
      we could have implemented this feature like this.)


.. py:class:: TutorialRawText

    Document with tutorial text and DIVs for rich content

    Read in tutorial text, break down into sections, identify pieces
    where augmentation from the git repo is required.

    Ctor inputs:

    - Filename of markdown file.

    Representation:

    Soup?  Whose job is it to manipulate the soup to add the
    attributes etc. to the DIVs for interactive commits?  And who owns
    the soup?  Probably OK for it to live in the TutorialRawText, but
    for the convention to be that when that TutorialRawText is handed
    over to the TutorialBundle ctor, the contained soup is available
    for the TutorialBundle to mutate.

.. py:class:: TutorialBundle

    Filesystem fragment (tutorial.html, assets/ directory)

    Representation of everything needed to emit the tutorial bundle:

    - Raw text (`TutorialRawText`)
    - Git repo / project history (:py:class:`ProjectHistory`)

    Constructed from the above two things.

    .. py:method:: write_zipfile(filename)



TODOs
=====

Validation and/or warnings would be nice, including:

* each project asset is added once and then left alone
* each project asset has a path within the 'project-assets/' directory
* exactly those commits tagged as adding project assets do in fact add project assets
* all changes to the code file are tagged with identifier-slugs
* all untagged commits are changes to the tutorial.md file
* there is exactly one base in the history
* the history has no merges
