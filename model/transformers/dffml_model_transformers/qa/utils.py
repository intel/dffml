import ast
import json


def parser(json_file: str, is_training: bool) -> dict:
    with open(json_file) as f:
        parsed_data = {}
        data = json.load(f)["data"]
        answers = []
        for entry in data:
            title = entry["title"]
            for para in entry["paragraphs"]:
                context = para["context"]
                for qa in para["qas"]:
                    id = qa["id"]
                    question = qa["question"]
                    start_pos_char = None
                    answer_text = None
                    answers = []
                    is_impossible = (
                        qa["is_impossible"] if "is_impossible" in qa else False
                    )
                    if not is_impossible:
                        if ast.literal_eval(is_training):
                            answer = qa["answers"][0]
                            answer_text = answer["text"]
                            start_pos_char = answer["answer_start"]
                        else:
                            answers = [{"text": " ", "answer_start": 0}]
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
