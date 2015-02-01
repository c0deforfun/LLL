# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/UIValueViewerWidget.ui'
#
# Created: Wed Jan 28 21:48:37 2015
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

class Ui_ValueViewerWidget(object):
    def setupUi(self, ValueViewerWidget):
        ValueViewerWidget.setObjectName(_fromUtf8("ValueViewerWidget"))
        ValueViewerWidget.resize(268, 599)
        self.verticalLayout = QtGui.QVBoxLayout(ValueViewerWidget)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.value_container = QtGui.QVBoxLayout()
        self.value_container.setSizeConstraint(QtGui.QLayout.SetDefaultConstraint)
        self.value_container.setObjectName(_fromUtf8("value_container"))
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.chkShowAutos = QtGui.QCheckBox(ValueViewerWidget)
        self.chkShowAutos.setObjectName(_fromUtf8("chkShowAutos"))
        self.horizontalLayout.addWidget(self.chkShowAutos)
        self.value_container.addLayout(self.horizontalLayout)
        self.verticalLayout.addLayout(self.value_container)
        self.tree = QtGui.QTreeView(ValueViewerWidget)
        self.tree.setObjectName(_fromUtf8("tree"))
        self.verticalLayout.addWidget(self.tree)

        self.retranslateUi(ValueViewerWidget)
        QtCore.QMetaObject.connectSlotsByName(ValueViewerWidget)

    def retranslateUi(self, ValueViewerWidget):
        ValueViewerWidget.setWindowTitle(_translate("ValueViewerWidget", "Form", None))
        self.chkShowAutos.setText(_translate("ValueViewerWidget", "Autos", None))

