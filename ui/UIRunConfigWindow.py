from PyQt4.QtGui import QDialog
from UIRunConfig import Ui_DiagRunConfig
import os

class RunConfigWindow(QDialog):
    def __init__(self):
        super(RunConfigWindow, self).__init__()
        self.ui = Ui_DiagRunConfig()
        self.ui.setupUi(self)
        self.args = ""
        self.arglist = []
        self.workDir = os.getcwd()

    def reset(self):    
        self.ui.txtWorkDir.setText(self.workDir)
        self.ui.txtArgs.setPlainText(self.args)

    def setArgStr(self, argStr):
        self.ui.txtArgs.setPlainText(argStr)

    def setWorkingDir(self, txt):
            self.ui.txtWorkDir.setText(txt)

    def accept(self):
        self.args = self.ui.txtArgs.toPlainText()
        self.workDir = self.ui.txtWorkDir.text()
        argLine = str(self.args.replace("\n"," "))
        self.arglist = argLine.split()
        QDialog.accept(self)


    def reject(self):
        self.reset()
        QDialog.reject(self)

