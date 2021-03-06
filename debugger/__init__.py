"""Debugger

This module contains wrapper classes of lldb objects for convenience

"""
import lldb
import re
from lldb import SBDebugger, SBStringList,\
                 SBCommandReturnObject, SBError, SBStream
import logging

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
        self.file_cu_mapping = {}

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

    @staticmethod
    def get_filename_and_lineNo(addr):
        if not addr.IsValid():
            return None, 0
        line_entry = addr.GetLineEntry()
        if not line_entry.IsValid():
            return None, 0
        return line_entry.GetFileSpec(), line_entry.GetLine()

    def open_file(self, exe_file_name):
        """ open the executable and create SBTarget and also find the
            main function"""
        if len(exe_file_name) == 0:
            return None, -1
        self.file_cu_mapping = {}
        exe_file_name = str(exe_file_name)
        #TODO: check arch
        self.target = self.dbg.CreateTargetWithFileAndArch(exe_file_name, \
                                                         lldb.LLDB_ARCH_DEFAULT)
        if not self.target.IsValid():
            self.target = None
            return None, -1
        sym_ctx_list = self.target.FindFunctions('main')
        if not sym_ctx_list.IsValid() or sym_ctx_list.GetSize() != 1:
            return None, 0
        main_sym_ctx = sym_ctx_list[0]#.GetFunction()
        main_func = main_sym_ctx.GetFunction()
        if not main_func.IsValid():
            return None, 0
        main_addr = main_func.GetStartAddress()
        filename, lineno = self.get_filename_and_lineNo(main_addr)
        if not filename:
            return None, 0
        self._my_listener.add_target_broadcaster(self.target.GetBroadcaster())
        return filename, lineno

    def getBPLocationFromDesc(self, bp):
        # find the bp's line No. from desc as bp location may use different line No.
        # but file name is from location because for command "b foo.c", the desc does
        # not return full path.
        loc = bp.GetLocationAtIndex(0)
        filename, lineno = self.get_filename_and_lineNo(loc.GetAddress())
        stream = SBStream()
        bp.GetDescription(stream)
        desc = stream.GetData()
        matched = re.search('file = \'(.*)\', line = (.*),', desc)
        if matched:
            line_no = int(matched.group(2))
            return filename.fullpath, line_no
        return None, None

    def toggle_breakpoint(self, file_name, line_no):
        """ toggle a break point"""
        target = self.dbg.GetSelectedTarget()
        if target is None or not target.IsValid():
            return []
        bp_lines = []
        existing_bp = None
        # TODO: don't visit all bps
        for bp in target.breakpoint_iter():
            bp_file_name, bp_line_no  = self.getBPLocationFromDesc(bp)
            if not bp_file_name or not bp_line_no:
                continue
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

    def complete_tab(self, cmd):
        candidates = SBStringList()
        #TODO: currentl lldb only supports max_reeturn_elements == -1
        logging.debug('complete: %s:%d:%d' %(cmd, len(cmd), cmd.rfind(' ')+1))
        self._cmd_interp.HandleCompletion(cmd, len(cmd) - 1, cmd.rfind(' ') + 1, -1, candidates)
        if candidates.GetSize() == 0:
            return None
        if candidates.GetSize() == 1:
            return candidates[0]
        msg = 'Candidates: '
        for s in candidates:
            msg += s + ' '
        logging.info(msg)

    def execute(self, cmd, cmd_line):
        """do the 'execute' command """
        if cmd:
            if not self._cmd_interp.CommandExists(cmd) and not self._cmd_interp.AliasExists(cmd):
                return 'Invalid cmd ' + cmd

        res = SBCommandReturnObject() #TODO:global?
        self._cmd_interp.HandleCommand(cmd_line, res, True)
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

        process = target.Launch(self._my_listener.sb_listener, args, env,
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

    def step_out(self):
        """ step out"""
        thread = self.curr_thread
        if thread is not None:
            thread.StepOut()

    def finish(self):
        """ Finish the frame """
        thread = self.curr_thread
        if thread is None:
            return
        thread.StepOut()

    def getCompileUnitFromFile(self, filename):
        if not self.target or not self.target.IsValid():
            return None
        if filename in self.file_cu_mapping:
            return self.file_cu_mappiing[filename]

        for m in self.target.module_iter():
            for cu in m.compile_unit_iter():
                if filename == cu.GetFileSpec().fullpath:
                    self.file_cu_mapping[filename] = cu
                    return cu

    def disassemble(self, filename):
        cu = self.getCompileUnitFromFile(filename)
        if not cu:
            return
        for line_entry in cu:
            start_addr = line_entry.GetStartAddress()
            end_addr = line_entry.GetEndAddress()
            print('line %d : [%x %x]') %(line_entry.GetLine(), start_addr, end_addr)
            instrs = self.target.ReadInstructions(start_addr, end_addr.offset - start_addr.offset)
            for instr in instrs:
                print('%s') %(instr)

