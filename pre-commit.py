#!/usr/bin/env python
import sys
from flake8.hooks import git_hook

COMPLEXITY = -1
STRICT = True

if __name__ == '__main__':
    sys.exit(git_hook(complexity=COMPLEXITY, strict=STRICT, ignore='E501'))
    # Alternatively
    # sys.exit(git_hook(complexity=COMPLEXITY, strict=STRICT,
    #                   ignore=['E501']))
