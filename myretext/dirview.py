#!/usr/bin/env python

import os
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIcon,QColor
from PyQt5.QtCore import QDir,pyqtSignal
from shutil import *
import subprocess
import re
import git


class TreeView(QTreeView):

    def __init__(self, parent=None):
        super(TreeView, self).__init__(parent)
        self.parent = parent
        self.__model = QFileSystemModel()
        self.__model.setRootPath(QDir.rootPath())
        self.setModel(self.__model)
        self.current_select_path = None
        self.doubleClicked.connect(self.open)
        self.srcFileName = None
        self.srcPath = None
        self.destPath = None
        self.CUT_FLAG = False
        self.projectPath = None
        self.PATH_FLAG = 1

    def open(self):
        if os.path.isfile(self.__model.filePath(self.currentIndex())):
            self.parent.openFileWrapper(self.__model.filePath(self.currentIndex()))

    # 设置TreeView的跟目錄
    def setPath(self, path):
        self.setRootIndex(self.__model.index(path))
        self.projectPath = path

    # 获得当前选中的节点的路径
    def getCurPath(self):
        return self.__model.filePath(self.currentIndex())

    def contextMenuEvent(self, event):
        self.current_select_path = self.__model.filePath(self.currentIndex())
        menu = QMenu(self)
        newDirAction = menu.addAction("new directory")
        newFileAction = menu.addAction("new file")
        secondmenu = menu.addMenu("git command")
        gitPushAction = menu.addAction("upload")
        repoUploadAll = menu.addAction("upload all")
        renameAction = menu.addAction("rename")
        copyAction = menu.addAction("copy")
        cutAction = menu.addAction("cut")
        pasteAction = menu.addAction("paste")
        deleteAction = menu.addAction("delete")
        gitresetAction = secondmenu.addAction("checkout file")
        gitcheckdiffAction = secondmenu.addAction("check diff file")
        gitpullAction = secondmenu.addAction("git pull")

        if not self.__model.filePath(self.currentIndex()):
            deleteAction.setEnabled(False)
            pasteAction.setEnabled(False)
            copyAction.setEnabled(False)
            repoUploadAll.setEnabled(False)
            gitPushAction.setEnabled(False)
            renameAction.setEnabled(False)
            cutAction.setEnabled(False)
            gitresetAction.setEnabled(False)
            gitcheckdiffAction.setEnabled(False)
            gitpullAction.setEnabled(False)

        if not self.srcPath:
            pasteAction.setEnabled(False)

        path = self.current_select_path
        if path and os.path.exists(path):
            if os.path.isfile(path):
                path = os.path.dirname(path)
            os.chdir(path)
            status,output = subprocess.getstatusoutput("git status")
            if status == 0 and re.search("nothing to commit",output):
                repoUploadAll.setEnabled(False)
                gitPushAction.setEnabled(False)
            elif status != 0:
                repoUploadAll.setEnabled(False)
                gitPushAction.setEnabled(False)
            os.chdir(os.path.dirname(self.current_select_path))
            status,output = subprocess.getstatusoutput("git status "+self.current_select_path)
            if status == 0 and not re.search(os.path.basename(self.current_select_path),output):
                gitPushAction.setEnabled(False)

        newDirAction.triggered.connect(self.createNewDir)
        newFileAction.triggered.connect(self.createNewFile)
        deleteAction.triggered.connect(self.deleteFile)
        renameAction.triggered.connect(self.reName)
        gitPushAction.triggered.connect(self.gitPush)
        copyAction.triggered.connect(self.copy)
        pasteAction.triggered.connect(self.paste)
        cutAction.triggered.connect(self.cut)
        repoUploadAll.triggered.connect(self.repoUploadAll)
        gitpullAction.triggered.connect(self.gitPull)
        gitresetAction.triggered.connect(self.gitCheckOutFile)
        gitcheckdiffAction.triggered.connect(self.checkDiffFile)
        menu.exec_(event.globalPos())

    '''上下文菜单槽函数'''

    def get_repo(self):
        for parent, dirnames, filenames in os.walk(self.projectPath):
            if '.git' in dirnames:
                gitPath = parent
                break
        repo = git.Repo(gitPath)
        return repo

    def gitPull(self):
        for parent, dirnames, filenames in os.walk(self.projectPath):
            if '.git' in dirnames:
                gitPath = parent
                break
        repo = git.Repo(gitPath)
        remote = repo.remote()
        remote.pull()

    def checkDiffFile(self):
        beforePath = os.getcwd()
        if os.path.isfile(self.current_select_path):
            self.current_select_path = os.path.dirname(self.current_select_path)
        os.chdir(self.current_select_path)
        status,output = subprocess.getstatusoutput("git diff --name-only")
        if status == 0:
            QMessageBox.about(self,"diff file",output)
        else:
            QMessageBox.about(self,"error",output)
        os.chdir(beforePath)

    def gitCheckOutFile(self):
        status,output = subprocess.getstatusoutput("git checkout "+os.path.basename(self.current_select_path))
        if status != 0:
            QMessageBox.about(self,"output",output)

    def cut(self):
        self.srcPath = self.getCurPath()
        self.CUT_FLAG = True

    def copy(self):
        self.srcPath = self.getCurPath()

    def paste(self):
        if not self.srcPath:
            return
        self.srcFileName = os.path.basename(self.srcPath)
        self.destPath = self.getCurPath()
        if os.path.isfile(self.destPath):
          self.destPath = os.path.dirname(self.getCurPath())
        self.destPath = self.destPath + "/" + self.srcFileName

        if os.path.exists(self.srcPath):
            if os.path.exists(self.destPath):
                QMessageBox.about(self, "error", "file alreadly exists")
            else:
                if os.path.isdir(self.srcPath):
                    copytree(self.srcPath,self.destPath)
                if os.path.isfile(self.srcPath):
                    copyfile(self.srcPath,self.destPath)
                if self.CUT_FLAG == True:
                    if os.path.isdir(self.srcPath):
                        rmtree(self.srcPath)
                    else:
                        os.remove(self.srcPath)
                    self.CUT_FLAG = False
                self.srcPath = None
                self.destPath = None
        self.update()


    def gitPush(self):
        self.upload(1)

    def repoUploadAll(self):
        self.upload(0)

    def upload(self,push_flag):
        sourcePath = self.current_select_path
        # if os.path.isfile(self.current_select_path):
        #     self.current_select_path = os.path.dirname(self.current_select_path)
        repo = self.get_repo()
        remote = repo.remote()
        remote.pull()
        index = repo.index
        if push_flag:
            repo_git = repo.git
            repo_git.add(sourcePath)
        else:
            index.add('*')

        message, okPressed = QInputDialog.getText(self, "commit message", "please input gitcommit message", QLineEdit.Normal,"")
        if okPressed and message:
            index.commit(message)
        else:
            QMessageBox.about(self, "error", "commit message cannot empty")
            return -1
        remote.push()
        QMessageBox.about(self, "success!!", "upload success!!!!")
        self.update()


    def reName(self):
        oldFilePath = self.getCurPath()
        filename = os.path.basename(oldFilePath)
        text, okPressed = QInputDialog.getText(self, "rename", "please input new filename", QLineEdit.Normal,filename)
        if okPressed and text != '':
            newFilePath = os.path.dirname(oldFilePath) + "/" + text
            os.rename(oldFilePath,newFilePath)
        self.update()

    def deleteFile(self):
        reply = QMessageBox.information(self,"deleteFile","are you sure to delete?",QMessageBox.No | QMessageBox.Yes,QMessageBox.Yes)
        if reply == QMessageBox.Yes:
            filePath = self.__model.filePath(self.currentIndex())
            if os.path.exists(filePath):
                subprocess.getstatusoutput("git rm -rf "+filePath)
        self.update()

    def createNewFile(self):
        beforePath = os.getcwd()
        text, okPressed = QInputDialog.getText(self, "createNewFile", "please input filename", QLineEdit.Normal, "")

        if okPressed:
            if text:
                filePath = self.getCurPath()
                if filePath:
                    if os.path.isdir(filePath):
                        os.chdir(filePath)
                        filePath = filePath + "/" + text + ".md"
                    else:
                        filePath = os.path.dirname(filePath)
                        os.chdir(filePath)
                        filePath = filePath + "/" + text + ".md"
                    if os.path.exists(filePath):
                        QMessageBox.about(self, "error", "file alreadly exists")
                    else:
                        file = open(filePath, 'w')
                        file.close()
                        # 新创建的文件，得用git add 添加一波
                        repo = self.get_repo()
                        repo_git = repo.git
                        repo_git.add(filePath)

                    os.chdir(beforePath)
                else:
                    filePath = self.projectPath + "/" + text + ".md"
                    file = open(filePath, 'w')
                    file.close()
            else:
                QMessageBox.about(self, "error", "A name should be specified")
            self.update()

    def createNewDir(self):
        text, okPressed = QInputDialog.getText(self, "createNewDir", "please input Dirname", QLineEdit.Normal, "")
        if okPressed and text != '':
            dirPath = self.getCurPath()
            if dirPath:
                if os.path.isdir(dirPath):
                    dirPath = dirPath + "/" + text
                else:
                    dirPath = os.path.dirname(dirPath)
                    dirPath = dirPath + "/" + text
                if (os.path.exists(dirPath)):
                    QMessageBox.about(self,"error","file alreadly exists")
                else:
                    os.mkdir(dirPath)
            else:
                dirPath = self.projectPath + "/" + text
                os.mkdir(dirPath)
        self.update()
