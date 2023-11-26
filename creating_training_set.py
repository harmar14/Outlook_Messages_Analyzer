import spacy
import json
import random

def load_data(file):
    # Процедура получает данные из json-файла.
    with open(file, "r") as f:
        data = json.load(f)

def save_data(file, data):
    # Функция записывает данные в файл.
    with open(file, "w") as f:
        json.dump(data, f) # Преобразование объекта Python в объект JSON
    return data

def test_model(model, text):
    doc = nlp(text)
    results = []
    entities = []
    for ent in doc.ents:
        entities.append((ent.start_char, ent.end_char, ent.label_))
    if (len(entities) > 0):
        results = [text, {"entities":entities}]
    return results

# SpaCy принимает данные для обучения в виде: [(text, {"entities":[(start, end, label)]})]

#patterns = create_training_data(PROJECTS_JSON, "PROJECT")
#generate_rules(patterns)

TRAIN_DATA = [] # Переменная для обучающих данных в Python пишется заглавными буквами. 

nlp = spacy.load("model_with_rules")
with open("./folder_name/message.txt", "r") as f:
    text = f.read()

results = test_model(nlp, text)
if (resilts != None):
    TRAIN_DATA.append(result)

save_data("./data/training_data.json", TRAIN_DATA)
