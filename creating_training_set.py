import spacy
import json
import re #https://docs.python.org/3/library/re.html
import random

def save_data(file, data):
    # Функция записывает данные в файл.
    with open(file, "w") as f:
        json.dump(data, f) # Преобразование объекта Python в объект JSON.
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
    long_date_regex = "(\d{1,2})\s+(янв(?:|аря)|фев(?:|р|раля)|мар(?:|та)|апр(?:|еля)|ма(?:й|я)|июн(?:|ь|я)|июл(?:|ь|я)|авг(?:|уста)|сент(?:|ября)|окт(?:|ября)|ноя(?:|бря)|дек(?:|абря))\s+(\d{4})"
    dates = re.findall(long_date_regex, text, re.I) # re.I для регистронезависимости (re.IGNORECASE).
    dates = [' '.join(dates[i]) for i in range(len(dates))]
    return dates

def get_long_dates_without_year(text):
    long_date_regex = "(\d{1,2})\s+(янв(?:|аря)|фев(?:|р|раля)|мар(?:|та)|апр(?:|еля)|ма(?:й|я)|июн(?:|ь|я)|июл(?:|ь|я)|авг(?:|уста)|сент(?:|ября)|окт(?:|ября)|ноя(?:|бря)|дек(?:|абря))\s"
    dates = re.findall(long_date_regex, text, re.I)
    dates = [' '.join(dates[i]) for i in range(len(dates))]
    return dates

def delete_repeats(long_dates, long_dates_no_year):
    for long_date in long_dates:
        no_year = long_date[0:len(long_date)-5] # Отбрасываем год и ищем полученную строку в long_dates_no_year.
        # Будем удалять совпадения, чтобы не использовать их снова.
        if (no_year in long_dates_no_year):
            long_dates_no_year.remove(no_year)
    return long_dates_no_year

def retrieve_dates(text):
    short_dates = get_short_dates(text)
    short_dates_no_year = get_short_dates_without_year(text)
    long_dates = get_long_dates(text)
    long_dates_no_year = get_long_dates_without_year(text)
    # Даты могут быть записаны как с годом, так и без, а получать нужно все.
    # Поэтому получаем отдельно с годами и отдельно без годов при помощи regex, потом вычищаем повторы.
    short_dates_no_year = delete_repeats(short_dates, short_dates_no_year)
    long_dates_no_year = delete_repeats(long_dates, long_dates_no_year)
    # Объединяем получившиеся 4 массива в один.
    dates = [*short_dates, *long_dates, *short_dates_no_year, *long_dates_no_year]
    return dates

def extract_weekdays(text):
    regex = "\s(?:(пн|вт|ср|чт|пт|сб|вс)|(понедельник(?:|а|у|ом)|вторник(?:|а|у|ом)|сред(?:а|ы|е|ой)|четверг(?:|а|у|ом)|пятниц(?:а|у|ы|ей)|суббот(?:а|у|ы|ой)|воскресень(?:е|я|ю|ем)))\s"
    data = re.findall(regex, text, re.I) # re.I для регистронезависимости (re.IGNORECASE).
    #print(data)
    data = [''.join(data[i]) for i in range(len(data))]
    return data

def get_phones(text):
    phone_regex = "(?:([+]\d{1,4})(-)?)?(?:(\()(\d{3})(\))(-)?)?(\d{2,4})(-)?(\d{2,4})(-)?(\d{2,9})"
    phones = re.findall(phone_regex, text)
    phones = [''.join(phones[i]) for i in range(len(phones))]
    return phones

def get_emails(text):
    email_regex = "[\w.+-]+@[\w-]+\.[\w.-]+"
    emails = re.findall(email_regex, text)
    emails = [''.join(emails[i]) for i in range(len(emails))]
    return emails

def add_pattern_positions(entities, text, patterns, type):
    text_backup = text
    start = 0
    start_backup = 0
    end = 0
    end_backup = 0
    for pattern in patterns:
        start = text.find(pattern, start, len(text))
        start_backup = text_backup.find(pattern, start_backup, len(text_backup))
        if (start != -1):
            text = text.replace(pattern, '', 1)
            end = start + len(pattern)
            end_backup = start_backup + len(pattern)
            if [start_backup, end_backup, type] not in entities:
                entities.append([start_backup, end_backup, type])
    text = text_backup
    return entities

def prepare_result_data(text):
    nlp = spacy.load("model_with_rules")   
    doc = nlp(text)
    results = []
    entities = []
    # APP, PROJECT, POSITION, WEEKDAY.
    for ent in doc.ents:
        if (ent.start_char, ent.end_char, ent.label_) not in entities:
            entities.append((ent.start_char, ent.end_char, ent.label_))
    # DATE.
    dates = retrieve_dates(text) # Извлечение дат.
    entities = add_pattern_positions(entities, text, dates, "DATE")
    # PHONE.  
    phones = get_phones(text) # Извлечение номеров телефона.
    entities = add_pattern_positions(entities, text, phones, "PHONE")
    # EMAIL.
    emails = get_emails(text) # Извлечение адресов электронной почты.
    entities = add_pattern_positions(entities, text, emails, "EMAIL")
    # Извлекаем сущности базовой моделью Spacy.
    nlp = spacy.load("ru_core_news_lg")
    doc = nlp(text)
    for ent in doc.ents:
        # Исключаем Organization, Location.
        if (ent.label_ == 'PER'):
            entities.append((ent.start_char, ent.end_char, ent.label_))
    # Преобразовываем данные при их наличии.
    if (len(entities) > 0):
        results = [text, {"entities":entities}]
    return results

TRAIN_DATA = []

# 1-80 для train_data_set.json, 80-101 для dev_data_set.json.
for i in range (80, 101):
    with open(f"./data/messages/{i}.txt", "r", encoding="utf-8") as f:
        text = f.read()
        results = prepare_result_data(text)
        #print(results)
        if (results != None):
            TRAIN_DATA.append(results)

print(TRAIN_DATA)

save_data("./data/dev_data_set.json", TRAIN_DATA)
