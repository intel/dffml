Dataflow
========

HttpChannelConfig
-----------------
    - ``path : str``

        Route in server.

    - ``dataflow : DataFlow``

        Flow to which inputs from request to path is forwarded too.

    - ``input_mode : str``

        Mode according to which input data is passed to the dataflow,``default:default``.

            - ``default`` :
                Inputs are expected to be mapping of context to list of input
                    to definition mappings
                    eg:

                    .. code-block:: console

                        {
                        "insecure-package":
                            [
                                {
                                    "value":"insecure-package",
                                    "definition":"package"
                                }
                            ]
                        }

            - ``preprocess:definition_name`` :
                Input as whole is treated as value with the given definition after preprocessing.
                Supported preprocess tags : [json,text,bytes,stream]
