FROM ubuntu:latest

RUN apt-get update --fix-missing && apt-get install -y git sudo libssl-dev
RUN apt-get install -y build-essential cmake doxygen graphviz


RUN git clone https://github.com/opencv/opencv.git \
    && mkdir build_opencv \
    && cd build_opencv \
    && cmake -D CMAKE_BUILD_TYPE=Release -D CMAKE_INSTALL_PREFIX=/usr/local ../opencv/ \
    && make -j4 \
    && make install

RUN apt-get install -y python3 python3-pip libopenexr-dev
RUN pip3 install opencv-python matplotlib pillow scipy==1.1.0

#mdp is ubuntu
RUN useradd -ms /bin/bash -p "$(openssl passwd -1 ubuntu)" dock
RUN usermod -aG sudo dock

#End of file
USER dock
WORKDIR /home/dock