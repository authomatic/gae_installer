from distutils.command.build import build
from distutils.command.build_scripts import build_scripts
from distutils.core import setup
from md5 import md5
import os
import tempfile
import urllib
import zipfile

import version


VERSION = version.full_version if version.full_version.count('.') == 2 else \
    version.full_version.rsplit('.', 1)[0]

GAE_URL = ('https://storage.googleapis.com/appengine-sdks/{0}/'
           'google_appengine_{1}.zip')
GAE_URL_FEATURED = GAE_URL.format('featured', VERSION)
GAE_URL_DEPRECATED = GAE_URL.format('deprecated/{0}'
                                    .format(VERSION.replace('.', '')), VERSION)

SHEBANG_TEMPLATE = '#!/usr/bin/env bash\n'
GAE_DIR_SCRIPT_NAME = '_get_gae_dir'
SCRIPT_TEMPLATE = 'python `{0}`/`basename $0`.py "$@"'\
    .format(GAE_DIR_SCRIPT_NAME)

script_paths = []

class BuildScripts(build_scripts):
    """Custom build_scripts command"""
    def finalize_options(self):
        global script_paths
        build_scripts.finalize_options(self)
        self.scripts = script_paths


class Build(build):
    """Custom build command"""

    zip_path = os.path.join(tempfile.gettempdir(),
                            'google_appengine_{0}.zip'.format(VERSION))

    def run(self):
        # assert False, (self.build_base, self.build_temp)
        self._get_from_cache_or_download()
        self._populate_files()
        self._populate_scripts()

        build.run(self)

    def _populate_scripts(self):
        """
        Generates script wrapper files for all GAE SDK scripts
        and populates the global script_paths variable with their paths.
        """
        global script_paths
        files = os.listdir(os.path.join(self.build_lib, 'google_appengine'))

        # Exclude the run_tests.py file
        files.remove('run_tests.py')

        scripts_temp = os.path.join(self.build_temp, 'scripts')

        os.makedirs(scripts_temp)

        # Create script for getting the path of the installed GAE SDK
        gae_dir_script_path = os.path.join(scripts_temp, GAE_DIR_SCRIPT_NAME)
        with open(gae_dir_script_path, 'w') as f:
            f.write(SHEBANG_TEMPLATE + 'python -c "import google.appengine; print google.__file__'
                    '.split(\'/google/\')[0]"')

        script_paths = [gae_dir_script_path]
        for name in files:
            if name.endswith('.py') and name[0] != '_':
                name = name[:-3]
                script_path = os.path.join(scripts_temp, name)
                script_paths.append(script_path)
                with open(script_path, 'w') as f:
                    print 'Generating script file: {0}'.format(script_path)
                    f.write(SHEBANG_TEMPLATE + SCRIPT_TEMPLATE)

    def _populate_files(self):
        """Unzips the downloaded GAE SDK and creates a PTH file"""
        os.makedirs(self.build_lib)
        self._unzip()
        pth_path = os.path.join(self.build_lib, 'google_appengine.pth')
        with open(pth_path, 'w') as f:
            f.write('google_appengine')

    def _get_from_cache_or_download(self):
        """Gets the GAE SDK from cache or downloads it."""
        if os.path.isfile(self.zip_path):
            print('GAE SDK zip found at {0}'.format(self.zip_path))
            if not self._checksum(self.zip_path):
                print('GAE zip checksum doesnt match with {0}!'
                      .format(version.checksum))
                self._download_gae()
        else:
            self._download_gae()

    def _unzip(self):
        """Unzips the GAE SDK"""
        zf = zipfile.ZipFile(self.zip_path)
        print('Extracting {0} to {1}'.format(self.zip_path, self.build_lib))
        zf.extractall(self.build_lib)

    def _download_gae(self):
        """Downloads the GAE SDK"""
        os.makedirs(self.build_base)
        print('Downloading GAE SDK {0} from {1} to {2}'
              .format(VERSION, GAE_URL_FEATURED, self.zip_path))
        print('Please be patient, this can take a while...')
        file_path, response = urllib.urlretrieve(GAE_URL_FEATURED,
                                                 self.zip_path)
        if response.type != 'application/zip':
            print('GAE SDK {0} is deprecated!'.format(VERSION))
            print('Downloading deprecated GAE SDK {0} from {1}'
                  .format(VERSION, GAE_URL_DEPRECATED))
            file_path, response = urllib.urlretrieve(GAE_URL_DEPRECATED,
                                                     self.zip_path)
        if not self._checksum(self.zip_path):
            raise Exception("The downloaded GAE SDK {0} doesn't match the "
                            "MD5 checksum '{1}'"
                            .format(VERSION, version.checksum))

        print('Download OK')
        return file_path

    def _checksum(self, zip_path):
        """Validates the GAE SDK against a checksum."""
        cs = md5(open(zip_path, 'rb').read()).hexdigest()
        if cs == version.checksum:
            print('Checksum OK')
            return True


setup(
    name='gae_installer',
    version=version.full_version,
    author='Peter Hudec',
    author_email='peterhudec@peterhudec.com',
    description='Google App Engine Installer',
    long_description=open(os.path.join(os.path.dirname(__file__), 'README.rst'))
        .read(),
    keywords='google appengine gae sdk installer',
    url='https://github.com/peterhudec/gae_installer',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: System :: Installation/Setup',
    ],
    license='MIT',
    package_data={'': ['*.txt', '*.rst']},
    # If packages is empty, contents of ./build/lib will not be copied!
    packages=['gae_installer'],
    scripts=['if', 'empty', 'BuildScripts', 'will', 'be', 'ignored'],
    cmdclass=dict(build=Build, build_scripts=BuildScripts)
)
