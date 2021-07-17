Python
==========

This is an example of how you can use the web API from Python.

.. code-block:: python

  import requests

  from dffml_model_scikit import LinearRegressionModel

  model = LinearRegressionModel(
      features=Features(
          Feature("Years", int, 1),
          Feature("Expertise", int, 1),
          Feature("Trust", float, 1),
      ),
      predict=Feature("Salary", int, 1),
      location="tempdir",
  )

  ## Configure model

  URL = "https://127.0.0.1:5000/configure/model/{model}/{label}".format(model = "fake", label = "mymodel")
  PARAMS = {
    {
      "model": {
        "plugin": null,
        "config": {
          "location": {
            "plugin": [
              "/home/user/modeldirs/mymodel"
            ],
            "config": {}
          },
          "features": {
            "plugin": [
              {
                "name": "Years",
                "dtype": "int",
                "length": 1
              },
              {
                "name": "Expertise",
                "dtype": "int",
                "length": 1
              },
              {
                "name": "Trust",
                "dtype": "float",
                "length": 1
              }
            ],
            "config": {}
          }
        }
      }
    }
  }

  result = requests.post(url = URL, params = PARAMS)

  *Note*: On successful creation and configuration the server will return  {"error": null}

  ## Context Creation

  URL = "https://127.0.0.1:5000/context/mdoel/{label}/{ctx_label}".format(label = "mymodel", ctx_label = "ctx_mymodel")
  result = requests.get(url = URL, params = {})

  *Note*: On successful creation of a context the server will return {"error": null}

  ## Train the Model

  URL = "https://127.0.0.1:5000/model/{ctx_label}/train".format(ctx_label = "ctx_mymodel")
  params = {
    [
      "my_training_dataset"
    ]
  }
  result = requests.post(url = URL, params = PARAMS)

  *Note*: On successful execution the server will return {"error": null}

  ## Assess Accuracy

  URL = "https://127.0.0.1:5000/model/{ctx_label}/accuracy".format(ctx_label = "ctx_mymodel")
  params = {
    [
      "my_test_dataset"
    ]
  }
  result = requests.post(url = URL, params = PARAMS)

  *Note*: On successful execution the response will be a JSON object containing the accuracy as a float value : {"accuracy": 0.42}

  ## Make Prediction

  URL = "https://127.0.0.1:5000/model/{ctx_label}/predict/0".format(ctx_label = "ctx_mymodel")
  PARAMS = {
    {
      "42": {
        "features": {
          "by_ten": 420
        }
      }
    }
  }

  *Note*: The JSON passed as param maps key of the record to the JSON representation of dffml.record.Record as received by the source record endpoint

  result = requests.post(url = URL, params = PARAMS)

  *Note*: On successful execution the response will be a JSON object similar to this:

  response = {
    "iterkey": null,
    "records": {
      "42": {
        "key": "42",
        "features": {
          "by_ten": 420
        },
        "prediction": {
          "confidence": 42,
          "value": 4200
        },
        "last_updated": "2019-10-15T08:19:41Z",
        "extra": {}
      }
    }
  }
