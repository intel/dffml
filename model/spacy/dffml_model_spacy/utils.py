import ast
import json


def parser(json_file: str, is_training: bool) -> dict:
    with open(json_file) as f:
        parsed_data = {}
        data = json.load(f)["data"]
        for id, entry in enumerate(data):
            entities = []
            sentence = entry["sentence"]
            if is_training:
                for entity in entry["entities"]:
                    start = entity["start"]
                    end = entity["end"]
                    tag = entity["tag"]
                    context = para["context"]
                    entities.append((start, end, tag))
            parsed_data[id] = {
                "features": {"sentence": sentence, "entities": entities,}
            }
        return parsed_data
