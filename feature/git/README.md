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

## TODO

- Transforms
  - Take data of one defintion and label it as another definition.
```json
{
  "defintions": {},
  "operations": {},
  "transforms": {
    "quarter_date_to_git_date": {
      "quarter_date": ["git_date"]
    },
    "thing_to_other_data_types": {
      "thing": ["first_data_type", "second_data_type"]
    },
  },
}
```

## License

DFFML DFFML Features For Git Version Control are distributed under the
[MIT License](LICENSE).
