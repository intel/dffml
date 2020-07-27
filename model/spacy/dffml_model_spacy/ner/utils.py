import ast
import json


def parser(json_file: str, is_predicting: bool) -> dict:
    with open(json_file) as f:
        parsed_data = {}
        data = json.load(f)["data"]
        for id, entry in enumerate(data):
            entities = []
            sentence = entry["sentence"]
            if not ast.literal_eval(is_predicting):
                for entity in entry["entities"]:
                    start = entity["start"]
                    end = entity["end"]
                    tag = entity["tag"]
                    entities.append((start, end, tag))
            parsed_data[id] = {
                "features": {"sentence": sentence, "entities": entities,}
            }
        return parsed_data
