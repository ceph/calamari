
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
