import os
from glob import glob
import yaml


bot_path = "bots"

def all_bots():
    return [
        {
            'path': path,
            'title': os.path.basename(path).split(".")[0].replace("-", " ").title(),
            'base': os.path.basename(path).split(".")[0],
            'tokens': [],
            'history': [],
            **yaml.safe_load(open(path))
        }
        for path in sorted(glob(f"{bot_path}/*.yaml"))
    ]
