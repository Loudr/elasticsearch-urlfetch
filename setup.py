from setuptools import setup, find_packages
from os import path


with open(path.join(path.dirname(__file__), 'README.md')) as readme:
    long_description = readme.read()

version_file_path = path.join(path.dirname(__file__), 'elasticsearch_urlfetch', 'VERSION')
with open(version_file_path) as version_file:
    elasticsearch_urlfetch_version = version_file.read().strip()

setup(
    name="elasticsearch_urlfetch",
    version=elasticsearch_urlfetch_version,
    author="Josh Whelchel",
    author_email="josh@loudr.fm",
    description="Provides a URLFetchConnection connection_class for https://github.com/elastic/elasticsearch-py",
    license="MIT License",
    url="https://github.com/Loudr/elasticsearch-urlfetch",
    packages=find_packages(exclude=('tests',)),
    package_data={
        'elasticsearch_urlfetch': ['VERSION']
    },
    install_requires=[
        'elasticsearch>=0.4.5',
    ],
)
