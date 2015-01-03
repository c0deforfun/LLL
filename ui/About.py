""" for configuring working dir and args"""
from PyQt4.QtGui import QDialog
from PyQt4.QtCore import QT_VERSION_STR
from PyQt4.Qt import PYQT_VERSION_STR
from sip import SIP_VERSION_STR
from ui.UIAbout import Ui_AboutDialog

VERSION = "0.1"
class AboutDialog(QDialog):
    """ Config window"""
    def __init__(self):
        super(AboutDialog, self).__init__()
        self.ui = Ui_AboutDialog()
        self.ui.setupUi(self)
        self.ui.label_ver.setText(VERSION)
        self.ui.label_Qt_ver.setText(QT_VERSION_STR)
        self.ui.label_pyqt_ver.setText(PYQT_VERSION_STR)
        self.ui.label_sip_ver.setText(SIP_VERSION_STR)

