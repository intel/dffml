# DFFML Features For Git Version Control

Git features scrape data from Git repositories.

## Demo

![Demo](https://github.com/intel/dffml/raw/master/docs/images/commits_demo.gif)

## Usage

Here's how you scrape data on the number of commits using the `commit` feature.

```console
dffml evaluate repo -keys https://github.com/intel/dffml -features commits \
  -log debug
```

## License

DFFML DFFML Features For Git Version Control are distributed under the
[MIT License](LICENSE).
