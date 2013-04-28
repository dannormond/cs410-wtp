#!/bin/bash

SCRIPT_LOC=$(dirname $0)

cd $SCRIPT_LOC/src
python wtp_crawler.py

cd ..
git add data/wtp.json
git commit -m "Periodic data run"
git push
