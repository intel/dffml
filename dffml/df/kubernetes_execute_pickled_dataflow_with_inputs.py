import os
import json
import pickle
import pathlib
import logging

import dffml
import dffml.noasync


def main():
    # Turn on logging
    logging.basicConfig(level=logging.DEBUG, filename=os.environ["LOG_FILE"])
    # Assume one context is being run and we want the output of that context
    # [(ctx_as_str, {'product': 36})]
    # So use [0] for first context returned and then [1] to select results
    print(
        json.dumps(
            dffml.export(
                list(
                    dffml.noasync.run(
                        dffml.DataFlow._fromdict(
                            **json.loads(
                                pathlib.Path(
                                    os.environ["DATAFLOW"]
                                ).read_text()
                            )
                        ),
                        [
                            dffml.Input._fromdict(**item)
                            for item in json.loads(
                                pathlib.Path(os.environ["INPUTS"]).read_bytes()
                            )
                        ],
                    )
                )[0][1]
            )
        )
    )


if __name__ == "__main__":
    main()
