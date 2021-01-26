import pytest

from pydictionaria.__main__ import main


@pytest.fixture
def _main(repos):
    def _(*args):
        main(args=['--repos', str(repos)] + list(args))
    return _


def test_ls(capsys, _main):
    _main('ls')
    assert 'First Author' in capsys.readouterr()[0]


# def test_add_comparison_meanings(mocker, _main):
#     _main('add_comparison_meanings')
#     log = mocker.Mock()
#     commands.add_comparison_meanings(_args(mocker, repos, 'sub_excel', log=log))
#     assert log.warn.called


def test_process(_main, repos):
    _main('process', 'sub_sfm_flex_ref')


def test_check_sfm(_main):
    _main('check', 'sub_sfm')


def test_process_sfm(_main, mocker, repos, tmpdir):
    _main('process', 'sub_sfm')
    proc = repos.joinpath('submissions', 'sub_sfm', 'processed')
    assert "Custom" in (proc / 'senses.csv').read_text(encoding='utf-8').split('\n')[0]
    assert "Custom" in (proc / 'entries.csv').read_text(encoding='utf-8').split('\n')[0]

    _main('process', 'sub_sfm_with_examples')
    _main('release', 'sub_sfm_with_examples', str(tmpdir))


def test_new(_main, repos):
    _main('new', 'new')
    assert repos.joinpath('submissions', 'new', 'md.json').exists()
