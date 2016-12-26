#!/bin/bash

if [[ "$TRAVIS_OS_NAME" == "osx" ]]; then
    #sudo sh -c 'echo "deb http://mirrors.cat.pdx.edu/ubuntu precise main" >> /etc/apt/sources.list'
    # Install gcc-multilib (fixed some errors)
    #sudo apt-get update -qq
    #sudo apt-get install gcc-multilib
    # Install CMake 3
    echo "osx"
    export CXX=clang++
    export CC=clang
else
    wget https://s3.amazonaws.com/biibinaries/thirdparty/cmake-3.0.2-Linux-64.tar.gz
    tar -xzf cmake-3.0.2-Linux-64.tar.gz
    sudo cp -fR cmake-3.0.2-Linux-64/* /usr
    rm -rf cmake-3.0.2-Linux-64
    rm cmake-3.0.2-Linux-64.tar.gz
fi
# Download conan
sudo pip install conan
# Adjust config and settings
if [[ "$TRAVIS_OS_NAME" == "osx" ]]; then
    echo -e "\ncompiler=clang" >> ~/.conan/conan.conf
    echo -e "\ncompiler.version=$(clang -dumpversion)" >> ~/.conan/conan.conf
fi
conan --version
conan user selenorks
#echo -e "\ncompiler=gcc" >> ~/.conan/conan.conf
#
