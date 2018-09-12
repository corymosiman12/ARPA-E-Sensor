# Introduction
The following outlines 3 different ways to install opencv, imutils, and their required dependencies on Ubuntu16.04 KVM for the Antsle.  It took quite a few tries to get opencv working, and the first method presented is actually the easiest and was discovered last.  The other references are kept in case of difficulties.  Anything proceeded by `$` should be run at the command line.  Note that for any of this to work, the Antsle must have an outbound internet connection.

We will use the `ubuntu` user for all of the individual antlet setups.  If, at any point, a network error is encountered, simply restart the Antsle.  This typically works.

# OpenCV Setup
## 1. Easiest Method
This is a combination of the update posted in [this install guide](https://medium.com/@debugvn/installing-opencv-3-3-0-on-ubuntu-16-04-lts-7db376f93961), addressing the [errors noted here](https://stackoverflow.com/questions/47113029/importerror-libsm-so-6-cannot-open-shared-object-file-no-such-file-or-directo).  Note that parts 1 and 2 are just to get the virtualenv setup.  Once we are in the virtualenv, it follows the first install guide.

1. Install pip
`$ wget https://bootstrap.pypa.io/get-pip.py`
`$ python3 get-pip.py`
`$ rm get-pip.py`
`$ pip3 install virtualenv virtualenvwrapper`

2. virtualenv and virtualenvwrapper setup
`$ nano .bashrc` and add the following 3 lines to bottom
export VIRTUALENVWRAPPER_PYTHON=/usr/bin/python3
export WORKON_HOME=$HOME/.virtualenvs
source /usr/local/bin/virtualenvwrapper.sh

Exit out of the `.bashrc` file and run at the command line
`$ source .bashrc`

3. Create a new virtualenv called 'cv'
`$ mkvirtualenv cv`

When you are in the virtualenv, (cv) should appear at the front now.  You can run `(cv) $ deactivate` to exit out of a virtualenv.  Then run `$ workon cv` to enter back into the virtualenv.  See here for docs: https://virtualenvwrapper.readthedocs.io/en/latest/command_ref.html

4. Install OpenCV (+ 3 dependencies), influxdb client, imutils
`(cv) $ pip install opencv-contrib-python`
`(cv) $ apt update && apt install -y libsm6 libxext6`
`(cv) $ apt install -y libxrender-dev`
`(cv) $ pip install imutils`


## 2. Other method
This basically follows this [PyImageSearch Post](https://www.pyimagesearch.com/2015/07/20/install-opencv-3-0-and-python-3-4-on-ubuntu/), but with a few modifications.
1. Update and upgrade packages.
--- demo2 start ---
`$ apt update`
`$ apt upgrade`
--- demo2 end ---

Note: *If unable to lock /var/lib/dpkg/, run `$ ps aux | grep apt`, then kill the process with `$ kill [processNumber]`*

2. Install Requirements to Build OpenCV
`$ apt install build-essential cmake git pkg-config`
`$ apt install libjpeg8-dev libtiff5-dev libjasper-dev libpng12-dev -y`
`$ apt install libavcodec-dev libavformat-dev libswscale-dev libv4l-dev`

3. Install pip
`$ wget https://bootstrap.pypa.io/get-pip.py`
`$ python3 get-pip.py`
`$ rm get-pip.py`
`$ pip3 install virtualenv virtualenvwrapper`

4. virtualenv and virtualenvwrapper setup
`$ nano .bashrc` and add the following 3 lines to bottom
export VIRTUALENVWRAPPER_PYTHON=/usr/bin/python3
export WORKON_HOME=$HOME/.virtualenvs
source /usr/local/bin/virtualenvwrapper.sh

Exit out of the `.bashrc` file and run at the command line
`$ source .bashrc`

5. Create a new virtualenv called 'cv'
`$ mkvirtualenv cv`

When you are in the virtualenv, (cv) should appear at the front now.  You can run `(cv) $ deactivate` to exit out of a virtualenv.  Then run `$ workon cv` to enter back into the virtualenv.  See here for docs: https://virtualenvwrapper.readthedocs.io/en/latest/command_ref.html

6. Install numpy, opencv, influxdb, imutils
`(cv) $ pip install numpy`
`(cv) $ pip install opencv-python`
`(cv) $ pip install influxdb`
`(cv) $ pip install imutils`
`(cv) $ apt update`
`(cv) $ apt upgrade`

## 3. Another: Condensed Method 2
This basically follows this [PyImageSearch Post](https://www.pyimagesearch.com/2015/07/20/install-opencv-3-0-and-python-3-4-on-ubuntu/), but with a few modifications.
1. Update and upgrade packages.
`$ apt update`
`$ apt upgrade`

Note: *If unable to lock /var/lib/dpkg/, run `$ ps aux | grep apt`, then kill the process with `$ kill [processNumber]`*

2. Install pip
`$ wget https://bootstrap.pypa.io/get-pip.py`
`$ python3 get-pip.py`
`$ rm get-pip.py`
`$ pip3 install virtualenv virtualenvwrapper`

3. virtualenv and virtualenvwrapper setup
`$ nano .bashrc` and add the following 3 lines to bottom
export VIRTUALENVWRAPPER_PYTHON=/usr/bin/python3
export WORKON_HOME=$HOME/.virtualenvs
source /usr/local/bin/virtualenvwrapper.sh

Exit out of the `.bashrc` file and run at the command line
`$ source .bashrc`

4. Create a new virtualenv called 'cv'
`$ mkvirtualenv cv`

When you are in the virtualenv, (cv) should appear at the front now.  You can run `(cv) $ deactivate` to exit out of a virtualenv.  Then run `$ workon cv` to enter back into the virtualenv.  See here for docs: https://virtualenvwrapper.readthedocs.io/en/latest/command_ref.html

5. Install numpy, opencv, influxdb, imutils
`(cv) $ pip install numpy`
`(cv) $ pip install opencv-python`
`(cv) $ pip install influxdb`
`(cv) $ pip install imutils`
`(cv) $ apt update`
`(cv) $ apt upgrade`

# Mount HDD
Now that the 