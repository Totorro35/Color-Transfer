FROM ubuntu:latest

RUN apt-get update --fix-missing
RUN DEBIAN_FRONTEND=noninteractive apt-get install -y \
    build-essential \
    cmake \
    git \
    sudo \
    libssl-dev \
    python3 \
    python3-pip \
    libopenexr-dev \
    zlib1g-dev \
    openexr \
    python3-tk \
    libsm-dev

RUN pip3 install \
    opencv-python \
    matplotlib \
    pillow \
    scipy==1.1.0 \
    tensorflow-gpu \
    tensorlayer==1.11.0 \
    OpenEXR \
    numpy==1.16.2

#mdp is ubuntu
RUN useradd -ms /bin/bash -p "$(openssl passwd -1 ubuntu)" dock
RUN usermod -aG sudo dock

#End of file
USER dock
WORKDIR /home/dock