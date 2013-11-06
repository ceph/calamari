
Things to know:

- You've gotta use brew's python, not the one that comes with OSX, that
  means setting --python=/usr/local/bin/python2.7 when creating your
  virtualenv
- You've gotta enable site-packages in order to get a brew-built
  pycairo, that means setting --site-packages when creating
  your virtualenv
- Use brew to install cairo and pycairo
- To use nodeenv to install a local node setup, you must have
  the 'full' XCode installed, not just the 'Command Line' version.
