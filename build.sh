#!/bin/bash
set -Eeuo pipefail

# example environment setup for each (virtualised) macOS version:
# install homebrew if not already installed, then `brew install pyenv pyenv-virtualenv xz` and complete post-setup environment setup
#
# pyenv install 3.7.17
# pyenv install 3.8.20
# pyenv install 3.9.20
# pyenv install 3.10.15
# pyenv install 3.11.10
# pyenv install 3.12.7
# pyenv install 3.13.2
#
# pyenv virtualenv 3.7.17 pyoslog37
# pyenv virtualenv 3.8.20 pyoslog38
# pyenv virtualenv 3.9.20 pyoslog39
# pyenv virtualenv 3.10.15 pyoslog310
# pyenv virtualenv 3.11.10 pyoslog311
# pyenv virtualenv 3.12.7 pyoslog312
# pyenv virtualenv 3.13.2 pyoslog313

# this build script is quite forceful about setup - make sure not to mess up the system python
PYTHON_VENV=$(python3 -c "import sys; sys.stdout.write('1') if hasattr(sys, 'real_prefix') or sys.base_prefix != sys.prefix else sys.stdout.write('0')")
if [ "$PYTHON_VENV" == 0 ]; then
  echo 'Warning: not running in a Python virtual environment. Please either activate a venv or edit the script to confirm this action'
  exit 1
fi

module=${PWD##*/} # get module name - relies on directory name == module name
module=${module:-/}

rm -rf build
rm -rf dist

# check and upload built files with whatever python binary is globally set; use custom pyenv pyoslog versions below for building
python -m pip install --quiet --upgrade pip
python -m pip install --quiet twine

if [ "${1:-0}" == 'all' ]; then
  versions=(36 37 38 39 310 311 312 313) # run as "./build.sh all" to build with all reasonable python versions
else
  versions=(default)
fi
for i in "${versions[@]}"; do
  if [ "$i" == 'default' ]; then
    python_binary='python'
  else
    python_binary="${PYENV_ROOT}/versions/pyoslog$i/bin/python"
  fi
  printf "\nBuilding %s with Python %s (%s)\n" "$module" "$i" "$python_binary"

  printf "\nPreparing environment for %s…\n" "$module"
  $python_binary -m pip install --quiet --upgrade pip
  $python_binary -m pip install --quiet setuptools build packaging importlib_metadata coverage mypy sphinx # we don't have a requirements.txt, so easiest just to be sure to build dependencies exist every time
  $python_binary -m pip install --quiet --force-reinstall . # install pyoslog itself (for tests)

  printf '\nType checking %s…\n' "$module"
  $python_binary -m mypy pyoslog

  # note: for 100% test coverage, building must take place on macOS 12 or later, and debug logging must be enabled for all log objects:
  # > sudo log config --mode 'level:debug' --subsystem 'ac.robinson.pyoslog'
  # > sudo log config --mode 'level:debug'
  # (the system mode can be restored to default afterwards via: `sudo log config --mode 'level:default'`)
  printf '\nRunning tests and checking coverage for %s…\n' "$module"
  if [ "$i" == '36' ] || [ "$i" == '38' ]; then
    printf '\nSkipping tests for Python %s due to PyObjC incompatibility\n' "$i"
  else
    $python_binary -m pip install --quiet pyobjc-framework-OSLog # separated from other installations because it will fail on unsupported platforms
    (cd tests && $python_binary -m coverage run -m unittest)     # note re: test output - we selectively skip tests where they need a macOS version above our minimum
    set +e                                                       # in environments we can't test (e.g., no OSLog framework) we don't care if coverage fails
    (cd tests && $python_binary -m coverage html --include '*/pyoslog/*' --omit '*test*')
    set -e
  fi

  if [ "$i" == '36' ]; then
    printf '\nSkipping documentation for Python %s due to PyObjC incompatibility\n' "$i"
  else
    printf '\nBuilding documentation for %s…\n' "$module"
    $python_binary -m pip install --quiet -r docs/requirements.txt
    export SPHINXOPTS=-q
    if [ "$i" != 'default' ]; then
      export SPHINXBUILD="${PYENV_ROOT}/versions/pyoslog$i/bin/sphinx-build"
    fi
    (cd docs && make clean html)
  fi

  printf '\nBuilding source and wheel (universal) distributions for %s…\n' "$module"
  $python_binary -m build
done

printf '\nValidating %s packages…\n' "$module"
python -m twine check dist/*

if [ "${1:-0}" != 'deploy' ]; then
  printf '\nBuild complete - exiting script. Run "./build.sh deploy" to also upload to PyPi / Read the Docs (please git commit first)\n\n'
  exit 0
fi

printf "\nUpload the $(tput bold)%s$(tput sgr0) package to the \033[0;32m$(tput bold)Test PyPI repository$(tput sgr0)\033[0m via Twine? (y to confirm; n to skip; any other key to exit): " "$module"
read -r answer

if [ "$answer" != "${answer#[Yy]}" ]; then
  PYPI_TEST_TOKEN=$(<versions/pypi-test.token)
  if python -m twine upload -u __token__ -p "$PYPI_TEST_TOKEN" --repository testpypi dist/*; then
    echo "Upload of $module completed – install via: python -m pip install --force-reinstall --index-url https://test.pypi.org/simple/ $module (forcing version via $module==X.X.X if needed)"
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
    echo ''
  else
    echo "Error: $module upload failed"
    exit 1
  fi
else
  echo "Live upload of $module cancelled"
  exit 0
fi
