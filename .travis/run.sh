#!/bin/bash

set -e
set -x

if [ $ANDROID == 1 ]; then
    export ANDROID_NDK=`pwd`/android-ndk-r10c
fi

if [[ "$(uname -s)" == 'Darwin' ]]; then
    if which pyenv > /dev/null; then
    eval "$(pyenv init -)"
    fi
    pyenv activate conan
fi

python build.py
