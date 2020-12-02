#!/bin/bash
#
# Author:  Dlo Bagari
# created Date: 12-10-2019
sleep 20
export FLASK_ENV=development
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd $DIR
cd ..
python3 ./services/events_app/ingest.py "$@"