# DFFML model_name Models

## About

Models created using scikit.

## Install

```console
python3.7 -m pip install --user dffml-model-scikit
```

## Usage

1. Linear Regression Model

For implementing linear regression to a dataset, let us take a simple example:

| Years of Experience  |  Expertise | Trust Factor | Salary |
| -------------------- | ---------- | ------------ | ------ |
|          0           |     01     |      0.2     |   10   |
|          1           |     03     |      0.4     |   20   |
|          2           |     05     |      0.6     |   30   |
|          3           |     07     |      0.8     |   40   |
|          4           |     09     |      1.0     |   50   |
|          5           |     11     |      1.2     |   60   |

```console
```console
$ cat > dataset.csv << EOF
Years,Expertise,Trust,Salary
0,01,0.2,10
1,03,0.4,20
2,05,0.6,30
3,07,0.8,40
4,09,1.0,50
5,11,1.2,60
EOF
```

## License

Scikit Models are distributed under the terms of the
[MIT License](LICENSE).
