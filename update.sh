#!/bin/bash
# Send a new version to the various places

echo Checking out the master branch
git checkout master

echo Uploading to PyPI
python setup.py register sdist upload

echo Build the website
cd website/build
ant
cd -

echo Uploading the website
scp -r website/publish/* www-data@thomaslevine.com:/srv/www/hacks/dumptruck
