from pathlib import Path

from pydictionaria import commands


def _args(mocker, repos, *args, **kw):
    kw.setdefault('internal', False)
    kw.setdefault('log', mocker.Mock())
    return mocker.Mock(repos=repos, args=args, **kw)


def test_ls(capsys, mocker, repos):
    commands.ls(_args(mocker, repos))
    assert 'First Author' in capsys.readouterr()[0]


def test_stat(capsys, mocker, repos):
    commands.stat(_args(mocker, repos, 'sub_sfm'))
    assert 'xv' in capsys.readouterr()[0]


def test_repair(mocker, repos):
    commands.repair(_args(mocker, repos, 'sub_sfm'))


def test_add_comparison_meanings(mocker, repos):
    log = mocker.Mock()
    commands.add_comparison_meanings(_args(mocker, repos, 'sub_excel', log=log))
    assert log.warn.called


def test_process(mocker, repos):
    commands.process(_args(mocker, repos, 'sub_excel'))
    assert repos.joinpath('submissions', 'sub_excel', 'processed').exists()


def test_check_sfm(mocker, repos):
    commands.check(_args(mocker, repos, 'sub_sfm'))


def test_process_sfm(mocker, repos, tmpdir):
    commands.process(_args(mocker, repos, 'sub_sfm'))
    proc = repos.joinpath('submissions', 'sub_sfm', 'processed')
    assert "Custom" in (proc / 'senses.csv').read_text(encoding='utf-8').split('\n')[0]
    assert "Custom" in (proc / 'entries.csv').read_text(encoding='utf-8').split('\n')[0]

    commands.process(_args(mocker, repos, 'sub_sfm_with_examples'))
    commands.release(_args(mocker, repos, 'sub_sfm_with_examples', Path(str(tmpdir))))


def test_new(mocker, repos):
    commands.new(_args(mocker, repos, 'new'))
    assert repos.joinpath('submissions', 'new', 'md.json').exists()
