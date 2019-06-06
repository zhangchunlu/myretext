from PyQt5.QtWidgets import *
import subprocess
import os
from ReText.loadGif import LoadingGifWin
import threading
from PyQt5.QtCore import pyqtSignal
from ReText import (readListFromSettings, writeListToSettings)

class InputdialogDemo(QDialog):

    loadDialog_close_signal = pyqtSignal()

    def __init__(self, parent=None):
        super(InputdialogDemo, self).__init__(parent)
        self.parent = parent
        self.setWindowTitle('new project')
        self.nameLb1 = QLabel('&GitcloneUrl')
        self.nameEd1 = QLineEdit()
        self.nameLb1.setBuddy(self.nameEd1)
        self.nameLb2 = QPushButton("Location")
        self.nameEd2 = QLineEdit()
        self.btnOk = QPushButton('&OK')
        self.btnCancel = QPushButton('&Cancel')
        self.mainLayout = QGridLayout()
        self.mainLayout.addWidget(self.nameLb1, 0, 0)
        self.mainLayout.addWidget(self.nameEd1, 0, 1, 1, 2)
        self.mainLayout.addWidget(self.nameLb2, 1, 0)
        self.mainLayout.addWidget(self.nameEd2, 1, 1, 1, 2)
        self.mainLayout.addWidget(self.btnOk, 2, 1)
        self.mainLayout.addWidget(self.btnCancel, 2, 2)
        self.btnOk.clicked.connect(self.exitOk)
        self.btnCancel.clicked.connect(self.exitCancal)
        self.nameLb2.clicked.connect(self.getIext)
        self.setLayout(self.mainLayout)
        self.gitCloneUrl = None
        self.location = None
        self.loadingGitWin = LoadingGifWin()
        self.loadDialog_close_signal.connect(self.loadingGitWin.close)
        self.status = -1
        self.ouput = None

    def gitclone(self):
        os.chdir(self.location)
        self.status,self.output = subprocess.getstatusoutput('git clone '+ self.gitCloneUrl)
        self.loadDialog_close_signal.emit()

    # def gitclone(self):
    #     os.chdir(self.location)
    #     self.status,self.output = subprocess.getstatusoutput("git clone " + self.gitCloneUrl)
    #     self.loadDialog_close_signal.emit()

    def exec_loading(self):
        self.loadingGitWin.exec_()

    def upToRecntProject(self,projectPath,gitCloneUrl):
        projectNameList = readListFromSettings("rencentProject")
        gitCloneUrlList = readListFromSettings("gitCloneUrlList")
        if projectPath in projectNameList:
            index = projectNameList.index(projectPath)
            projectNameList.remove(projectPath)
            del gitCloneUrlList[index]
        projectNameList.insert(0, projectPath)
        gitCloneUrlList.insert(0,gitCloneUrl)
        writeListToSettings("rencentProject", projectNameList)
        writeListToSettings("gitCloneUrlList",gitCloneUrlList)

    def exitOk(self):
        self.gitCloneUrl = self.nameEd1.text()
        self.location = self.nameEd2.text()

        if not self.gitCloneUrl:
            QMessageBox.about(self,"fatal","gitCloneUrl cannot be empty")
        elif not self.location:
            QMessageBox.about(self,"fatal","location cannot be empty")
        elif not os.path.exists(self.location):
            QMessageBox.about(self,"fatal","location not exists")
        elif not os.path.isdir(self.location):
            QMessageBox.about(self, "fatal", "please select a empty directory as location")
        else:
            output = os.listdir(self.location)
            if output:
                QMessageBox.about(self,"fatal","please select a empty directory as location")
            else:
                self.close()
                thread_loding = threading.Thread(target=self.gitclone)
                thread_loding.start()
                self.loadingGitWin.exec_()
                if self.status != 0:
                    QMessageBox.about(self, "error", self.output)
                else:
                    self.parent.dirTree.setPath(self.location)
                    self.parent.dirTree.setVisible(True)
                    self.parent.dirTree.update()
                    QMessageBox.about(self, "success!!", "create new project successful!!!")
                    self.upToRecntProject(self.location,self.gitCloneUrl)

    def exitCancal(self):
        self.close()

    def getIext(self):
        dlg = QFileDialog()
        dlg.setFileMode(QFileDialog.Directory)
        if dlg.exec_():
            filename = dlg.selectedFiles()
            if filename:
                self.nameEd2.setText(filename[0])