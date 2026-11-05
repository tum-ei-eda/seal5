import ast
from typing import Union
from pathlib import Path
import csv


def read_metrics(metrics_file: Union[str, Path], allow_missing: bool = True):
    if not Path(metrics_file).is_file():
        assert allow_missing
        return {}
    data = {}
    with open(metrics_file, "r") as infile:
        reader = csv.reader(infile)
        data = []
        for row in reader:
            data.append(row)
        assert len(data) == 2
        keys = data[0]
        vals = data[1]
        # Pandas writes unavailable measurements (None) as empty CSV cells.
        vals = [None if not value.strip() else ast.literal_eval(value) for value in vals]
        data = dict(zip(keys, vals))
    return data
