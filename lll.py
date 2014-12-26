#!/bin/python2
"""Main controller of LLL
"""
import sys, os, inspect, re, ConfigParser, logging
from PyQt4.QtCore import QThread, pyqtSignal, pyqtSlot
from PyQt4 import QtGui, QtCore, Qt
from PyQt4.QtGui import QMessageBox
from ptyview import PtyView
import clang.cindex

def main():
    """ entry function"""
    curr_path = os.path.split(inspect.getfile(inspect.currentframe()))[0]
    cmd_folder = os.path.realpath(os.path.abspath(curr_path))
    if cmd_folder not in sys.path:
        sys.path.insert(0, cmd_folder)

    config = ConfigParser.RawConfigParser()
    config.read('lll.ini')
    lldb_path = '../llvm/lib/python2.7/site-packages'
    logging_level = logging.INFO
    if config.has_section('common'):
        clang_lib_path = config.get('common', 'clang_lib_path')
        lldb_path = config.get('common', 'lldb_path')
        logging_level = config.get('common', 'logging_level')
    sys.path.append(lldb_path)
    clang.cindex.Config.set_library_path(clang_lib_path)
    logging.basicConfig(level=logging_level)
    app = QtGui.QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())


import lldb
from lldb import SBTarget, SBProcess, SBEvent, \
                 SBStream, SBBreakpoint
from ui.UIMain import Ui_MainWindow
from ui.codeEditor import CodeEditor
from ui.UIRunConfigWindow import RunConfigWindow
from debugger import Debugger

class MainWindow(QtGui.QMainWindow):
    """ Main window of the debugger"""
    def __init__(self):
        QtGui.QMainWindow.__init__(self)
        self.init_ui()
        self.cfg_window = RunConfigWindow()
        self.pty_stdout = PtyView(self.ui.commander)
        stdout_path = self.pty_stdout.get_file_path()

        self.debugger = Debugger(stdout_path, stdout_path, self.cfg_window.workDir)
        self.last_highlighted_editor = None
        self.my_listener = MyListeningThread(self.debugger.dbg)
        self.my_listener.FocuseLine.connect(self.do_focuse_line)
        self.my_listener.StateChanged.connect(self.on_state_changed)
        self.debugger.listener = self.my_listener
        self.my_listener.start()

        self.opened_files = {}

        args = Qt.qApp.arguments()
        self.cfg_window.setWorkingDir(os.getcwd())
        if len(args) > 1:
            self.do_exe_file_open(args[1])
        if len(args) > 2:
            self.cfg_window.setArgStr(' '.join([str(x) for x in args[2:]]))

    def init_ui(self):
        """initialize UI"""
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.tabCodeEditor.clear()
        self.ui.tabCodeEditor.setTabsClosable(True)
        self.ui.tabCodeEditor.setTabShape(QtGui.QTabWidget.Triangular)
        self.connect(self.ui.action_Open, QtCore.SIGNAL('triggered()'), self.do_exe_file_open)
        self.connect(self.ui.action_Run, QtCore.SIGNAL('triggered()'), self.do_run)
        self.connect(self.ui.action_StepOver, QtCore.SIGNAL('triggered()'), self.do_step_over)
        self.connect(self.ui.action_StepInto, QtCore.SIGNAL('triggered()'), self.do_step_into)
        self.ui.commander.commandEntered.connect(self.do_command)
        self.connect(self.ui.action_Run_Config, QtCore.SIGNAL('triggered()'), self.do_config)

    def closeEvent(self, event):
        """when close event is triggered"""
        reply = QtGui.QMessageBox.question(self, 'Message', 'Quit?', \
                                           QMessageBox.Yes, QMessageBox.No)
        if reply == QtGui.QMessageBox.Yes:
            self.my_listener.quit()
            event.accept()
        else:
            event.ignore()

    def do_config(self):
        """show run-config window"""
        self.cfg_window.show()

    def do_exe_file_open(self, exe_filename=None):
        """open executable"""
        if not exe_filename:
            exe_filename = QtGui.QFileDialog.getOpenFileName(self, \
                self.tr('Open Executable'), \
                '', self.tr('Executable Files (*)'))
        if exe_filename is None:
            return
        main_file = self.debugger.open_file(exe_filename)
        if main_file is not None:
            self.open_src_file(main_file.fullpath)
            self.ui.action_Run.setEnabled(True)
            self.my_listener.add_target_broadcaster(self.debugger.target.GetBroadcaster())
        else:
            logging.info('error opening executable: %s', exe_filename)

    @pyqtSlot(str, int, name='on_eventListener_FocuseLine')
    def do_focuse_line(self, filename, line_no):
        """ slot for focuing line event"""
        if filename is None:
            editor = None
        else:
            filename = str(filename)
            logging.debug('Focusing [%s]:%d', filename, line_no)
            if filename not in self.opened_files:
                self.open_src_file(filename)
            editor = self.opened_files[filename]

        if self.last_highlighted_editor != editor:
            if self.last_highlighted_editor is not None:
                self.last_highlighted_editor.setExtraSelections([])

        if editor is not None:
            editor.focuseLine(line_no)
            self.ui.tabCodeEditor.setCurrentWidget(editor)

        self.last_highlighted_editor = editor

    def on_state_changed(self, state):
        """slot for state change event"""
        if state == lldb.eStateExited or state == lldb.eStateCrashed \
           or state == lldb.eStateSuspended:
            self.do_focuse_line(None, -1)

        process = self.debugger.curr_process
        if process is not None:
            self.ui.action_StepOver.setEnabled(process.is_alive)
            self.ui.action_StepInto.setEnabled(process.is_alive)

    def open_src_file(self, src_filename):
        """show the source file in editor"""
        if not os.path.isfile(src_filename) or not os.access(src_filename, os.R_OK):
            #TODO: show error message
            return
        if src_filename in self.opened_files:
            return

        editor = CodeEditor()
        self.ui.tabCodeEditor.addTab(editor, os.path.basename(src_filename))
        editor.openSourceFile(src_filename)
        self.opened_files[str(src_filename)] = editor
        editor.lineNumberArea.BPToggled.connect(self.toggle_breakpoint)

    def toggle_breakpoint(self, line_no):
        """ control the bp toggling"""
        sender = self.sender()
        filename = sender.fileName
        sender.breakpoints = self.debugger.toggle_breakpoint(filename, line_no)
        sender.repaint()

    def do_command(self, cmd):
        """ on command entered"""
        msg = self.debugger.execute(cmd)
        self.ui.commander.append(msg)

    def do_run(self, args=None, from_cmd=False):
        """ on run command entered"""
        process = self.debugger.run(args, from_cmd, self.cfg_window.arglist)
        if process is not None:
            self.my_listener.add_process_broadcaster(process.GetBroadcaster())

    def do_step_over(self):
        """ on step over clicked"""
        self.debugger.next(True)

    def do_step_into(self):
        """ on step into clicked"""
        self.debugger.next(False)

