#!/bin/python2
"""Main controller of LLL
"""
import sys, os, inspect, re, ConfigParser, logging
from PyQt4 import QtGui, QtCore, Qt
from PyQt4.QtCore import QThread, pyqtSignal, pyqtSlot
from PyQt4.QtGui import QMessageBox
from ptyview import PtyView
import clang.cindex

currPath = os.path.split(inspect.getfile(inspect.currentframe()))[0]
cmd_folder = os.path.realpath(os.path.abspath(currPath))
if cmd_folder not in sys.path:
    sys.path.insert(0, cmd_folder)

cf = ConfigParser.RawConfigParser()
cf.read('lll.ini')
lldbPath = '../llvm/lib/python2.7/site-packages'
loggingLevel = logging.INFO
if cf.has_section('common'):
    clangLibPath = cf.get('common', 'clang_lib_path')
    lldbPath = cf.get('common', 'lldb_path')
    loggingLevel = cf.get('common', 'logging_level')
sys.path.append(lldbPath)
clang.cindex.Config.set_library_path(clangLibPath)
logging.basicConfig(level=loggingLevel)


from lldb import SBTarget, SBProcess, SBDebugger, SBEvent, \
                 SBCommandReturnObject, SBError, SBStream, SBBreakpoint
from ui.UIMain import Ui_MainWindow
from ui.codeEditor import CodeEditor
from ui.UIRunConfigWindow import RunConfigWindow
from debugger import Debugger

