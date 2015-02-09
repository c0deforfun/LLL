""" for configuring working dir and args"""
from PyQt4.QtGui import QDialog
from ui.UIRunConfigWindow import Ui_DiagRunConfig
import os

class RunConfigWindow(QDialog):
    """ Config window"""
    def __init__(self):
        super(RunConfigWindow, self).__init__()
        self.ui = Ui_DiagRunConfig()
        self.ui.setupUi(self)
        self._arglist = []
        self._working_dir = os.getcwd()

    def reset(self):
        """ discard inputs """
        self.ui.txtWorkDir.setText(self._working_dir)
        self.ui.txtArgs.setPlainText(' '.join(self._arglist))

    @property
    def arglist(self):
        """ get arguments """
        return self._arglist

    @arglist.setter
    def arglist(self, args):
        """ set args from command line or this window"""
        self._arglist = args
        self.ui.txtArgs.setPlainText(' '.join(args))

    @property
    def working_dir(self):
        """ get working directory """
        return self._working_dir

    @working_dir.setter
    def working_dir(self, txt):
        """ working directory"""
        self.ui.txtWorkDir.setText(txt)

    def accept(self):
        """ OK """
        args = str(self.ui.txtArgs.toPlainText()).replace("\n", " ")
        self.arglist = args.split(' ')
        self._working_dir = str(self.ui.txtWorkDir.text())
        QDialog.accept(self)

    def reject(self):
        """ Cancel """
        self.reset()
        QDialog.reject(self)
