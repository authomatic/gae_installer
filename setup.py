import os
from distutils.command.build import build
from distutils.command.build_scripts import build_scripts
from distutils.core import setup
import hashlib
import urllib
import zipfile

VESRION = '1.9.6'

GAE_URL = ('https://storage.googleapis.com/appengine-sdks/{0}/'
           'google_appengine_{1}.zip')
GAE_URL_FEATURED = GAE_URL.format('featured', VESRION)
GAE_URL_DEPRECATED = GAE_URL.format('deprecated/{0}'
                                    .format(VESRION.replace('.', '')), VESRION)

GAE_CHECKSUM = '888a6687d868ac37f973ea2fb986931338a1c040'
BASE_PATH = os.path.abspath(os.path.dirname(__file__))
BUILD_PATH = 'build'
ZIP_PATH = os.path.join(BUILD_PATH, 'gae.zip')
LIB_PATH = os.path.join(BUILD_PATH, 'lib')
SCRIPTS_PATH = os.path.join(BUILD_PATH, 'scripts')
README_PATH = os.path.join(BASE_PATH, 'README.rst')
SCRIPT_TEMPLATE = 'python `get_gae_dir`/`basename $0`.py "$@"'


class BuildScripts(build_scripts):
    """Custom build_scripts command"""
    def finalize_options(self):
        global script_paths
        build_scripts.finalize_options(self)
        self.scripts = script_paths


class Build(build):
    """Custom build command"""
    def run(self):
        # download
        self._get_from_cache_or_download()

        # unzip and create pth for OSX
        self._populate_files(LIB_PATH)

        # unzip and create pth for other platforms
        self._populate_files(self.build_platlib)

        self._populate_scripts()

        build.run(self)

    def _populate_scripts(self):
        """
        Generates script wrapper files for all GAE SDK scripts
        and populates the global script_paths variable with their paths.
        """
        global script_paths
        files = os.listdir(os.path.join(LIB_PATH, 'google_appengine'))

        os.makedirs(SCRIPTS_PATH)
        script_paths = []
        for name in files:
            if name.endswith('.py') and name[0] != '_':
                name = name[:-3]
                script_path = os.path.join(SCRIPTS_PATH, name)
                script_paths.append(script_path)
                with open(script_path, 'w') as f:
                    print 'Generating script file: {0}'.format(script_path)
                    f.write(SCRIPT_TEMPLATE)

    def _populate_files(self, build_path):
        """Unzips the downloaded GAE SDK and creates a PTH file"""
        os.makedirs(build_path)
        self._unzip(build_path)
        pth_path = os.path.join(build_path, 'google_appengine.pth')
        with open(pth_path, 'w') as f:
            f.write('google_appengine')

    def _get_from_cache_or_download(self):
        """Gets the GAE SDK from cache or downloads it."""
        if os.path.isfile(ZIP_PATH):
            print('GAE SDK zip found at {0}'.format(ZIP_PATH))
            if not self._checksum(ZIP_PATH):
                print('GAE zip checksum doesnt match with {0}!'
                      .format(GAE_CHECKSUM))
                self._download_gae(ZIP_PATH)
        else:
            self._download_gae(ZIP_PATH)
            if not self._checksum(ZIP_PATH):
                raise Exception("The downloaded GAE SDK {0} doesn't match the "
                                "SHA1 checksum '{1}'"
                                .format(VESRION, GAE_CHECKSUM))

    def _unzip(self, build_path):
        """Unzips the GAE SDK"""
        zf = zipfile.ZipFile(ZIP_PATH)
        print('Extracting {0} to {1}'.format(ZIP_PATH, build_path))
        zf.extractall(build_path)

    def _download_gae(self, zip_path):
        """Downloads the GAE SDK"""
        os.makedirs(BUILD_PATH)
        print('Downloading GAE SDK {0} from {1} to {2}'
              .format(VESRION, GAE_URL_FEATURED, zip_path))
        print('Please be patient, this can take a while...')
        file_path, response = urllib.urlretrieve(GAE_URL_FEATURED, zip_path)
        if response.type != 'application/zip':
            print('GAE SDK {0} is deprecated!'.format(VESRION))
            print('Downloading deprecated GAE SDK {0} from {1}'
                  .format(VESRION, GAE_URL_DEPRECATED))
            file_path, response = urllib.urlretrieve(GAE_URL_DEPRECATED,
                                                     zip_path)

        print('Download OK')
        return file_path

    def _checksum(self, zip_path):
        """Validates the GAE SDK against a checksum."""
        cs = hashlib.sha1(open(zip_path, 'rb').read()).hexdigest()
        if cs == GAE_CHECKSUM:
            print('Checksum OK')
            return True


setup(
    name='gae_installer',
    version=VESRION,
    author='Peter Hudec',
    author_email='peterhudec@peterhudec.com',
    description='Google App Engine Installer',
    long_description=open(README_PATH).read(),
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
