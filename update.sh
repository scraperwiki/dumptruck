#!/bin/bash
# Send a new version to the various places

if [ "$1" = "pypi" ]
  then

  echo Checking out the master branch
  git checkout master

  echo Uploading to PyPI
  python setup.py register sdist upload

elif [ "$1" = "website" ]
  then

  echo Build the website
  (
    cd website/build
    ant
  )

  echo Uploading the website
  scp -r website/publish/* www-data@thomaslevine.com:/srv/www/hacks/dumptruck

else
  echo "usage: $0 [command]"
  echo \ 
  echo Commands
  echo "  $0 pypi      Upload the master branch to pypi."
  echo "  $0 website   Build the website and upload it to the web server."
fi
