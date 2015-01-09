#!/bin/python2
"""Main controller of LLL
"""
import sys, os, inspect, re, ConfigParser, logging
from PyQt4.QtCore import QThread, pyqtSignal
from PyQt4 import QtGui, QtCore, Qt
from PyQt4.QtGui import QMessageBox, QAction
from ptyview import PtyView
import clang.cindex

def initialize():
    """ read config file and initialize sys path etc."""
    config = ConfigParser.RawConfigParser()
    curr_path = os.path.split(inspect.getfile(inspect.currentframe()))[0]
    cmd_folder = os.path.realpath(os.path.abspath(curr_path))

    #search config file in: program's dir/lll.ini, ~/.lll.ini
    config.read([cmd_folder + '/lll.ini', os.path.expanduser('~/.lll.ini')])
    logging_level = logging.INFO
    if config.has_section('common'):
        clang_lib_path = config.get('common', 'clang_lib_path')
        lldb_path = config.get('common', 'lldb_path')
        logging_level = config.get('common', 'logging_level')
        sys.path.append(lldb_path)
        clang.cindex.Config.set_library_path(clang_lib_path)
    logging.basicConfig(level=logging_level)

initialize()
import lldb
from lldb import SBTarget, SBProcess, SBEvent, \
                 SBStream, SBBreakpoint
from debugger import Debugger
from ui.UIMain import Ui_MainWindow
from ui.codeEditor import CodeEditor
from ui.UIRunConfigWindow import RunConfigWindow
from ui.About import AboutDialog

