from collections import defaultdict
import os
import json
import re
import tomllib

import make_requests

versions: dict[str, str] = defaultdict()

VERBOSE = False


def _parse_file(file_name: str, input: str, root: str,  DEBUG: bool = False):
    """
    Parse all the types of files that can contain packages in the different ways it can recorded
    """

    match file_name:
        case "bin/activate":
            pass
        case "conda-meta/":
            pass
        case "go.mod":
            # to impliment
            pass
            """ for package in contents.split("\n"):
                _, package_name, version = package.split(" ")
                make_requests.make_request(version=version, package_name=package_name, ecosystem="Go") """
        case "Pipfile.lock":
            pass
        case "poetry.lock":
            pass
        case "pyproject.toml":
            packages = re.findall('"(.*)==(.*)",', input)
            package_and_version = re.findall(r"(.*) \= \".?(\d+\.\d+\.\d+)\"", input)
            project = input.split("\n\n")
            if packages:
                for package in packages:
                    make_requests.make_request(
                        version=package[1],
                        package_name=package[0],
                        ecosystem="PyPI",
                        file_name=file_name,
                        root_folder=root,
                        VERBOSE=VERBOSE,
                        DEBUG=DEBUG,
                    )
            
            if package_and_version:
                print("found package and version")
                for each_package in package_and_version:
                    # print(f"Name: {each_package[0]}, Version: {each_package[1]}")
                    make_requests.make_request(
                        version=each_package[1],
                        package_name=each_package[0],
                        ecosystem="PyPI",
                        file_name=file_name,
                        root_folder=root,
                        VERBOSE=VERBOSE,
                        DEBUG=DEBUG
                    )

            for details in project: 
                if not "name" in details or not "version" in details:
                    continue
                project_name = re.findall("name = \"(.*)\"", details)
                dep_version = re.findall("version = \"(.*)\"", details)

                project_name = project_name[0] if len(project_name) == 1 else "ERROR"
                dep_version = dep_version[0] if len(dep_version) == 1 else "ERROR"

                if dep_version != "ERROR" and project_name != "ERROR":
                    make_requests.make_request(
                        version=dep_version,
                        package_name=project_name,
                        ecosystem="PyPI",
                        file_name=file_name,
                        root_folder=root,
                        VERBOSE=VERBOSE,
                        DEBUG=DEBUG
                    )

        case "pyvenv.cfg":
            pass
        case "requirements-dev.txt":
            for package in input.split("\n"):
                if "=" in package and not input[0] == "[":
                    package_name, version = package.split("==", 2)

                    remember_package = f"{package_name}_{version}"

                    if versions.get(remember_package, None) == version:
                        # Already checked
                        if VERBOSE:
                            print("Already checked: ", remember_package)
                        break
                    else:
                        versions[remember_package] = version

                    make_requests.make_request(
                        version=version,
                        package_name=package_name,
                        ecosystem="PyPI",
                        file_name=file_name,
                        root_folder=root,
                        VERBOSE=VERBOSE,
                        DEBUG=DEBUG,
                    )
                if input[0] == "[":  # Checking for is this pip list --format=JSON
                    json_file = json.loads(input)
                    for each_pacakge in json_file:
                        make_requests.make_request(
                            version=each_pacakge.get("version"),
                            package_name=each_pacakge.get("name"),
                            ecosystem="PyPI",
                            file_name=file_name,
                            root_folder=root,
                            VERBOSE=VERBOSE,
                            DEBUG=DEBUG,
                        )
        case "requirements.txt":
            for package in input.split("\n"):
                if "=" in package and not input[0] == "[":
                    package_name, version = package.split("==", 2)

                    remember_package = f"{package_name}_{version}"

                    if versions.get(remember_package, None) == version:
                        # Already checked
                        if VERBOSE:
                            print("Already checked: ", remember_package)
                        break
                    else:
                        versions[remember_package] = version

                    make_requests.make_request(
                        version=version,
                        package_name=package_name,
                        ecosystem="PyPI",
                        file_name=file_name,
                        root_folder=root,
                        VERBOSE=VERBOSE,
                        DEBUG=DEBUG,
                    )
                if input[0] == "[":  # Checking for is this pip list --format=JSON
                    json_file = json.loads(input)
                    for each_pacakge in json_file:
                        make_requests.make_request(
                            version=each_pacakge.get("version"),
                            package_name=each_pacakge.get("name"),
                            ecosystem="PyPI",
                            file_name=file_name,
                            root_folder=root,
                            VERBOSE=VERBOSE,
                            DEBUG=DEBUG,
                        )
        case "uv.lock":
            pass
        case _:
            pass

    return


def find(location: str, v: bool, DEBUG: bool = False):
    """
    Traverse the location recursively for all the different files that could exist, and contain package details
    """

    VERBOSE = v

    python_files = [
        "pyvenv.cfg",
        "bin/activate",
        "poetry.lock",
        "Pipfile.lock",
        "conda-meta/",
        "requirements.txt",
        "pyproject.toml",
    ]

    python_files = [file.lower() for file in python_files]

    for root, _, files in os.walk(location):

        for file in files:
            file_name = os.path.join(root, file)

            if file.lower() in python_files or file == "go.mod":
                with open(file_name, "r") as r:
                    contents = r.read()
            else:
                continue

            if len(contents) == 0:
                continue

            if VERBOSE:
                print(f"Found {file} in {root}")

            _parse_file(file, contents, root, DEBUG=DEBUG)
