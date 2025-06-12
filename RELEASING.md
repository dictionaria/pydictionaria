
Releasing pydictionaria
=======================

- Do platform test via tox:
```
tox -r
```

- Make sure flake8 passes:
```
flake8 src
```

- Update the version number, by removing the trailing `.dev0` in:
  - `pyproject.toml`
  - `src/pydictionaria/__init__.py`

- Create the release commit:
```shell
git commit -a -m "release <VERSION>"
```

- Create a release tag:
```
git tag -a v<VERSION> -m"<VERSION> release"
```

- Make sure [build][build] and [twine][twine] are installed
```shell
pip install build twine
```

[build]: https://pypi.org/project/build/
[twine]: https://pypi.org/project/twine/

- Release to PyPI:
```shell
test -d ./dist/ && rm -r ./dist/
python -m build
twine upload dist/*
```

- Push to github:
```
git push origin
git push --tags
```

- Increment version number and append `.dev0` to the version number for the new development cycle:
  - `src/pydictionaria/__init__.py`
  - `setup.py`

- Commit/push the version change:
```shell
git commit -a -m "bump version for development"
git push origin
```
