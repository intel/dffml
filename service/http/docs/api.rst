API
===

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

- ``/list/{thing to list}``

List APIs return JSON objects where the keys are the names of the loadable
classes for a given type of DFFML plugin. The values are that plugin's
configuration options.

Sources
~~~~~~~

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

Configuration options can be found in the `DFFML Plugin docs <https://intel.github.io/dffml/plugins/>`_
or via the :ref:`list` endpoint.

Current supported DFFML plugins are as follows.

- ``source``

To configure a plugin, send a ``POST`` request to the endpoint containing only
the JSON object to be used as the configuration of the requested plugin.

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
------

- ``/source/{label}/{source context method}/{...}``

The source endpoint exposes all of the methods you'd find in
:py:class:`dffml.source.BaseSourceContext`. The label parameter in the URL is
the label of the source that was configured with the :ref:`configure` API.

If the label provided does not exists, for instance the configure API was not
used prior to calling a source method, the server will return a 404, Not Found
response.

.. code-block:: json

    {"error": "Source not loaded"}

.. _repo:

Repo
~~~~

- ``/source/{label}/repo/{key}``

Access a repo by it's unique key. The response will be the JSON representation
of the repo. Here's an example response.

.. code-block:: json

    {
      "src_url": "myrepo",
      "features": {
        "myfeature": "somevalue"
      }
    }

Just as with DFFML, you'll still get a repo even if the repo doesn't exist
within the source.

Update
~~~~~~

- ``/source/{label}/update/{key}``

Update a repo by it's unique key. ``POST`` data in the same format received from
:ref:`repo`.

.. code-block:: json

    {
      "src_url": "myrepo",
      "features": {
        "myfeature": "somevalue"
      }
    }

Unless something goes wrong within the source, you'll get a null error response.

.. code-block:: json

    {"error": null}

Repos
~~~~~

- ``/source/{label}/repos/{chunk_size}``
- ``/source/{label}/repos/{iterkey}/{chunk_size}``

Initially, client makes a request to the API with the ``chunk_size`` for the
first iteration. ``chunk_size`` is the number of repos to return in one
iteration. The response object will have two properties, ``iterkey`` and
``repos``.

``repos`` is a key value mapping of repo ``src_url``'s to their JSON serialized
repo object.

``iterkey`` will be ``null`` if there are no more repos in the source. If
``iterkey`` is not ``null`` then there are more repos to iterate over. The API
should be called using the response's ``iterkey`` value until the response
contains an ``iterkey`` value of ``null``.

Sample response where ``chunk_size`` is ``1`` and there are more repos to
iterate over.

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
