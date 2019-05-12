#!/bin/bash

set -x -e


sudo modprobe  v4l2loopback exclusive_caps=1