class MainWindow(QtGui.QMainWindow):
    """ Main window of the debugger"""
    def __init__(self):
        QtGui.QMainWindow.__init__(self)
        self.init_ui()
        self.cfg_window = RunConfigWindow()
        self.about_dialog = AboutDialog()
        self.pty_stdout = PtyView(self.ui.commander)
        stdout_path = self.pty_stdout.get_file_path()

        self.debugger = Debugger(stdout_path, stdout_path, self.cfg_window.working_dir)
        self.last_highlighted_editor = None
        self.my_listener = MyListeningThread(self.debugger.dbg)
        self.my_listener.FocusLine.connect(self.do_focus_line)
        self.my_listener.StateChanged.connect(self.on_state_changed)
        self.debugger.listener = self.my_listener
        self.my_listener.start()

        self.opened_files = {}

        args = Qt.qApp.arguments()
        self.cfg_window.working_dir = os.getcwd()
        if len(args) > 1:
            self.do_exe_file_open(args[1])
        if len(args) > 2:
            self.cfg_window.arglist = [str(x) for x in args[2:]]

    def init_ui(self):
        """initialize UI"""
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.tabCodeEditor.clear()
        self.ui.tabCodeEditor.setTabsClosable(True)
        self.ui.tabCodeEditor.setTabShape(QtGui.QTabWidget.Triangular)
        self.action_Frames = self.ui.frame_dock.toggleViewAction()
        self.ui.menuView.addAction(self.action_Frames)
        self.action_Frames.setCheckable(True)
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap((":/icons/icons/frame.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.action_Frames.setIcon(icon1)

        layout = QtGui.QVBoxLayout()
        #scroll_area = QtGui.QScrollArea()
        #scroll_area.setWidget(self.ui.frame_viewer)
        layout.addWidget(self.ui.frame_viewer)
        #layout.addWidget(scroll_area)
        self.ui.dockWidgetContents.setLayout(layout)
        #self.ui.frame_viewer.headerHidden = True
        #self.ui.frame_viewer.header().hide()
        self.ui.frame_viewer.expandToDepth(1)

        self.connect(self.ui.action_Open, QtCore.SIGNAL('triggered()'), self.do_exe_file_open)
        self.connect(self.ui.action_Run, QtCore.SIGNAL('triggered()'), self.do_run)
        self.connect(self.ui.action_StepOver, QtCore.SIGNAL('triggered()'), self.do_step_over)
        self.connect(self.ui.action_StepInto, QtCore.SIGNAL('triggered()'), self.do_step_into)
        self.connect(self.ui.action_StepOut, QtCore.SIGNAL('triggered()'), self.do_step_out)
        self.connect(self.ui.action_Frames, QtCore.SIGNAL('triggered()'), self.do_frames)
        self.connect(self.ui.frame_viewer, QtCore.SIGNAL('activated(const QModelIndex&)'), self.select_frame)

        self.ui.action_Exit.triggered.connect(Qt.qApp.quit)
        self.ui.commander.commandEntered.connect(self.do_command)
        self.connect(self.ui.action_Run_Config, QtCore.SIGNAL('triggered()'), self.do_config)
        self.connect(self.ui.action_About, QtCore.SIGNAL('triggered()'), self.show_about)

    def closeEvent(self, event):
        """when close event is triggered"""
        reply = QtGui.QMessageBox.question(self, 'Message', 'Quit?', \
                                           QMessageBox.Yes, QMessageBox.No)
        if reply == QtGui.QMessageBox.Yes:
            self.my_listener.quit()
            event.accept()
        else:
            event.ignore()

    def show_about(self):
        """ show "About" window"""
        self.about_dialog.show()

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
        main_file, line = self.debugger.open_file(exe_filename)
        if main_file is not None:
            print("src:%s:%s") %(main_file, main_file.fullpath)
            self.open_src_file(main_file.fullpath, line)
            self.ui.action_Run.setEnabled(True)
            self.my_listener.add_target_broadcaster(self.debugger.target.GetBroadcaster())
        elif line == 0:
            logging.info('cannot find entry function')
        else:
            logging.info('error opening executable: %s', exe_filename)

    def do_focus_line(self, filename, line_no):
        """ slot for focusing line event"""
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
            editor.focus_line(line_no)
            self.ui.tabCodeEditor.setCurrentWidget(editor)

        self.last_highlighted_editor = editor

    def select_frame(self, idx):
        print("idx is %s") (str(idx))
    def update_frame_info(self):
        if not self.action_Frames.isChecked():
            return
        process = self.debugger.curr_process
        if process is None or not process.is_alive:
            return

        frame_data = QtGui.QStandardItemModel()
        frame_data.setColumnCount(2)
        frame_data.setHorizontalHeaderLabels(['',''])
        root = frame_data.invisibleRootItem()
        #if process.num_of_threads == 1:
        for thread in process:
            thread_name = thread.GetName()
            if not thread_name:
                thread_name = '[No Thread]'
            thread_row = QtGui.QStandardItem(thread_name)
            thread_row.setEditable(False)
            root.appendRow([thread_row, None])
            for frame in reversed(thread.frames):
                frame_idx = '#%d: ' % frame.idx
                frame_info =''
                if frame.name:
                    frame_idx += frame.name
                    args = ','.join(map(str, frame.args))
                    frame_info += ' (%s)' % args

                line = frame.line_entry
                if line:
                    file_info = ' at %s:%d' % (str(line.GetFileSpec()), line.GetLine())
                    frame_info += file_info
                else:
                    frame_info += str(frame.module.GetFileSpec())
                if frame.is_inlined:
                    frame_info += ' (inlined)'
                print("Frame %s") %(str(frame))
                col_idx = QtGui.QStandardItem(frame_idx)
                col_idx.setEditable(False)
                col_info = QtGui.QStandardItem(frame_info)
                col_info.setEditable(False)
                thread_row.appendRow([col_idx, col_info])

        self.ui.frame_viewer.setModel(frame_data)
        self.ui.frame_viewer.resizeColumnToContents(1)
        self.ui.frame_viewer.setAutoScroll(True)
        #self.ui.frame_viewer.resizeColumnToContents(1)
        #.ui.frame_viewer.resizeColumnToContents(2)
        self.ui.frame_viewer.expandToDepth(1)

    def on_state_changed(self, state):
        """slot for state change event"""
        process = self.debugger.curr_process
        steppable = process is not None and process.is_alive and state != lldb.eStateRunning
        if process is not None:
            self.ui.action_StepOver.setEnabled(steppable)
            self.ui.action_StepInto.setEnabled(steppable)
            self.ui.action_StepOut.setEnabled(steppable)
        self.ui.action_Run.setEnabled(state!=lldb.eStateRunning)

        if state == lldb.eStateExited or state == lldb.eStateCrashed \
           or state == lldb.eStateSuspended:
            self.do_focus_line(None, -1)
        if state == lldb.eStateExited:
            if process is not None:
                logging.info('process exited: [%d]:%s', process.GetExitStatus(),
                             process.GetExitDescription())
            return
        self.update_frame_info()
        if state == lldb.eStateCrashed:
            logging.info('crashed')

    def open_src_file(self, src_filename, line=0):
        """show the source file in editor"""
        if not os.path.isfile(src_filename) or not os.access(src_filename, os.R_OK):
            #TODO: show error message
            return
        if src_filename in self.opened_files:
            return

        editor = CodeEditor()
        self.ui.tabCodeEditor.addTab(editor, os.path.basename(src_filename))
        editor.open_source_file(src_filename)
        self.opened_files[str(src_filename)] = editor
        editor.line_number_area.BPToggled.connect(self.toggle_breakpoint)
        if line > 0:
            self.do_focus_line(src_filename, line)

    def toggle_breakpoint(self, line_no):
        """ control the bp toggling"""
        sender = self.sender()
        filename = sender.filename
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

    def do_step_out(self):
        """ on step out of frame"""
        self.debugger.step_out()

    def do_frames(self):
        if self.ui.action_Frames.isChecked():
            pass
        else:
            pass

class MyListeningThread(QThread):
    """Listening events"""
    FocusLine = pyqtSignal(str, int, name='FocusLine')
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
                    logging.debug('process stopped')

                    for thread in process:
                        reason = thread.GetStopReason()
                        if reason == lldb.eStopReasonBreakpoint:
                            #assert(thread.GetStopReasonDataCount() == 2)
                            bp_id = thread.GetStopReasonDataAtIndex(0)
                            logging.debug('bp_id:%s', bp_id)
                            bp = target.FindBreakpointByID(int(bp_id))
                            if bp.GetNumLocations() == 1:
                                bp_loc = bp.GetLocationAtIndex(0)
                            else:
                                bp_loc_id = thread.GetStopReasonDataAtIndex(1)
                                bp_loc = bp.FindLocationByID(bp_loc_id)
                            line_entry = bp_loc.GetAddress().GetLineEntry()
                            file_spec = line_entry.GetFileSpec()
                            filename = file_spec.fullpath
                            line_no = line_entry.GetLine()
                            logging.debug('stopped @ %s:%d', filename, line_no)
                            if filename is not None:
                                self.FocusLine.emit(filename, int(line_no))
                            else:
                                self.FocusLine.emit(None, -1)
                        elif reason == lldb.eStopReasonWatchpoint or \
                             reason == lldb.eStopReasonPlanComplete:
                            frame = thread.GetFrameAtIndex(0)
                            line_entry = frame.GetLineEntry()
                            file_spec = line_entry.GetFileSpec()
                            filename = file_spec.fullpath
                            line_no = line_entry.GetLine()
                            logging.debug('stopped @ %s:%d', filename, line_no)
                            if filename is not None:
                                self.FocusLine.emit(filename, int(line_no))
                            break
                        elif reason == lldb.eStopReasonThreadExiting:
                            logging.debug('thread exit')
                        elif reason == lldb.eStopReasonSignal or \
                             reason == lldb.eStopReasonException:
                            logging.debug('signal/exception %x', thread.GetStopReasonDataAtIndex(0))

                        elif reason == lldb.eStopReasonExec:
                            logging.debug('re-run')
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
    """ entry function"""
    #QtGui.QApplication.setGraphicsSystem("native")
    app = QtGui.QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
