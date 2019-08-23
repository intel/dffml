import pkg_resources


def main():
    for entrypoint in pkg_resources.iter_entry_points("console_scripts"):
        if entrypoint.name == "dffml":
            return entrypoint.load()()
    raise Exception("Could not find dffml entrypoint")


if __name__ == "__main__":
    main()
