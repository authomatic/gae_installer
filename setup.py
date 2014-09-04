import os
from distutils.command.build import build as _build
from distutils.core import setup
import hashlib
import urllib
import zipfile

VESRION = '1.9.6'

GAE_URL = 'https://storage.googleapis.com/appengine-sdks/{0}/google_appengine_{1}.zip'
GAE_URL_FEATURED = GAE_URL.format('featured', VESRION)
GAE_URL_DEPRECATED = GAE_URL.format('deprecated/{0}'.format(VESRION.replace('.', '')), VESRION)

GAE_CHECKSUM = '888a6687d868ac37f973ea2fb986931338a1c040'
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


def _download_gae(zip_path):
    print('Downloading GAE SDK {0} from {1}'.format(VESRION, GAE_URL_FEATURED))
    print('Please be patient, this can take a while...')
    file_path, response = urllib.urlretrieve(GAE_URL_FEATURED, zip_path)
    if response.type != 'application/zip':
        print('GAE SDK {0} is deprecated!'.format(VESRION))
        print('Downloading deprecated GAE SDK {0} from {1}'
              .format(VESRION, GAE_URL_DEPRECATED))
        file_path, response = urllib.urlretrieve(GAE_URL_DEPRECATED, zip_path)

    print('Download OK')
    return file_path


def checksum(zip_path):
    cs = hashlib.sha1(open(zip_path, 'rb').read()).hexdigest()
    if cs == GAE_CHECKSUM:
        print('Checksum OK')
        return True


class build(_build):
    def run(self):
        os.makedirs(LIB_PATH)
        self._download()
        with open(os.path.join(LIB_PATH, 'google_appengine.pth'), 'w') as f:
            f.write('google_appengine')
        _build.run(self)

    def _download(self):
        if os.path.isfile(ZIP_PATH):
            print('GAE SDK zip found at {0}'.format(ZIP_PATH))
            if not checksum(ZIP_PATH):
                print('GAE zip checksum {0} doesnt match with {1}!'
                      .format(checksum, GAE_CHECKSUM))
                _download_gae(ZIP_PATH)
        else:
            _download_gae(ZIP_PATH)
            if not checksum(ZIP_PATH):
                raise Exception("The downloaded GAE SDK {0} doesn't match the "
                                "SHA1 checksum '{1}'"
                                .format(VESRION, GAE_CHECKSUM))

        zf = zipfile.ZipFile(ZIP_PATH)
        print('Extracting {0} to {1}'.format(ZIP_PATH, LIB_PATH))
        zf.extractall(LIB_PATH)

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
    packages=['gae_installer'], # If not empty, contents of ./build/lib will not be copied
    scripts=[os.path.join(SCRIPTS_PATH, i) for i in SCRIPTS],
    cmdclass=dict(build=build)
)
