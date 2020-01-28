"""
Script to get a keyword argument from a call to setup
"""
import argparse
import unittest.mock
import importlib.util


def get_kwargs(setup_filepath: str):
    setup_kwargs = {}

    def grab_setup_kwargs(**kwargs):
        setup_kwargs.update(kwargs)

    spec = importlib.util.spec_from_file_location("setup", setup_filepath)
    with unittest.mock.patch("setuptools.setup", new=grab_setup_kwargs):
        setup = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(setup)
    return setup_kwargs


def main():
    parser = argparse.ArgumentParser(
        description="Grab argument from setup call in a setup.py file"
    )
    parser.add_argument("setup_filepath", help="Path to setup.py")
    parser.add_argument("kwarg", help="Keyword argument to write to stdout")

    args = parser.parse_args()
    print(get_kwargs(args.setup_filepath)[args.kwarg])


if __name__ == "__main__":
    main()
