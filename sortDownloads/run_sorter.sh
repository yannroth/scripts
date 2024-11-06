#!/bin/bash

source venv/bin/activate

python sortdl.py /home/yann/nas/downloadNas /home/yann/nas/movies /home/yann/nas/tvshows -c "$@"
