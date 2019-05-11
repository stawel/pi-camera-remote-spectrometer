#!/bin/bash

set -x -e

. config.sh


#gst-launch-1.0 -v souphttpsrc location=$STREAM_URL ! jpegparse  ! jpegdec  ! videoconvert ! autovideosink sync=0
gst-launch-1.0 -v souphttpsrc location=$STREAM_URL ! jpegparse  ! jpegdec  ! videoconvert ! fpsdisplaysink sync=0