import pathlib

from cldfbench import scaffold


class Template(scaffold.Template):
    dirs = [pathlib.Path(__file__).parent / 'dataset_template']
