import sys
from PyQt5.QtWidgets import QApplication, QLabel ,QWidget,QDialog
from PyQt5.QtCore import Qt 
from PyQt5.QtGui import QMovie
import os

class LoadingGifWin(QDialog):
    def __init__(self,parent=None):
        super(LoadingGifWin, self).__init__(parent)
        self.label =  QLabel('', self)
        self.setFixedSize(128,128)
        self.setWindowFlags( Qt.Dialog| Qt.CustomizeWindowHint)
        path = os.path.dirname(os.path.dirname(__file__)) + "/icons/loading.gif"
        self.movie =  QMovie(path)
        self.label.setMovie(self.movie)
        self.movie.start()

    def drop(self):
        self.close()
