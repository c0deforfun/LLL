# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/UIAbout.ui'
#
# Created: Fri Jan  2 18:20:06 2015
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

class Ui_AboutDialog(object):
    def setupUi(self, AboutDialog):
        AboutDialog.setObjectName(_fromUtf8("AboutDialog"))
        AboutDialog.resize(366, 248)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/icons/icons/fix_bug.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        AboutDialog.setWindowIcon(icon)
        self.label_logo = QtGui.QLabel(AboutDialog)
        self.label_logo.setGeometry(QtCore.QRect(20, 10, 51, 51))
        self.label_logo.setText(_fromUtf8(""))
        self.label_logo.setPixmap(QtGui.QPixmap(_fromUtf8(":/icons/icons/fix_bug.png")))
        self.label_logo.setScaledContents(True)
        self.label_logo.setObjectName(_fromUtf8("label_logo"))
        self.layoutWidget = QtGui.QWidget(AboutDialog)
        self.layoutWidget.setGeometry(QtCore.QRect(70, 80, 234, 120))
        self.layoutWidget.setObjectName(_fromUtf8("layoutWidget"))
        self.gridLayout = QtGui.QGridLayout(self.layoutWidget)
        self.gridLayout.setMargin(0)
        self.gridLayout.setHorizontalSpacing(18)
        self.gridLayout.setVerticalSpacing(19)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.label = QtGui.QLabel(self.layoutWidget)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.label_2 = QtGui.QLabel(self.layoutWidget)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout.addWidget(self.label_2, 1, 0, 2, 1)
        self.label_3 = QtGui.QLabel(self.layoutWidget)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.gridLayout.addWidget(self.label_3, 3, 0, 1, 1)
        self.label_pyqt_ver = QtGui.QLabel(self.layoutWidget)
        self.label_pyqt_ver.setObjectName(_fromUtf8("label_pyqt_ver"))
        self.gridLayout.addWidget(self.label_pyqt_ver, 1, 1, 2, 1)
        self.label_ver = QtGui.QLabel(self.layoutWidget)
        self.label_ver.setObjectName(_fromUtf8("label_ver"))
        self.gridLayout.addWidget(self.label_ver, 0, 1, 1, 1)
        self.label_Qt_ver = QtGui.QLabel(self.layoutWidget)
        self.label_Qt_ver.setObjectName(_fromUtf8("label_Qt_ver"))
        self.gridLayout.addWidget(self.label_Qt_ver, 3, 1, 1, 1)
        self.label_4 = QtGui.QLabel(self.layoutWidget)
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.gridLayout.addWidget(self.label_4, 4, 0, 1, 1)
        self.label_sip_ver = QtGui.QLabel(self.layoutWidget)
        self.label_sip_ver.setObjectName(_fromUtf8("label_sip_ver"))
        self.gridLayout.addWidget(self.label_sip_ver, 4, 1, 1, 1)

        self.retranslateUi(AboutDialog)
        QtCore.QMetaObject.connectSlotsByName(AboutDialog)

    def retranslateUi(self, AboutDialog):
        AboutDialog.setWindowTitle(_translate("AboutDialog", "About", None))
        self.label.setText(_translate("AboutDialog", "Version:", None))
        self.label_2.setText(_translate("AboutDialog", "PyQt Version:", None))
        self.label_3.setText(_translate("AboutDialog", "Qt Version:", None))
        self.label_pyqt_ver.setText(_translate("AboutDialog", "TextLabel", None))
        self.label_ver.setText(_translate("AboutDialog", "TextLabel", None))
        self.label_Qt_ver.setText(_translate("AboutDialog", "TextLabel", None))
        self.label_4.setText(_translate("AboutDialog", "SIP Version:", None))
        self.label_sip_ver.setText(_translate("AboutDialog", "TextLabel", None))

import resources_rc
