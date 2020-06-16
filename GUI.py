import sys
import typing
from PySide2.QtUiTools import *
from PySide2.QtWidgets import *
from PySide2.QtCore import *

import DBManager

# todo change user


class TableModel(QAbstractTableModel):
    def __init__(self, parent, data):
        QAbstractTableModel.__init__(self, parent)
        self.my_list = data
        self.header = ['Meal time', 'Food name', 'Grammage', 'Calories']

    def rowCount(self, parent: QModelIndex = ...):
        return len(self.my_list)

    def columnCount(self, parent: QModelIndex = ...):
        if self.my_list:
            return len(self.my_list[0])
        else:
            return 0

    def data(self, index: QModelIndex, role: int = ...):
        if not index.isValid():
            return None
        elif role != Qt.DisplayRole:
            return None
        return self.my_list[index.row()][index.column()]

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = ...):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self.header[section]
        return None

    def setData(self, index: QModelIndex, value: typing.Any, role: int = ...):
        self.beginResetModel()
        self.my_list = value
        start = self.index(0, 0)
        end = self.index(len(self.my_list) - 1, len(self.my_list[0]) - 1)
        self.endResetModel()
        self.dataChanged.emit(start, end)

    def clear(self):
        self.beginResetModel()
        self.my_list.clear()
        self.endResetModel()

    def flags(self, index: QModelIndex):
        return QAbstractTableModel.flags(self, index) | Qt.ItemIsEditable


def complete_dialog(dialog, data):
    date_time = QDateTime.fromString(data[0], 'dd-MMM-yyyy hh:mm:ss')
    dialog.dteMealTime.setDateTime(date_time)
    dialog.leFoodName.setText(data[1])
    dialog.leGrammage.setText(str(data[2]))
    dialog.leCalories.setText(str(data[3]))


