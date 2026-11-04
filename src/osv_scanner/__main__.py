import os
import argparse

import find_files


def main():

    # Get the path of the script, remove the last two folders (src/osv_scanner) and use that as the basis to make the docs folder IF it doesn't exist
    docs_folder = f"{os.path.sep}".join(
        os.path.split(os.path.dirname(os.path.realpath(__file__)))[:-2]
    )
    os.makedirs(f"./{docs_folder}", exist_ok=True)

    flags = argparse.ArgumentParser()
    flags.add_argument(
        "--base-location",
        help="This is the location you want to start the search for.\nThis will look for requirements.txt and go.mod",
        required=True,
    )

    flags.add_argument(
        "--verbose", help="Extra printing to show what is going on", action="store_true"
    )

    args = flags.parse_args()

    VERBOSE = args.verbose

    if not args.base_location:
        print("[ERROR]: there was no base location passed in, where to start looking")

    if not os.path.exists(args.base_location):
        issuse = f"{args.base_location} appears not to exist"
        raise NotADirectoryError(issuse)

    find_files.find(args.base_location, v=VERBOSE)


if __name__ == "__main__":
    VERBOSE = False
    main()