class MainWindow(QtGui.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.initUI()
        self.runCfgWindow = RunConfigWindow()
        self.pty_stdout = PtyView(self.ui.commander)
        stdoutPath = self.pty_stdout.get_file_path()

        self.debugger = Debugger(stdoutPath, stdoutPath, self.runCfgWindow.workDir)
        self.ci = self.debugger.dbg.GetCommandInterpreter()

        self.lastArgs = None
        self.lastHighlightedEditor = None
        self.myListener = MyListeningThread(self.debugger.dbg)
        self.myListener.FocuseLine.connect(self.doFocuseLine) #TODO
        self.myListener.StateChanged.connect(self.onStateChanged)
        self.debugger.listener = self.myListener
        self.myListener.start()

        self.openedFiles = {}

        args = Qt.qApp.arguments()
        self.runCfgWindow.setWorkingDir(os.getcwd())
        if len(args) > 1:
            self.doExeFileOpen(args[1])
        if len(args) > 2:
            self.runCfgWindow.setArgStr(' '.join(map(str, args[2:])))

    def initUI(self):
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.tabCodeEditor.clear()
        self.ui.tabCodeEditor.setTabsClosable(True)
        self.ui.tabCodeEditor.setTabShape(QtGui.QTabWidget.Triangular)
        self.connect(self.ui.action_Open, QtCore.SIGNAL('triggered()'), self.doExeFileOpen)
        self.connect(self.ui.action_Run, QtCore.SIGNAL('triggered()'), self.doRun)
        self.connect(self.ui.action_StepOver, QtCore.SIGNAL('triggered()'), self.doStepOver)
        self.connect(self.ui.action_StepInto, QtCore.SIGNAL('triggered()'), self.doStepInto)
        self.ui.commander.commandEntered.connect(self.doCommand)
        self.connect(self.ui.action_Run_Config, QtCore.SIGNAL('triggered()'), self.doRunConfig)

    def log(self, msg):
        self.statusBar().showMessage(msg)

    def closeEvent(self, event):
        reply = QtGui.QMessageBox.question(self, 'Message', 'Quit?', \
                                           QMessageBox.Yes, QMessageBox.No)
        if reply == QtGui.QMessageBox.Yes:
            self.myListener.quit()
            event.accept()
        else:
            event.ignore()

    def doRunConfig(self):
        self.runCfgWindow.show()

    def doExeFileOpen(self, exeFileName=None):
        if not exeFileName:
            exeFileName = QtGui.QFileDialog.getOpenFileName(self, \
                self.tr('Open Executable'), \
                '', self.tr('Executable Files (*)'))
        if exeFileName is None:
            return
        mainFile = self.debugger.open_file(exeFileName)
        if mainFile is not None:
            self.openSrcFile(mainFile.fullpath)
            self.ui.action_Run.setEnabled(True)
            self.myListener.addTargetBroadcaster(self.debugger.target.GetBroadcaster())
        else:
            logging.info('error opening executable: %s', exeFileName)

    @pyqtSlot(str, int, name='on_eventListener_FocuseLine')
    def doFocuseLine(self, fileName, lineNo):
        if fileName is None:
            editor = None
        else:
            fileName = str(fileName)
            logging.debug('Focusing [%s]:%d', fileName, lineNo)
            if fileName not in self.openedFiles:
                self.openSrcFile(fileName)
            editor = self.openedFiles[fileName]

        if self.lastHighlightedEditor != editor:
            if self.lastHighlightedEditor is not None:
                self.lastHighlightedEditor.setExtraSelections([])

        if editor is not None:
            editor.focuseLine(lineNo)
            self.ui.tabCodeEditor.setCurrentWidget(editor)

        self.lastHighlightedEditor = editor

    def onStateChanged(self, state):
        if state == lldb.eStateExited or state == lldb.eStateCrashed \
           or state == lldb.eStateSuspended:
            self.doFocuseLine(None, -1)

        process = self.debugger.curr_process
        if process is not None:
            self.ui.action_StepOver.setEnabled(process.is_alive)
            self.ui.action_StepInto.setEnabled(process.is_alive)

    def openSrcFile(self, srcFilePath):
        if not os.path.isfile(srcFilePath) or not os.access(srcFilePath, os.R_OK):
            #TODO: show error message
            return
        if srcFilePath in self.openedFiles:
            return

        myText = CodeEditor()
        self.ui.tabCodeEditor.addTab(myText, os.path.basename(srcFilePath))
        myText.openSourceFile(srcFilePath)
        self.openedFiles[str(srcFilePath)] = myText
        myText.lineNumberArea.BPToggled.connect(self.toggle_breakpoint)

    def toggle_breakpoint(self, lineNo):
        sender = self.sender()
        fileName = sender.fileName
        sender.breakpoints = self.debugger.toggle_breakpoint(fileName, lineNo)
        sender.repaint()

    def doCommand(self, cmd):
        msg = self.debugger.execute(cmd)
        self.ui.commander.append(msg)

    def doRun(self, args=None, fromCmd=False):
        process = self.debugger.run(args, fromCmd, self.runCfgWindow.arglist)
        if process is not None:
            self.myListener.addProcessBroadcaster(process.GetBroadcaster())

    def doStepOver(self):
        self.debugger.next(True)

    def doStepInto(self):
        self.debugger.next(False)

class MyListeningThread(QThread):
    FocuseLine = pyqtSignal(str, int, name='FocuseLine')
    StateChanged = pyqtSignal(int, name='StateChanged')

    def __init__(self, dbg):
        QThread.__init__(self)
        self.dbg = dbg
        self.dbgListener = dbg.GetListener()
        #self.stopped = False
        self.processBroadcaster = None
        self.targetBroadcaster = None

    def addTargetBroadcaster(self, broadcaster):
        mask = SBTarget.eBroadcastBitBreakpointChanged or SBTarget.eBroadcastBitModulesLoaded or \
               SBTarget.eBroadcastBitModulesUnloaded or SBTarget.eBroadcastBitSymbolIsLoaded or \
               SBTarget.eBroadcastBitWatchpointChanged
        self.targetBroadcaster = broadcaster
        broadcaster.AddListener(self.dbgListener, mask)
        self.dbgListener.StartListeningForEvents(broadcaster, mask)

    def addProcessBroadcaster(self, broadcaster):
        mask = SBProcess.eBroadcastBitStateChanged or \
               SBProcess.eBroadcastBitSTDERR or \
               SBProcess.eBroadcastBitSTDOUT or \
               lldb.SBProcess.eBroadcastBitInterrupt
        broadcaster.AddListener(self.dbgListener, SBProcess.eBroadcastBitStateChanged)
        self.dbgListener.StartListeningForEvents(broadcaster, mask)
        self.processBroadcaster = broadcaster

    def run(self):
        event = SBEvent()
        ss = SBStream()
        while self.dbgListener.IsValid():
            self.dbgListener.WaitForEvent(1, event)
            if not event.IsValid():
                event.Clear()
                continue

            #Check for target events
            target = self.dbg.GetSelectedTarget()
            state = None
            if not target.IsValid():
                continue
            #Handle BP events
            if SBBreakpoint.EventIsBreakpointEvent(event):
                bp = SBBreakpoint.GetBreakpointFromEvent(event)
                logging.debug('bp changed %s', str(bp))
            #Handle Process events
            if SBProcess.EventIsProcessEvent(event):
                process = SBProcess.GetProcessFromEvent(event)
                state = process.GetState()
                if state == lldb.eStateLaunching:
                    logging.debug('launching')
                elif state == lldb.eStateRunning:
                    logging.debug('running')
                elif state == lldb.eStateStopped:
                    logging.debug('stopped')

                    for thread in process:
                        reason = thread.GetStopReason()
                        if reason == lldb.eStopReasonBreakpoint:
                            #assert(thread.GetStopReasonDataCount() == 2)
                            bp_id = thread.GetStopReasonDataAtIndex(0)
                            logging.debug('bp_id:%s', bp_id)
                            bp = target.FindBreakpointByID(int(bp_id))
                            if bp.GetNumLocations() == 1:
                                ss = SBStream()
                                ss.Clear()
                                bp.GetDescription(ss)
                                desc = ss.GetData()
                                matched = re.search('file = \'(.*)\', line = (.*),', desc)
                                if matched:
                                    bpFileName = matched.group(1)
                                    bpLineNo = int(matched.group(2))
                                    self.FocuseLine.emit(bpFileName, int(bpLineNo))
                                logging.debug('stopped @ %s', desc)
                            else:
                                bp_loc_id = thread.GetStopReasonDataAtIndex(1)
                                bp_loc = bp.FindLocationByID(bp_loc_id)
                                lineEntry = bp_loc.GetAddress().GetLineEntry()
                                fileSpec = lineEntry.GetFileSpec()
                                fileName = fileSpec.fullpath
                                lineNo = lineEntry.GetLine()
                                logging.debug('stopped @ %s:%d', fileName, lineNo)
                                if fileName is not None:
                                    self.FocuseLine.emit(fileName.fullpath, int(lineNo))
                                else:
                                    self.FocuseLine.emit(None, -1)
                        elif reason == lldb.eStopReasonWatchpoint or \
                             reason == lldb.eStopReasonPlanComplete:
                            frame = thread.GetFrameAtIndex(0)
                            lineEntry = frame.GetLineEntry()
                            fileSpec = lineEntry.GetFileSpec()
                            fileName = fileSpec.fullpath
                            lineNo = lineEntry.GetLine()
                            logging.debug('stopped @ %s:%d', fileName, lineNo)
                            if fileName is not None:
                                self.FocuseLine.emit(fileName, int(lineNo))
                            break
                        elif reason == lldb.eStopReasonThreadExiting:
                            logging.debug('thread exit')
                        elif reason == lldb.eStopReasonSignal or \
                             reason == lldb.eStopReasonException:
                            logging.debug('signal/exception %x', thread.GetStopReasonDataAtIndex(0))

                        elif reason == lldb.eStopReasonExec:
                            logging.debug('re-run')

                elif state == lldb.eStateExited:
                    logging.debug('exited')
                elif state == lldb.eStateCrashed:
                    logging.debug('crashed')
                elif state == lldb.eStateSuspended:
                    logging.debug('suspended')
                elif state == lldb.eStateStepping:
                    logging.debug('stepping')
                else:
                    logging.debug('state is %s', state)
            if state is not None:
                self.StateChanged.emit(state)
            event.GetDescription(ss)
            logging.debug('Event desc: %s', ss.GetData())
            ss.Clear()
            event.Clear()

def main():
    app = QtGui.QApplication(sys.argv)
    mainW = MainWindow()
    mainW.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
