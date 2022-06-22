.. _usage_webhook:

Redeploying on receiving GitHub webhook
=======================================

We'll move ``ffmpeg`` to a GitHub repo, and set up a webhook DataFlow such that whenever
we push to the default branch, the new version is pulled and its docker container is built and run.

Webhook Dataflow
----------------

We'll be using operations from ``dffml-operations-deploy``, ``dffml-feature-git``, ``dffml-config-yaml``.

.. code-block:: console

    $ pip install dffml-operations-deploy dffml-feature-git dffml-config-yaml

Setup a http server in ``ffmpeg/deploy/webhook``, to receive webhook and redploy ffmpeg

.. code-block:: console

    $ mkdir -p deploy/webhook/df deploy/webhook/mc/http
    $ dffml dataflow create \
        -configloader yaml \
        -inputs \
          true=valid_git_repository_URL \
        -config \
          ini=check_secret_match.secret.plugin \
          "./deploy/webhook/secret.ini"=check_secret_match.secret.config.filename \
        -- \
          check_secret_match \
          get_url_from_payload \
          clone_git_repo \
          check_if_default_branch \
          get_image_tag \
          get_running_containers \
          get_status_running_containers \
          parse_docker_commands \
          docker_build_image \
          restart_running_containers \
          cleanup_git_repo \
        | tee deploy/webhook/df/webhook.yaml

Through config we specify the dataflow to use ini file plugin and use the ini file
located at deploy/webhook/secret.ini that contains the secret token, which we’ll
setup in GitHub.

**deploy/webhook/secret.ini**

.. literalinclude:: /../examples/ffmpeg/deploy/webhook/secret.ini

Config

**deploy/webhook/mc/http/webhook.yaml**

.. code-block:: console

    $ cat > ./deploy/webhook/mc/http/webhook.yaml <<EOF
    path: /webhook/github
    output_mode: json
    input_mode: bytes:payload
    forward_headers: webhook_headers
    immediate_response:
        status: 200
        content_type: application/json
        data:
            status: Received
    EOF

Note that the input_mode is ``bytes:payload``, this means that inputs
from post request will be passed as bytes to the dataflow with
``payload`` definition. We don't want to wait until the dataflow
completes running to send a response back, so we also add an
``immediate_response`` to the server configuration.


Deploy it in port 8081 as 8080 is being used by ffmpeg http service

.. code-block:: console

    $ dffml service http server -insecure -mc-config deploy/webhook -port 8081

.. note::

    If you're not setting this up on a server directly accessible on the internet,
    here are two methods of exposing the webhook,

    Using `localhost.run <https://localhost.run>`_

    .. code-block:: console

        $ ssh -R 80:localhost:8081 $RANDOM@ssh.localhost.run

    .. image:: ./images/localhost_run.png

    Using ngrok

    .. code-block:: console

        $ ~/ngrok http 8081

    .. image:: ./images/ngrok_out.png

Copy paste the output url to ``Payload URL`` in webhook settings of ffmpeg repo and set
the secret token.

.. image:: ./images/github_settings.png

Now whenever there's a push to the default branch of the repo, the ffmpeg container
which is running gets redeployed from the fresh pull. To check this we will modify the
end time of the conversion from 10 to 12 in ``ffmpeg/operations.py`` by changing

.. code-block:: python

    proc = await asyncio.create_subprocess_exec(
        "ffmpeg",
        "-ss",
        "0.3",
        "-t",
        "10",
        ..
        ..
    )

to

.. code-block:: python

    proc = await asyncio.create_subprocess_exec(
        "ffmpeg",
        "-ss",
        "0.3",
        "-t",
        "12",
        ..
        ..
    )

on pushing the changes to our repo, the container will be redeployed. To verify this run
``docker ps`` and check the up time of the container.
