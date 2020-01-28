# DFFML Scratch Models

## About

Models created without a machine learning framework.

## Install

```console
python3.7 -m pip install --user dffml-model-scratch
```

## Usage

If we have a dataset of years of experience in a job and the Salary (in
thousands) at that job we can use the Simple Linear Regression model to predict
a salary given the years of experience (or the other way around).

First we create the file containing the dataset. Then we train the model, get
its accuracy. And using `echo` pipe a new csv file of data to predict into the
model, and it will give us it prediction of the Salary.

```console
$ cat > dataset.csv << EOF
Years,Salary
1,40
2,50
3,60
4,70
5,80
EOF
$ dffml train -model scratchslr -model-features Years:int:1 -model-predict Salary -sources f=csv -source-filename dataset.csv -source-readonly -log debug
$ dffml accuracy -model scratchslr -model-features Years:int:1 -model-predict Salary -sources f=csv -source-filename dataset.csv -source-readonly -log debug
1.0
$ echo -e 'Years,Salary\n6,0\n' | dffml predict all -model scratchslr -model-features Years:int:1 -model-predict Salary -sources f=csv -source-filename /dev/stdin -source-readonly -log debug
[
    {
        "extra": {},
        "features": {
            "Salary": 0,
            "Years": 6
        },
        "last_updated": "2019-07-19T09:46:45Z",
        "prediction": {
            "confidence": 1.0,
            "value": 90.0
        },
        "key": "0"
    }
]
```

## License

Scratch Models are distributed under the terms of the [MIT License](LICENSE).
