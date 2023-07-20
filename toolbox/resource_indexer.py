#!/bin/python3
"""
Resource Indexer.

Usage:
    resource_indexer.py [(-o | --output) <filepath>]
    resource_indexer.py (-h | --help)

Options:
    -h --help      Show this screen.
    -o --output    Set the output file path [default: resources.index].
"""

import os
import json
import mimetypes
import re
from docopt import docopt


def retrieve_valid_filepaths():
    """
    Retrieve the valid file paths.

    Returns
    -------
    array
        an array of valid file path.
    """
    valid_files = []
    for root, _directory_names, file_names in os.walk("."):
        for file_name in file_names:
            file_path = os.path.join(root, file_name)
            _, extension = os.path.splitext(file_path)
            if root == "./.import" or extension == ".import":
                continue
            valid_files.append(file_path)
    return valid_files


def build_resources_index(valid_files):
    """
    Build the index out of the valid files.

    Parameters
    ----------
    valid_files : array
        list of valid files path, relative to the root of the project.

    Returns
    -------
    dict
        a dictionary containing all the cross references and validity of resources.
    """
    # Set the mimetypes so we can recognize the godot files.
    mimetypes.init()
    mimetypes.add_type("text/godot-script", ".gd")
    mimetypes.add_type("text/godot-script", ".cs")
    mimetypes.add_type("text/godot-resource", ".res")
    mimetypes.add_type("text/godot-resource", ".tres")
    mimetypes.add_type("text/godot-scene", ".tscn")
    mimetypes.add_type("text/godot-shader", ".gdshader")
    mimetypes.add_type("text/godot-configuration", ".cfg")
    mimetypes.add_type("text/godot-configuration", ".json")
    mimetypes.add_type("text/godot-project", ".godot")
    resource_pattern = re.compile('"*?(res:/)(/[^"%]+\\.[a-zA-Z0-9]+)"')
    index = {}
    for path in valid_files:
        mime_type, _ = mimetypes.guess_type(path)
        if mime_type is not None and mime_type.startswith("text/godot"):
            if path not in index:
                index[path] = {"valid": True, "references": [], "count": 0, "by": []}
            else:
                index[path]["valid"] = True
            # Let's dissect the file.
            with open(path, "r", encoding="UTF-8") as file:
                line_number = 0
                for line in file:
                    result = resource_pattern.findall(line)
                    if len(result) > 0:  # We got a reference.
                        for res_group in result:
                            # Get the file path without the res://
                            res_local_path = f".{res_group[1]}"
                            valid_res = res_local_path in valid_files
                            if res_local_path not in index:
                                index[res_local_path] = {
                                    "valid": valid_res,
                                    "count": 1,
                                    "references": [],
                                    "by": [],
                                }
                            else:
                                index[res_local_path]["count"] += 1
                            # The info is a bit redundant, but it will ease the further treatments.
                            index[path]["references"].append(
                                {
                                    "line": line_number,
                                    "path": res_local_path,
                                    "valid": valid_res,
                                }
                            )
                            index[res_local_path]["by"].append(
                                {"source": path, "at": line_number}
                            )
                    line_number += 1
    return index


def save_index(index, output_filepath):
    """
    Write down the index to disk.

    Parameters
    ----------
    index : dict
        the cross reference index.
    output_filepath : str
        path to the output file.
    """
    with open(output_filepath, "w", encoding="UTF-8") as output_file:
        output_file.write(json.dumps(index, indent=4))


def diagnosis_bad_references(index):
    """
    Diagnosis bad references.

    Parameters
    ----------
    index: dict
        the index
    """
    print("--- Bad References to Resources ---")
    for key, data in index.items():
        if not data["valid"]:
            if key.startswith("./.import"):
                print(f"Warning ! Referencing an import '{key}'")
            else:
                print(
                    f"The resource '{key}' is not valid. Referenced {data['count']} time(s) at :"
                )
            for ref in data["by"]:
                print(f"\t{ref['source']}:{ref['at']}")


def diagnosis_orphan_resources(index):
    """
    Diagnosis orphan resources.

    Parameters
    ----------
    index : dict
        the index
    """
    print("--- Orphan resources ---")
    print(
        (
            "!! Beware, a null reference count doesn't assess that "
            "a resource is orphan. It might be indirectly referenced (script inheritance "
            "or resource path computation in scripts) !!"
        )
    )
    for key, data in index.items():
        if data["count"] == 0:
            print(f"'{key}'")


def main():
    """
    Main function and entry point.
    The script requires :
    - python3-docopt
    """
    arguments = docopt(__doc__, options_first=True)
    output_filepath = "resources.index"

    if arguments["--output"]:
        output_filepath = arguments["<filepath>"]
    print(f"Output file path is '{output_filepath}'")

    valid_files = retrieve_valid_filepaths()
    index = build_resources_index(valid_files)
    save_index(index, output_filepath)
    diagnosis_bad_references(index)
    diagnosis_orphan_resources(index)


if __name__ == "__main__":
    main()
