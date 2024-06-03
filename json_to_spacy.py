import json
import re
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
        # NER.
        ents = []
        isUrgent = False
        for start, end, label in annotations["entities"]:
            span = doc.char_span(start, end, label=label)
            if span is None:
                print("Skipping entity")
            else:
                ents.append(span)
                if ( label == "DATE" or label == "WEEKDAY" ):
                    isUrgent = True
                elif ( label == "POSITION" ):
                    checkEnt = re.findall("руководитель", text[start:end], re.I)
                    if ( len(checkEnt) > 0 ):
                        isUrgent = True                    
        doc.ents = ents
        print(ents)
        print(isUrgent)
        # Classification.
        if ( isUrgent ):
            doc.cats["positive"] = 1
            doc.cats["negative"] = 0
        else:
            doc.cats["positive"] = 0
            doc.cats["negative"] = 1           
        db.add(doc)
    db.to_disk("./data/train_2.spacy")

TRAIN_DATA = load_data("./data/training_data_set.json")
convert_data(TRAIN_DATA)
