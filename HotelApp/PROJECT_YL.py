import sqlite3
import sys

from PyQt5.QtCore import QTimer, Qt
from PyQt5 import QtGui

import datetime

from PyQt5.QtGui import QPixmap, QIcon
from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QMessageBox, QInputDialog, QLabel, QLineEdit, QTableWidgetItem, QFileDialog
from PyQt5.QtWidgets import QMainWindow


class MainWindowHotel(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('designes for project/MainWindowHOTEL.ui', self)
        self.setWindowTitle('Hotel APP')
        self.setWindowIcon(QIcon('images for project/icon_MainWindow.ico'))
        self.setFixedSize(1130, 810)
        spis = list(cur.execute('SELECT FloorNumber, RoomNumber FROM Rooms'))
        dicti = {1: [], 2: [], 3: [], 4: []}
        for i in spis:
            dicti[i[0]].append(i[1])
        self.sp_widgets = [self.listWidget, self.listWidget_2, self.listWidget_3, self.listWidget_4]
        for i in range(len(self.sp_widgets)):
            self.add_buttons(dicti[i + 1], i)
            self.sp_widgets[i].itemDoubleClicked.connect(self.room_hotel)
        self.OpenListGuests.clicked.connect(self.menu_guests)
        self.spis_room_images = ['images for project/RoomZa3000P.png', 'images for project/RoomZa5000P.png',
                                 'images for project/RoomZa7000P.png', 'images for project/RoomZa10000P.png']
        self.sp_admin_btns = [self.AddRoom, self.AddRoom_2, self.AddRoom_3, self.AddRoom_4,
                              self.ExitAdmin]
        for i in self.sp_admin_btns[:-1]:
            i.clicked.connect(self.settings_floors)
        for i in self.sp_admin_btns:
            i.setEnabled(False)
        self.OpenAdmin.clicked.connect(self.open_admin)
        self.ExitAdmin.clicked.connect(self.admin_buttons_hide)
        self.ResetRooms.clicked.connect(self.reseting)
        self.DoReport.clicked.connect(self.spravka)
        self.FoundFastRoom.clicked.connect(self.fast_room)

    def reseting(self):
        for i in self.sp_widgets:
            for j in range(i.count()):
                i.item(j).setText('   ' + str(i.item(j).text().strip()[:4]) + 'номер\n\n\n')
        mesgbox = QMessageBox()
        mesgbox.setText('Бронь со всех номеров сброшена!')
        mesgbox.setWindowTitle('Успешно!')
        mesgbox.exec()

    def settings_floors(self):
        num = int(self.sender().text()[-1]) - 1
        ex2 = Settings_Floor(self, num)
        ex2.show()

    def spravka(self):
        with open('spravka_hotel.txt', 'w', encoding='utf-8') as write_file:
            dates = cur.execute("""SELECT FloorNumber, Price, HumansInRoom FROM Rooms""").fetchall()
            dicti = {1: 0, 2: 0, 3: 0, 4: 0}
            for i in dates:
                if i[-1]:
                    min_date = []
                    for j in i[-1].split('&')[:-1]:
                        min_date.append(cur.execute(f"""SELECT CheckInDate FROM Humans
                         WHERE PassportID = {int(j)}""").fetchall()[0][0])
                    days = (datetime.date.today() - datetime.date(*list(map(int, min(min_date).split('-'))))).days + 1
                    dicti[i[0]] += i[1] * len(i[-1].split('&')[:-1]) * days
            for i, j in dicti.items():
                write_file.write(f'{i} Этаж: {j} рублей\n')
        mesgbox = QMessageBox()
        mesgbox.setText('Сохранено в файле "spravka_hotel.txt"')
        mesgbox.setWindowTitle('Успешно!')
        mesgbox.exec()

    def fast_room(self):
        dates = cur.execute("""SELECT RoomNumber FROM Rooms WHERE Busy = 0""").fetchall()[0][0]
        df = self.sp_widgets[int(str(dates)[0]) - 1].item(int(str(dates)[1:]) - 1)
        self.sp_widgets[int(str(dates)[0]) - 1].setCurrentItem(df)
        self.room_hotel(df)

    def room_hotel(self, item):
        ex1 = RoomHotel(self, item.text(), self.sp_widgets, self.spis_room_images)
        ex1.show()

    def menu_guests(self):
        ex1 = MenuGuests(self)
        ex1.show()

    def add_buttons(self, spis, wdg):
        spis_bsy = list(map(lambda x: x[0], cur.execute("SELECT Busy FROM Rooms WHERE FloorNumber = ?",
                                                        (wdg + 1, )).fetchall()))
        for i in range(len(spis)):
            if spis_bsy[i]:
                self.sp_widgets[wdg].addItem('   ' + str(spis[i]) + ' номер/ /Занят\n\n\n')
            else:
                self.sp_widgets[wdg].addItem('   ' + str(spis[i]) + ' номер\n\n\n')

    def open_admin(self):
        password, ok = QInputDialog.getText(self, 'Вход', 'Введите пароль:', QLineEdit.Password)
        if ok and password == 'U8qSG0':
            self.admin_buttons_show()
        elif not ok:
            mesgbox = QMessageBox()
            mesgbox.setText('Вход отменен!')
            mesgbox.setWindowTitle('Вход не выполнен!')
            mesgbox.exec()
        else:
            mesgbox = QMessageBox()
            mesgbox.setText('Пароль неверный!')
            mesgbox.setWindowTitle('Вход не выполнен!')
            mesgbox.exec()

    def admin_buttons_show(self):
        for i in self.sp_admin_btns:
            i.setEnabled(True)
        mesgbox = QMessageBox()
        mesgbox.setText('Вы вошли в режим администратора')
        mesgbox.setWindowTitle('Вход выполнен!')
        mesgbox.exec()

    def admin_buttons_hide(self):
        for i in self.sp_admin_btns:
            i.setEnabled(False)
        mesgbox = QMessageBox()
        mesgbox.setText('Вы вышли из режима администратора')
        mesgbox.setWindowTitle('Выход выполнен!')
        mesgbox.exec()


class MenuGuests(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        uic.loadUi('designes for project/GuestsMenu.ui', self)
        self.setWindowTitle(f'Список гостей')
        self.setFixedSize(1000, 800)
        self.updateButton.clicked.connect(self.update_result)
        self.tableWidget.itemChanged.connect(self.item_changed)
        self.saveButton.clicked.connect(self.save_results)
        self.modified = {}
        self.adding()

    def adding(self):
        try:
            self.result = cur.execute("SELECT * FROM Humans").fetchall()
            if self.result:
                self.tableWidget.setRowCount(len(self.result))
                self.tableWidget.setColumnCount(len(self.result[0]))
                cur.execute('PRAGMA table_info("TEST")')
                self.titles = [i[1] for i in cur.fetchall()]
                self.tableWidget.setColumnCount(len(self.titles))
                self.tableWidget.setHorizontalHeaderLabels(self.titles)
                # Заполнили таблицу полученными элементами
                for i, elem in enumerate(self.result):
                    for j, val in enumerate(elem):
                        self.tableWidget.setItem(i, j, QTableWidgetItem(str(val)))
            else: raise IndexError
        except IndexError:
            self.statusBar().showMessage('Нет гостей :(')

    def update_result(self):
        if self.lineEdit.text():
            result = cur.execute("SELECT * FROM Humans WHERE PassportID=?",
                                 (item_id := self.lineEdit.text(),)).fetchall()
        else:
            result = cur.execute("SELECT * FROM Humans").fetchall()
            item_id = '...'
        # Заполнили размеры таблицы
        self.tableWidget.setRowCount(len(result))
        # Если запись не нашлась, то не будем ничего делать
        if not result:
            self.statusBar().showMessage('Ничего не нашлось')
            return
        else:
            self.statusBar().showMessage(f"Нашлась запись с номером паспорта: {item_id}")
        self.tableWidget.setColumnCount(len(result[0]))
        self.titles = [description[0] for description in cur.description]
        # Заполнили таблицу полученными элементами
        for i, elem in enumerate(result):
            for j, val in enumerate(elem):
                self.tableWidget.setItem(i, j, QTableWidgetItem(str(val)))
        self.modified = {}

    def item_changed(self, item):
        self.modified[self.titles[item.column()]] = item.text()

    def save_results(self):
        if self.modified:
            que = "UPDATE Humans SET\n"
            que += ", ".join([f"{key}='{self.modified.get(key)}'"
                              for key in self.modified.keys()])
            que += "WHERE PassportID = ?"
            print(que)
            cur.execute(que, (self.lineEdit.text(),))
            con.commit()
            self.modified.clear()


class RoomHotel(QMainWindow):
    def __init__(self, parent=None, name='', wdget=None, spis_images=None):
        super().__init__(parent)
        self.parent1 = parent
        self.name = name
        self.wdgets = wdget
        self.setFixedSize(390, 500)
        # spis = ['images for project/RoomZa3000P.png', 'images for project/RoomZa5000P.png',
        #         'images for project/RoomZa7000P.png', 'images for project/RoomZa10000P.png']
        self.pixmap = QPixmap(spis_images[int(name.strip()[0]) - 1]).scaled(340, 250)
        self.image = QLabel(self)
        self.image.move(30, 20)
        self.image.resize(340, 250)
        self.image.setPixmap(self.pixmap)
        uic.loadUi('designes for project/RoomHOTEL.ui', self)
        self.setWindowTitle(self.name)
        self.addInhabitantButton.clicked.connect(self.addInHabbitant)
        self.CalculationButton.clicked.connect(self.doOplata)
        self.Busy_button.clicked.connect(self.busy_func)

    def busy_func(self):
        curr = self.wdgets[int(self.name.strip()[0]) - 1].currentItem()
        if curr.text().strip()[-1] == 'р':
            curr.setText('   ' + curr.text().strip() + '/ /Занят\n\n\n')
            cur.execute('UPDATE Rooms SET Busy = ? WHERE RoomNumber = ?', (1, int(self.name.strip()[:4])))
            con.commit()
        else:
            curr.setText('   ' + curr.text().strip()[:9] + '\n\n\n')
            cur.execute('UPDATE Rooms SET Busy = ? WHERE RoomNumber = ?', (0, int(self.name.strip()[:4])))
            con.commit()

    def addInHabbitant(self):
        dialog = AnketaForRoom(self, self.name)
        dialog.show()

    def doOplata(self):
        dialog = OplataRoom(self, self.name)
        dialog.show()


class Settings_Floor(QMainWindow):
    def __init__(self, parent=None, num=None):
        super().__init__(parent)
        self.num = num
        self.setFixedSize(270, 475)
        uic.loadUi('designes for project/SettingsFloor.ui', self)
        self.setWindowTitle(f'Настройки этажа {str(self.num)[0]}')
        self.EditImageRooms.clicked.connect(self.edit_photo)
        self.AddRoom.clicked.connect(self.add_room)
        self.DeletingRoom.clicked.connect(self.delete_room)

    def edit_photo(self):
        fname, ok_prs = QFileDialog.getOpenFileName(
            self, 'Выбрать картинку', '',
            'Картинка (*.jpg);;Картинка (*.png)')
        if ok_prs:
            self.parent().spis_room_images[self.num] = fname
            mesgbox = QMessageBox()
            mesgbox.setText('Изменение фото этажа')
            mesgbox.setWindowTitle('Изменено успешно!')
            mesgbox.exec()
        else:
            mesgbox = QMessageBox()
            mesgbox.setText('Отменено!')
            mesgbox.setWindowTitle('Не изменено!')
            mesgbox.exec()

    def delete_room(self):
        inp, ok = QInputDialog.getText(self, 'Ввод...', 'Введите номер комнаты:', QLineEdit.Normal)
        if inp:
            listItems = self.parent().sp_widgets[self.num]
            for item in range(listItems.count()):
                if listItems.item(item).text().strip()[:4].strip() == inp.strip():
                    listItems.takeItem(int(inp.strip()[1:]) - 1)
                    cur.execute("""DELETE FROM Rooms WHERE RoomNumber = ?""", (int(inp),))
                    con.commit()
                    return
        return

    def add_room(self):
        inp, ok = QInputDialog.getText(self, 'Ввод...', 'Введите номер комнаты:', QLineEdit.Normal)
        if inp:
            self.parent().sp_widgets[self.num].addItem('   ' + str(inp.strip()) + ' номер\n\n\n')
            price = cur.execute("""SELECT Price FROM Rooms WHERE FloorNumber = ?""", (self.num + 1,)).fetchall()[0][0]
            cur.execute("""INSERT INTO Rooms VALUES (NULL, ?, ?, ?, ?, 0)""", (self.num + 1, inp, price, ''))
            con.commit()
        return


class AnketaForRoom(QMainWindow):
    def __init__(self, parent=None, name=''):
        super().__init__(parent)
        self.name = name
        uic.loadUi('designes for project/AnketaForPersonInRoom.ui', self)
        self.setWindowTitle(f'Анкета заселения для комнаты {self.name.strip()[:4]}')
        self.addInhabitant.clicked.connect(self.addInhsbbitantRoom)
        self.setFixedSize(420, 430)

    def addInhsbbitantRoom(self):
        lst = [self.NamePerson.text(), self.SurnamePerson.text(),
               self.PatronymicPerson.text(), self.PassportID.text()]
        if all(lst[:-1]):
            if not len(lst[-1]) == 10:
                try:
                    int(lst[-1])
                except ValueError:
                    self.statusBar().showMessage('Неверны серия и номер паспорта')
                    return
                self.statusBar().showMessage('Неверны серия и номер паспорта')
                return
            dlina = cur.execute(f"SELECT HumansInRoom FROM Rooms WHERE RoomNumber = ?",
                                (self.name.strip()[:4],)).fetchall()
            if len(dlina[0][0]) >= 21:
                self.statusBar().showMessage('Номер занят')
                return
            cur.execute("INSERT OR IGNORE INTO Humans VALUES (NULL, ?, ?, ?, ?, ?, ?, NULL)",
                        (self.name.strip()[:4], *lst, str(datetime.date.today())))
            cur.execute('UPDATE Rooms SET HumansInRoom = ? WHERE RoomNumber = ?', (dlina[0][0] + lst[-1] + '&',
                                                                                   self.name.strip()[:4]))
            con.commit()
            self.close()
        else:
            self.statusBar().showMessage('Ошибка :/')


class OplataRoom(QMainWindow):
    def __init__(self, parent=None, name=''):
        super().__init__(parent)
        self.name = name
        uic.loadUi('designes for project/OplataHOTEL.ui', self)
        self.setWindowTitle(f'Рассчет суммы для оплаты комнаты {self.name}')
        self.PrOplataButton.clicked.connect(self.summa)
        self.OplataButton.clicked.connect(self.oplata)
        self.spis_checkBox = [self.Minibar, self.Fitnes, self.SpaSalon]
        for i in self.spis_checkBox:
            i.stateChanged.connect(self.edit)
        self.f_proverka_summa = False
        self.setFixedSize(350, 440)

    def edit(self):
        if self.sender().isChecked():
            self.SummaLabel.setText(str(int(self.SummaLabel.text()) + 3000))
        else:
            self.SummaLabel.setText(str(int(self.SummaLabel.text()) - 3000))

    def oplata(self):
        if self.f_proverka_summa:
            oplata = OplataEndingRoom(self, self.sp_dates_humans)
            oplata.show()

    def summa(self):
        humans_passpIDs = cur.execute(f"SELECT HumansInRoom FROM Rooms WHERE RoomNumber"
                                      f" = '{int(self.name.strip()[:4])}'").fetchall()[0][0]
        self.sp_dates_humans = [i for i in humans_passpIDs.split('&') if i != '']
        if self.sp_dates_humans:
            sp_dates = []
            for i in self.sp_dates_humans:
                date_zaselenia = cur.execute(f"SELECT CheckInDate FROM Humans"
                                             f" WHERE PassportID = {str(i)}").fetchall()[0][0]
                sp_dates.append(date_zaselenia)
            self.min_date = min(sp_dates)
            days = (datetime.date.today() - datetime.date(*list(map(int, self.min_date.split('-'))))).days + 1
            cena = cur.execute(f"SELECT Price FROM Rooms WHERE RoomNumber ="
                               f" '{int(self.name.strip()[:4])}'").fetchall()[0][0]
            if not self.f_proverka_summa:
                self.SummaLabel.setText(str(int(self.SummaLabel.text()) + (cena * len(sp_dates) * days)))
            self.f_proverka_summa = True
        else:
            self.statusBar().showMessage('Номер пуст')


class OplataEndingRoom(QMainWindow):
    def __init__(self, parent=None, sp=None):
        super().__init__(parent)
        uic.loadUi('designes for project/OplataEndingHOTEL.ui', self)
        self.setWindowTitle(f'Оплата терминалом...')
        self.setFixedSize(330, 440)
        self.label3.setAlignment(Qt.AlignCenter)
        self.label = QLabel(self)
        self.label.setGeometry(80, 20, 200, 200)
        self.OtmenaButton.clicked.connect(self.otmena)
        self.f = True
        self.sp = sp
        path = 'images for project/loa.gif'
        self.gif = QtGui.QMovie(path)
        self.label.setMovie(self.gif)
        self.gif.start()
        self.timer(5000)

    def otmena(self):
        self.f = False
        self.label3.setText('Отменено...')
        self.gif.stop()
        timer = QTimer(self)
        timer.singleShot(1000, self.close)

    def timer(self, time):
        if self.f:
            timer = QTimer(self)
            timer.singleShot(time, self.on_timeout)

    def on_timeout(self):
        if self.f:
            self.label3.setText('Успешно!')
            self.gif.stop()
            for i in self.sp:
                cur.execute(f"""DELETE FROM Humans WHERE PassportID = {int(i)}""")
                cur.execute(f"""UPDATE Rooms SET HumansInRoom = '', Busy = 0
                 WHERE RoomNumber = {self.parent().name.strip()[:4]}""")
                con.commit()
            timer = QTimer(self)
            timer.singleShot(1500, self.close)


if __name__ == '__main__':
    con = sqlite3.connect('databases/database_for_hotel.sqlite')
    cur = con.cursor()
    app = QApplication(sys.argv)
    ex = MainWindowHotel()
    ex.show()
    sys.exit(app.exec())
