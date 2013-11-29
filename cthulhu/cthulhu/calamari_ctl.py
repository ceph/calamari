
import argparse
from cthulhu import config
from cthulhu.persistence import sync_objects


def initialize(args):
    sync_objects.initialize(config.DB_PATH)


def main():
    parser = argparse.ArgumentParser()

    subparsers = parser.add_subparsers()
    initialize_parser = subparsers.add_parser('initialize')
    initialize_parser.set_defaults(func=initialize)

    args = parser.parse_args()
    args.func(args)
