# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/UIMain.ui'
#
# Created: Thu Dec 25 20:13:41 2014
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

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName(_fromUtf8("MainWindow"))
        MainWindow.resize(873, 675)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(MainWindow.sizePolicy().hasHeightForWidth())
        MainWindow.setSizePolicy(sizePolicy)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/icons/icons/fix_bug.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        MainWindow.setWindowIcon(icon)
        MainWindow.setLocale(QtCore.QLocale(QtCore.QLocale.English, QtCore.QLocale.UnitedStates))
        self.centralWidget = QtGui.QWidget(MainWindow)
        self.centralWidget.setEnabled(True)
        self.centralWidget.setObjectName(_fromUtf8("centralWidget"))
        self.verticalLayout = QtGui.QVBoxLayout(self.centralWidget)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.tabCodeEditor = QtGui.QTabWidget(self.centralWidget)
        self.tabCodeEditor.setObjectName(_fromUtf8("tabCodeEditor"))
        self.verticalLayout.addWidget(self.tabCodeEditor)
        self.commander = CommandWindow(self.centralWidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(3)
        sizePolicy.setHeightForWidth(self.commander.sizePolicy().hasHeightForWidth())
        self.commander.setSizePolicy(sizePolicy)
        self.commander.setPlainText(_fromUtf8(">"))
        self.commander.setObjectName(_fromUtf8("commander"))
        self.verticalLayout.addWidget(self.commander)
        MainWindow.setCentralWidget(self.centralWidget)
        self.menuBar = QtGui.QMenuBar(MainWindow)
        self.menuBar.setGeometry(QtCore.QRect(0, 0, 873, 21))
        self.menuBar.setObjectName(_fromUtf8("menuBar"))
        self.menu_File = QtGui.QMenu(self.menuBar)
        self.menu_File.setObjectName(_fromUtf8("menu_File"))
        self.menu_Help = QtGui.QMenu(self.menuBar)
        self.menu_Help.setObjectName(_fromUtf8("menu_Help"))
        self.menu_Edit = QtGui.QMenu(self.menuBar)
        self.menu_Edit.setObjectName(_fromUtf8("menu_Edit"))
        self.menuRun = QtGui.QMenu(self.menuBar)
        self.menuRun.setObjectName(_fromUtf8("menuRun"))
        MainWindow.setMenuBar(self.menuBar)
        self.statusBar = QtGui.QStatusBar(MainWindow)
        self.statusBar.setObjectName(_fromUtf8("statusBar"))
        MainWindow.setStatusBar(self.statusBar)
        self.toolBar = QtGui.QToolBar(MainWindow)
        self.toolBar.setObjectName(_fromUtf8("toolBar"))
        MainWindow.addToolBar(QtCore.Qt.TopToolBarArea, self.toolBar)
        self.action_Open = QtGui.QAction(MainWindow)
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(_fromUtf8(":/icons/icons/fileOpen.png")), QtGui.QIcon.Normal, QtGui.QIcon.On)
        self.action_Open.setIcon(icon1)
        self.action_Open.setObjectName(_fromUtf8("action_Open"))
        self.action_Save = QtGui.QAction(MainWindow)
        self.action_Save.setObjectName(_fromUtf8("action_Save"))
        self.action_Save_As = QtGui.QAction(MainWindow)
        self.action_Save_As.setObjectName(_fromUtf8("action_Save_As"))
        self.action_Exit = QtGui.QAction(MainWindow)
        self.action_Exit.setObjectName(_fromUtf8("action_Exit"))
        self.action_About = QtGui.QAction(MainWindow)
        self.action_About.setObjectName(_fromUtf8("action_About"))
        self.action_New = QtGui.QAction(MainWindow)
        self.action_New.setObjectName(_fromUtf8("action_New"))
        self.action_Cut = QtGui.QAction(MainWindow)
        self.action_Cut.setObjectName(_fromUtf8("action_Cut"))
        self.action_Copy = QtGui.QAction(MainWindow)
        self.action_Copy.setObjectName(_fromUtf8("action_Copy"))
        self.action_Paste = QtGui.QAction(MainWindow)
        self.action_Paste.setObjectName(_fromUtf8("action_Paste"))
        self.action_Undo = QtGui.QAction(MainWindow)
        self.action_Undo.setObjectName(_fromUtf8("action_Undo"))
        self.action_Redo = QtGui.QAction(MainWindow)
        self.action_Redo.setObjectName(_fromUtf8("action_Redo"))
        self.action_Run = QtGui.QAction(MainWindow)
        self.action_Run.setEnabled(False)
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(_fromUtf8(":/icons/icons/run.png")), QtGui.QIcon.Normal, QtGui.QIcon.On)
        self.action_Run.setIcon(icon2)
        self.action_Run.setObjectName(_fromUtf8("action_Run"))
        self.action_StepInto = QtGui.QAction(MainWindow)
        self.action_StepInto.setEnabled(False)
        icon3 = QtGui.QIcon()
        icon3.addPixmap(QtGui.QPixmap(_fromUtf8(":/icons/icons/step_into.png")), QtGui.QIcon.Normal, QtGui.QIcon.On)
        self.action_StepInto.setIcon(icon3)
        self.action_StepInto.setObjectName(_fromUtf8("action_StepInto"))
        self.action_StepOver = QtGui.QAction(MainWindow)
        self.action_StepOver.setEnabled(False)
        icon4 = QtGui.QIcon()
        icon4.addPixmap(QtGui.QPixmap(_fromUtf8(":/icons/icons/step_over.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.action_StepOver.setIcon(icon4)
        self.action_StepOver.setObjectName(_fromUtf8("action_StepOver"))
        self.action_Continue = QtGui.QAction(MainWindow)
        self.action_Continue.setObjectName(_fromUtf8("action_Continue"))
        self.action_Run_Config = QtGui.QAction(MainWindow)
        self.action_Run_Config.setObjectName(_fromUtf8("action_Run_Config"))
        self.menu_File.addAction(self.action_Open)
        self.menu_File.addAction(self.action_Exit)
        self.menu_Help.addAction(self.action_About)
        self.menu_Edit.addAction(self.action_Undo)
        self.menu_Edit.addAction(self.action_Redo)
        self.menu_Edit.addAction(self.action_Cut)
        self.menu_Edit.addAction(self.action_Copy)
        self.menu_Edit.addAction(self.action_Paste)
        self.menuRun.addAction(self.action_Run_Config)
        self.menuRun.addAction(self.action_Run)
        self.menuRun.addAction(self.action_StepInto)
        self.menuRun.addAction(self.action_StepOver)
        self.menuRun.addAction(self.action_Continue)
        self.menuBar.addAction(self.menu_File.menuAction())
        self.menuBar.addAction(self.menu_Edit.menuAction())
        self.menuBar.addAction(self.menuRun.menuAction())
        self.menuBar.addAction(self.menu_Help.menuAction())
        self.toolBar.addAction(self.action_Open)
        self.toolBar.addAction(self.action_Run)
        self.toolBar.addAction(self.action_StepOver)
        self.toolBar.addAction(self.action_StepInto)

        self.retranslateUi(MainWindow)
        self.tabCodeEditor.setCurrentIndex(-1)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(_translate("MainWindow", "lll", None))
        self.menu_File.setTitle(_translate("MainWindow", "&File", None))
        self.menu_Help.setTitle(_translate("MainWindow", "&Help", None))
        self.menu_Edit.setTitle(_translate("MainWindow", "&Edit", None))
        self.menuRun.setTitle(_translate("MainWindow", "&Run", None))
        self.toolBar.setWindowTitle(_translate("MainWindow", "toolBar", None))
        self.action_Open.setText(_translate("MainWindow", "&Open...", None))
        self.action_Save.setText(_translate("MainWindow", "&Save", None))
        self.action_Save_As.setText(_translate("MainWindow", "Save &As", None))
        self.action_Exit.setText(_translate("MainWindow", "E&xit", None))
        self.action_About.setText(_translate("MainWindow", "&About", None))
        self.action_New.setText(_translate("MainWindow", "&New", None))
        self.action_Cut.setText(_translate("MainWindow", "Cu&t", None))
        self.action_Copy.setText(_translate("MainWindow", "&Copy", None))
        self.action_Paste.setText(_translate("MainWindow", "&Paste", None))
        self.action_Undo.setText(_translate("MainWindow", "&Undo", None))
        self.action_Redo.setText(_translate("MainWindow", "&Redo", None))
        self.action_Run.setText(_translate("MainWindow", "Run/Rerun", None))
        self.action_Run.setIconText(_translate("MainWindow", "Run/Continue", None))
        self.action_Run.setToolTip(_translate("MainWindow", "Run/Continue", None))
        self.action_StepInto.setText(_translate("MainWindow", "Step Into", None))
        self.action_StepOver.setText(_translate("MainWindow", "Step Over", None))
        self.action_StepOver.setShortcut(_translate("MainWindow", "F2", None))
        self.action_Continue.setText(_translate("MainWindow", "Continue", None))
        self.action_Run_Config.setText(_translate("MainWindow", "Run Config ...", None))

from ui.codeEditor.commandwindow import CommandWindow
import resources_rc
