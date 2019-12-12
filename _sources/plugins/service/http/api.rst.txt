API
===

An example of using the API from JavaScript can be found in
`examples/web/api.js <https://github.com/intel/dffml/blob/master/service/http/examples/web/api.js>`_.

.. contents:: REST-like HTTP API

Service
-------

Various APIs specific to this service rather than DFFML are under this path.

Upload
~~~~~~

- ``/service/upload/{filename}``

Upload a file to the ``-upload-dir`` specified when starting the server. You can
make the filename include a path, but the server won't create any directories
that don't already exist.

.. code-block:: json

    {"error": null}

If no ``-upload-dir`` was given on the command line, an error will be returned.
The HTTP status code will be 501, Not Implemented.

.. code-block:: json

    {"error": "Uploads not allowed"}

If you attempt to use ``../../`` or anything which would cause a path outside of
the given ``-upload-dir`` this endpoint will return an error. The HTTP status
code will be 400, Bad Request.

.. code-block:: json

    {"error": "Attempted path traversal"}

If your multipart data doesn't have a field with the ``name`` of ``file``, you
will get an error. The HTTP status code will be 400, Bad Request.

.. code-block:: json

    {"error": "Missing 'file' field"}

.. _list:

List
----

- ``/list/{plugin_type}``

List APIs return JSON objects where the keys are the names of the loadable
classes for a given type of DFFML plugin. The values are that plugin's
configuration options.

Current supported DFFML plugins are as follows.

- ``sources``
- ``models``

To list available plugins, send a ``GET`` request to the endpoint.

The following is an example response body for a request to list available
sources.

- ``/list/sources``

.. code-block:: json

    {
      "csv": {
        "source": {
          "arg": null,
          "config": {
            "csv": {
              "arg": null,
              "config": {
                "filename": {
                  "arg": {},
                  "config": {}
                },
                "readonly": {
                  "arg": {
                    "type": "bool",
                    "action": "store_true",
                    "default": false
                  },
                  "config": {}
                },
                "label": {
                  "arg": {
                    "type": "str",
                    "default": "unlabeled"
                  },
                  "config": {}
                },
                "key": {
                  "arg": {
                    "type": "str",
                    "default": null
                  },
                  "config": {}
                }
              }
            }
          }
        }
      }
    }

.. _configure:

Configure
---------

- ``/configure/{dffml plugin type}/{plugin name}/{label}``

The configure API allows for creation of instances of DFFML plugin types.
Callers supply the type of plugin to instantiate, the name of that plugin, and
then label it will be assigned when using it.

Configuration options can be found in the docs for the various plugins or via
the :ref:`list` endpoint.

To configure a plugin, send a ``POST`` request to the endpoint containing only
the JSON object to be used as the configuration of the requested plugin.

On successful creation and configuration the server will return ``null``
for ``error``.

.. code-block:: json

    {"error": null}

If the plugin name requested is not loadable the server will return a HTTP
status code of 404, Not Found.

.. code-block:: json

    {"error": "source non-existant not found"}

If there is a problem with configuration the server will tell the client. The
HTTP status code will be 400, Bad Request.

.. code-block:: json

    {"error": "CSVSource missing 'filename' from source.mydataset"}

Source
~~~~~~

The following is an example request body to configure the ``csv`` source. The
URL this ``POST`` request is sent to is.

- ``/configure/source/csv/mydataset``

.. code-block:: json

    {
      "source": {
        "arg": null,
        "config": {
          "filename": {
            "arg": [
              "dataset.csv"
            ],
            "config": {}
          },
          "readonly": {
            "arg": [
              true
            ],
            "config": {}
          }
        }
      }
    }

Model
~~~~~

The following is an example request body to configure a model. The URL this
``POST`` request is sent to is.

- ``/configure/source/fake/mymodel``

