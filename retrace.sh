#!/usr/bin/python

FILE_NAME=$1
FILE_PATH="./crashreport/$FILE_NAME"

~/Library/Android/sdk/cmdline-tools/latest/bin/retrace mapping.txt $FILE_PATH