class GUI(QStackedWidget):
    def __init__(self):
        QStackedWidget.__init__(self)
        self.setWindowTitle("Calorie calculator")
        # user relaed info
        self.food_info = None
        self.account_id = None
        self.old_data = None #data pt update

        # pagini
        self.pageAuthentication = None
        self.pageNewUser = None
        self.pageUserHistory = None
        self.dialogEditEntry = None
        self.dialogNewFood = None

        # incarcare pagini
        loader = QUiLoader()

        ui_file = QFile("authentication.ui")
        ui_file.open(QFile.ReadOnly)
        self.pageAuthentication = loader.load(ui_file)
        ui_file.close()

        ui_file = QFile("newUser.ui")
        ui_file.open(QFile.ReadOnly)
        self.pageNewUser = loader.load(ui_file)
        ui_file.close()

        ui_file = QFile("userHistory.ui")
        ui_file.open(QFile.ReadOnly)
        self.pageUserHistory = loader.load(ui_file)
        ui_file.close()
        self.pageUserHistory.dteMealTime.setDate(QDate.currentDate())
        self.pageUserHistory.dteMealTime.setMaximumDate(QDate.currentDate())

        self.pageUserHistory.calendar.setSelectedDate(QDate.currentDate())
        self.pageUserHistory.calendar.setMaximumDate(QDate.currentDate())

        ui_file = QFile("editEntry.ui")
        ui_file.open(QFile.ReadOnly)
        self.dialogEditEntry = loader.load(ui_file)
        ui_file.close()
        self.dialogEditEntry.setVisible(False)
        self.dialogEditEntry.dteMealTime.setMaximumDate(QDate.currentDate())

        ui_file = QFile("newFood.ui")
        ui_file.open(QFile.ReadOnly)
        self.dialogNewFood = loader.load(ui_file)
        ui_file.close()
        self.dialogNewFood.setVisible(False)

        # creare model pt tableView
        self.model = TableModel(self, [])
        self.pageUserHistory.tvHistory.setSelectionBehavior(QTableView.SelectRows)
        self.pageUserHistory.tvHistory.setModel(self.model)
        self.pageUserHistory.tvHistory.resizeColumnsToContents()
        self.pageUserHistory.tvHistory.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        # setare qcompleter
        db = DBManager.DBManager.get_instance()
        foods_list = db.get_foods()
        completer = QCompleter(foods_list, parent=None)
        completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.pageUserHistory.leFoodName.setCompleter(completer)
        self.dialogEditEntry.leFoodName.setCompleter(completer)

        # conectare signal->slot
        self.pageAuthentication.buttonNewUser.clicked.connect(self.on_buttonNewUser_clicked)
        self.pageAuthentication.buttonLogin.clicked.connect(self.on_buttonLogin_clicked)

        self.pageNewUser.buttonCreateUser.clicked.connect(self.on_buttonCreateUser_clicked)

        self.pageUserHistory.leFoodName.editingFinished.connect(self.check_food_name)
        self.pageUserHistory.leGrammage.textChanged.connect(self.check_grammage)
        self.pageUserHistory.buttonAddEntry.clicked.connect(self.on_buttonAddEntry_clicked)
        self.pageUserHistory.buttonDelete.clicked.connect(self.on_buttonDeleteEntry_clicked)
        self.pageUserHistory.buttonEdit.clicked.connect(self.on_buttonEditEntry_clicked)
        self.pageUserHistory.buttonNewFood.clicked.connect(self.on_buttonNewFood_clicked)
        self.pageUserHistory.calendar.selectionChanged.connect(self.on_calendar_selectionChanged)

        self.dialogEditEntry.leFoodName.editingFinished.connect(self.check_food_name)
        self.dialogEditEntry.leGrammage.textChanged.connect(self.check_grammage)
        self.dialogEditEntry.accepted.connect(self.update_entry)

        self.dialogNewFood.accepted.connect(self.new_food)
        self.dialogNewFood.leCalories.editingFinished.connect(self.check_calories)
        self.dialogNewFood.lePortionSize.editingFinished.connect(self.check_portion_size)

        # adaugare pagini la window
        self.addWidget(self.pageNewUser)
        self.addWidget(self.pageAuthentication)
        self.addWidget(self.pageUserHistory)

        self.setCurrentWidget(self.pageAuthentication)

    @Slot()
    def on_buttonNewUser_clicked(self):
        self.setCurrentWidget(self.pageNewUser)

    @Slot()
    def on_buttonLogin_clicked(self):
        username = self.pageAuthentication.leUsername.text()
        password = self.pageAuthentication.lePass.text()

        result = None
        if username and password:
            db = DBManager.DBManager.get_instance()
            result = db.log_in(username, password)

        if result is None:
            self.pageAuthentication.labelMessage.setText("Authentication failed!\nInvalid username or password")
        else:
            # setare acc curent
            self.account_id = result

            # aflare date user si cmpletare caseta leRDCI
            user_info = db.get_user_info(self.account_id)
            if user_info[0] == 'M':
                RDCI = 10 * user_info[2] + 6.25 * user_info[3] - 5 * user_info[1] + 5
            else:
                RDCI = 10 * user_info[2] + 6.25 * user_info[3] - 5 * user_info[1] - 161

            self.pageUserHistory.leRDCI.setText(str(RDCI))
             # setare data maxima la addEntry
            self.pageUserHistory.dteMealTime.setMinimumDate(QDate.fromString(user_info[4], 'dd-MM-yyyy'))
            self.dialogEditEntry.dteMealTime.setMinimumDate(QDate.fromString(user_info[4], 'dd-MM-yyyy'))
            self.pageUserHistory.calendar.setMinimumDate(QDate.fromString(user_info[4], 'dd-MM-yyyy'))

            # setare date View si caseta ADCI
            date = self.pageUserHistory.calendar.selectedDate()
            date = date.toString('dd-MM-yyyy')

            entries = db.get_entries(self.account_id, date)
            ADCI = 0

            if entries:
                for entry in entries:
                    ADCI += entry[3]
                self.model.setData(self.model.index(0, 0), entries)

            self.pageUserHistory.leADCI.setText(str(ADCI))
            self.setCurrentWidget(self.pageUserHistory)

    @Slot()
    def on_buttonCreateUser_clicked(self):
        check = 1
        db = DBManager.DBManager.get_instance()

        username = self.pageNewUser.leUsername.text()
        if not username:
            check = 0
            self.pageNewUser.labelErrUsername.setText('Empty username')
        else:
            result = db.check_username(username)
            if result:
                check = 0
                self.pageNewUser.labelErrUsername.setText('Username already exists')
            else:
                if len(username) > 30:
                    self.pageNewUser.labelErrName.setText('Username too long')
                else:
                    self.pageNewUser.labelErrUsername.setText('')

        password = self.pageNewUser.lePass.text()
        if not password:
            check = 0
            self.pageNewUser.labelErrPass.setText('Empty password')
        else:
            if len(password) < 5:
                check = 0
                self.pageNewUser.labelErrPass.setText('Password too short')
            else:
                if len(password) > 40:
                    check = 0
                    self.pageNewUser.labelErrPass.setText('Password too long')
                else:
                    self.pageNewUser.labelErrPass.setText('')

        name = self.pageNewUser.leName.text()
        if not name:
            check = 0
            self.pageNewUser.labelErrName.setText('Empty name')
        else:
            if len(name) > 50:
                check = 0
                self.pageNewUser.labelErrName.setText('Name too long')
            else:
                self.pageNewUser.labelErrName.setText('')

        sex = self.pageNewUser.boxSex.currentText()

        age = self.pageNewUser.leAge.text()
        if age.isdigit():
            age = int(self.pageNewUser.leAge.text())
            if age > 110:
                check = 0
                self.pageNewUser.labelErrAge.setText('Invalid age (>110)')
            else:
                if age < 10:
                    check = 0
                    self.pageNewUser.labelErrAge.setText('Invalid age (<10)')
                else:
                    self.pageNewUser.labelErrAge.setText('')
        else:
            check = 0
            self.pageNewUser.labelErrAge.setText('Invalid age')

        weight = self.pageNewUser.leWeight.text()
        if weight.isdigit():
            weight = int(self.pageNewUser.leWeight.text())
            if weight > 200:
                check = 0
                self.pageNewUser.labelErrWeight.setText('Invalid weight(>200)')
            else:
                if weight < 40:
                    check = 0
                    self.pageNewUser.labelErrWeight.setText('Invalid weight(<40)')
                else:
                    self.pageNewUser.labelErrWeight.setText('')
        else:
            check = 0
            self.pageNewUser.labelErrWeight.setText('Invalid weight')

        height = self.pageNewUser.leHeight.text()
        if height.isdigit():
            height = int(self.pageNewUser.leHeight.text())
            if height > 220:
                check = 0
                self.pageNewUser.labelErrHeight.setText('Invalid height(>220)')
            else:
                if height < 120:
                    check = 0
                    self.pageNewUser.labelErrHeight.setText('Invalid height(<120)')
                else:
                    self.pageNewUser.labelErrHeight.setText('')
        else:
            check = 0
            self.pageNewUser.labelErrHeight.setText('Invalid height')

        if check == 1:
            params = [username, password, name, age, sex, weight, height]
            db = DBManager.DBManager.get_instance()
            db.create_user(params)
            self.setCurrentWidget(self.pageAuthentication)

    @Slot()
    def on_buttonAddEntry_clicked(self):
        food_name = self.pageUserHistory.leFoodName.text()
        grammage = self.pageUserHistory.leGrammage.text()
        meal_time = self.pageUserHistory.dteMealTime.dateTime()
        calories = self.pageUserHistory.leCalories.text()

        db = DBManager.DBManager.get_instance()
        foods_list = db.get_foods()
        if food_name and grammage:
            if food_name in foods_list and grammage.isdigit():
                already_exists = db.check_entry(self.account_id, self.food_info[0], meal_time.toString("yyyy-MM-dd hh:mm:ss"), int(grammage))
                if not already_exists:
                    db.add_entry(self.account_id, self.food_info[0], meal_time.toString("yyyy-MM-dd hh:mm:ss"), int(grammage), int(calories))

                    date = self.pageUserHistory.calendar.selectedDate()
                    date = date.toString('dd-MM-yyyy')

                    self.model.setData(self.model.index(0, 0), db.get_entries(self.account_id, date))
                    if meal_time.date() == self.pageUserHistory.calendar.selectedDate():
                        currentADCI = int(self.pageUserHistory.leADCI.text())
                        self.pageUserHistory.leADCI.setText(str(int(calories)+currentADCI))

    @Slot()
    def on_buttonDeleteEntry_clicked(self):
        selectionModel = self.pageUserHistory.tvHistory.selectionModel()
        indexes = selectionModel.selectedIndexes()

        if indexes:
            data = []
            for cell in indexes:
                data.append(cell.data())

            db = DBManager.DBManager.get_instance()
            db.delete_entry(self.account_id, data[0], data[1], data[2])

            currentADCI = int(self.pageUserHistory.leADCI.text())
            self.pageUserHistory.leADCI.setText(str(currentADCI - data[3]))

            date = self.pageUserHistory.calendar.selectedDate()
            date = date.toString('dd-MM-yyyy')
            entries = db.get_entries(self.account_id, date)
            if entries:
                self.model.setData(self.model.index(0, 0), entries)
            else:
                self.model.clear()

    @Slot()
    def on_buttonEditEntry_clicked(self):
        selectionModel = self.pageUserHistory.tvHistory.selectionModel()
        indexes = selectionModel.selectedIndexes()

        if indexes:
            self.old_data = []
            for cell in indexes:
                self.old_data.append(cell.data())

            complete_dialog(self.dialogEditEntry, self.old_data)
            self.dialogEditEntry.setVisible(True)

    @Slot()
    def on_calendar_selectionChanged(self):
        date = self.pageUserHistory.calendar.selectedDate()
        date = date.toString('dd-MM-yyyy')
        db = DBManager.DBManager.get_instance()
        newEntries = db.get_entries(self.account_id, date)
        ADCI = 0
        if newEntries:
            self.model.setData(self.model.index(0, 0), newEntries)
            for entry in newEntries:
                ADCI += entry[3]
        else:
            self.model.clear()

        self.pageUserHistory.leADCI.setText(str(ADCI))

    @Slot()
    def on_buttonNewFood_clicked(self):
        self.dialogNewFood.setVisible(True)


    @Slot()
    def new_food(self):
        food_name = self.dialogNewFood.leFoodName.text()
        portion_size = self.dialogNewFood.lePortionSize.text()
        calories = self.dialogNewFood.leCalories.text()
        if portion_size.isdigit() and calories.isdigit():
            db = DBManager.DBManager.get_instance()
            db.insert_new_food(food_name, calories, portion_size)
            foods_list = db.get_foods()
            completer = QCompleter(foods_list, parent=None)
            completer.setCaseSensitivity(Qt.CaseInsensitive)
            self.pageUserHistory.leFoodName.setCompleter(completer)
            self.dialogEditEntry.leFoodName.setCompleter(completer)


    @Slot()
    def update_entry(self):
        food_name = self.dialogEditEntry.leFoodName.text()
        grammage = self.dialogEditEntry.leGrammage.text()
        meal_time = self.dialogEditEntry.dteMealTime.dateTime()
        meal_time = meal_time.toString("yyyy-MM-dd hh:mm:ss")
        calories = self.dialogEditEntry.leCalories.text()

        db = DBManager.DBManager.get_instance()
        foods_list = db.get_foods()
        if food_name and grammage:
            if food_name in foods_list and grammage.isdigit():
                db.update_entry(self.account_id, self.old_data[0], self.old_data[1], self.old_data[2], meal_time, food_name, grammage, calories)

        self.old_data = None

        date = self.pageUserHistory.calendar.selectedDate()
        date = date.toString('dd-MM-yyyy')
        entries = db.get_entries(self.account_id, date)
        if entries:
            self.model.setData(self.model.index(0, 0), entries)
        else:
            self.model.clear()

        ADCI = 0
        for entry in entries:
            ADCI += entry[3]
        self.pageUserHistory.leADCI.setText(str(ADCI))

    @Slot()
    def check_food_name(self):
        sender = self.sender()
        food_name = sender.text()
        db = DBManager.DBManager.get_instance()
        foods_list = db.get_foods()
        if food_name not in foods_list:
            sender.setText('Please select one of the available options')
        else:
            self.food_info = db.get_food_info(food_name)
            sender.parentWidget().leGrammage.setToolTip("Portion size ~= %d grams" % self.food_info[3])
            grammage = sender.parentWidget().leGrammage.text()
            if grammage and grammage.isdigit():
                sender.parentWidget().leCalories.setText("%d" % (int(grammage) / 100 * self.food_info[2]))

    @Slot()
    def check_grammage(self):
        sender = self.sender()
        grammage = sender.text()
        if grammage.isdigit():
            grammage = int(grammage)

            food_name = sender.parentWidget().leFoodName.text()
            if food_name:
                db = DBManager.DBManager.get_instance()
                self.food_info = db.get_food_info(food_name)

            if self.food_info:
                sender.parentWidget().leCalories.setText("%d" % (grammage / 100 * self.food_info[2]))
        else:
            sender.parentWidget().leCalories.setText("Invalid grammage")

    @Slot()
    def check_calories(self):
        calories = self.dialogNewFood.leCalories.text()
        if not calories.isdigit():
            self.dialogNewFood.leCalories.setText("Invalid")

    @Slot()
    def check_portion_size(self):
        portion_size = self.dialogNewFood.lePortionSize.text()
        if not portion_size.isdigit():
            self.dialogNewFood.lePortionSize.setText("Invalid")

if __name__ == "__main__":
    app = QApplication(sys.argv)

    stackedWidget = GUI()
    stackedWidget.show()

    sys.exit(app.exec_())
