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
                    "insecure-package": [
                        {
                            "value": "insecure-package",
                            "definition": "package"
                        }
                    ]
                }

    - ``preprocess:definition_name``

        - Input as whole is treated as value with the given definition after preprocessing.
          Supported preprocess tags : [json,text,bytes,stream]

- ``path : str``

    - Route in server.

- ``output_mode : str``

    - Mode according to which output from dataflow is treated.

        - ``bytes:content_type:OUTPUT_KEYS``

            - OUTPUT_KEYS are ``.`` separated string which is used as keys to traverse the ouput of the flow.
              eg:

              .. code-block:: python

                  results = {
                      "post_input": {
                          "hex": b'speak'
                      }
                  }

              then ``bytes:post_input.hex`` will return ``b'speak'``.

        - ``text:OUTPUT_KEYS``

        - ``json``

            - Output of dataflow (Dict) is passes as json

- ``immediate_response: Dict[str,Any]``

    - If provided with a response, server responds immediately with
      it, whilst scheduling to run the dataflow.
      Expected keys:

        - ``status``: HTTP status code for the response

        - ``content_type``: MIME type, if not given, determined
          from the presence of body/text/json

        - ``body/text/json``: One of this according to content_type

        - ``headers``

      .. code-block:: json

          {
              "status": 200,
              "content_type": "application/json",
              "data": {"text": "ok"}
          }
