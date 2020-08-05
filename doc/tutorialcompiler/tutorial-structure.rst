Tutorial structure
==================

TODO: What is the starting point for the code?  The ``{base}`` commit
of the tutorial should add the ``code.py`` file with the same contents
as the IDE starts off with in the code pane.  This changed with the
introduction of the auto-registration code, so might need review.


Structure on the server
-----------------------

The URL structure of the tutorials is::

  pytch.org/[betas/1234abcd/]
  ├── index.html
  ├── about.html
  ├── pytch.css
  ├── pytch-gui.js
  :
  └── tutorials/
       ├── index.json  ## TODO: Would this be useful?
       ├── bunner/
       │   ├── tutorial.html
       │   └── project-assets/
       │       └── images/
       │           ├── bunner-background.png
       │           ├── car00.png
       :           :   :
       │           └── digit-9.png
       ├── boing/
       │   ├── tutorial.html
       │   └── project-assets/
       │       └── images/
       │           ├── left-bat.png
       │           ├── right-bat.png
       :           :   :
       │           └── digit-9.png
       :
       etc.


Structure of HTML fragment
--------------------------

The ``tutorial.html`` file is not a complete HTML page.  It is a
fragment whose top-level element is a ``<div>``, which contains the
*front-matter* and the *chapters* of the tutorial.

The structure is::

   <div class="tutorial-bundle">
     <div class="front-matter"
          data-complete-code-text="import pytch etc">
       <h1>Bunner!</h1>
       <p>In this tutorial etc.</p>
     </div>
     <div class="chapter-content">  <!-- first chapter -->
       <h2>Making the stage</h2>
       <p>First we make the stage etc.</p>
       <div class="patch"
            data-code-as-of-commit="import pytch etc">
         <table> <!-- rows for lines of first hunk of patch --> </table>
         <table> <!-- rows for lines of second hunk of patch --> </table>
       </div>
       <p>And then we etc.</p>
       <div class="patch">
         <!-- <table>s for hunks of patch -->
       </div>
     </div>
     <div class="chapter-content">  <!-- second chapter -->
       <h2>Adding our hero</h2>
       <p>Next we bring in the rabbit etc.</p>
       <!-- more <p>s, patch-<div>s, <h3>s, etc. -->
     </div>
     <!-- further chapters -->
   </div>


The ``<table>`` elements of class ``patch`` have their bodies grouped
into ``<tbody>>`` elements, grouping together each kind of hunk line —
*add*, *delete*, or *unchanged*.

An *add* ``<tbody>`` has an attribute ``data-added-text`` whose value
is the text added by that group of lines.  The IDE picks this up to
allow the *copy* functionality to work.


TODOs
-----

Syntax highlighting via Pygments?

Launch at any chapter via query param.  (Front-matter is 'chapter 0'.)
The History API for browsers might make a nice addition, to allow you
to bookmark a particular chapter of the tutorial.

Challenges for the learner / alternative development approaches: GS
notes/asks: *If I wanted to show an alternative way to code something
in the tutorial then I wonder if I could make a branch and have that
somehow presented in the tutorial as an alternative to the main-line
of the tutorial? I wouldn't want to do this much because I think it
would make the tutorial very untidy and hard to navigate.*
