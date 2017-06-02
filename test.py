"""
Tests the setup.py script by running ``python setup.py install`` in a
temporarily activated virtual environment.
"""

import os
import re
import shutil
import subprocess
import sys
import unittest
import urllib2

import version


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
            os.system('virtualenv {0} -q -p python2.7'.format(VENV_PATH))
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

    def _install(self):
        os.system('python {0} -q install'
                  .format(os.path.join(BASE_PATH, 'setup.py')))

    def _import_gae(self):
        import google.appengine

    def test_import(self):

        # GAE import should fail first
        self.assertRaises(ImportError, self._import_gae)

        # When we install it...
        self._install()

        # (we need to activate venv again, otherwise it won't work)
        self._activate_venv()

        # (remove shadowing google modules if any)
        if 'google' in sys.modules:
            del sys.modules['google']

        # Now the import should not fail
        import google.appengine

        # Ensure that the imported module lives in our venv
        assert VENV_PATH in google.appengine.__path__[0]

        # Pattern for elimination of _e/lib/python2.7 and _e/local/lib/python2.7
        # differences in scripts output
        venv_lib_pattern = re.compile(r'(_e/).*(/python)')
        venv_lib_replacement = r'\1...\2'

        # The _get_gae_dir file should exist
        get_gae_dir_path = os.path.join(VENV_PATH, 'bin', '_get_gae_dir')
        self.assertTrue(os.path.isfile(get_gae_dir_path))

        # The _get_gae_command should return the path of the
        # installed google_appengine SDK
        gae_dir = google.appengine.__file__.split('/google/')[0]
        output, error = subprocess.Popen(['_get_gae_dir'],
                                         stderr=subprocess.PIPE,
                                         stdout=subprocess.PIPE,
                                         shell=True).communicate()

        output = venv_lib_pattern.sub(venv_lib_replacement, output.strip())
        gae_dir_clean = venv_lib_pattern.sub(venv_lib_replacement, gae_dir)
        self.assertEquals(output, gae_dir_clean)

        # Skip the run_tests.py file
        original_commands = os.listdir(gae_dir)
        original_commands.remove('run_tests.py')

        # Patter for replacing time in output
        time_pattern = re.compile(r'\d\d:\d\d:\d\d,\d\d\d')

        for command in original_commands:
            if command.endswith('.py') and command[0] != '_':
                original_file = os.path.join(gae_dir, command)
                name = command[:-3]

                self.assertTrue(os.path.isfile(original_file),
                                "File {} doesn't exist!".format(original_file))

                original_output, original_error = subprocess.Popen(
                    ['python', original_file],
                    stderr=subprocess.PIPE,
                    stdout=subprocess.PIPE
                ).communicate()

                self.assertTrue(os.path.isfile(
                    os.path.join(VENV_PATH, 'bin', name)),
                    "File {} doesn't exist!".format(name)
                )

                output, error = subprocess.Popen(
                    [name],
                    stderr=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    shell=True
                ).communicate()

                # Output can contain varying time so we need to eliminate it
                original_output = time_pattern.sub('', original_output)
                original_error = time_pattern.sub('', original_error)
                output = time_pattern.sub('', output)
                error = time_pattern.sub('', error)

                # Eliminate of _e/lib/python2.7 and _e/local/lib/python2.7
                # differences
                original_output = venv_lib_pattern.sub(venv_lib_replacement,
                                                       original_output)
                original_error = venv_lib_pattern.sub(venv_lib_replacement,
                                                      original_error)
                output = venv_lib_pattern.sub(venv_lib_replacement, output)
                error = venv_lib_pattern.sub(venv_lib_replacement, error)

                assert output == original_output
                assert error == original_error

                self.assertEquals(output, original_output,
                                  "Stdouts of {} and {} don't match!"
                                  .format(name, original_file))
                self.assertEquals(error, original_error,
                                  "Stderrs of {} and {} don't match!"
                                  .format(name, original_file))

                ok = output == original_output and error == original_error
                print 'TESTING SCRIPT: {} {}'\
                    .format(name, 'OK' if ok else 'ERROR')


class TestNewVersion(unittest.TestCase):
    def test_new_version(self):
        """
        Tests whether the current version is the most recent one.
        """
        prefix = 'google_appengine_'

        major, minor, micro = map(int, version.version.split('.'))
        bucket_list = urllib2.urlopen('https://storage.googleapis.com/'
                                      'appengine-sdks/').read()

        match = re.search(
            pattern=r'{}({}\.\d+.\d+)'.format(prefix, major + 1),
            string=bucket_list
        )

        if not match:
            match = re.search(
                pattern=r'{}({}\.{}.\d+)'.format(prefix, major, minor + 1),
                string=bucket_list
            )

        if not match:
            match = re.search(
                pattern=r'{}({}\.{}.{})'
                    .format(prefix, major, minor, micro + 1),
                string=bucket_list
            )

        self.assertIsNone(
            obj=match,
            msg='New GAE version {} available!'.format(match.groups()[0])
                if match else ''
        )


if __name__ == '__main__':
    if sys.version_info.major == 2 and sys.version_info.minor >= 7:
        unittest.main(failfast=True)
    else:
        sys.exit('GAE Installer requires Python 2.7 or higher!')
