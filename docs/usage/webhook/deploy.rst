.. _usage_ffmpeg_deploy:

Deploying on http server
========================

Dataflow and Config files
-------------------------

Create a ``Dataflow`` with operation ``convert_to_gif`` and save it in ``deploy/df/ffmpeg.yaml``

.. code-block:: console

    $ mkdir -p deploy/mc/http deploy/df
    $ cat > /tmp/operations <<EOF
    convert_to_gif
    EOF

    $ dffml dataflow create -config yaml $(cat /tmp/operations) > deploy/df/ffmpeg.yaml

Create the `Config <../../plugins/service/http/dataflow.html#HttpChannelConfig>`__ file for the http server
in ``deploy/mc/http/ffmpeg.yaml``

.. code-block:: console

    $ cat > ./deploy/mc/http/ffmpeg.yaml <<EOF
    path: /ffmpeg
    presentation: json
    asynchronous: false
    EOF

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

    $ curl -s \
  --header "Content-Type: application/json" \
  --request POST \
  --data '{"convert": [{"value":"PATH_TO_INPUT","definition":"input_file"},
  {"value":"PATH_TO_OUTPUT","definition":"output_file"},
  {"value":1920,"definition":"resolution"}]}' \
  http://localhost:8080/ffmpeg






