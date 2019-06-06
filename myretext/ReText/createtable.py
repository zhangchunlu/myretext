from PyQt5.QtWidgets import *
import subprocess
import os
from ReText.loadGif import LoadingGifWin
import threading
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QIntValidator,QDoubleValidator,QFont
from ReText import (readListFromSettings, writeListToSettings)

class Table(QDialog):

    loadDialog_close_signal = pyqtSignal()

    def __init__(self, parent=None):
        super(Table, self).__init__(parent)
        self.parent = parent
        self.setWindowTitle('创建表格')
        self.nameLb1 = QLabel('行')
        self.nameEd1 = QLineEdit()
        self.nameEd1.setValidator(QIntValidator())
        self.nameLb1.setBuddy(self.nameEd1)
        self.nameLb2 = QLabel("列")
        self.nameEd2 = QLineEdit()
        self.nameEd2.setValidator(QIntValidator())
        self.btnOk = QPushButton('确定')
        self.btnCancel = QPushButton('取消')
        self.mainLayout = QGridLayout()
        self.mainLayout.addWidget(self.nameLb1, 0, 0)
        self.mainLayout.addWidget(self.nameEd1, 0, 1, 1, 2)
        self.mainLayout.addWidget(self.nameLb2, 1, 0)
        self.mainLayout.addWidget(self.nameEd2, 1, 1, 1, 2)
        self.mainLayout.addWidget(self.btnOk, 2, 1)
        self.mainLayout.addWidget(self.btnCancel, 2, 2)
        self.btnOk.clicked.connect(self.exitOk)
        self.btnCancel.clicked.connect(self.exitCancal)
        self.setLayout(self.mainLayout)


    def exitOk(self):
        hang = int(self.nameEd1.text())
        lie = int(self.nameEd2.text())
        # if not self.hang:
        #     QMessageBox.about(self,"fatal","gitCloneUrl cannot be empty")
        # elif not self.lie:
        #     QMessageBox.about(self,"fatal","location cannot be empty")
        #
        cursor = self.parent.currentTab.editBox.textCursor()
        table_string = '\n' + '|      ' * lie + '|' + '\n' + '| ---- ' * lie + '|' + ('\n' + '|      ' * lie + '|') * (
                    hang - 1)
        cursor.insertText(table_string)
        self.close()

    def exitCancal(self):
        self.close()
