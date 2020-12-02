#!/usr/bin/python3
#
# functionality: execute ingest  cli_ofm which pulls event from okta and send them to FBA
# Author:  Dlo Bagari
# created Date: 08-10-2019

import os
from eventcli.cliargs import CliArgs


cli_args = CliArgs("ingest.py")
parser = cli_args.get_parser()
args = parser.parse_args()
args.function(args)
