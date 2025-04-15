from io import StringIO
import pathlib
import shlex
import shutil

import pytest

from cldfbench.__main__ import main


MOCK_STDIN = """\
testbench
Title
License
URL
Citation"""


def _main(cmd, **kw):
    main(['--no-config', *shlex.split(cmd)], **kw)


@pytest.fixture
def testdata_dir():
    return pathlib.Path(__file__).parent / 'test_data'


@pytest.fixture
def tmp_dataset(tmp_path, mocker):
    mocker.patch('sys.stdin', StringIO(MOCK_STDIN))
    _main(f"new --template dictionaria --out '{tmp_path}'")
    return tmp_path / 'testbench'


@pytest.fixture
def sfm_dataset(testdata_dir, tmp_dataset):
    shutil.copy(testdata_dir / 'sub_sfm' / 'db.sfm', tmp_dataset / 'raw' / 'db.sfm')
    shutil.copy(testdata_dir / 'sub_sfm' / 'md.json', tmp_dataset / 'etc' / 'md.json')
    return tmp_dataset


@pytest.fixture
def sfm_dataset_with_examples(testdata_dir, tmp_dataset):
    shutil.copy(testdata_dir / 'sub_sfm_with_examples' / 'db.sfm', tmp_dataset / 'raw' / 'db.sfm')
    shutil.copy(testdata_dir / 'sub_sfm_with_examples' / 'examples.sfm', tmp_dataset / 'raw' / 'examples.sfm')
    shutil.copy(testdata_dir / 'sub_sfm_with_examples' / 'intro.md', tmp_dataset / 'raw' / 'intro.md')
    shutil.copy(testdata_dir / 'sub_sfm_with_examples' / 'md.json', tmp_dataset / 'etc' / 'md.json')
    return tmp_dataset


@pytest.fixture
def sfm_dataset_flex_ref(testdata_dir, tmp_dataset):
    shutil.copy(testdata_dir / 'sub_sfm_flex_ref' / 'db.sfm', tmp_dataset / 'raw' / 'db.sfm')
    shutil.copy(testdata_dir / 'sub_sfm_flex_ref' / 'md.json', tmp_dataset / 'etc' / 'md.json')
    return tmp_dataset


def test_makecldf(sfm_dataset, mocker):
    mocker.patch('cldfbench.__main__.BUILTIN_CATALOGS', [])
    _main("makecldf '{}'".format(sfm_dataset / 'cldfbench_testbench.py'))
    assert (sfm_dataset / 'cldf' / 'cldf-metadata.json').exists()


def test_makecldf_with_examples(sfm_dataset_with_examples, mocker):
    mocker.patch('cldfbench.__main__.BUILTIN_CATALOGS', [])
    _main("makecldf '{}'".format(sfm_dataset_with_examples / 'cldfbench_testbench.py'))
    assert (sfm_dataset_with_examples / 'cldf' / 'cldf-metadata.json').exists()


def test_makecldf_with_flex_ref(sfm_dataset_flex_ref, mocker):
    mocker.patch('cldfbench.__main__.BUILTIN_CATALOGS', [])
    _main("makecldf '{}'".format(sfm_dataset_flex_ref / 'cldfbench_testbench.py'))
    assert (sfm_dataset_flex_ref / 'cldf' / 'cldf-metadata.json').exists()


def test_release(sfm_dataset_with_examples):
    _main("dictionaria.release '{}'".format(sfm_dataset_with_examples / 'cldfbench_testbench.py'))
    assert (sfm_dataset_with_examples / 'README.md').exists()
    assert (sfm_dataset_with_examples / '.zenodo.json').exists()
