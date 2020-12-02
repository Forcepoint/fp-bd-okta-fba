#!/usr/bin/python3

from cli_ofm.cli_args import CliArgs

if __name__ == "__main__":
    cli_args = CliArgs("orgapp.sh")
    parser = cli_args.get_parser()
    args = parser.parse_args()
    args.function(args)
