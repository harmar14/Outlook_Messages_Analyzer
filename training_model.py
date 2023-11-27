import spacy
import json
import random

def load_data(file):
    # Процедура получает данные из json-файла.
    with open(file, "r") as f:
        data = json.load(f)

def train_model(data, iterations):
    TRAIN_DATA = data
    # Создание новой модели.
    nlp = spacy.blank("ru")
    # Если в модели нет пайплайна NER, нужно создать.
    if ("ner" not in nlp.pipe_names):
        ner = nlp.create_pipe("ner")
        nlp.add_pipe(ner, last = True)
    # Добавление имен сущностей в модель.
    for _, annotations in TRAIN_DATA:
        for ent in annotations.get("entities"):
            ner.add_label(ent[2])
    # Затрагивать только пайплайн NER.
    other_pipes = [pipe for pipe in nlp.pipe_names if pipe != "ner"]
    with nlp.disable_pipes(*other_pipes):
        # Обучение модели.
        optimizer = nlp.begin_training()
        for itn in range(iterations):
            print("Starting iteration " + str(itn))
            # Данные для обучения берутся в случайном порядке, чтобы модель не привязывалась к их порядку.
            random.shuffle(TRAIN_DATA)
            losses = {}
            for text, annotations in TRAIN_DATA:
                nlp.update([text], [annotations], drop = 0.2, sqd = optimizer, losses = losses)
                print(losses)
    return nlp
    
# Закомментировать этот блок после обучения модели.
TRAIN_DATA = load_data("./data/training_data.json")
nlp = train_model(TRAIN_DATA, 30)
nlp.to_disk("trained_model")

# Написать тут любой текст для теста.
#test = ""

# Тест модели.
#nlp = spacy.load("trained_model")
#doc = nlp(test)
#for ent in doc.ents:
    #print(ent.text, ent.label_)
