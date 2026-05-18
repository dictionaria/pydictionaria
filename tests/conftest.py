from pathlib import Path

import shutil
import pytest


@pytest.fixture
def repos(tmpdir):
    repos = tmpdir.join('repos')
    shutil.copytree(Path(__file__).parent.joinpath('repos'), str(repos))
    return Path(str(repos))
