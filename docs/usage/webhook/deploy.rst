.. _usage_ffmpeg_deploy:

Deploying with the HTTP Service
===============================

In this tutorial we will deploy a dataflow(ffmpeg dataflow) which converts a video to gif over an http server.We'll also
see how to deploy the same http server in a docker container.Finally in :ref:`usage_ffmpeg_deploy_serve`
we'll setup another http server which waits on GitHub webhooks to rebuilt and deploy the ffmpeg dataflow.

.. note::

    All the code for this example is located under the
    `examples/ffmpeg <https://github.com/intel/dffml/blob/master/examples/ffmpeg/>`_
    directory of the DFFML source code.Rest of the tutorial is ran from the root of
    this folder.

Write operations and definitions to convert videos files to gif by calling
``ffmpeg`` (Make sure you `download and install <https://www.ffmpeg.org/download.html>`_ it.).
The operation accepts bytes (of the video), converts it to gif and outputs it as bytes.

**ffmpeg/operations.py**

.. literalinclude:: /../examples/ffmpeg/ffmpeg/operations.py

Dataflow and Config files
-------------------------

**ffmpeg/dataflow.py**

.. literalinclude:: /../examples/ffmpeg/ffmpeg/dataflow.py

.. code-block:: console

    $ mkdir -p deploy/mc/http deploy/df
    $ dffml service dev export -config yaml ffmpeg.dataflow:DATAFLOW > deploy/df/ffmpeg.yaml

Create the config file for the HTTP service
in ``deploy/mc/http/ffmpeg.yaml``

.. code-block:: console

    $ cat > ./deploy/mc/http/ffmpeg.yaml <<EOF
    path: /ffmpeg
    input_mode: bytes:Input_file
    output_mode: bytes:post_input.Output_file
    EOF

- ``input_mode``

    - ``bytes:Input_file``

        - We want the input from the request to be treated as bytes with definition ``Input_file``.

- ``output_mode``

    - ``bytes:post_input.Output_file``

        - We want the response to be bytes taken from  ``results["post_input"]["Output_file"]``, where ``results`` is the output of the dataflow.

For more details see `HttpChannelConfig <../../plugins/service/http/dataflow.html#HttpChannelConfig>`__ .

.. _usage_ffmpeg_deploy_serve:

Serving the DataFlow
--------------------

Serving the dataflow on port 8080

.. code-block:: console

    $ dffml service http server -insecure -mc-config deploy -port 8080

.. warning::

    The ``-insecure`` flag is only being used here to speed up this
    tutorial. See documentation on HTTP API
    :doc:`/plugins/service/http/security` for more information.

Now from another terminal, we can send post requests to the dataflow running at this port.

.. code-block:: console

    $ curl -v --request POST --data-binary @input.mp4 http://localhost:8080/ffmpeg -o output.gif

You should replace ``input.mp4`` with path to your video file and ``output.gif`` to where you want the converted gif
to be output to. An example video is available `here <https://github.com/intel/dffml/blob/master/examples/ffmpeg/>`_ .

Deploying on docker container
=============================

A ``Dockerfile`` is already generated in ffmpeg folder. We need to modify it to include ``ffmpeg``.

**Dockerfile**

.. literalinclude:: /../examples/ffmpeg/Dockerfile

.. note::
    The run command in the comment section of the Dockerfile will be used to execute
    the container after receving webhooks , so make sure you change it to your usecase.

For this tutorial we will change it to

.. code-block:: json

    docker run --rm -d -ti -p 8080:8080 $USER/ffmpeg -mc-config deploy -insecure -log debug

.. note::

    The image built after pulling the contaier will be taged ``USERNAME/REPONAME``, where USERNAME and REPONAME
    are gathered from the github html url, received in the webhook.

We can run the container and sent a post request to verify that the container is working.

.. code-block:: console

    $ docker build -t $USER/ffmpeg .
    $ docker run --rm -d -ti -p 8080:8080 $USER/ffmpeg -mc-config deploy -insecure -log debug

.. code-block:: console

    $ curl -v --request POST --data-binary @input.mp4 http://localhost:8080/ffmpeg -o output.gif

Now in :ref:`usage_webhook` we'll setup this container to be automatically redeployed
whenever we push to the Git repo containing this code.