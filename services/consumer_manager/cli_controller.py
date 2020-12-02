#!/usr/bin/python3
#
# Author:  Dlo Bagari
# created Date: 12-10-2019
from cli_consumer.cliargsparse import CliArgsParse

if __name__ == "__main__":
    cli_args = CliArgsParse("consumerManager.sh")
    parser = cli_args.get_parser()
    args = parser.parse_args()
    for i in args.function(args):
        if i == 100:
            exit(0)
        print(i)
