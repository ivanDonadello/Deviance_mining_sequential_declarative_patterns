#!/usr/bin/env bash
source ./venv/bin/activate
python3 main.py "BPI2011_dCC.json" && python3 main.py "BPI2011_m13.json" && python3 main.py "BPI2011_m16.json" && python3 main.py "BPI2011_t101.json" && python3 main.py "sepsis_er.json" && python3 main.py "synth_xray.json" && python3 main.py "synth_mr_tagged.json"