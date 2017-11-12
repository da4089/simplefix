Publishing a Release
====================

Check the setup.py version.
Commit and push everything.
Activate the 3.6 venv (to get twine, wheel, etc)
Run: rm -rf dist
Run: python setup.py sdist
Run: python setup.py bdist_wheel --universal
Run: twine upload dist/*
Run: git tag v$VERSION
Run: git push --tags
Go to GitHub and make a release
Bump the setup.py version for next time, and commit.

