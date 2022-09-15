#!/usr/bin/env bash
if [ ! -f data/bpi2011.xes.gz ]; then
    echo "Downloading The BPI2011 Dataset"
    wget -O data/logs/bpi2011.xes.gz https://www.win.tue.nl/bpi/lib/exe/fetch.php?media=2011:hospital_log.xes.gz
    gzip -d data/logs/bpi2011.xes.gz
fi
#if [ ! -f data/bpi2017.xes.gz ]; then
#    echo "Downloading The BPI2017 Dataset"
#    wget -O data/logs/bpi2017.xes.gz https://data.4tu.nl/ndownloader/files/24044117
#    gzip -d data/logs/bpi2017.xes.gz
#fi
cp ./LogGeneration/genlog/xray/merged_xray.xes data/logs/merged_xray.xes