class MyListeningThread(QThread):
    """Listening events"""
    FocuseLine = pyqtSignal(str, int, name='FocuseLine')
    StateChanged = pyqtSignal(int, name='StateChanged')

    def __init__(self, dbg):
        QThread.__init__(self)
        self.dbg = dbg
        self.sb_listener = dbg.GetListener()
        #self.stopped = False
        self.process_broadcaster = None
        self.target_broadcaster = None

    def add_target_broadcaster(self, broadcaster):
        """ add broadcaster for targget events"""
        mask = SBTarget.eBroadcastBitBreakpointChanged or SBTarget.eBroadcastBitModulesLoaded or \
               SBTarget.eBroadcastBitModulesUnloaded or SBTarget.eBroadcastBitSymbolsLoaded or \
               SBTarget.eBroadcastBitWatchpointChanged
        self.target_broadcaster = broadcaster
        broadcaster.AddListener(self.sb_listener, mask)
        self.sb_listener.StartListeningForEvents(broadcaster, mask)

    def add_process_broadcaster(self, broadcaster):
        """ add broadcaster for process events"""
        mask = SBProcess.eBroadcastBitStateChanged or \
               SBProcess.eBroadcastBitSTDERR or \
               SBProcess.eBroadcastBitSTDOUT or \
               lldb.SBProcess.eBroadcastBitInterrupt
        broadcaster.AddListener(self.sb_listener, SBProcess.eBroadcastBitStateChanged)
        self.sb_listener.StartListeningForEvents(broadcaster, mask)
        self.process_broadcaster = broadcaster

    def run(self):
        """ listerning loop"""
        event = SBEvent()
        ss = SBStream()
        while self.sb_listener.IsValid():
            self.sb_listener.WaitForEvent(1, event)
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
                                    bp_filename = matched.group(1)
                                    bp_line_no = int(matched.group(2))
                                    self.FocuseLine.emit(bp_filename, int(bp_line_no))
                                logging.debug('stopped @ %s', desc)
                            else:
                                bp_loc_id = thread.GetStopReasonDataAtIndex(1)
                                bp_loc = bp.FindLocationByID(bp_loc_id)
                                line_entry = bp_loc.GetAddress().GetLineEntry()
                                file_spec = line_entry.GetFileSpec()
                                filename = file_spec.fullpath
                                line_no = line_entry.GetLine()
                                logging.debug('stopped @ %s:%d', filename, line_no)
                                if filename is not None:
                                    self.FocuseLine.emit(filename.fullpath, int(line_no))
                                else:
                                    self.FocuseLine.emit(None, -1)
                        elif reason == lldb.eStopReasonWatchpoint or \
                             reason == lldb.eStopReasonPlanComplete:
                            frame = thread.GetFrameAtIndex(0)
                            line_entry = frame.GetLineEntry()
                            file_spec = line_entry.GetFileSpec()
                            filename = file_spec.fullpath
                            line_no = line_entry.GetLine()
                            logging.debug('stopped @ %s:%d', filename, line_no)
                            if filename is not None:
                                self.FocuseLine.emit(filename, int(line_no))
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

if __name__ == '__main__':
    main()
