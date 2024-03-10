import spacy
import json
import re
import random

def load_data(file):
    # ��������� �������� ������ �� json-�����.
    with open(file, "r") as f:
        data = json.load(f)

def save_data(file, data):
    # ������� ���������� ������ � ����.
    with open(file, "w") as f:
        json.dump(data, f) # �������������� ������� Python � ������ JSON
    return data

def get_short_dates(text):
    short_date_regex = '([1-9]|1[0-9]|2[0-9]|3[0-1]|0[0-9])(.|-|\/)([1[0-2]|0[0-9])(.|-|\/)(20[0-9][0-9])'
    dates = re.findall(short_date_regex, text)
    dates = [''.join(dates[i]) for i in range(len(dates))]
    return dates

def get_short_dates_without_year(text):
    short_date_regex = '([1-9]|1[0-9]|2[0-9]|3[0-1]|0[0-9])[.|-|\/](1[0-2]|0[0-9])'
    dates = re.findall(short_date_regex, text)
    dates = ['.'.join(dates[i]) for i in range(len(dates))]
    return dates

def get_long_dates(text):    
    long_date_regex = "(\d{1,2})\s+(���(?:|���)|���(?:|�|����)|���(?:|��)|���(?:|���)|��(?:�|�)|���(?:|�|�)|���(?:|�|�)|���(?:|����)|����(?:|����)|���(?:|����)|���(?:|���)|���(?:|����))\s+(\d{4})"
    dates = re.findall(long_date_regex, text, re.I) # re.I ��� ��������������������� (re.IGNORECASE).
    dates = [' '.join(dates[i]) for i in range(len(dates))]
    return dates

def get_long_dates_without_year(text):
    long_date_regex = "(\d{1,2})\s+(���(?:|���)|���(?:|�|����)|���(?:|��)|���(?:|���)|��(?:�|�)|���(?:|�|�)|���(?:|�|�)|���(?:|����)|����(?:|����)|���(?:|����)|���(?:|���)|���(?:|����))\s"
    dates = re.findall(long_date_regex, text, re.I)
    dates = [' '.join(dates[i]) for i in range(len(dates))]
    return dates

def delete_repeats(long_dates, long_dates_no_year):
    for long_date in long_dates:
        no_year = long_date[0:len(long_date)-5] # ����������� ��� � ���� ���������� ������ � long_dates_no_year.
        # ����� ������� ����������, ����� �� ������������ �� �����.
        if (no_year in long_dates_no_year):
            long_dates_no_year.remove(no_year)
    return long_dates_no_year

def retrieve_dates(text):
    short_dates = get_short_dates(text)
    short_dates_no_year = get_short_dates_without_year(text)
    long_dates = get_long_dates(text)
    long_dates_no_year = get_long_dates_without_year(text)
    # ���� ����� ���� �������� ��� � �����, ��� � ���, � �������� ����� ���.
    # ������� �������� �������� � ������ � �������� ��� ����� ��� ������ regex, ����� �������� �������.
    short_dates_no_year = delete_repeats(short_dates, short_dates_no_year)
    long_dates_no_year = delete_repeats(long_dates, long_dates_no_year)
    # ���������� ������������ 4 ������� � ����.
    dates = [*short_dates, *long_dates, *short_dates_no_year, *long_dates_no_year]
    return dates

def extract_weekdays(text):
    regex = "\s(?:(��|��|��|��|��|��|��)|(�����������(?:|�|�|��)|�������(?:|�|�|��)|����(?:�|�|�|��)|�������(?:|�|�|��)|������(?:�|�|�|��)|������(?:�|�|�|��)|����������(?:�|�|�|��)))\s"
    data = re.findall(regex, text, re.I) # re.I ��� ��������������������� (re.IGNORECASE).
    print(data)
    data = [''.join(data[i]) for i in range(len(data))]
    return data

def prepare_result_data(model, text, dates):
    doc = nlp(text)
    results = []
    entities = []
    # PROJECT
    for ent in doc.ents:
        entities.append((ent.start_char, ent.end_char, ent.label_))
    # DATE
    start = 0
    end = 0
    text_backup = text
    for pattern in dates:
        start = text.find(pattern)
        if (start != -1):
            text = text.replace(pattern, '')
            end = start + len(pattern)
            entities.append((start, end, "DATE"))
    text = text_backup
    # WEEKDAY
    #weekdays = extract_weekdays(text)
    #for pattern in weekdays:
        #start = text.find(' ' + pattern + ' ')
        #if (start != -1):
            #start += 1
            #end = start + len(pattern)
            #text = text.replace(pattern, '')
            #entities.append((start, end, "WEEKDAY"))
    #text = text_backup
    
    if (len(entities) > 0):
        results = [text_backup, {"entities":entities}]
    return results

TRAIN_DATA = []

nlp = spacy.load("model_with_rules")
with open("./Shishkina Ekaterina - ���� �������� ���� ��������/message.txt", "r") as f:
    text = f.read()

dates = retrieve_dates(text) # ���������� ���.
#print(dates)

results = prepare_result_data(nlp, text, dates)
print(results)
#if (results != None):
    #TRAIN_DATA.append(results)

#save_data("./data/training_data.json", TRAIN_DATA)