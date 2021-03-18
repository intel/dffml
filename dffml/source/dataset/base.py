from ..wrapper import (
    context_managed_wrapper_source,
    ContextManagedWrapperSource,
)


def dataset_source(entrypoint_name) -> ContextManagedWrapperSource:
    r"""
    Allows us to quickly programmatically provide access to existing datasets
    via existing or custom sources.

    Under the hood this is an alias for
    :py:func:`dffml.source.wrapper.context_managed_wrapper_source`
    with ``qualname_suffix`` set to "DatasetSource".

    Examples
    --------

    Say we have the following dataset hosted at
    http://example.com/my_training.csv

    Let's test this locally by creating a file and serving it from our local
    machine. Write the following file.

    **my_training.csv**

    .. code-block::
        :test:
        :filepath: my_training.csv

        feed,face,dead,beef
        0.0,0,0,0
        0.1,1,10,100
        0.2,2,20,200
        0.3,3,30,300
        0.4,4,40,400

    We can start an HTTP server using Python

    .. code-block:: console
        :test:
        :daemon: 8080

        $ python3 -m http.server 8080

    We could write a dataset source to download and cache the contents locally
    as follows. We want to make sure that we validate the contents of datasets
    using SHA 384 hashes (see
    :py:func:`cached_download <dffml.util.net.cached_download>` for more
    details). Without hash validation we risk downloading the wrong file or
    potentially malicious files.

    **my_training.py**

    .. literalinclude:: /../examples/source/dataset/base/dataset_source/my_training.py
        :test:

    We can use it from Python in two different ways as follows

    **run.py**

    .. literalinclude:: /../examples/source/dataset/base/dataset_source/my_training_run.py
        :test:
        :filepath: run.py

    .. code-block:: console
        :test:
        :replace: cmds[0][-2] = cmds[0][-2].replace("8080", str(ctx["HTTP_SERVER"]["8080"]))

        $ python3 run.py http://localhost:8080/my_training.csv cache_dir

    Or we can use it from the command line

    .. code-block:: console
        :test:
        :replace: cmds[0][-1] = cmds[0][-1].replace("8080", str(ctx["HTTP_SERVER"]["8080"]))

        $ dffml list records \
            -sources training=my_training:my_training_dataset.source \
            -source-training-cache_dir cache_dir \
            -source-training-url http://localhost:8080/my_training.csv

    """
    return context_managed_wrapper_source(
        entrypoint_name, qualname_suffix="DatasetSource"
    )
