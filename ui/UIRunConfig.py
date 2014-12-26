# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/UIRunConfig.ui'
#
# Created: Thu Dec 25 20:13:42 2014
#      by: PyQt4 UI code generator 4.11.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_DiagRunConfig(object):
    def setupUi(self, DiagRunConfig):
        DiagRunConfig.setObjectName(_fromUtf8("DiagRunConfig"))
        DiagRunConfig.resize(400, 300)
        DiagRunConfig.setModal(True)
        self.buttonBox = QtGui.QDialogButtonBox(DiagRunConfig)
        self.buttonBox.setGeometry(QtCore.QRect(30, 240, 341, 32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.txtArgs = QtGui.QPlainTextEdit(DiagRunConfig)
        self.txtArgs.setGeometry(QtCore.QRect(20, 30, 361, 131))
        self.txtArgs.setObjectName(_fromUtf8("txtArgs"))
        self.label = QtGui.QLabel(DiagRunConfig)
        self.label.setGeometry(QtCore.QRect(20, 10, 101, 16))
        self.label.setObjectName(_fromUtf8("label"))
        self.label_2 = QtGui.QLabel(DiagRunConfig)
        self.label_2.setGeometry(QtCore.QRect(20, 170, 101, 16))
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.txtWorkDir = QtGui.QLineEdit(DiagRunConfig)
        self.txtWorkDir.setGeometry(QtCore.QRect(20, 190, 281, 22))
        self.txtWorkDir.setObjectName(_fromUtf8("txtWorkDir"))

        self.retranslateUi(DiagRunConfig)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), DiagRunConfig.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), DiagRunConfig.reject)
        QtCore.QMetaObject.connectSlotsByName(DiagRunConfig)

    def retranslateUi(self, DiagRunConfig):
        DiagRunConfig.setWindowTitle(_translate("DiagRunConfig", "Dialog", None))
        self.label.setText(_translate("DiagRunConfig", "Arguments:", None))
        self.label_2.setText(_translate("DiagRunConfig", "Working Directory:", None))

