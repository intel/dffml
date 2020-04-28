import sys
import subprocess


def literalinclude_blocks():
    literalincludes = subprocess.check_output(
        ["git", "grep", "-A", "10", ".. literalinclude::"]
    )
    literalincludes = literalincludes.decode()
    section = []
    for line in "\n".join(literalincludes.split("\n--\n")).split("\n"):
        if not line.strip():
            continue
        # If literalinclude is in the output git grep will separate with :
        # instead of -
        if ".. literalinclude::" in line:
            line = line.split(":", maxsplit=1)
        else:
            line = line.split("-", maxsplit=1)
        # For blank lines
        if section and (len(line) != 2 or not line[1]):
            yield section
            section = []
            continue
        contains_literalinclude, filecontents = line
        if ".. literalinclude::" in filecontents:
            section = [contains_literalinclude, [filecontents]]
        elif section:
            section[1].append(filecontents)


def main():
    # Map filenames that might have changed to the file which references it's
    # line numbers
    check_changed = {}
    for contains_literalinclude, lines in literalinclude_blocks():
        # Skip blocks that don't reference specific lines
        if not ":lines:" in "\n".join(lines):
            continue
        # Grab the file being referenced
        # Remove /../ used by sphinx docs to reference files outside docs dir
        referenced = lines[0].split()[-1].replace("/../", "", 1)
        check_changed.setdefault(referenced, {})
        check_changed[referenced].setdefault(contains_literalinclude, False)
    # Get the list of changed files
    changed_files = subprocess.check_output(
        ["git", "diff-index", "origin/master"]
    )
    changed_files = changed_files.decode()
    changed_files = list(
        map(
            lambda line: line.split()[-1],
            filter(bool, changed_files.split("\n")),
        )
    )
    rm_paths = []
    for filepath in check_changed:
        if not filepath in changed_files:
            rm_paths.append(filepath)
    for filepath in rm_paths:
        del check_changed[filepath]
    for filepath in check_changed:
        if filepath in changed_files:
            for has_been_updated in check_changed[filepath]:
                if has_been_updated in changed_files:
                    check_changed[filepath][has_been_updated] = True
    # Fail if any are referenced_by
    fail = False
    for referenced_changed, should_have_changed in check_changed.items():
        for filepath, was_changed in should_have_changed.items():
            if not was_changed:
                fail = True
                print(
                    f"{filepath!r} might need updating as line numbers of "
                    + f"{referenced_changed!r} may have changed"
                )
    if not fail:
        return
    sys.exit(1)


if __name__ == "__main__":
    main()
