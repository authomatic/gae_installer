import unittest
import os
import sys
import shutil


VENV_NAME = '_e'

BASE_PATH = os.path.abspath(os.path.dirname(__file__))
VENV_PATH = os.path.join(BASE_PATH, VENV_NAME)
BUILD_PATH = 'build'
ACTIVATE_THIS_PATH = os.path.join(VENV_PATH, 'bin', 'activate_this.py')


def _which(program):
    """Returns path of command executable path."""
    import os
    def is_exe(fpath):
        return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

    fpath, fname = os.path.split(program)
    if fpath:
        if is_exe(program):
            return program
    else:
        for path in os.environ["PATH"].split(os.pathsep):
            path = path.strip('"')
            exe_file = os.path.join(path, program)
            if is_exe(exe_file):
                return exe_file


class Test(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.tearDownClass()
        if _which('virtualenv'):
            os.system('virtualenv {0} -p python2.7'.format(VENV_PATH))
            if not os.path.isdir(VENV_PATH):
                sys.exit('Failed to create virtual environment "{0}"!'
                         .format(VENV_PATH))
            cls._activate_venv()
        else:
            sys.exit('Cannot run tests because the "virtualenv" '
                     'command is not installed on your system!'
                     '\nRead installation instructions '
                     'here:\nhttps://virtualenv.pypa.io/en/latest/virtualenv'
                     '.html#installation')

    @classmethod
    def tearDownClass(cls):
        cls._remove_venv()
        cls._remove_build()

    @classmethod
    def _remove_venv(cls):
        """Removes virtual environment"""
        if os.path.isdir(VENV_PATH):
            shutil.rmtree(VENV_PATH)

    @classmethod
    def _remove_build(cls):
        """Removes virtual environment"""
        if os.path.isdir(BUILD_PATH):
            shutil.rmtree(BUILD_PATH)

    @classmethod
    def _activate_venv(cls):
        """
        Activates virtual environment

        http://virtualenv.readthedocs.org/en/latest/virtualenv.html#using-virtualenv-without-bin-python
        """
        execfile(ACTIVATE_THIS_PATH, dict(__file__=ACTIVATE_THIS_PATH))

    def _import_gae(self):
        import google.appengine

    def test_import(self):
        # On Ubuntu, there is a google module in system site-packages
        # which shadows the google module from google_appengine.
        # Therefore we will keep only the virtualenv paths in the pythonpath.
        sys.path = sys.path[:3]

        # GAE import should fail first
        self.assertRaises(ImportError, self._import_gae)

        # After running setup.py,
        os.system('python {0} install'
                  .format(os.path.join(BASE_PATH, 'setup.py')))


        # and activating the virtual environment
        self._activate_venv()

        # GAE should not fail
        self._import_gae()


if __name__ == '__main__':
    if sys.version_info.major == 2 and sys.version_info.minor >= 7:
        unittest.main()
    else:
        sys.exit('GAE Installer requires Python 2.7 or higher!')
