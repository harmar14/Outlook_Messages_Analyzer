import json
import spacy
from spacy.tokens import DocBin

def load_data(file):
    # Функция получает данные из json-файла.
    with open(file, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data

def convert_data(json_data):
    nlp = spacy.load("ru_core_news_lg")
    db = DocBin()
    for text, annotations in json_data:
        print(text)
        print(annotations)        
        doc = nlp.make_doc(text)
        ents = []
        for start, end, label in annotations["entities"]:
            span = doc.char_span(start, end, label=label)
            if span is None:
                print("Skipping entity")
            else:
                ents.append(span)
        doc.ents = ents
        db.add(doc)
    db.to_disk("./data/dev.spacy")

TRAIN_DATA = load_data("./data/dev_data_set.json")
convert_data(TRAIN_DATA)
