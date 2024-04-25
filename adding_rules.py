import spacy
from spacy.lang.ru import Russian
from spacy.pipeline import EntityRuler
import json

PROJECTS_JSON = "./data/projects.json"
WEEKDAYS_JSON = "./data/weekdays.json"
POSITIONS_JSON = "./data/positions.json"
APPS_JSON = "./data/apps.json"

def load_data(file):
    # Функция получает данные из json-файла.
    with open(file, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data

def generate_better_patterns(file):
    # Функция учитывает вариации написания.
    data = load_data(file)
    new_patterns = []
    for item in data:
        new_patterns.append(item)
        new_patterns.append(item.lower())
        new_patterns.append(item.upper())
    return new_patterns

def create_training_data(file, type):
    # Функция подготовки данных для отправки в модель.
    data = generate_better_patterns(file)
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
    nlp.to_disk("model_with_rules")
    
def test_model(model, text):
    doc = nlp(text)
    results = []
    for ent in doc.ents:
        results.append([ent.text, ent.label_])
    return results

projects_patterns = create_training_data(PROJECTS_JSON, "PROJECT")
weekdays_patterns = create_training_data(WEEKDAYS_JSON, "WEEKDAY")
positions_patterns = create_training_data(POSITIONS_JSON, "POSITION")
apps_patterns = create_training_data(APPS_JSON, "APP")

generate_rules([*projects_patterns, *weekdays_patterns, *positions_patterns, *apps_patterns])

# Тест модели.
nlp = spacy.load("model_with_rules")
with open("./folder_name/message.txt", "r") as f:
    text = f.read()
#print(text)
doc = nlp(text)
for ent in doc.ents:
    print(ent.text, ent.label_)
