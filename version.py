import re

with open('README.rst') as readme:
    content = readme.read()
    checksum = re.search(r'\|checksum\| replace:: ``(.*)``', content).group(1)
    version = re.search(r'\|version\| replace:: (.*)', content).group(1)
    version_suffix = re.search(r'\|fullversion\| replace:: \|version\|(.*)',
                               content).group(1)
    full_version = version + version_suffix
