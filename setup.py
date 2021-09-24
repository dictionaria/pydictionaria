from setuptools import setup, find_packages


setup(
    name='pydictionaria',
    version='2.1',
    description='',
    long_description='',
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
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
        'pybtex',
        'requests',
        'html5lib>=1.1',
        'purl',
        'python-dateutil',
        'csvw>=1.5.4',
        'BeautifulSoup4',
        'attrs>=19.1',
        'clldutils>=3.5.1',
        # for MediaTable support
        'pycldf>=1.20',
        'pycdstar>=1.0.1',
        'cdstarcat>=1.0.0',
        'transliterate>=1.7.6',
        'pyconcepticon>=1.1.1',
        'cldfbench',
    ],
    extras_require={
        'dev': ['flake8'],
        'test': [
            'tox',
            'pluggy>=0.12',
            'pytest>=5',
            'pytest-mock',
            'pytest-cov',
            'coverage>=4.2',
        ],
    },
    entry_points={
        'cldfbench.commands': ['dictionaria=pydictionaria.commands'],
        'cldfbench.scaffold': [
            'dictionaria=pydictionaria.scaffold:Template'
        ],
    },
    tests_require=[],
    test_suite="pydictionaria")
