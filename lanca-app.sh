#!/bin/bash
cd "${0%/*}"
python app.py runserver -h 0.0.0.0 -p 8080 --threaded |& tee -a braz.log
