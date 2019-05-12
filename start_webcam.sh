#!/bin/bash

set -x -e

. config.sh

gst-launch-1.0 -v souphttpsrc location=$STREAM_URL ! jpegparse  ! jpegdec  ! videoconvert ! v4l2sink device=$VIDEO_DEV sync=0