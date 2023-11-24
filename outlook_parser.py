import win32com.client
import os
import datetime
import re

def incoming_messages(date):
    # Функция получения писем по заданной дате.
    # Подключение к Outlook.
    outlook = win32com.client.Dispatch("Outlook.Application").GetNamespace("MAPI")
    # Получение содержимого папки 'Входящие' в отсортированном по дате получения виде.
    messages = outlook.GetDefaultFolder(6).Items
    messages.Sort("[ReceivedTime]", False)
    # Сбор писем за заданную дату.
    msgList = []
    msg = messages.GetLast()
    while msg:
        recievedDate = msg.ReceivedTime.strftime("%d-%m-%Y")
        if date == recievedDate:
            msgList.append(msg)
        msg = messages.GetPrevious()
    
    return msgList

def print_msg_info(message):
    # Функция выводит данные о письме: conversation, sender, subject.
    conversation = message.ConversationID
    sender = message.SenderName
    #if "-" in sender:
        #sender = sender.split("-", 1)[1]
    sender = sender
    subject = message.Subject
    print(conversation, sender, subject)

def create_folder(folderName):
    # Функция создает папку для данных письма или чистит имеющуюся.
    directory = './' + folderName
    if not os.path.exists(directory):
        os.mkdir(directory)
    else:
        delete_files_in_folder(directory)
    return directory

def delete_files_in_folder(directory):
    # Удаление объектов из директории.
    for fileName in os.listdir(directory):
        filePath = os.path.join(directory, fileName)
        try:
            if os.path.isfile(filePath):
                os.remove(filePath)
        except Exception as e:
            print(f'Ошибка при удалении файла {filePath}. {e}')


def getData(msgList, conversation, directory):
    # Функция, которая получает текст выбранного письма.
    for msg in msgList:
        if (msg.ConversationID == conversation):
            file = open(directory + "/message.txt", "w")
            file.write(msg.Body.replace('\n', '').replace(' \CR',''))
            file.close()
            break

def Main():
    # Ввод даты, за которую требуется искать письма, и приведение ее формата.
    print('Введите дату формата %d.%m.%Y')
    inputDate = datetime.datetime.strptime(input(), "%d.%m.%Y")
    # Получение входящих писем по заданной дате.
    msgList = incoming_messages(inputDate.date().strftime("%d-%m-%Y"))
    
    # ПОЛЬЗОВАТЕЛЬ БУДЕТ ВЫБИРАТЬ ПИСЬМО ЧЕРЕЗ ИНТЕРФЕЙС, А ПОКА ВОЗЬМЕМ ОДНО ЛЮБОЕ    
    print_msg_info(msgList[1])
    
    specificID = msgList[1].ConversationID
    folderName = msgList[1].SenderName + ' - ' + msgList[1].Subject
    # Создание папки и сохранение тела письма в файл внутри нее.
    getData(msgList, specificID, create_folder(folderName))
    
Main()
#24.11.2023
