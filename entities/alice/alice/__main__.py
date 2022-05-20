import pkg_resources


def main():
    for entrypoint in pkg_resources.iter_entry_points("console_scripts"):
        if entrypoint.name == "alice":
            return entrypoint.load()()
    raise Exception("Could not find alice's `console_scripts` entrypoint")


if __name__ == "__main__":
    main()
