import os
from distutils.command.build import build as _build
from distutils.core import setup
import hashlib
import urllib
import zipfile


VESRION = '1.9.4'
GAE_URL = ('https://storage.googleapis.com/appengine-sdks/featured/'
           'google_appengine_{0}.zip').format(VESRION)
GAE_CHECKSUM = 'ee44f7bcc16b4d72c3af0a4f744048d44f75c5ce'
BASE_PATH = os.path.abspath(os.path.dirname(__file__))
BUILD_PATH = 'build'
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
    print('Downloading {0}'.format(GAE_URL))
    return urllib.urlretrieve(GAE_URL, zip_path)[0]

class build(_build):
    def run(self):
        os.makedirs(LIB_PATH)
        self._download_gae()
        with open(os.path.join(LIB_PATH, 'google_appengine.pth'), 'w') as f:
            f.write('google_appengine')
        _build.run(self)

    def _download_gae(self):
        zip_path = os.path.join(BUILD_PATH, 'gae.zip')

        if os.path.isfile(zip_path):
            print('GAE SDK zip found at {0}'.format(zip_path))
            checksum = hashlib.sha1(open(zip_path, 'rb').read()).hexdigest()
            if checksum == GAE_CHECKSUM:
                print('GAE zip checksum OK')
            else:
                print('GAE zip checksum {0} doesnt match with {1}!'
                      .format(checksum, GAE_CHECKSUM))
                _download_gae(zip_path)
        else:
            _download_gae(zip_path)

        zf = zipfile.ZipFile(zip_path)
        print('Extracting {0} to {1}'.format(zip_path, LIB_PATH))
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
    packages=[''], # If not empty, contents of ./build/lib will not be copied
    scripts=[os.path.join(SCRIPTS_PATH, i) for i in SCRIPTS],
    cmdclass=dict(build=build)
)
