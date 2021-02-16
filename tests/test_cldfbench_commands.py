from io import StringIO
import pathlib
import shlex
import shutil

import pytest

import pydictionaria
from cldfbench.__main__ import main


MOCK_STDIN = """\
testbench
Title
License
URL
Citation"""


def _main(cmd, **kw):
    main(['--no-config'] + shlex.split(cmd), **kw)


@pytest.fixture
def testdata_dir():
    return pathlib.Path(__file__).parent / 'test_data'


@pytest.fixture
def tmp_dataset(testdata_dir, tmp_path, mocker):
    mocker.patch('sys.stdin', StringIO(MOCK_STDIN))
    _main("new --template dictionaria_submission --out '{}'".format(tmp_path))
    bench_path = tmp_path / 'testbench'
    shutil.copy(testdata_dir / 'intro.md', bench_path / 'raw' / 'intro.md')
    shutil.copy(testdata_dir / 'db.sfm', bench_path / 'raw' / 'db.sfm')
    return bench_path


def test_release(tmp_dataset):
    _main('dictionaria.release {}'.format(tmp_dataset / 'cldfbench_testbench.py'))
    assert (tmp_dataset / 'README.md').exists()
    assert (tmp_dataset / '.zenodo.json').exists()
