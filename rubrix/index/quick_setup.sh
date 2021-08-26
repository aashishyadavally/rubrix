#!/bin/bash

# This script is useful when following instructions for quick setup.

# Download yolo-v4 code repository
echo "[INFO] Stage 1/2: Downloading darknet code repository"
if [ ! -d "darknet" ]; then
	git clone https://github.com/AlexeyAB/darknet.git
else
	echo "/darknet directory already exists! Moving on..."
fi
echo "[INFO] Stage 1/2: Complete."
echo ""


# Create darknet binary files
echo "[INFO] Stage 2/2: Building darknet code repository"
cd darknet
make
cd ..
echo "[INFO] Stage 2/2: Complete."
echo ""
