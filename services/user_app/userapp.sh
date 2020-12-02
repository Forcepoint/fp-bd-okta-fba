#!/bin/bash
#
# Author:  Dlo Bagari
# created Date: 12-10-2019
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
export FLASK_ENV=development
python3 $DIR/cli_controller.py "$@"