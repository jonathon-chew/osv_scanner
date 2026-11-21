import argparse
import os
import sys
import unittest
import tempfile

import find_files


class FindFiles(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.DEBUG = True
        cls.Verbose = True

    def test_find_files(self) -> None:

        sys.argv.extend(["--base-location", ".", "--verbose"])

        flags = argparse.ArgumentParser()
        flags.add_argument(
            "--base-location",
        )
        flags.add_argument(
            "--verbose",
            action="store_true",
        )
        flags.add_argument(
            "--ignore-cache",
            action="store_true",
        )
        flags.add_argument(
            "--ignore-n-old",
            type=int,
            default=-1,
        )
        args = flags.parse_args()

        temp_file_dir = tempfile.mkdtemp()

        for file in os.listdir("./tests/fixtures/python_project"):
            try:
                with open(f"./tests/fixtures/python_project/{file}", "r") as r:
                    content = r.read()
                with open(f"{temp_file_dir}/{file}", "w") as w:
                    w.write(content)
            except Exception as e:
                print(e)

        # IF DEBUG IS ON THIS WILL NEVER MAKE THE REQUEST, LOOK FOR FILES OR ANYTHING
        find_files.find(
            location=temp_file_dir, v=self.Verbose, DEBUG=self.DEBUG, args=args
        )


if __name__ == "__main__":
    unittest.main()
