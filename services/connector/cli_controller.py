#!/usr/bin/python3
#
# Author:  Dlo Bagari
# created Date: 12-10-2019

from cli.cliargs import CliArgs

if __name__ == "__main__":
    cli_args = CliArgs("connector.sh")
    parser = cli_args.get_parser()
    args = parser.parse_args()
    args.function(args)
