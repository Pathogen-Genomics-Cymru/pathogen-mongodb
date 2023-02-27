#!/usr/bin/env python3


import argparse
from utils import testconnection
from lodestone import lodestone_import
from phwtb import phwtb_import
from ukhsa import ukhsa_import_geno_csv


def main():

    parser = argparse.ArgumentParser()

    parser.add_argument("-l", "--lodestone-dir", dest="lodestoneDir", required=False,
                        help="""Output directory from lodestone run""")

    parser.add_argument("-p", "--phw-dir", dest="phwDir", required=False,
                        help="""Output directory for PHW results""")

    parser.add_argument("-u", "--ukhsa-dir", dest="ukhsaDir", required=False,
                        help="""Output directory for UKHSA results""")

    args = parser.parse_args()

    testconnection()

    if args.lodestoneDir:
        lodestone_import(args.lodestoneDir)

    if args.phwDir:
        phwtb_import(args.phwDir)

    if args.ukhsaDir:
        ukhsa_import_geno_csv(args.ukhsaDir)


if __name__ == '__main__':
    main()

