#!/bin/python2
"""Main controller of LLL
"""
import sys, os, inspect, ConfigParser
import logging
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
from ui.UIFrameInfoWidget import Ui_FrameInfoWidget

class MainWindow(QtGui.QMainWindow):
    """ Main window of the debugger"""
    FocusLine = pyqtSignal(str, int, name='FocusLine')
    def __init__(self):
        QtGui.QMainWindow.__init__(self)
        self.init_ui()
        self.cfg_window = RunConfigWindow()
        self.about_dialog = AboutDialog()
        self.pty_stdout = PtyView(self.ui.commander)
        stdout_path = self.pty_stdout.get_file_path()

        self.debugger = Debugger(stdout_path, stdout_path, self.cfg_window.working_dir)
        self.last_highlighted_editor = None
        self.my_listener = MyListeningThread(self.debugger.dbg, self.FocusLine)
        self.FocusLine.connect(self.do_focus_line)
        self.my_listener.StateChanged.connect(self.on_state_changed)
        self.my_listener.BPChanged.connect(self.on_bp_changed)
        self.debugger.listener = self.my_listener
        self.my_listener.start()
        self.opened_files = {}
        self.bp_locations = {}

        args = Qt.qApp.arguments()
        self.cfg_window.working_dir = os.getcwd()
        if len(args) > 1:
            self.do_exe_file_open(args[1])
        if len(args) > 2:
            self.cfg_window.arglist = [str(x) for x in args[2:]]

        logging.info('Ready')

    def init_ui(self):
        """initialize UI"""
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.tabCodeEditor.clear()
        self.ui.tabCodeEditor.setTabsClosable(True)
        self.ui.tabCodeEditor.setTabShape(QtGui.QTabWidget.Triangular)

        # setup frame viewer dock
        self.action_Frames = self.ui.frame_dock.toggleViewAction()
        self.ui.menuView.addAction(self.action_Frames)
        self.action_Frames.setCheckable(True)
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap((":/icons/icons/frame.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.action_Frames.setIcon(icon1)
        self.ui.frame_viewer.set_focus_signal(self.FocusLine)

        # setup source file tree dock
        self.action_SourceTree = self.ui.file_tree_dock.toggleViewAction()
        self.ui.menuView.addAction(self.action_SourceTree)
        self.action_SourceTree.setCheckable(True)
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap((":/icons/icons/directory.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.action_SourceTree.setIcon(icon1)
        self.ui.source_tree.set_open_file_signal(self.FocusLine)

        self.connect(self.ui.action_Open, QtCore.SIGNAL('triggered()'), self.do_exe_file_open)
        self.connect(self.ui.action_Run, QtCore.SIGNAL('triggered()'), self.do_run)
        self.connect(self.ui.action_StepOver, QtCore.SIGNAL('triggered()'), self.do_step_over)
        self.connect(self.ui.action_StepInto, QtCore.SIGNAL('triggered()'), self.do_step_into)
        self.connect(self.ui.action_StepOut, QtCore.SIGNAL('triggered()'), self.do_step_out)
        self.connect(self.ui.btn_frame_up, QtCore.SIGNAL('clicked()'), self.ui.frame_viewer.up)
        self.connect(self.ui.btn_frame_down, QtCore.SIGNAL('clicked()'), self.ui.frame_viewer.down)
        self.ui.frame_viewer.set_show_args(self.ui.chk_show_args)

        self.connect(self.ui.tabCodeEditor, QtCore.SIGNAL('tabCloseRequested(int)'), self.close_tab)

        self.ui.action_Exit.triggered.connect(Qt.qApp.quit)
        self.ui.commander.commandEntered.connect(self.do_command)
        self.connect(self.ui.action_Run_Config, QtCore.SIGNAL('triggered()'), self.do_config)
        self.connect(self.ui.action_About, QtCore.SIGNAL('triggered()'), self.show_about)

    def closeEvent(self, event):
        """overrided. when close event is triggered"""
        if not (self.debugger.curr_process and
                self.debugger.curr_process.is_alive):
            event.accept()
            return
        reply = QtGui.QMessageBox.question(self, 'Message', 'Quit?', \
                                           QMessageBox.Yes, QMessageBox.No)
        if reply == QtGui.QMessageBox.Yes:
            self.my_listener.quit()
            event.accept()
        else:
            event.ignore()

    def close_tab(self, idx):
        editor = self.ui.tabCodeEditor.widget(idx)
        #self.opened_files.remove()
        #editor.close
        self.close_src_file(editor.source_file)
        self.ui.tabCodeEditor.removeTab(idx)

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
            self.open_src_file(main_file.fullpath, line)
            self.ui.action_Run.setEnabled(True)
            self.my_listener.add_target_broadcaster(self.debugger.target.GetBroadcaster())
            self.ui.source_tree.set_root(main_file.GetDirectory())
        elif line == 0:
            logging.info('cannot find entry function')
        else:
            logging.info('error opening executable: %s', exe_filename)

    def do_focus_line(self, filename, line_no):
        """ slot for focusing line event"""
        # if line_no is 0, just focus the tab
        if not filename:
            editor = None
        else:
            filename = str(filename)
            logging.debug('Focusing [%s]:%d', filename, line_no)
            if filename not in self.opened_files:
                self.open_src_file(filename)
            editor = self.opened_files[filename]

        if editor is not None:
            self.ui.tabCodeEditor.setCurrentWidget(editor)
            if line_no:
                if self.last_highlighted_editor and self.last_highlighted_editor != editor:
                    # clear previous highlight
                    self.last_highlighted_editor.setExtraSelections([])
                editor.focus_line(line_no)
                self.last_highlighted_editor = editor

    @staticmethod
    def get_state_name(state):
        names = {lldb.eStateCrashed : 'Crashed',
                 lldb.eStateExited : 'Exited',
                 lldb.eStateLaunching : 'Launching',
                 lldb.eStateRunning : 'Running',
                 lldb.eStateStepping : 'Stepping',
                 lldb.eStateStopped : 'Stopped',
                 lldb.eStateSuspended : 'Suspended'}
        if state in names:
            return names[state]
        else:
            return 'Unknown'

    def on_state_changed(self, state):
        """slot for state change event"""
        self.ui.statusBar.update_state(self.get_state_name(state))
        process = self.debugger.curr_process
        steppable = process is not None and process.is_alive and state == lldb.eStateStopped
        if steppable:
            self.ui.frame_viewer.show_frame_info(process)
        else:
            self.ui.frame_viewer.clear()

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
            self.ui.frame_viewer.clear()
            return

    def on_bp_changed(self, bp, bp_type):
        # TODO: might be multiple locations for a BP
        filename, line_no = self.debugger.getBPLocationFromDesc(bp)
        if not filename or not line_no:
            logging.warning('Cannot find location from BP')
            return

        if filename not in self.bp_locations:
            self.bp_locations[filename] = []

        if bp_type == lldb.eBreakpointEventTypeAdded:
            self.bp_locations[filename].append(line_no)

        elif bp_type == lldb.eBreakpointEventTypeRemoved:
            if line_no in self.bp_locations[filename]:
                self.bp_locations[filename].remove(line_no)
            else:
                logging.warning('removing non-existed BP ' + filename + ':' + str(line_no))
                # TODO: trigger a rescan of all BPs?
                return
        else:
            logging.debug('Unhandled BP event:' + str(bp_type))
            return

        if filename in self.opened_files:
            lna = self.opened_files[filename].line_number_area
            lna.breakpoints = self.bp_locations[filename]
            lna.repaint()

    def close_src_file(self, name):
        editor = self.opened_files[name]
        editor.setParent(None)
        del self.opened_files[name]

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
        # it should trigger BPChanged signal.
        self.debugger.toggle_breakpoint(filename, line_no)


    def do_command(self, cmd):
        """ on command entered"""
        cmd = str(cmd)
        cmds = cmd.split()
        cmd0 = cmds[0].lower()
        cmd1 = ''

        if len(cmds) > 1:
            cmd1 = cmds[1].lower()
        if cmd0 == 'r' or cmd0 == 'run' or (cmd0 == 'process' and cmd1 == 'launch'):
            if cmd0[0] == 'r' or cmd0 == 'run':
                args = cmds[1:]
            else:
                args = cmds[2:]
            self.do_run(args, True)
            return
        msg = self.debugger.execute(cmd0, cmd)
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

class MyListeningThread(QThread):
    """Listening events"""

    StateChanged = pyqtSignal(int, name='StateChanged')
    BPChanged = pyqtSignal(SBBreakpoint, int, name='StateChanged')

    def __init__(self, dbg, focus_signal):
        QThread.__init__(self)
        self.dbg = dbg
        self.sb_listener = dbg.GetListener()
        #self.stopped = False
        self.process_broadcaster = None
        self.target_broadcaster = None
        self.focus_signal = focus_signal

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

            # Check for target events
            target = self.dbg.GetSelectedTarget()
            state = None
            if not target.IsValid():
                continue
            # Handle BP events
            if SBBreakpoint.EventIsBreakpointEvent(event):
                type = SBBreakpoint.GetBreakpointEventTypeFromEvent(event)
                bp = SBBreakpoint.GetBreakpointFromEvent(event)
                self.BPChanged.emit(bp, type)
                continue

            state = None
            # Handle Process state events
            if SBProcess.EventIsProcessEvent(event):
                process = SBProcess.GetProcessFromEvent(event)
                state = process.GetState()
                if state == lldb.eStateStopped:
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
                            logging.debug('stopped for BP %d: %s:%d', bp_id, filename, line_no)
                            if filename is not None:
                                self.focus_signal.emit(filename, int(line_no))
                            else:
                                self.focus_signal.emit('', -1)
                        elif reason == lldb.eStopReasonWatchpoint or \
                             reason == lldb.eStopReasonPlanComplete:
                            frame = thread.GetFrameAtIndex(0)
                            line_entry = frame.GetLineEntry()
                            file_spec = line_entry.GetFileSpec()
                            filename = file_spec.fullpath
                            line_no = line_entry.GetLine()
                            logging.debug('stopped @ %s:%d', filename, line_no)
                            if filename is not None:
                                self.focus_signal.emit(filename, int(line_no))
                            break
                        elif reason == lldb.eStopReasonThreadExiting:
                            logging.debug('thread exit')
                        elif reason == lldb.eStopReasonSignal or \
                             reason == lldb.eStopReasonException:
                            logging.debug('signal/exception %x', thread.GetStopReasonDataAtIndex(0))

                        elif reason == lldb.eStopReasonExec:
                            logging.debug('re-run')

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
