#!/usr/bin/python

FILE_NAME=$1
FILE_PATH="./crashreport/$FILE_NAME"

/home/android-sdk/cmdline-tools/bin/retrace mapping.txt $FILE_PATH
