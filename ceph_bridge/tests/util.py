import json
import os


def load_fixture(name):
    return json.load(
        open(os.path.join(os.path.dirname(__file__), name), 'r')
    )
