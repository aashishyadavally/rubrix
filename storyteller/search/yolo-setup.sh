#!/bin/sh

# Instructions:
# =============
# 1. Give `gpu` as the first argument to build darknet
#    binary files for machines with GPU and CUDA set up.
#


# Download yolo-v4 code repository
if [ ! -d "darknet" ]; then
	git clone https://github.com/AlexeyAB/darknet.git
else
	echo "/darknet directory already exists! Moving on..."
	echo ""
fi

# Copy corresponding Makefile
# Copy config file into /darknet
if [[ $1 == "gpu" ]]; then
	cp ../assets/yolo/Makefile-gpu darknet/Makefile
fi

while true; do
    echo "Edit config file at darknet/cfg/yolov4.cfg"
    echo "" 
    read -p "Continue?" yn
    case $yn in
        # TO DO: Might need to change this to make it
        # more consistent across operating systems
        [Yy]* )
            nano darknet/cfg/yolov4.cfg;
            break;;
        [Nn]* )
            exit;;
        * )
            echo "Please answer yes or no.";;
    esac
done

# Create darknet binary files
cd darknet
make
