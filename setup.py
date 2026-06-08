from pathlib import Path

from setuptools import find_packages
from setuptools import setup

BASE_DIR = Path(__file__).resolve().parent
README_PATH = BASE_DIR / "README.md"

setup(
    name="osv-scanner",
    version="0.1.0",
    description=""
    author="Jonathon Chew",
    author_email="example@email.com",
    long_description=README_PATH.read_text(encoding="utf-8"),
    long_description_content_type="text/markdown",
    url="",
    python_requires=">=3.10",
    package_dir={"": "src"},
    packages=find_packages(where="src", exclude=("tests*",)),
    entry_points={
        "console_scripts": [
            "osv-scanner=osv-scanner.__main__:main",
        ]
    },
)
