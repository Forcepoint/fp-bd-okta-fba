#!/usr/bin/python3
#
# Author:  Dlo Bagari
# created Date: 12-10-2019
from cli_user.cliargs import CliArgs

if __name__ == "__main__":
    cli_args = CliArgs("userapp.sh")
    parser = cli_args.get_parser()
    args = parser.parse_args()
    args.function(args)

