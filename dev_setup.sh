#!/usr/bin/env bash
######################################################
# dev_setup.sh
# @author sean.fitzgerald (aka clusterfudge)
#
# The purpose of this script is to create a self-
# contained development environment using
# virtualenv for python dependency sandboxing.
# This script will create a virtualenv (using the
# conventions set by virtualenv-wrapper for
# location and naming) and install the requirements
# laid out in requirements.txt, pocketsphinx, and
# pygtk into the virtualenv. Mimic will be
# installed and built from source inside the local
# checkout.
#
# The goal of this script is to create a development
# environment in user space that is fully functional.
# It is expected (and even encouraged) for a developer
# to work on multiple projects concurrently, and a
# good OSS citizen respects that and does not pollute
# a developers workspace with it's own dependencies
# (as much as possible).
# </endRant>
######################################################

# exit on any error
set -Ee

if [ $(id -u) -eq 0 ]; then
  echo "This script should not be run as root or with sudo."
  exit 1
fi

TOP=$(cd $(dirname $0) && pwd -L)

if [ -z "$WORKON_HOME" ]; then
    VIRTUALENV_ROOT=${VIRTUALENV_ROOT:-"${HOME}/.virtualenvs/mycroft"}
else
    VIRTUALENV_ROOT="$WORKON_HOME/mycroft"
fi

# create virtualenv, consistent with virtualenv-wrapper conventions
if [ ! -d ${VIRTUALENV_ROOT} ]; then
   mkdir -p $(dirname ${VIRTUALENV_ROOT})
  virtualenv -p python2.7 ${VIRTUALENV_ROOT}
fi

source ${VIRTUALENV_ROOT}/bin/activate
cd ${TOP}
easy_install pip #==7.1.2 # force version of pip
pip install --upgrade virtualenv

# copy global open-cv to virtual env, pip open-cv version doesnt work
# https://medium.com/@manuganji/installation-of-opencv-numpy-scipy-inside-a-virtualenv-bf4d82220313
sudo cp /usr/lib/python2.7/dist-packages/cv* $VIRTUALENV_ROOT/lib/python2.7/site-packages/

# tensorflow from binary
pip2 install --upgrade https://storage.googleapis
.com/tensorflow/linux/cpu/tensorflow-1.2.1-cp34-cp34m-linux_x86_64.whl

# install requirements (except pocketsphinx)
pip2 install -r requirements.txt


if  [[ $(free|awk '/^Mem:/{print $2}') -lt  1572864 ]] ; then
  CORES=1
else
  CORES=$(nproc)
fi

echo "Building with $CORES cores."

#build and install pocketsphinx
#cd ${TOP}
#${TOP}/scripts/install-pocketsphinx.sh -q

#build and install mimic
cd "${TOP}"
echo "WARNING: The following can take a long time to run!"
"${TOP}/scripts/install-mimic.sh"

# install pygtk for desktop_launcher skill
${TOP}/scripts/install-pygtk.sh




