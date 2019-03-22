import pytest
from clldutils.path import Path, copytree


@pytest.fixture
def repos(tmpdir):
    repos = tmpdir.join('repos')
    copytree(Path(__file__).parent.joinpath('repos'), str(repos))
    return Path(str(repos))
