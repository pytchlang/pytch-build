Tutorial structure
==================

The ``{base}`` commit of the tutorial should add the ``code.py`` file
with the same contents as the IDE starts off with in the code pane.


Structure on the server
-----------------------

The URL structure of the tutorials is::

  pytch.org/[beta/1234abcd/]
  ├── index.html
  :
  └── tutorials/1234abcd1234abcd1234
       ├── tutorial-index.html
       ├── bunner/
       │   ├── tutorial.html
       │   ├── summary.html
       │   ├── project-assets.json
       │   ├── tutorial-assets/
       │   │   └── summary-screenshot.png
       │   └── project-assets/
       │       └── images/
       │           ├── world.png
       │           ├── car00.png
       :           :   :
       │           └── digit-9.png
       ├── boing/
       │   ├── tutorial.html
       │   ├── summary.html
       │   ├── project-assets.json
       │   ├── tutorial-assets/
       │   │   └── summary-screenshot.png
       │   └── project-assets/
       │       └── images/
       │           ├── robot-normal.png
       │           ├── robot-flash.png
       :           :   :
       │           └── table.png
       :
       etc.

(The ``1234abcd1234abcd1234`` is a shortened SHA1 to avoid false
cacheing of updated tutorial content.)


Structure of HTML fragment
--------------------------

The ``tutorial.html`` file is not a complete HTML page.  It is a
fragment whose top-level element is a ``<div>``, which contains the
*front-matter* and the *chapters* of the tutorial.

The structure is::

   <div class="tutorial-bundle" data-tip-sha1="...SHA1...">
     <div class="front-matter"
          data-complete-code-text="import pytch etc">
       <h1>Bunner!</h1>
       <p>In this tutorial etc.</p>
     </div>
     <div class="chapter-content">  <!-- first chapter -->
       <h2>Making the stage</h2>
       <p>First we make the stage etc.</p>
       <div class="patch-container"
            data-code-as-of-commit="import pytch etc">
         <div class="patch">
           <table> <!-- rows for lines of first hunk of patch --> </table>
           <table> <!-- rows for lines of second hunk of patch --> </table>
         </div>
       </div>
       <p>And then we etc.</p>
       <div class="patch-container"
            data-code-as-of-commit="...">
          <div class="patch">
            <!-- <table>s for hunks of patch -->
          </div>
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

The ``data-tip-sha1`` attribute on the top-level ``div`` notes which
commit the tutorial was generated from.  Currently it's not used but
might one day be part of a 'technical details' report for diagnostics.


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
