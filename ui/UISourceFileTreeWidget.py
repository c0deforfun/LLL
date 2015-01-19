# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/SourceFileTreeWidget.ui'
#
# Created: Sun Jan 18 16:25:01 2015
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

class Ui_SourceFileTreeWidget(object):
    def setupUi(self, SourceFileTreeWidget):
        SourceFileTreeWidget.setObjectName(_fromUtf8("SourceFileTreeWidget"))
        SourceFileTreeWidget.resize(479, 441)
        self.verticalLayout = QtGui.QVBoxLayout(SourceFileTreeWidget)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.label = QtGui.QLabel(SourceFileTreeWidget)
        self.label.setObjectName(_fromUtf8("label"))
        self.horizontalLayout_2.addWidget(self.label)
        self.custom_root = QtGui.QLineEdit(SourceFileTreeWidget)
        self.custom_root.setObjectName(_fromUtf8("custom_root"))
        self.horizontalLayout_2.addWidget(self.custom_root)
        self.ok_root = QtGui.QPushButton(SourceFileTreeWidget)
        self.ok_root.setMaximumSize(QtCore.QSize(35, 16777215))
        self.ok_root.setObjectName(_fromUtf8("ok_root"))
        self.horizontalLayout_2.addWidget(self.ok_root)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.tree = QtGui.QTreeView(SourceFileTreeWidget)
        self.tree.setObjectName(_fromUtf8("tree"))
        self.verticalLayout.addWidget(self.tree)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.Filter = QtGui.QLabel(SourceFileTreeWidget)
        self.Filter.setObjectName(_fromUtf8("Filter"))
        self.horizontalLayout.addWidget(self.Filter)
        self.custom_filter = QtGui.QLineEdit(SourceFileTreeWidget)
        self.custom_filter.setObjectName(_fromUtf8("custom_filter"))
        self.horizontalLayout.addWidget(self.custom_filter)
        self.ok_filter = QtGui.QPushButton(SourceFileTreeWidget)
        self.ok_filter.setMaximumSize(QtCore.QSize(35, 16777215))
        self.ok_filter.setObjectName(_fromUtf8("ok_filter"))
        self.horizontalLayout.addWidget(self.ok_filter)
        self.verticalLayout.addLayout(self.horizontalLayout)

        self.retranslateUi(SourceFileTreeWidget)
        QtCore.QMetaObject.connectSlotsByName(SourceFileTreeWidget)

    def retranslateUi(self, SourceFileTreeWidget):
        SourceFileTreeWidget.setWindowTitle(_translate("SourceFileTreeWidget", "Form", None))
        self.label.setText(_translate("SourceFileTreeWidget", "Root:", None))
        self.ok_root.setText(_translate("SourceFileTreeWidget", "OK", None))
        self.Filter.setText(_translate("SourceFileTreeWidget", "Filter:", None))
        self.custom_filter.setText(_translate("SourceFileTreeWidget", "*.c;*.h;*.cpp;*.hpp", None))
        self.ok_filter.setText(_translate("SourceFileTreeWidget", "OK", None))

