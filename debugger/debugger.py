import lldb
import re
from lldb import SBTarget, SBProcess, SBDebugger, SBEvent, SBCommandReturnObject, SBError, SBStream, SBBreakpoint

class Debugger():
    def __init__(self, stdout, stderr, workdir):
        self.dbg = SBDebugger.Create()
        self.ci = self.dbg.GetCommandInterpreter()
        self.target = None
        self.stdout = stdout
        self.stderr = stderr
        self.workdir = workdir
        self.myListener = None
        self.lastArgs=None

    def setListener(self, listener):
        self.myListener = listener

    def setArgs(self, args):
        self.lastArgs = args

    def openFile(self, exeFileName):
        if len(exeFileName) == 0:
            return None
        exeFileName = str(exeFileName)
        self.target = self.dbg.CreateTargetWithFileAndArch(exeFileName, lldb.LLDB_ARCH_DEFAULT) #TODO: check arch
        if not self.target.IsValid():
            return None
        symCtxList = self.target.FindFunctions('main')
        mainSymCtx = symCtxList[0]
        mainCU = mainSymCtx.GetCompileUnit()
        mainFile = mainCU.GetFileSpec()
        self.myListener.addTargetBroadcaster(self.target.GetBroadcaster())
        return mainFile

    def toggleBreakPoint(self, fileName, lineNo):
        target = self.dbg.GetSelectedTarget()
        if target is None or not target.IsValid():
            return []
        bp_lines = []
        existingBp = None
        ss = SBStream()
        #find the bp's line No. from desc as bp location may use different line No.
        for bp in target.breakpoint_iter():
            ss.Clear()
            bp.GetDescription(ss)
            desc = ss.GetData()
            matched = re.search('file = \'(.*)\', line = (.*),', desc)
            if matched:
                bpFileName = matched.group(1)
                bpLineNo = int(matched.group(2))
            if fileName == bpFileName and bpLineNo == lineNo:
                existingBp = bp
            else:
                bp_lines.append(bpLineNo)

        if existingBp:
            target.BreakpointDelete(existingBp.GetID()) #FIXME: delete the whole bp
        else:
            #The lineNo send to API may be different from the actually created one
            bp = target.BreakpointCreateByLocation(fileName, lineNo)
            bp_lines.append(lineNo)
        return bp_lines

    def execute(self, cmd):
        cmd = str(cmd)
        cmds = cmd.split()
        c0 = ''
        c1 = ''
        if len(cmds) > 0:
            c0 = cmds[0].lower()
            if not self.ci.CommandExists(c0) and not self.ci.AliasExists(c0):
                return 'Invalid cmd ' + c0

        if len(cmds) > 1:
            c1 = cmds[1].lower()
        if c0 == 'r' or c0 == 'run' or (c0 == 'process' and c1 == 'launch'):
            if c0[0] == 'r':
                args = cmds[1:]
            else:
                args = cmds[2:]
            self.run(args, True)
            return ''
        
        res = SBCommandReturnObject() #TODO:global?
        self.ci.HandleCommand(cmd, res, True)
        return res.GetOutput()
        
    def run(self, args = None, fromCmd = False, defaultArgs = None):
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
        if fromCmd:
            if args is None or len(args) == 0:
                args = self.lastArgs
                if args is None:
                    args = defaultArgs
        else:
            args = defaultArgs
        self.lastArgs = args

        process = target.Launch(self.myListener.dbgListener, args, env,
                                stdin, self.stdout, self.stderr,
                                self.workdir,
                                0, #launch flags
                                True, #stop at entry
                                err)
        return process

    def getCurrProcess(self):
        if self.target is not None and self.target.IsValid():
            return self.target.GetProcess()
        else:
            return None

    def getCurrThread(self):
        process = self.getCurrProcess()
        if process is None:
            return None
        return process.GetSelectedThread()

    def next(self, step_over, instruction = False):
        thread = self.getCurrThread()
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
        thread = self.getCurrThread()
        if thread is None:
            return
        thread.StepOut()





