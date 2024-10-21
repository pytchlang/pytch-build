Regression testing
==================

This is manual currently.

Generate a zipfile of all tutorials under the "old" code by checking
out the old code and then doing::

  poetry run pytchbuild-gather-tutorials \
    -o /tmp/tuts-old.zip \
    -r $PYTCH_TUTORIALS_REPO_ROOT \
    --index-source RECIPES_TIP

Then generate a corresponding zipfile for the output under the "new"
code, by checking out the new code and then doing::

  poetry run pytchbuild-gather-tutorials \
    -o /tmp/tuts-new.zip \
    -r $PYTCH_TUTORIALS_REPO_ROOT \
    --index-source RECIPES_TIP

Unzip these two into their own directory structures and compare::

  cd /tmp
  mkdir tuts-old tuts-new
  ( cd tuts-old && unzip -q ../tuts-old.zip )
  ( cd tuts-new && unzip -q ../tuts-new.zip )
  diff -Naur tuts-old tuts-new
