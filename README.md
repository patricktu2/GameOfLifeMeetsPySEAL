# GameOfLifeMeetsPySEAL

This is a implementation of Cornway's Game of Life in python using homomorphic encryption with the PySEAL library (https://github.com/Lab41/PySEAL). PySEAL is a python wrapper of the Simple Encrypted Arithmetic Library (SEAL) developed by Microsoft. The scope of this project includes a GUI using tkinter in python and a (simulated) server that is performing the computational operations.

## Dependencies

### Docker
In order to build the python wrapper of the C++ library it needs to be dockerized. Hence, docker needs to be installed.
Docker can be found here: https://docs.docker.com/install/

### XQuartz (Just needed for MacOS)
To run GUI applications using Docker for Mac, it is neccessary to install XQuartz and later execute the start commands in the XQuartz terminal. The installation guide can be found here: https://www.xquartz.org/ 
For Ubuntu this is not neccessary.

## Run the Application
There are shell scripts that are used to run the application. The most important ones are the following
* `build.sh`: Builds the docker image and creates the python wrapper for SEAL
* `run.sh`: Runs the docker container. To run this for ubuntu, the code for Ubuntu needs to be uncomment. This script starts the GUI client and the server in two separate terminals by executing `main.sh`
* `debug.sh`: This script copies the content of the terminals and writes it into a `log_server` and `log_client` file. This was usually used for debugging purposes after the application was stopped 
