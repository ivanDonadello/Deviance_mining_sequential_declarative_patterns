#!/usr/bin/env bash

# Installing the interpreters
sudo apt-get install -y openjdk-14-jdk openjdk-14-jre python3.8 python3-pip

# Pulling the repos
git submodule update --init --recursive

# installing skfeature as a submodule
pushd submodules/skfeature && python3 setup.py install && popd

# installing the remaining requirements
pip3 install testresources
pip3 install --upgrade setuptools pip
pip3 install -r requirements.txt
