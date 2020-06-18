import json
import inspect
import pathlib
import tempfile

from dffml.source.df import DataFlowSource, DataFlowSourceConfig
from dffml.util.asynctestcase import AsyncTestCase
from dffml.util.os import chdir
from dffml.cli.cli import CLI
from dffml.feature import Features, Feature
from dffml.source.source import Sources
from dffml.source.memory import MemorySource, MemorySourceConfig
from dffml.record import Record
from dffml.df.base import op
from dffml.df.types import Input, DataFlow, Definition, InputFlow
from dffml.operation.output import AssociateDefinition


FILE_DATA = {
    "data": [
        {
            "title": "feedface",
            "paragraphs": [
                {
                    "context": "Feeda da facea",
                    "qas": [
                        {
                            "answers": [
                                {"answer_start": 10, "text": "dead beef"}
                            ],
                            "question": "babebabe?",
                            "id": "42",
                        }
                    ],
                }
            ],
        }
    ]
}


def parser(json_file: str) -> dict:
    with open(json_file) as f:
        parsed_data = {}
        data = json.load(f)["data"]
        for entry in data:
            title = entry["title"]
            for para in entry["paragraphs"]:
                context = para["context"]
                for qa in para["qas"]:
                    id = qa["id"]
                    question = qa["question"]
                    start_pos_char = None
                    answers = []
                    answer_text = None

                    if "is_impossible" in qa:
                        is_impossible = qa["is_impossible"]
                    else:
                        is_impossible = False
                    if not is_impossible:
                        answer = qa["answers"][0]
                        answer_text = answer["text"]
                        start_pos_char = answer["answer_start"]
                    parsed_data[id] = {
                        "features": {
                            "question": question,
                            "context": context,
                            "answer_text": answer_text,
                            "start_pos_char": start_pos_char,
                            "title": title,
                            "is_impossible": is_impossible,
                            "answers": answers,
                        }
                    }
        return parsed_data


class TestOpSource(AsyncTestCase):
    async def test_records(self):
        records = []

        with tempfile.NamedTemporaryFile(
            mode="w+t"
        ) as fileobj, tempfile.NamedTemporaryFile(
            mode="w+t", prefix="op_source_test_", suffix=".py"
        ) as pyfile:
            # Initial check to make sure parser works
            json.dump(FILE_DATA, fileobj)
            fileobj.seek(0)
            self.assertEqual(len(parser(fileobj.name)), 1)
            # Write parser to file
            pyfile.write(
                inspect.cleandoc(
                    """
                    import json
                    """
                )
                + "\n\n"
                + inspect.getsource(parser)
            )
            pyfile.seek(0)
            # Now test that operation source works
            with chdir(pathlib.Path(pyfile.name).parent):
                # Load the records
                records = await CLI.cli(
                    "list",
                    "records",
                    "-sources",
                    "a=op",
                    "-source-opimp",
                    f"{pathlib.Path(pyfile.name).stem}:{parser.__name__}",
                    "-source-args",
                    fileobj.name,
                )
                # Make sure they're correct
                self.assertEqual(len(records), 1)
                self.assertDictEqual(
                    records[0].export(),
                    {
                        "key": "42",
                        "features": {
                            "question": "babebabe?",
                            "context": "Feeda da facea",
                            "answer_text": "dead beef",
                            "start_pos_char": 10,
                            "title": "feedface",
                            "is_impossible": False,
                            "answers": [],
                        },
                        "extra": {},
                    },
                )
