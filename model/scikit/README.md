# DFFML Models For scikit / sklearn

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
$ cat > train.csv << EOF
Years,Expertise,Trust,Salary
0,1,0.2,10
1,3,0.4,20
2,5,0.6,30
3,7,0.8,40
EOF
$ cat > test.csv << EOF
Years,Expertise,Trust,Salary
4,9,1.0,50
5,11,1.2,60
EOF
$ dffml train \
    -model scikitlr \
    -model-features Years:int:1 Expertise:int:1 Trust:float:1 \
    -model-predict Salary \
    -sources f=csv \
    -source-filename train.csv \
    -source-readonly \
    -log debug
$ dffml accuracy \
    -model scikitlr \
    -model-features Years:int:1 Expertise:int:1 Trust:float:1 \
    -model-predict Salary \
    -sources f=csv \
    -source-filename test.csv \
    -source-readonly \
    -log debug
$ echo -e 'Years,Expertise,Trust\n6,13,1.4\n' | \
  dffml predict all \
    -model scikitlr \
    -model-features Years:int:1 Expertise:int:1 Trust:float:1 \
    -model-predict Salary \
    -sources f=csv \
    -source-filename /dev/stdin \
    -source-readonly \
    -log debug
```

## License

Scikit Models are distributed under the terms of the
[MIT License](LICENSE).
