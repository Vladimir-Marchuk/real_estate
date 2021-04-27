from PyQt5 import QtWidgets, uic, QtCore

class Ui(QtWidgets.QDialog):
    rezet_pz_signal = QtCore.pyqtSignal()
    get_start_data_signal = QtCore.pyqtSignal()


    def __init__(self):
        super(Ui, self).__init__()
        uic.loadUi('new_obj.ui', self)

        self.bt_add.clicked.connect(self.add_clicked)
        self.bt_cancel.clicked.connect(self.cancel_clicked)


    def get_values(self):
        return (
            self.cb_type.currentText(),
            self.sb_rooms.value(),
            self.sb_square.value(),
            self.ed_city.text(),
            self.sb_price.value()
        )

    def add_clicked(self):
        if (len(self.ed_city.text())>0) and (self.cb_type.currentIndex()>-1):
            self.accept()
        else:
            msg = QtWidgets.QMessageBox()
            msg.setIcon(QtWidgets.QMessageBox.Critical)
            msg.setText("Заполните все поля объекта!")
            msg.setWindowTitle("Ошибка")
            msg.exec_()

    def cancel_clicked(self):
        self.reject()

    def showEvent(self, event):
        self.cb_type.setCurrentIndex(-1)
        self.sb_rooms.setValue(1)
        self.sb_square.setValue(0)
        self.ed_city.setText('')
        self.sb_price.setValue(0)
