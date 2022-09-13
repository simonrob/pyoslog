# this build script is quite forceful about setup - make sure not to mess up the system python
PYTHON_VENV=$(python -c "import sys; sys.stdout.write('1') if hasattr(sys, 'real_prefix') or sys.base_prefix != sys.prefix else sys.stdout.write('0')")
if [ "$PYTHON_VENV" == 0 ]; then
  echo 'Warning: not running in a Python virtual environment. Please either activate a venv or edit the script to confirm this action'
  exit 1
fi

module=${PWD##*/} # get module name - relies on directory name == module name
module=${module:-/}

printf "\nPreparing environment for %s…\n" "$module"
python -m pip install --quiet --upgrade pip
python -m pip install --quiet setuptools wheel twine mypy sphinx # we don't have a requirements.txt, so easiest just to be sure build dependencies exist every time
rm -rf dist
rm -rf build

python -m pip install --quiet --force-reinstall . # install pyoslog itself

printf '\nType checking %s…\n' "$module"
python -m mypy pyoslog

printf '\nRunning tests for %s…\n' "$module"
python -m pip install --quiet pyobjc-framework-OSLog # separated from other installations because it will fail on unsupported platforms
(cd tests && python -m unittest)                     # we don't fail on failed tests because they need a macOS version above our minimum

printf '\nBuilding documentation for %s…\n' "$module"
python -m pip install --quiet -r docs/requirements.txt
export SPHINXOPTS=-q
(cd docs && make clean html)

printf '\nBuilding source and wheel (universal) distributions for %s ("can'\''t clean" messages can be ignored)…\n' "$module"
python setup.py -q clean --all sdist bdist_wheel --universal

printf '\nValidating %s packages…\n' "$module"
python -m twine check dist/*

if [ -z "$1" ]; then # exit unless a parameter is provided (we use 'deploy' but don't actually care what it is)
  printf '\nExiting build script - run "./build.sh deploy" to also upload to PyPi / Read the Docs (please git commit first)\n\n'
  exit 0
fi

printf "\nUpload the $(tput bold)%s$(tput sgr0) package to the \033[0;32m$(tput bold)Test PyPI repository$(tput sgr0)\033[0m via Twine? (y to confirm; n to skip; any other key to exit): " "$module"
read -r answer

if [ "$answer" != "${answer#[Yy]}" ]; then
  PYPI_TEST_TOKEN=$(<versions/pypi-test.token)
  if python -m twine upload -u __token__ -p "$PYPI_TEST_TOKEN" --repository testpypi dist/*; then
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
  if python -m twine upload -u __token__ -p "$PYPI_DEPLOY_TOKEN" dist/*; then
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
