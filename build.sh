module=${PWD##*/} # get module name - relies on directory name == module name
module=${module:-/}

echo "Preparing environment for $module"
python -m pip install twine # we don't have a requirements.txt so easiest just to be sure twine exists every time
rm -rf dist
rm -rf build

printf '\nType checking %s…\n' "$module"
mypy pyoslog

printf '\nRunning tests for %s…\n' "$module"
(cd tests && python -m unittest) # we don't fail on failed tests because they need a macOS version above our minimum

printf '\nBuilding documentation for %s…\n' "$module"
python -m pip install -r docs/requirements.txt
(cd docs && make clean html)

printf '\nBuilding source and wheel (universal) distributions for %s…\n' "$module"
python setup.py clean --all sdist bdist_wheel --universal

printf '\nValidating %s packages…\n' "$module"
twine check dist/*

if [ -z "$1" ]; then # exit unless a parameter is provided (we use 'deploy' but don't actually care what it is)
  printf '\nExiting build script - run "./build.sh deploy" to also upload to PyPi / Read the Docs\n'
  exit 1
fi

printf "\nUpload the $(tput bold)%s$(tput sgr0) package to the \033[0;32m$(tput bold)Test PyPI repository$(tput sgr0)\033[0m via Twine? (y to confirm; n to skip; any other key to exit): " "$module"
read -r answer

if [ "$answer" != "${answer#[Yy]}" ]; then
  PYPI_TEST_TOKEN=$(<versions/pypi-test.token)
  if twine upload -u __token__ -p "$PYPI_TEST_TOKEN" --repository testpypi dist/*; then
    echo "Upload of $module completed – install via: python -m pip install --force-reinstall --index-url https://test.pypi.org/simple/ $module"
  else
    echo "Error uploading $module; exiting"
    exit 1
  fi
elif [ "$answer" != "${answer#[Nn]}" ]; then
  echo "Skipping Test PyPi upload of $module"
else
  echo "Test upload of $module cancelled; exiting"
  exit 0
fi

printf "\nUpload the \033[0;31m$(tput bold)%s$(tput sgr0)\033[0m package to the \033[0;31m$(tput bold)LIVE PyPI repository$(tput sgr0)\033[0m via Twine? (y to confirm; any other key to exit): " "$module"
read -r answer

if [ "$answer" != "${answer#[Yy]}" ]; then
  PYPI_DEPLOY_TOKEN=$(<versions/pypi-deploy.token)
  if twine upload -u __token__ -p "$PYPI_DEPLOY_TOKEN" dist/*; then
    echo "Upload of $module completed – view at https://pypi.org/project/$module"

    READTHEDOCS_TOKEN=$(<versions/readthedocs.token)
    echo "Triggering a Read the Docs build for $module – view at https://$module.readthedocs.io"
    curl -X POST -H "Authorization: Token $READTHEDOCS_TOKEN" "https://readthedocs.org/api/v3/projects/$module/versions/latest/builds/"
  else
    echo "Error: $module upload failed"
    exit 1
  fi
else
  echo "Live upload of $module cancelled"
  exit 0
fi
