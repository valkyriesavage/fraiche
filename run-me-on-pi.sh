#!/bin/sh

cd /home/pi/fraiche
nohup python server.py --scheduler=naive --freshness=personal-naive &
