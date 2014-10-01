import os
from distutils.command.build import build as _build
from distutils.core import setup
import hashlib
import platform
import urllib
import zipfile


VESRION = '1.9.6'
GAE_CHECKSUM = '888a6687d868ac37f973ea2fb986931338a1c040'

GAE_URL = ('https://storage.googleapis.com/appengine-sdks/{0}/'
           'google_appengine_{1}.zip')
GAE_URL_FEATURED = GAE_URL.format('featured', VESRION)
GAE_URL_DEPRECATED = GAE_URL.format('deprecated/{0}'
                                    .format(VESRION.replace('.', '')), VESRION)

BASE_PATH = os.path.abspath(os.path.dirname(__file__))
BUILD_PATH = 'build'
ZIP_PATH = os.path.join(BUILD_PATH, 'gae.zip')
LIB_PATH = os.path.join(BUILD_PATH, 'lib')
SCRIPTS_PATH = os.path.join(BASE_PATH, 'scripts')
README_PATH = os.path.join(BASE_PATH, 'README.rst')
SCRIPTS = [
    'get_gae_dir',
    'api_server',
    'backends_conversion',
    'bulkload_client',
    'bulkloader',
    'dev_appserver',
    'download_appstats',
    'endpointscfg',
    'gen_protorpc',
    'google_sql',
    'old_dev_appserver',
    'php_cli',
    'remote_api_shell',
    'wrapper_util',
]


def checksum(zip_path):
    """Checks the downloaded GAE SDK against its checksum."""
    cs = hashlib.sha1(open(zip_path, 'rb').read()).hexdigest()
    if cs == GAE_CHECKSUM:
        print('Checksum OK')
        return True


class build(_build):
    def run(self):
        # On Mac OSX we need to collect all the files to be installed in the
        # ./build/lib directory, because it ignores the files in
        # ./build/lib.<plat>/. On other platforms ./build/lib is ignored.
        # http://goo.gl/MYCNnJ
        is_mac = platform.system().lower() == 'darwin'
        build_dir = LIB_PATH if is_mac else self.build_platlib
        
        # Create build directory
        os.makedirs(build_dir)
        
        # Download and unzip GAE SDK
        self._get_gae_sdk(build_dir)
        
        # Create PTH file
        pth_path = os.path.join(build_dir, 'google_appengine.pth')
        with open(pth_path, 'w') as f:
            f.write('google_appengine')
        
        _build.run(self)

    def _get_gae_sdk(self, build_dir):
        """
        Downloads and unzips the GAE SDK.
        If a previously downloaded file is found skips the download.
        """
        if os.path.isfile(ZIP_PATH):
            print('GAE SDK zip found at {0}'.format(ZIP_PATH))
            if not checksum(ZIP_PATH):
                print('GAE zip checksum {0} doesnt match with {1}!'
                      .format(checksum, GAE_CHECKSUM))
                self._download_gae(ZIP_PATH)
        else:
            self._download_gae(ZIP_PATH)
            if not checksum(ZIP_PATH):
                raise Exception("The downloaded GAE SDK {0} doesn't match the "
                                "SHA1 checksum '{1}'"
                                .format(VESRION, GAE_CHECKSUM))

        # Unzip
        zf = zipfile.ZipFile(ZIP_PATH)
        print('Extracting {0} to {1}'.format(ZIP_PATH, build_dir))
        zf.extractall(build_dir)

    def _download_gae(self, zip_path):
        """Downloads GAE SDK."""
        print('Downloading GAE SDK {0} from {1}'
              .format(VESRION, GAE_URL_FEATURED))
        print('Please be patient, this can take a while...')
        file_path, response = urllib.urlretrieve(GAE_URL_FEATURED, zip_path)

        # If the response is not a zip file the requested version is deprecated
        # and we need to download it from the archive.
        if response.type != 'application/zip':
            print('GAE SDK {0} is deprecated!'.format(VESRION))
            print('Downloading deprecated GAE SDK {0} from {1}'
                  .format(VESRION, GAE_URL_DEPRECATED))
            file_path, response = urllib.urlretrieve(GAE_URL_DEPRECATED,
                                                     zip_path)

        print('Download OK')
        return file_path

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
    license = 'MIT',
    package_data={'': ['*.txt', '*.rst']},
    # If packages is empty, contents of ./build/lib will not be copied!
    packages=['gae_installer'],
    scripts=[os.path.join(SCRIPTS_PATH, i) for i in SCRIPTS],
    cmdclass=dict(build=build)
)
