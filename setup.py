import os
import re
import ast
from setuptools import setup


_version_re = re.compile(r'__version__\s+=\s+(.*)')


with open('sage_utils/__init__.py', 'rb') as f:
    version = str(ast.literal_eval(_version_re.search(
        f.read().decode('utf-8')).group(1))
    )


requirements = [
    'aioamqp==0.12.0',
]


def read(f):
    return open(os.path.join(os.path.dirname(__file__), f)).read().strip()


def get_packages(package):
    """
    Return root package and all sub-packages.
    """
    return [
        dirpath
        for dirpath, dirnames, filenames in os.walk(package)
        if os.path.exists(os.path.join(dirpath, '__init__.py'))
    ]


args = dict(
    name='sage-utils',
    version=version,
    url='https://github.com/OpenMatchmaking/sage-utils-python',
    license='BSD',
    author='Valeryi Savich',
    author_email='relrin78@gmail.com',
    description='SDK for Open Matchmaking microservices in Python',
    long_description=read('README.rst'),
    packages=get_packages('sage_utils'),
    include_package_data=True,
    zip_safe=False,
    platforms='any',
    install_requires=requirements,
    classifiers=[
        'License :: OSI Approved :: BSD License',
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Topic :: Internet :: WWW/HTTP'
    ],
)


if __name__ == '__main__':
    setup(**args)
