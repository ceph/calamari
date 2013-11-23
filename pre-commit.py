#!/usr/bin/env python
import os
import re
import shutil
import subprocess
import sys
import tempfile


# There are lots of variations on this theme online, this
# one was cribbed from https://gist.github.com/oubiwann/3381472

PEP8_ARGS = ["--max-line-length=120"]


def system(*args, **kwargs):
    kwargs.setdefault('stdout', subprocess.PIPE)
    proc = subprocess.Popen(args, **kwargs)
    out, err = proc.communicate()
    return (out or b"").decode("utf-8"), err


def main():
    modified = re.compile('^[AM]+\s+(?P<name>.*\.py)', re.MULTILINE)
    files, file_err = system('git', 'status', '--porcelain')
    files = modified.findall(files)
    tempdir = tempfile.mkdtemp()

    print("Scanning modified files...")
    for name in files:
        print("\t%s" % name)
        filename = os.path.join(tempdir, name)
        filepath = os.path.dirname(filename)
        if not os.path.exists(filepath):
            os.makedirs(filepath)
        with open(filename, 'w') as f:
            system('git', 'show', ':' + name, stdout=f)
    pep8_out, pep8_err = system(*(['pep8'] + PEP8_ARGS + ['.']), cwd=tempdir)
    flakes_out, flakes_err = system('pyflakes', '.', cwd=tempdir)
    shutil.rmtree(tempdir)

    if pep8_out or flakes_out:
        if pep8_out:
            print("\nThe following PEP8 violations were found:\n")
            print(pep8_out)
        else:
            print("\nPEP8 Status: OK\n")
        if flakes_out:
            print("The following Python flakes were found:\n")
            print(flakes_out)
        else:
            print("\nPython Flakes Status: OK\n")
        sys.exit(1)


if __name__ == '__main__':
    main()
