#!/bin/bash

if [ $# -ne 2 ]
then
    echo "This script will auto-detect black bars in a video file and will crop the file accordingly."
    echo "usage: $0 inputVid outputVid"
    exit 0
fi

vid=$1
out=$2

crop=$(ffmpeg -ss 90 -i '$vid' -vframes 20 -vf cropdetect -f null - 2>&1 | awk '/crop/ { print $NF }' | tail -1 | sed -e 's/crop=//g')
echo "crop = $crop"
ffmpeg -i "$vid" -vf crop=$crop -c:a copy "$out"
exit 0
