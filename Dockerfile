FROM python:3.6

RUN apt-get update && apt-get install -y tmux

# Build SEAL libraries

RUN mkdir -p SEAL/
COPY /SEAL/ /SEAL/SEAL/
WORKDIR /SEAL/SEAL/
RUN chmod +x configure
RUN sed -i -e 's/\r$//' configure
RUN ./configure
RUN make
ENV LD_LIBRARY_PATH SEAL/bin:$LD_LIBRARY_PATH

# Build SEAL Python wrapper

COPY /SEALPython /SEAL/SEALPython
COPY /GameOfLife /SEAL/GameOfLife
WORKDIR /SEAL/SEALPython
RUN pip3 install --upgrade pip
RUN pip3 install setuptools
RUN pip3 install pybind11
RUN pip3 install cppimport
RUN pip3 install numpy
RUN pip3 install msgpack
RUN git clone https://github.com/pybind/pybind11.git
WORKDIR /SEAL/SEALPython/pybind11
RUN git checkout a303c6fc479662fd53eaa8990dbc65b7de9b7deb
WORKDIR /SEAL/SEALPython
RUN python3 setup.py build_ext -i
ENV PYTHONPATH $PYTHONPATH:/SEAL/SEALPython:/SEAL/bin

# return to SEAL root directory
WORKDIR /SEAL

# execute
COPY server server
COPY client client
COPY main.sh main.sh
CMD ./main.sh


