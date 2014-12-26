"""Debugger

This module contains wrapper classes of lldb objects for convenience

"""
import lldb
import re
from lldb import SBTarget, SBProcess, SBDebugger, SBEvent,\
                 SBCommandReturnObject, SBError, SBStream, SBBreakpoint

class Debugger(object):
    """This class represents a SBDebugger with some util functions"""
    def __init__(self, stdout, stderr, workdir):
        self.dbg = SBDebugger.Create()
        self._cmd_interp = self.dbg.GetCommandInterpreter()
        self.target = None
        self._my_listener = None
        self._stdout = stdout
        self._stderr = stderr
        self._workdir = workdir
        self._last_args = None

    @property
    def listener(self):
        """ my listener """
        return self._my_listener

    @listener.setter
    def listener(self, listener):
        """ set the listener """
        self._my_listener = listener

    def set_args(self, args):
        """ set the args for running the target"""
        self._last_args = args

    def open_file(self, exe_file_name):
        """ open the executable and create SBTarget and also find the
            main function"""
        if len(exe_file_name) == 0:
            return None
        exe_file_name = str(exe_file_name)
        #TODO: check arch
        self.target = self.dbg.CreateTargetWithFileAndArch(exe_file_name, \
                                                         lldb.LLDB_ARCH_DEFAULT)
        if not self.target.IsValid():
            return None
        sym_ctx_list = self.target.FindFunctions('main')
        main_sym_ctx = sym_ctx_list[0]
        main_cu = main_sym_ctx.GetCompileUnit()
        main_file = main_cu.GetFileSpec()
        self._my_listener.addTargetBroadcaster(self.target.GetBroadcaster())
        return main_file

    def toggle_breakpoint(self, file_name, line_no):
        """ toggle a break point"""
        target = self.dbg.GetSelectedTarget()
        if target is None or not target.IsValid():
            return []
        bp_lines = []
        existing_bp = None
        stream = SBStream()
        #find the bp's line No. from desc as bp location may use different line No.
        for bp in target.breakpoint_iter():
            stream.Clear()
            bp.GetDescription(stream)
            desc = stream.GetData()
            matched = re.search('file = \'(.*)\', line = (.*),', desc)
            if matched:
                bp_file_name = matched.group(1)
                bp_line_no = int(matched.group(2))
            if file_name == bp_file_name and bp_line_no == line_no:
                existing_bp = bp
            else:
                bp_lines.append(bp_line_no)

        if existing_bp:
            target.BreakpointDelete(existing_bp.GetID()) #FIXME: delete the whole bp
        else:
            #The line_no send to API may be different from the actually created one
            bp = target.BreakpointCreateByLocation(file_name, line_no)
            bp_lines.append(line_no)
        return bp_lines

    def execute(self, cmd):
        """do the 'execute' command """
        cmd = str(cmd)
        cmds = cmd.split()
        cmd0 = ''
        cmd1 = ''
        if len(cmds) > 0:
            cmd0 = cmds[0].lower()
            if not self._cmd_interp.CommandExists(cmd0) and not self._cmd_interp.AliasExists(cmd0):
                return 'Invalid cmd ' + cmd0

        if len(cmds) > 1:
            cmd1 = cmds[1].lower()
        if cmd0 == 'r' or cmd0 == 'run' or (cmd0 == 'process' and cmd1 == 'launch'):
            if cmd0[0] == 'r':
                args = cmds[1:]
            else:
                args = cmds[2:]
            self.run(args, True)
            return ''

        res = SBCommandReturnObject() #TODO:global?
        self._cmd_interp.HandleCommand(cmd, res, True)
        return res.GetOutput()

    def run(self, args=None, from_cmd=False, default_args=None):
        """run the target program"""
        target = self.dbg.GetSelectedTarget()
        if target is None or not target.IsValid():
            return None
        process = target.GetProcess()
        if process is not None and process.is_alive:
            process.Continue()
            return None
        err = SBError()
        env = None
        stdin = None
        if from_cmd:
            if args is None or len(args) == 0:
                args = self._last_args
                if args is None:
                    args = default_args
        else:
            args = default_args
        self._last_args = args

        process = target.Launch(self._my_listener.dbgListener, args, env,
                                stdin, self._stdout, self._stderr,
                                self._workdir,
                                0, #launch flags
                                True, #stop at entry
                                err)
        return process

    @property
    def curr_process(self):
        """ get current SBProcess or None"""
        if self.target is not None and self.target.IsValid():
            return self.target.GetProcess()
        else:
            return None

    @property
    def curr_thread(self):
        """get current SBThread or None"""
        process = self.curr_process
        if process is None:
            return None
        return process.GetSelectedThread()

    def next(self, step_over, instruction=False):
        """ next, nexti, step, stepi"""
        thread = self.curr_thread
        if thread is None:
            return
        if instruction:
            thread.StepInstruction(step_over)
            return
        if step_over:
            thread.StepOver()
        else:
            thread.StepInto()

    def finish(self):
        """ Finish the frame """
        thread = self.curr_thread
        if thread is None:
            return
        thread.StepOut()





