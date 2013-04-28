#!/bin/bash

SCRIPT_LOC=$(dirname $0)

cd $SCRIPT_LOC/src
source ../bin/activate

python wtp_crawler.py > $SCRIPT_LOC/log 2>&1

cd ..
git add data/wtp.json >> $SCRIPT_LOC/log 2>&1
git commit -m "Periodic data run" >> $SCRIPT_LOC/log 2>&1
git push >> $SCRIPT_LOC/log 2>&1
