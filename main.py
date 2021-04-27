import sys,os
import sqlite3
from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import QMessageBox,qApp

from new_obj import Ui as fm_new_obj


class DBController:
    def __init__(self):
        self.conn=sqlite3.connect('data.db',detect_types=sqlite3.PARSE_DECLTYPES)

    def get_data(self,obj_type='',price=0):
        sf='where 1=1 '
        if len(obj_type)>0:
            sf+='and obj_type="%s" '%obj_type
        if price>0:
            sf+='and price<=%d'%price
        s='select rowid,obj_type,rooms,square,city,price from base '+sf
        cur=self.conn.cursor()
        res=cur.execute(s).fetchall()
        return res

    def insert_obj(self,obj):
        cur=self.conn.cursor()
        cur.execute('insert into base (obj_type,rooms,square,city,price) values (?,?,?,?,?)',
                    obj)
        self.conn.commit()

    def delete_obj(self,id):
        cur=self.conn.cursor()
        cur.execute('delete from base where rowid=?',(id,))
        self.conn.commit()

    def __del__(self):
        self.conn.close()

class Ui(QtWidgets.QMainWindow):
    def __init__(self):
        super(Ui, self).__init__()
        uic.loadUi('main.ui', self)
        self.ac_exit.triggered.connect(qApp.quit)
        self.ac_add.triggered.connect(self.new_handler)
        self.ac_del.triggered.connect(self.del_handler)
        self.db=DBController()

        self.load_data()
        self.new_obj=fm_new_obj()

        self.bt_filter.clicked.connect(self.filter_handle)
        self.bt_reset.clicked.connect(self.reset_handle)

        """self.file_button.clicked.connect(self.file_menu_handle)
        self.edit_button.clicked.connect(self.edit_menu_handle)
        self.settings_button.clicked.connect(self.open_com_settings)

        self.fmNewPrj=fmNewProject()
        self.fmNewPrj.rezet_pz_signal.connect(self.rezet_pz)
        self.fmNewPrj.get_start_data_signal.connect(self.get_start_data)

        """

        self.show()

    def load_data(self,obj_type='',price=0):
        res=self.db.get_data(obj_type,price)
        self.table.setRowCount(0)
        for r in res:
            id,obj_type,rooms,square,city,price=r
            self.table.setRowCount(self.table.rowCount() + 1)
            current_row = self.table.rowCount() - 1
            self.table.setItem(current_row, 0, QtWidgets.QTableWidgetItem(str(id)))
            self.table.setItem(current_row, 1, QtWidgets.QTableWidgetItem(obj_type))
            self.table.setItem(current_row, 2, QtWidgets.QTableWidgetItem(str(rooms)))
            self.table.setItem(current_row, 3, QtWidgets.QTableWidgetItem('{0:.1f}'.format(square)))
            self.table.setItem(current_row, 4, QtWidgets.QTableWidgetItem(city))
            self.table.setItem(current_row, 5, QtWidgets.QTableWidgetItem('{0} $'.format(price)))

    def new_handler(self):
        if self.new_obj.exec_():
            v=self.new_obj.get_values()
            self.db.insert_obj(v)
            self.load_data()

    def del_handler(self):
        row = self.table.currentIndex().row()
        if row<0:
            return
        msg=QMessageBox(text='Удалить объект?')
        msg.setIcon(QMessageBox.Warning)
        msg.setWindowTitle("Подтверждение")
        msg.setStandardButtons(QMessageBox.Yes|QMessageBox.No)
        ret=msg.exec_()
        if ret==msg.Yes:
            id=self.table.item(row,0).text()
            self.db.delete_obj(id)
            self.load_data()

    def filter_handle(self):
        obj_type=self.cb_type.currentText()
        price=self.sb_price.value()
        self.load_data(obj_type,price)


    def reset_handle(self):
        self.cb_type.setCurrentIndex(0)
        self.sb_price.setValue(0)
        self.load_data()

    """
    def closeEvent(self, event):
        self.save_config()
        self.save_as_prj_handle(False)
        event.accept()

    def select_item(self):
        index=self.table.currentIndex()
        c=index.column()
        r=index.row()
        if (r<0) or (c<0):
            return
        if self.table.item(r, COL_STATUS).checkState()== QtCore.Qt.Checked:
            #if c==COL_LP:
            L=float(self.table.item(r, COL_SIZE).text())
            LP=float(self.table.item(r, COL_LP).text())
            self.LP_plot.show_marker(L,LP)
            #elif c==COL_VN:
            #L=float(self.table.item(r, COL_SIZE).text())
            VN=float(self.table.item(r, COL_VN).text())
            self.VN_plot.show_marker(L,VN)
            self.plot3d.show_marker(L,LP,VN)
            PZ=float(self.table.item(r, COL_PZ).text())
            temp=float(self.table.item(r, COL_TEMP).text())

            self.compass_canvas.update_figure(PZ)
            self._update_compas_info(PZ,temp)

        #value = index.sibling(r, c).data()

    def click_item(self,item):
        c=item.column()
        r=item.row()
        if c==COL_STATUS:
            if r==0:
                self.table.item(r,c).setCheckState(QtCore.Qt.Checked)
            else:
                self.recalculate_table()

    def add_data_to_table(self, glub, azimuth, pitch, roll, temp,CV,MV,battery,i_sys,i_gyro,i_acc,i_mag):
        if not self.table.isEnabled():
            return
        #azimuth=azimuth+self.declinator
        self.bur_size += glub
        self.table.setRowCount(self.table.rowCount() + 1)
        current_row = self.table.rowCount() - 1
        date_time = datetime.now()
        fl_time = date_time.strftime('%d.%m.%Y %H:%M:%S')
        sh_time = date_time.strftime('%H:%M')
        mes_date= date_time.strftime('%d.%m.%Y')
        ti = QtWidgets.QTableWidgetItem(sh_time)
        ti.setToolTip(fl_time)
        # Номер замера
        self.table.setItem(current_row, COL_NZAMER, QtWidgets.QTableWidgetItem('{0}'.format(self.bur_id)))
        # Глубина
        self.table.setItem(current_row, COL_SIZE, QtWidgets.QTableWidgetItem('{0}'.format(self.bur_size)))
        # Длина замера
        self.table.setItem(current_row, COL_LEN, QtWidgets.QTableWidgetItem('{0}'.format(glub)))
        # Азимут
        self.table.setItem(current_row, COL_AZIMUT, QtWidgets.QTableWidgetItem('{0:.2f}'.format(azimuth)))
        # Зенит
        self.table.setItem(current_row, COL_ZENIT, QtWidgets.QTableWidgetItem('{0:.2f}'.format(pitch)))
        # ПЗ
        self.table.setItem(current_row, COL_PZ, QtWidgets.QTableWidgetItem('{0:.2f}'.format(roll)))

        #Расчет параметров
        #Отклонение град.
        otkl_grad=azimuth-self.prj_azimut
        self.table.setItem(current_row, COL_OTKL, QtWidgets.QTableWidgetItem('{0:.2f}'.format(otkl_grad)))


        goriz_proek=0.0
        LP=0.0
        VN=0.0
        if current_row>0:
            prev_row=0
            for i in range(current_row-1,0,-1):# ищем последний активный замер
                if self.table.item(i,COL_STATUS).checkState()==QtCore.Qt.Checked:
                    prev_row=i
                    break

            #prev_row=current_row-1
            prev_bur_size=float(self.table.item(prev_row,COL_SIZE).text())
            prev_pitch=float(self.table.item(prev_row,COL_ZENIT).text())
            prev_roll=float(self.table.item(prev_row,COL_PZ).text())
            prev_otkl_grad=float(self.table.item(prev_row,COL_OTKL).text())
            prev_goriz_proek=float(self.table.item(prev_row,COL_GORIZ).text())
            prev_LP=float(self.table.item(prev_row,COL_LP).text())
            prev_VN=float(self.table.item(prev_row,COL_VN).text())

            #Гориз. проекция
            goriz_proek=(self.bur_size-prev_bur_size)/2*\
                        (cos(pitch*pi/180)*cos(otkl_grad*pi/180)+cos(prev_pitch*pi/180)*cos(prev_otkl_grad*pi/180))+prev_goriz_proek

            #Л/П
            LP=(self.bur_size-prev_bur_size)/2*\
                        (cos(pitch*pi/180)*sin(otkl_grad*pi/180)+cos(prev_pitch*pi/180)*sin(prev_otkl_grad*pi/180))+prev_LP

            #В/Н
            VN=(self.bur_size-prev_bur_size)/2*\
                        (sin(pitch*pi/180)+sin(prev_pitch*pi/180))+prev_VN


        #Гориз. проекция
        self.table.setItem(current_row, COL_GORIZ, QtWidgets.QTableWidgetItem('{0:.2f}'.format(goriz_proek)))

        #Л/П
        self.table.setItem(current_row, COL_LP, QtWidgets.QTableWidgetItem('{0:.2f}'.format(LP)))

        #В/Н
        self.table.setItem(current_row, COL_VN, QtWidgets.QTableWidgetItem('{0:.2f}'.format(VN)))

        # Время замера
        self.table.setItem(current_row, COL_TIME, ti)
        # Дата замера
        self.table.setItem(current_row, COL_DATE, QtWidgets.QTableWidgetItem('{0}'.format(mes_date)))

        # Температура
        self.table.setItem(current_row, COL_TEMP, QtWidgets.QTableWidgetItem('{0}'.format(round(temp))))

        # CV
        self.table.setItem(current_row, COL_CV, QtWidgets.QTableWidgetItem('{0:.2f}'.format(CV)))

        # MV
        self.table.setItem(current_row, COL_MV, QtWidgets.QTableWidgetItem('{0:.2f}'.format(MV)))

        # battery
        self.table.setItem(current_row, COL_BATTERY, QtWidgets.QTableWidgetItem('{0:.2f}'.format(battery)))
        self.sb_battery.setText('Заряд батареи: {0}%'.format(self._calc_battery(battery)))
        # Данные полученные с датчика (сырые данные)

        # sys
        self.table.setItem(current_row, COL_SYS, QtWidgets.QTableWidgetItem(str(i_sys)))
        # gyro
        self.table.setItem(current_row, COL_GYRO, QtWidgets.QTableWidgetItem(str(i_gyro)))
        # acc
        self.table.setItem(current_row, COL_ACC, QtWidgets.QTableWidgetItem(str(i_acc)))
        # mag
        self.table.setItem(current_row, COL_MAG, QtWidgets.QTableWidgetItem(str(i_mag)))
        self.sb_int.setText('sys={0} gyro={1} acc={2} mag={3}'.format(i_sys,i_gyro,i_acc,i_mag))


        # status
        tstatus = QtWidgets.QTableWidgetItem()
        tstatus.setCheckState(QtCore.Qt.Checked)
        self.table.setItem(current_row, 20, tstatus)

        self.bur_id += 1

        self.compass_canvas.update_figure(roll)
        self._update_compas_info(roll,temp)
        self.table.scrollToBottom()
        self.update_graphic()
        self.save_as_prj_handle(save_as=False)

    def measure_button_handler(self):
        self.mf.ok_button.setEnabled(False)
        if self.mf.exec_():
            values = self.mf.get_values()
            self.add_data_to_table(*values)

    def new_button_handler(self):
        #self.fmNewPrj.bt_reset_pz.setEnabled(self.modbus_client is not None)
        if self.fmNewPrj.exec_():
            v=self.fmNewPrj.get_values()
            self._set_prj_params(*v)
            self.prj_name = self.fmNewPrj.prj_name_edit.text()
            self.table.setRowCount(0)
            self.table.setEnabled(True)
            self.fmFileMenu.saveas_button.setEnabled(True)
            self.fmFileMenu.save_button.setEnabled(True)
            self.fmFileMenu.csv_button.setEnabled(True)
            self.edit_button.setEnabled(True)
            self.add_data_to_table(self.bur_size1,self.start_azimut,self.start_pitch,0,self.fmNewPrj.t,0,0,0,0,0,0,0)
            self.save_config()
            self.setWindowTitle(self.prj_name)

    def open_prj_handle(self,prj_name=''):
        if prj_name=='':
            prj_file = QtWidgets.QFileDialog.getOpenFileName(self, "Открыть проект",'./','*.rdgs;;*.*')[0]
        else:
            prj_file=prj_name
        if len(prj_file)>0:
            try:
                self.prj_name = prj_file
                self._load_prj(prj_file)
                self.fmFileMenu.saveas_button.setEnabled(True)
                self.fmFileMenu.save_button.setEnabled(True)
                self.fmFileMenu.csv_button.setEnabled(True)
                self.edit_button.setEnabled(True)
                self.update_graphic()
                self.save_config()
                self.setWindowTitle(self.prj_name)
            except:
                self.prj_name=''
                #raise

    def _show_message(self,text,title='Ошибка',icon=QMessageBox.Critical):
        msg=QMessageBox(text=text)
        msg.setIcon(icon)
        msg.setText(text)
        msg.setWindowTitle(title)
        msg.exec_()
    """

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = Ui()
    app.exec_()
