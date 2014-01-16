
Coding style
============

All the python code we write should pass two checks:

- PEP8 (http://www.python.org/dev/peps/pep-0008/), except E501 (line length)
- PyFlakes

Pre-commit hook
---------------

To automatically check your code before committing, a
script is provided for use as a git hook:

::

    calamari $ cd .git/hooks
    hooks $ ln -s ../../pre-commit.py pre-commit


Docstrings
----------

Docstrings in the REST API code are pulled up into the REST API documentation, with
two consequences for developers:

- It is very much worth writing good ``help_text`` attributes on fields and good
  docstrings on ``ViewSet`` classes.
- It is important not to write offhand or overly technical (or profane!) comments
  in the docstrings.  TODOs and FIXMEs should go in comments rather than docstrings.

