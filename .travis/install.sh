#!/bin/bash

set -e
set -x

if [ $ANDROID == 1 ]; then
    sudo apt-get install p7zip-full
    wget http://dl.google.com/android/ndk/android-ndk-r10c-linux-x86_64.bin -O $PWD/ndk.bin 
    7z x $PWD/ndk.bin > 7z.log
    export ANDROID_NDK=`pwd`/android-ndk-r10c
    rm $PWD/ndk.bin
fi

if [[ "$(uname -s)" == 'Darwin' ]]; then
    brew update || brew update
    brew outdated pyenv || brew upgrade pyenv
    brew install pyenv-virtualenv

    if which pyenv > /dev/null; then
    eval "$(pyenv init -)"
    fi

    pyenv install 2.7.10
    pyenv virtualenv 2.7.10 conan
    pyenv rehash
    pyenv activate conan
fi

pip install conan_package_tools # It install conan too
conan user