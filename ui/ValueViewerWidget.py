""" for showing source file tree"""
from PyQt4.QtGui import QWidget, QHeaderView, QStandardItemModel, QStandardItem
import logging, os

from ui.UIValueViewerWidget import Ui_ValueViewerWidget

class ValueViewerWidget(QWidget):

    """ Value Viewer Widget """
    def __init__(self, parent):
        super(ValueViewerWidget, self).__init__(parent)
        self.ui = Ui_ValueViewerWidget()
        self.ui.setupUi(self)
        self.value_model = QStandardItemModel()
        self.ui.tree.setModel(self.value_model)

        header = self.ui.tree.header()
        header.setResizeMode(QHeaderView.ResizeToContents)

    def show_values(self, frame):
        #args = frame.get_arguments()
        #statics = frame.get_statics()
        #autos = frame.get_locals()

        # v.GetValueType() : eValueType{Invalid,Register,RegisterSet,VariableArgument,VariableGlobal,VariableLocal,VariableStatic
        self.value_model.clear()
        self.value_model.setHorizontalHeaderLabels(['Name', 'Value', 'Type'])
        vals = frame.GetVariables(True, True, True, False)
        root = self.value_model.invisibleRootItem()
        for v in vals:
            name = v.GetName()
            value = v.GetValue()
            ty = v.GetType()
            row = [QStandardItem(name), QStandardItem(value), QStandardItem(ty.GetName())]
            root.appendRow(row)
            
        self.ui.tree.resizeColumnToContents(0)
