"""
Tests the setup.py script by running ``pip install gae_installer=={version}``
in a temporarily activated virtual environment.
"""

import os
import unittest
import sys

import version
import test


class TestPostRelease(test.Test):
    def _install(self):
        os.system('pip install gae_installer=={}'.format(version.full_version))


if __name__ == '__main__':
    if sys.version_info.major == 2 and sys.version_info.minor >= 7:
        unittest.main()
    else:
        sys.exit('GAE Installer requires Python 2.7 or higher!')