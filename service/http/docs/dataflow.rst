DataFlow
========

The following documentation explains how to configure and deploy DataFlows
via the HTTP service.

HttpChannelConfig
-----------------

- ``asynchronous: bool``

    - Unused right now but will be accessible over a websocket in the future and used for long running flows.

- ``dataflow : DataFlow``

    - Flow to which inputs from request to path is forwarded too.

- ``input_mode : str``

    - Mode according to which input data is passed to the dataflow, ``default:default``.

        - ``default``

            Inputs are expected to be mapping of context to list of input
            to definition mappings
            eg:

                .. code-block:: json

                                        {
                                        "insecure-package":
                                            [
                                                {
                                                    "value":"insecure-package",
                                                    "definition":"package"
                                                }
                                            ]
                                        }

        - ``preprocess:definition_name``

                Input as whole is treated as value with the given definition after preprocessing.
                Supported preprocess tags : [json,text,bytes,stream]

- ``path : str``

    - Route in server.

- ``output_mode : str``

    - Mode according to which output from dataflow is treated.

        - ``bytes:OUTPUT_KEYS``

            - OUTPUT_KEYS are ``.`` seperated string which is used as keys to traverse the ouput of the flow.
            eg:

            .. code-block:: json

                results = {
                    "post_input":
                        {
                            "hex":b'speak'
                        }
                    }

            then ``bytes:post_input.hex`` will return ``b'speak'``.

        - ``text:OUTPUT_KEYS``

        - `json`

            - output of dataflow (Dict) is passes as json

        - `stream:content_type:OUPUT_KEYS`

            - a response of stream type is returned,to which results.OUTPUT_KEYS are wrote.
