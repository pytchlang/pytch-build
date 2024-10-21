Unit testing
============

The input data for the tutorial compiler is a Git repo, so the unit
tests use various branches of this repo.

Branch ``unit-tests-commit-0``
  Starting empty-state of the collection of branches for testing.

Branch ``unit-tests-commits``
  A mostly-realistic example of a well-formed tutorial branch.  Used
  to test the 'good path' of the tutorial-compiler code.

Branch ``unit-tests-bad-commits``
  Various malformed commits for testing error handling.

Branches ``unit-tests-dupd-slugs-1`` and ``unit-tests-dupd-slugs-2``
  Branch with duplicated commit-slugs, for testing handling of that
  error.

Branch ``unit-test-catch-apple``
  Script-by-script ("per-method") style of program development.


Fixtures
--------

See the file ``conftest.py`` for fixtures.
