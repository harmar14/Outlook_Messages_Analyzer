import spacy
from spacy.lang.ru import Russian
from spacy.pipeline import EntityRuler
import json

PROJECTS_JSON = "./data/projects.json"

def load_data(file):
    # Функция получает данные из json-файла.
    with open(file, "r") as f:
        data = json.load(f)
    return data

def generate_better_projects(file):
    # Функция учитывает вариации написания названий проектов.
    data = load_data(file)
    new_projects = []
    for item in data:
        new_projects.append(item)
        new_projects.append(item.lower())
        new_projects.append(item.upper())
    return new_projects

def create_training_data(file, type):
    # Функция подготовки данных для дообучения.
    data = generate_better_projects(file)
    patterns = []
    for item in data:
        pattern = {"label":type, "pattern":item}
        patterns.append(pattern)
    return patterns

def generate_rules(patterns):
    # Процедура добавляет правила в модель.
    nlp = Russian()
    ruler = nlp.add_pipe("entity_ruler")
    ruler.add_patterns(patterns)
    nlp.to_disk("trained_model")
    
def test_model(model, text):
    doc = nlp(text)
    results = []
    for ent in doc.ents:
        results.append([ent.text, ent.label_])
    return results

#patterns = create_training_data(PROJECTS_JSON, "PROJECT")
#generate_rules(patterns)

# Тест модели.
nlp = spacy.load("trained_model")
with open("./Shishkina Ekaterina - День рождения Леры Пестовой/message.txt", "r") as f:
    text = f.read()
print(text)
doc = nlp(text)
for ent in doc.ents:
    print(ent.text, ent.label_)