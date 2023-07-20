# Toolbox

This directory contains a set of external/thirdparty tools that can be useful when managing a Godot project.

## Tools

### Resource Indexer

The resource indexer is a simple python script that retrieve reference to resources, indexes them and perform diagnosis (missing resources, invalid resources pointers).
It requires the following:
- Python 3
- python3-docopt

#### Usage

```resource_indexer.py [(-o | --output) <filepath>] [(-p | --project) <projectpath>] [--orphan] (-h | --help)```

Options:
 - ```-h --help``` : Display help.
 - ```-o --output``` : Set the output file path [default: resources.index].
 - ```-p --project``` : Path to the project to inspect [default: .].
 - ```--orphan``` : Display orphan resources (experimental).

