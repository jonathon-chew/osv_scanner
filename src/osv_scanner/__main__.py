import os
import argparse

import find_files

def main():

    flags = argparse.ArgumentParser()
    flags.add_argument("--base-location", help="This is the location you want to start the search for.\nThis will look for requirements.txt and go.mod", required=True)

    flags.add_argument("--verbose", help="Extra printing to show what is going on", action="store_true")

    args = flags.parse_args()

    VERBOSE = args.verbose

    if not args.base_location:
        print("[ERROR]: there was no base location passed in, where to start looking")

    find_files.find(args.base_location, VERBOSE=VERBOSE)

if __name__ == "__main__":
    VERBOSE = True
    main()