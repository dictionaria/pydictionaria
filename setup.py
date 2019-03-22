from setuptools import setup, find_packages


setup(
    name='pydictionaria',
    version='0.1.0',
    description='',
    long_description='',
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
    ],
    author='Robert Forkel',
    author_email='forkel@shh.mpg.de',
    url='',
    keywords='data linguistics',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'requests',
        'purl',
        'python-dateutil',
        'BeautifulSoup4',
        'clldutils~=2.0',
        'pycldf',
        'attrs',
        'cdstarcat>=0.2.1',
        'tqdm',
        'transliterate==1.7.6',
        'pyconcepticon>=1.1.1',
        'colorlog',
        'termcolor',
        'pybtex',
        'xlrd',
    ],
    extras_require={
        'dev': ['flake8'],
        'test': [
            'tox',
            'mock',
            'pytest>=3.1',
            'pytest-mock',
            'pytest-cov',
            'coverage>=4.2',
        ],
    },
    entry_points={
        'console_scripts': ['dictionaria=pydictionaria.__main__:main'],
    },
    tests_require=[],
    test_suite="pydictionaria")
