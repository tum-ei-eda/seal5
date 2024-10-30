import ast
from typing import Union
from pathlib import Path
import csv


def read_metrics(metrics_file: Union[str, Path], allow_missing: bool = True):
    # print("read_metrics", metrics_file, allow_missing)
    # input("?")
    if not Path(metrics_file).is_file():
        # print("not file")
        # input("!")
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
        print("keys", keys)
        print("vals", vals)
        # vals = list(map(lambda x: "{}" if x == "set()" else x, vals))
        vals = list(map(lambda x: ast.literal_eval(x), vals))
        data = dict(zip(keys, vals))
    # print("data", data)
    # input("ret")
    return data
