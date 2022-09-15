

# Overview of Methods in Business Process Deviance Mining

## Setup  Guide 

### Linux 

The script `install_deps.sh` install all the language interpreters and the repo's dependencies in one shot.

### Windows 

First, you need to install Java14 ([OpenJDK](https://github.com/AdoptOpenJDK/openjdk14-binaries/releases/download/jdk-14.0.2%2B12/OpenJDK14U-jdk_x86-32_windows_hotspot_14.0.2_12.msi)) and Python3 ([3.8.5](https://www.python.org/ftp/python/3.8.5/python-3.8.5-amd64.exe)). The former is required to run Weka, while the latter runs the actual project.

After doing this, install the `scikit-feature` library by invoking `python setup.py install` on `submodules/skfeature`

Last, install the requirements for the project by using `pip3 install -r requirements.txt`. 

## Run

`main.py` is the main entry-point of the project. 
 * The first argument is the `*.json` file used to start the pipeline. The default value (if missing) is `sepsis_er.json`
 * The second argument can be set to `skipPreprocessing` if the data has been already loaded and we want to directly compute the benchmark results. The data preprocessing is not skept by default