.. code-block:: json

  {
    "model": {
      "arg": null,
      "config": {
        "directory": {
          "arg": [
            "/home/user/modeldirs/mymodel"
          ],
          "config": {}
        },
        "features": {
          "arg": [
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

.. _context:

Context
-------

After a plugin has been configured, a context must be created. The context label
will be used in all requests for that plugin type, to reference which context
the respective methods should be called on.

- ``/context/{plugin_type}/{label}/{ctx_label}``

To create a context, send a ``GET`` or ``POST`` request to the endpoint
containing the JSON object to be used as the configuration parameters of the
requested plugin context type.

On successful creation of a context the server will return ``null`` for
``error``.

.. code-block:: json

    {"error": null}

If there is no configured plugin for the given label the server will return a
HTTP status code of 404, Not Found.

.. code-block:: json

    {"error": "mydataset source not found"}

Source
~~~~~~

The following is an example request body to create a source context. The URL
this ``GET`` request is sent to is.

- ``/context/source/mydataset/ctx_mydataset``

Model
~~~~~

The following is an example request body to create a model context. The URL
this ``GET`` request is sent to is.

- ``/context/model/mymodel/ctx_mymodel``

Source
------

- ``/source/{ctx_label}/{source context method}/{...}``

The source endpoint exposes all of the methods you'd find in
:py:class:`dffml.source.BaseSourceContext`. The ctx_label parameter in the URL
is the label of the source context that was configured via the :ref:`configure`
and then the :ref:`context` APIs.

If the ctx_label provided does not exist, for instance the configure and
context APIs were not used prior to calling a source method, the server will
return a 404, Not Found response.

.. code-block:: json

    {"error": "Source not loaded"}

.. _repo:

Repo
~~~~

Access a repo by it's unique key. The response will be the JSON representation
of the repo. Here's an example response for a ``GET`` request.

- ``/source/{ctx_label}/repo/{key}``

.. code-block:: json

    {
      "src_url": "myrepo",
      "features": {
        "myfeature": "somevalue"
      }
    }

Just as with DFFML, you'll still get a repo even if the repo doesn't exist
within the source. However, it will only contain the ``src_url``.

Update
~~~~~~

Update a repo by it's unique key. ``POST`` data in the same format received from
repo.

- ``/source/{ctx_label}/update/{key}``

.. code-block:: json

    {
      "src_url": "myrepo",
      "features": {
        "myfeature": "somevalue"
      }
    }

Unless something goes wrong within the source, you'll get a ``null`` error
response.

.. code-block:: json

    {"error": null}

Repos
~~~~~

Initially, client makes a ``GET`` request to the API with the ``chunk_size`` for
the first iteration. ``chunk_size`` is the number of repos to return in one
iteration. The response object will have two properties, ``iterkey`` and
``repos``.

``repos`` is a key value mapping of repo ``src_url``'s to their JSON serialized
repo object.

``iterkey`` will be ``null`` if there are no more repos in the source. If
``iterkey`` is not ``null`` then there are more repos to iterate over. The API
should be called using the response's ``iterkey`` value until the response
contains an ``iterkey`` value of ``null``.

Sample response where ``chunk_size`` is ``1`` and there are more repos to
iterate over. We continue making ``GET`` requests until ``iterkey`` is ``null``.

- ``/source/{ctx_label}/repos/{chunk_size}``
- ``/source/{ctx_label}/repos/{iterkey}/{chunk_size}``

.. code-block:: json

    {
      "iterkey": "1a164836c6d8a27fdf9cd12688440aaa16a852fd1814b170c924a89fba4e084c8ea7522c34f9f5a539803d6237238e90",
      "repos": {
        "myrepo": {
          "src_url": "myrepo",
          "features": {
            "myfeature": "somevalue"
          }
        }
      }
    }

Sample response where the end of iteration has been reached.

.. code-block:: json

    {
      "iterkey": null,
      "repos": {
        "anotherrepo": {
          "src_url": "anotherrepo",
          "features": {
            "myfeature": "othervalue"
          }
        }
      }
    }

Model
------

- ``/model/{ctx_label}/{model context method}/{...}``

The model endpoint exposes all of the methods you'd find in
:py:class:`dffml.model.ModelContext`. The ctx_label parameter in the URL
is the label of the model context that was configured via the :ref:`configure`
and then the :ref:`context` APIs.

If the ctx_label provided does not exist, for instance the configure and
context APIs were not used prior to calling a model method, the server will
return a 404, Not Found response.

.. code-block:: json

    {"error": "Model not loaded"}

.. _train:

Train
~~~~~

Send a ``POST`` request with the JSON body being a list of source context labels
to use as training data.

- ``/model/{ctx_label}/train``

.. code-block:: json

    [
      "my_training_dataset"
    ]

Unless something goes wrong within the model, you'll get a ``null`` error
response.

.. code-block:: json

    {"error": null}

Accuracy
~~~~~~~~

Send a ``POST`` request with the JSON body being a list of source context labels
to use as test data.

- ``/model/{ctx_label}/accuracy``

.. code-block:: json

    [
      "my_test_dataset"
    ]

The response will be a JSON object containing the ``accuracy`` as a float value.

.. code-block:: json

    {"accuracy": 0.42}

Unless something goes wrong within the model, you'll get a ``null`` error
response.

.. code-block:: json

    {"error": null}

Predict
~~~~~~~

To use a model for prediction, send a ``POST`` request to the following URL with
the body being a JSON object mapping ``src_url`` of the repo to the JSON
representation of :py:class:`dffml.repo.Repo` as received by the source repo
endpoint.

- ``/model/{ctx_label}/predict/0``

.. code-block:: json

    {
      "42": {
        "features": {
          "by_ten": 420
        }
      }
    }

Sample response.

.. code-block:: json

    {
      "iterkey": null,
      "repos": {
        "42": {
          "src_url": "42",
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
