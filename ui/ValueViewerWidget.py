""" for showing source file tree"""
from PyQt4.QtGui import QWidget, QHeaderView, QStandardItemModel, QStandardItem

from ui.UIValueViewerWidget import Ui_ValueViewerWidget

class ValueViewerWidget(QWidget):

    """ Value Viewer Widget """
    def __init__(self, parent):
        super(ValueViewerWidget, self).__init__(parent)
        self.ui = Ui_ValueViewerWidget()
        self.ui.setupUi(self)
        self.value_model = QStandardItemModel()
        self.ui.tree.setModel(self.value_model)
        self.ui.tree.expanded.connect(self.on_expand)

        header = self.ui.tree.header()
        header.setResizeMode(QHeaderView.ResizeToContents)
        self.idx_value = {}

    def show_value(self, var, parent):
        """ show the value of a variable """
        value = var.value
        if not value:
            value = ''
        value_item = QStandardItem(value)
        name_item = QStandardItem(var.name)
        parent.appendRow([name_item, value_item, QStandardItem(var.type.GetName())])
        # Lazy loading
        if var.GetNumChildren():
            dummy_item = QStandardItem('Loading...')
            dummy_item.setEnabled(False)
            row_loading = [dummy_item, QStandardItem(''), QStandardItem('')]
            self.idx_value[name_item.index()] = var
            name_item.appendRow(row_loading)

    def show_variables(self, frame):
        """ show variables in widget """
        #args = frame.get_arguments()
        #statics = frame.get_statics()
        #autos = frame.get_locals()

        # v.GetValueType() : eValueType{Invalid,Register,RegisterSet,VariableArgument,
        #                               VariableGlobal,VariableLocal,VariableStatic
        self.value_model.clear()
        self.idx_value.clear()

        self.value_model.setHorizontalHeaderLabels(['Name', 'Value', 'Type'])
        vals = frame.GetVariables(True, True, True, False)
        root = self.value_model.invisibleRootItem()
        for val in vals:
            self.show_value(val, root)

        self.ui.tree.resizeColumnToContents(0)
        self.ui.tree.resizeColumnToContents(1)
        self.ui.tree.resizeColumnToContents(2)

    def on_expand(self, index):
        """ load sub values when first expanded """
        item = self.value_model.itemFromIndex(index)
        if item.rowCount() != 1 or item.child(0).isEnabled():
            return
        var = self.idx_value[index]
        item.removeRow(0)
        for child in var:
            self.show_value(child, item)
        self.ui.tree.resizeColumnToContents(0)
        self.ui.tree.resizeColumnToContents(1)
        self.ui.tree.resizeColumnToContents(2)


