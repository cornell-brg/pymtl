# setup.py inspired by the PyPA sample project:
# https://github.com/pypa/sampleproject/blob/master/setup.py

from setuptools import setup, find_packages
from codecs     import open   # To use a consistent encoding
from os         import path

def get_long_description():
  here = path.abspath(path.dirname(__file__))
  with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
        long_description = f.read()

setup(

    name    = 'pymtl',
    version = '1.4alpha0', # https://www.python.org/dev/peps/pep-0440/

    description      = 'Python-based hardware modeling framework',
    long_description = get_long_description(),
    url              = 'https://github.com/cornell-brg/pymtl',

    author       = 'Derek Lockhart',
    author_email = 'lockhart@csl.cornell.edu',

    # BSD 3-Clause License:
    # - http://choosealicense.com/licenses/bsd-3-clause
    # - http://opensource.org/licenses/BSD-3-Clause
    license='BSD',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
      'Development Status :: 3 - Alpha',
      'License :: OSI Approved :: BSD License',
      'Programming Language :: Python :: 2.7',
      'Operating System :: MacOS :: MacOS X',
      'Operating System :: POSIX :: Linux',
    ],

    packages = find_packages(
      exclude=['scripts', 'tests', 'ubmark', 'perf_tests']
    ),

    package_data={
      'pymtl': [
        'tools/translation/verilator_wrapper.templ.c',
        'tools/translation/verilator_wrapper.templ.py',
        'tools/translation/cpp_wrapper.templ.py',
      ],
    },

    install_requires = [
      'cffi',
      'greenlet',
      'pytest',
      'pytest-xdist',
      # Note: leaving out numpy due to pypy incompatibility
      #'numpy==1.9.0',
    ],

)
