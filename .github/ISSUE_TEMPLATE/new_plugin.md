---
name: New Plugin
about: I've created a new plugin for DFFML
title: 'plugin: new: '
labels: documentation
assignees: ''

---

I've created a new plugin for DFFML!

The package name on PyPi is .... / GitHub repo is ....

It provides Sources / Models / Operations / Data Flow

The following are it's `entry_points`

```python
    # (copy paste yours here, example is from dffml/setup.py)
    entry_points={
        'dffml.source': [
            'csv = dffml.source.csv:CSVSource',
            'json = dffml.source.json:JSONSource',
            'memory = dffml.source.memory:MemorySource',
        ],
    }
```

Here is what each one does (in rST, leave the \`\`\` so it can be copy pasted)

`*Community*` means that you are a member of the DFFML community that is
contributing a plugin. If there is a plugin maintained within the DFFML git repo
that needs to be added to the documentation it will be an `*Official*` plugin.

```
CSV
---

*Community*

Loads and saves Repos from CSV files.

**Args**

- filename: String

  - Path to CSV file

- readonly: Boolean

  - True if the file should not be written back to
```
