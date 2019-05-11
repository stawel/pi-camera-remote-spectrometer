#!/bin/bash

set -x -e

. config.sh

sudo modprobe  v4l2loopback exclusive_caps=1

gst-launch-1.0 -v souphttpsrc location=$STREAM_URL ! jpegparse  ! jpegdec  ! videoconvert ! v4l2sink device=$VIDEO_DEV sync=0