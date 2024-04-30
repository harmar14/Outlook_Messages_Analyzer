from PyQt5 import QtCore, QtGui, QtWidgets
import win32com.client
import datetime
import os
import sys
import spacy
import subprocess
import tempfile

msgDataList = []

class AppWindow(object):
    def setupUI(self, MainWindow):
        # Создание окна.
        MainWindow.setObjectName("MainWindow")
        MainWindow.setWindowTitle("Анализ корреспонденции")
        # Окно не будет масштабироваться.
        MainWindow.resize(1113, 797)
        MainWindow.setMinimumSize(QtCore.QSize(1113, 797))
        MainWindow.setMaximumSize(QtCore.QSize(1113, 797))
        # Определяем размер шрифта (по умолчанию слишком мелкий).
        font = QtGui.QFont()
        font.setPointSize(9)
        MainWindow.setFont(font)
        
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        
        # Общий слой.
        self.mainLayout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.mainLayout.setSpacing(12)
        self.mainLayout.setObjectName("mainLayout")
        
        # Предупреждение.
        self.noticeLabel = QtWidgets.QLabel(self.centralwidget)
        self.noticeLabel.setText("! Перед работой необходимо запустить MS Outlook на этом компьютере и войти в учетную запись !")
        self.noticeLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.noticeLabel.setObjectName("noticeLabel")
        self.mainLayout.addWidget(self.noticeLabel)
        
        # Разделитель между предупреждением и рабочей областью.
        self.headerLine = QtWidgets.QFrame(self.centralwidget)
        self.headerLine.setFrameShape(QtWidgets.QFrame.HLine)
        self.headerLine.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.headerLine.setObjectName("headerLine")
        self.mainLayout.addWidget(self.headerLine)
        
        # Блок для выбора даты.
        self.dateContainer = QtWidgets.QHBoxLayout()
        self.dateContainer.setObjectName("dateContainer")
        # Отступ слева от даты.
        dateLeftSpacer = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.dateContainer.addItem(dateLeftSpacer)
        # Надпись "Выберите дату".
        self.dateLabel = QtWidgets.QLabel(self.centralwidget)
        self.dateLabel.setText("Выберите дату")
        self.dateLabel.setObjectName("dateLabel")
        self.dateContainer.addWidget(self.dateLabel)
        # Поле выбора даты.
        self.dateEdit = QtWidgets.QDateEdit(self.centralwidget)
        self.dateEdit.setDate(QtCore.QDate.fromString(datetime.date.today().strftime("%Y-%m-%d"), "yyyy-MM-dd")) # Заполнение текущей датой.
        self.dateEdit.setObjectName("dateEdit")
        self.dateContainer.addWidget(self.dateEdit)
        # Кнопка выбора даты.
        self.dateButton = QtWidgets.QPushButton(self.centralwidget)
        self.dateButton.setText("Выбрать")
        self.dateButton.setObjectName("dateButton")
        self.dateButton.clicked.connect(self.onDateSubmit)
        self.dateContainer.addWidget(self.dateButton)
        # Отступ справа от даты.
        dateRightSpacer = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.dateContainer.addItem(dateRightSpacer)
        self.mainLayout.addLayout(self.dateContainer)
        
        # Блок с таблицами.
        self.workContainer = QtWidgets.QHBoxLayout()
        self.workContainer.setObjectName("workContainer")
        # Таблица для вывода писем.
        self.mailTable = QtWidgets.QTableWidget(self.centralwidget)
        self.mailTable.setObjectName("mailTable")
        self.mailTable.setColumnCount(1)
        item = QtWidgets.QTableWidgetItem()
        item.setText("Письмо")
        self.mailTable.setHorizontalHeaderItem(0, item)
        self.mailTable.setColumnWidth(0, 535)
        self.mailTable.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.workContainer.addWidget(self.mailTable)        
        # Таблица для вывода сущностей.
        self.resultTable = QtWidgets.QTableWidget(self.centralwidget)
        self.resultTable.setObjectName("resultTable")
        self.resultTable.setColumnCount(1)
        item = QtWidgets.QTableWidgetItem()
        item.setText("Результат")
        self.resultTable.setHorizontalHeaderItem(0, item)
        self.resultTable.setColumnWidth(0, 535)
        self.resultTable.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.workContainer.addWidget(self.resultTable)        
        self.mainLayout.addLayout(self.workContainer)
        
        # Блок для выбора письма на анализ.
        self.letterContainer = QtWidgets.QHBoxLayout()
        self.letterContainer.setObjectName("letterContainer")
        # Отступ слева от выбора номера письма.
        letterLeftSpacer = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.letterContainer.addItem(letterLeftSpacer)
        # Надпись "Выберите номер письма".
        self.letterLabel = QtWidgets.QLabel(self.centralwidget)
        self.letterLabel.setText("Выберите номер письма")
        self.letterLabel.setObjectName("letterLabel")
        self.letterContainer.addWidget(self.letterLabel)
        # Поле выбора номера письма.
        self.letterEdit = QtWidgets.QSpinBox(self.centralwidget)
        self.letterEdit.setMinimum(1)
        self.letterEdit.setObjectName("letterEdit")
        self.letterContainer.addWidget(self.letterEdit)
        # Кнопка выбора номера письма.
        self.letterButton = QtWidgets.QPushButton(self.centralwidget)
        self.letterButton.setText("Выбрать")
        self.letterButton.setObjectName("letterButton")
        self.letterButton.clicked.connect(self.onLetterSubmit)
        self.letterContainer.addWidget(self.letterButton)
        # Отступ справа от выбора номера письма.
        letterRightSpacer = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.letterContainer.addItem(letterRightSpacer)
        self.mainLayout.addLayout(self.letterContainer)
        
        # Блок кнопки открытия письма.
        self.submitLayout = QtWidgets.QHBoxLayout()
        self.submitLayout.setObjectName("submitLayout")
        # Отступ слева от кнопки.
        submitLeftSpacer = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.submitLayout.addItem(submitLeftSpacer)
        # Кнопка открытия письма.
        self.submitButton = QtWidgets.QPushButton(self.centralwidget)
        self.submitButton.setText("Открыть письмо в Блокноте")
        self.submitButton.setObjectName("submitButton")
        self.submitButton.clicked.connect(self.onSubmit)
        self.submitLayout.addWidget(self.submitButton)
        # Отступ справа от кнопки.
        submitRightSpacer = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.submitLayout.addItem(submitRightSpacer)
        self.mainLayout.addLayout(self.submitLayout)
        
        MainWindow.setCentralWidget(self.centralwidget)
        
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
        
    def onDateSubmit(self):
        global msgDataList
        # Процедура, заполняющая mailTable списком писем по заданной дате.
        self.mailTable.setRowCount(0)
        # Получение даты из поля dateEdit и приведение ее формата.
        inputDateQT = str(self.dateEdit.date().toPyDate())
        inputDate = datetime.datetime.strptime(inputDateQT, "%Y-%m-%d")
        inputDateStr = inputDate.date().strftime("%d-%m-%Y")
        # Получение входящих писем по заданной дате.
        msgList = None
        try:
            msgList = getIncomingMessages(inputDateStr)
        except:
            error = QtWidgets.QMessageBox()
            error.setWindowTitle("Ошибка")
            error.setText("Ошибка подключения к MS Outlook.")
            error.setInformativeText("Пожалуйста, проверьте, что MS Outlook открыт и вход в учетную запись выполнен.")
            error.setIcon(QtWidgets.QMessageBox.Warning)
            error.setStandardButtons(QtWidgets.QMessageBox.Ok)
            error.exec_()
        if ( msgList is not None ):
            # Если msgList пуст, письма не найдены. Обработка исключения.
            if ( len(msgList) > 0 ):
                msgDataList = []
                getMessagesData(msgList)
                # Вывод всех писем на интерфейс.
                for msgData in msgDataList:
                    line = f"[{msgData[1]} - {msgData[2]}] {msgData[3]}"
                    rowCnt = self.mailTable.rowCount()
                    self.mailTable.insertRow(rowCnt)
                    self.mailTable.setItem(rowCnt, 0, QtWidgets.QTableWidgetItem(line))
                # После получения писем возможен выбор одного из них. Установим максимальное возможное значение для letterEdit.
                self.letterEdit.setMaximum(len(msgList))
            else:
                error = QtWidgets.QMessageBox()
                error.setWindowTitle("Ошибка")
                error.setText("Письма за указанную дату не найдены.")
                error.setInformativeText("Пожалуйста, выберите другую дату.")
                error.setIcon(QtWidgets.QMessageBox.Warning)
                error.setStandardButtons(QtWidgets.QMessageBox.Ok)
                error.exec_()
            
    def onLetterSubmit(self):
        global msgDataList
        # Процедура берет письмо по номеру и ищет в нем сущности.
        self.resultTable.setRowCount(0)
        # Получение значения letterEdit (номера письма).
        letterNum = int(self.letterEdit.value()) - 1
        # По умолчанию letterEdit хранит 1. Если перед кликом письма не получались - вывод ошибки.
        if ( self.mailTable.rowCount() > 0 ):
            text = msgDataList[letterNum][3]
            nlp = spacy.load("./data/model-best")
            doc = nlp(text)
            for ent in doc.ents:
                line = f"{ent.text} [{ent.label_}] ({ent.start_char}:{ent.end_char})"
                if ( len(ent.text) <= 30 ):
                    rowCnt = self.resultTable.rowCount()
                    self.resultTable.insertRow(rowCnt)
                    self.resultTable.setItem(rowCnt, 0, QtWidgets.QTableWidgetItem(line))
        else:
            error = QtWidgets.QMessageBox()
            error.setWindowTitle("Ошибка")
            error.setText("Письмо не найдено.")
            error.setInformativeText("Пожалуйста, сначала получите письма по дате.")
            error.setIcon(QtWidgets.QMessageBox.Warning)
            error.setStandardButtons(QtWidgets.QMessageBox.Ok)
            error.exec_()
            
    def onSubmit(self):
        global msgDataList
        # Процедура открывает выбранное письмо в блокноте.
        # Если письмо не выбрано, то ничего открыть невозможно - ошибка.
        if ( self.mailTable.rowCount() > 0 ):
            text = msgDataList[int(self.letterEdit.value()) - 1][3]
            # Запись текста во временный файл.
            with tempfile.NamedTemporaryFile(delete=False) as tf:
                tf.write(text.encode())
                temp_file_name = tf.name
            # Открытие блокнота с временным файлом.
            subprocess.Popen(f'notepad {temp_file_name}')
        else:
            error = QtWidgets.QMessageBox()
            error.setWindowTitle("Ошибка")
            error.setText("Невозможно открыть текст письма.")
            error.setInformativeText("Пожалуйста, сначала выберите письмо.")
            error.setIcon(QtWidgets.QMessageBox.Warning)
            error.setStandardButtons(QtWidgets.QMessageBox.Ok)
            error.exec_()
        
def getIncomingMessages(date):
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

def getMessagesData(msgList):
    global msgDataList
    for msg in msgList:
        conversation = msg.ConversationID
        sender = msg.SenderName
        subject = msg.Subject
        body = msg.Body.replace('\n', '')
        msgDataList.append([conversation, sender, subject, body])

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle('Fusion')
    MainWindow = QtWidgets.QMainWindow()
    ui = AppWindow()
    ui.setupUI(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
