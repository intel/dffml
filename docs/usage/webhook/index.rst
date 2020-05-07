Redeploy dataflow on webhook reception
======================================

This example shows how to deploy your dataflow and to set it up so that it gets redployed
on receiving webhooks from github.

For this example we will 

    - Build a dataflow (`ffmpeg dataflow`) which converts videos to gif.
    - Deploy ffmpeg dataflow on http server.
    - Setup another dataflow to receive webhooks from github.
    - Redeploy the ffmpeg dataflow on receiving webhook.

.. toctree::
    :maxdepth: 2
    :caption: Contents:

    deploy
    webhook
