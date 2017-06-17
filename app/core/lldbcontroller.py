import os
import re
import sys
import time
import shlex
import string
import logging
import argparse
import commands
import subprocess
from ctypes import *
from struct import *
from binascii import *
from threading import Thread
from mmap import mmap, PROT_READ

# app related imports
from capstone import *
from lldbEvents import LLDBEvents
from ..config import config
# lldb_python = "/Applications/Xcode.app/Contents/SharedFrameworks/LLDB.framework/Resources/Python/"
# lldb_python = "/Library/Developer/CommandLineTools/Library/PrivateFrameworks/LLDB.framework/Resources/Python/"

for lldb_python in config.lldb_python_paths:
    sys.path.append(lldb_python)

import lldb

logging.basicConfig(name="lldb",level=logging.DEBUG)

def bytesTohex(bytes):
    result = []
    for i in range(len(bytes)):
        result.append("%.2X"%int(bytes[i]))

    return " ".join(result)

def hexToAddr_t(address):
    return long(address,16)

def Addr_tToHex(address):
    return hex(address)

# Thanks for MACH* part of the code - Jonathan Salwan
class MACH_HEADER(Structure):
    _fields_ = [
                ("magic",           c_uint),
                ("cputype",         c_uint),
                ("cpusubtype",      c_uint),
                ("filetype",        c_uint),
                ("ncmds",           c_uint),
                ("sizeofcmds",      c_uint),
                ("flags",           c_uint)
               ]

class MACHOFlags:
    CPU_TYPE_I386               = 0x7
    CPU_TYPE_X86_64             = (CPU_TYPE_I386 | 0x1000000)
    CPU_TYPE_MIPS               = 0x8
    CPU_TYPE_ARM                = 12
    CPU_TYPE_SPARC              = 14
    CPU_TYPE_POWERPC            = 18
    CPU_TYPE_POWERPC64          = (CPU_TYPE_POWERPC | 0x1000000)
    LC_SEGMENT                  = 0x1
    LC_SEGMENT_64               = 0x19
    S_ATTR_SOME_INSTRUCTIONS    = 0x00000400
    S_ATTR_PURE_INSTRUCTIONS    = 0x80000000


class LLDBController:
    """
        LLDB Controller  - LLDB Power to Python
    """
    def __init__(self, debugger=None):
        if debugger:
            logging.debug("A debugger session exists already")
            self.debugger = debugger

        elif lldb.debugger:
            logging.debug("lldb.debugger is valid - probably running inside LLDB")
            self.debugger = debugger

        else:
            logging.debug("New session created")
            self.debugger = lldb.SBDebugger.Create()

        self.setAsync()

        if self.debugger:
            self.command_interpreter = self.debugger.GetCommandInterpreter()
            self.runCommands("settings set auto-confirm 1")
            self.runCommands("settings set target.x86-disassembly-flavor intel")
            self.error = lldb.SBError()

        self.lldbEventThread = LLDBEvents(self, lldb)

    def setAsync(self):
        self.debugger.SetAsync(True)

    def unSetAsync(self):
        self.debugger.SetAsync(False)

    def setTarget(self, exe, launchInfo=None):
        """
            Set target
        """
        if not self.ifTarget():
            self.exe    = exe
            self.target = self.debugger.CreateTarget(self.exe, None, None, True, self.error)

            if launchInfo:
                self.launch_info = lldb.SBLaunchInfo(launch_info)
            else:
                self.launch_info = lldb.SBLaunchInfo([])


            self.launch_info.SetLaunchFlags(lldb.eLaunchFlagDisableASLR + lldb.eLaunchFlagStopAtEntry)
            self.process = self.target.Launch(self.launch_info, self.error)

            if self.process != None:
                try:
                    self.lldbEventThread.start()
                except Exception,e:
                    print e

                while self.process.GetState() == lldb.eStateAttaching:
                    time.sleep(0.1)

                return True,
            else:
                self.target = None
                return False, "cannot create process"

        return False, "process already exists"

    def attach(self, attach_pid):
        attach_info = lldb.SBAttachInfo(attach_pid)
        

    def doContinue(self):
        """
            Continue
        """
        if self.ifTarget() and self.process:
            self.process.Continue()
            time.sleep(0.5)
            return True
        return False

    def doStop(self):
        """
            interrupt
        """
        if self.ifTarget() and self.process:
            self.process.Stop()
            time.sleep(0.1)
            return True
        return False

    def doStepInto(self):
        """
            thread StepInto
        """
        if self.ifTarget() and self.process and self.process.is_stopped:
            thread = self.getThread()
            thread.StepInstruction(False)
            time.sleep(0.1)
            return True

        return False

    def doStepOut(self):
        """
            thread StepOver
        """
        if self.ifTarget() and self.process and self.process.is_stopped:
            thread = self.getThread()
            thread.StepOut()
            time.sleep(0.1)
            return True

        return False

    def ifTarget(self):
        """
            check if valid target
        """
        if self.debugger.GetTargetAtIndex(0):
            return True
        return False

    def getEntryPoint(self):
        """
            Get the entrypoint of the binary from __text section
        """
        if self.ifTarget():
            modules  = self.target.modules
            for i in modules:
                j=str(i.file)
                if self.exe==j:
                    for k in i.sections:
                        for l in xrange(0,k.GetNumSubSections()):
                            sec = k.GetSubSectionAtIndex(l)
                            if sec.name == "__text":
                                return hex(sec.file_addr)

    def runCommands(self, command):
        """
            Run lldb commands
        """
        return_obj = lldb.SBCommandReturnObject()
        self.command_interpreter.HandleCommand(command, return_obj)
        time.sleep(0.5)
        if return_obj.Succeeded():
          return True, return_obj.GetOutput()
        else:
          return False, return_obj.GetError()

    def getFrame(self):
        #return lldb.debugger.GetSelectedTarget().process.selected_thread.GetSelectedFrame();
        # return self.debugger.GetSelectedTarget().GetProcess().GetSelectedThread().GetSelectedFrame()
        # return lldb.debugger.GetTargetAtIndex(0).process.selected_thread.GetFrameAtIndex(0);
        #return frame for stopped thread... there should be one at least...
        return self.process.selected_thread.GetFrameAtIndex(0);

    def getThread(self):
        return self.process.GetThreadAtIndex(0)

    def readMem(self, addrStart, addrSize):
        error = lldb.SBError()

        memory_buff = self.process.ReadMemory(addrStart, addrSize, error)

        if not error.Success():
            print error.GetError(), 'asds'
            return False, None

        return True, memory_buff

    def getArchAndMode(self):
        """
            Get Architecture and Mode for Disassembly with Capstone
        """
        data = bytearray(open(self.exe,'rb').read())
        mach_header = MACH_HEADER.from_buffer_copy(data)

        if mach_header.magic == 0xfeedface:
            mode = 4
        elif mach_header.magic == 0xfeedfacf:
            mode = 8

        if mach_header.cputype == MACHOFlags.CPU_TYPE_I386 or mach_header.cputype == MACHOFlags.CPU_TYPE_X86_64:
            return CS_ARCH_X86, mode
        if mach_header.cputype == MACHOFlags.CPU_TYPE_ARM:
            return CS_ARCH_ARM, mode
        if mach_header.cputype == MACHOFlags.CPU_TYPE_MIPS:
            return CS_ARCH_MIPS, mode
        else:
            return None, None

    def capstoneinit(self):
        arch, mode   = self.getArchAndMode()
        self.Csmd    = Cs(arch, mode)
        # self.Csmd.detail = True

    def disassemble(self, funcname, start_addr, end_addr):
        start_addr  = long(start_addr, 16)
        end_addr    = long(end_addr,16)

        logging.debug("start_addr: %s"%start_addr)
        logging.debug("end_addr: %s  "%end_addr)

        return self.capDisassemble(start_addr, end_addr - start_addr)

    def capDisassemble(self, addrStart, addrSize):
        """
            Capstone Disassemble
        """

        success, bytes = self.readMem(addrStart, addrSize)
        disasm = {}

        if success:
            firstLine = True
            for insn in self.Csmd.disasm(bytes, addrStart):
                address      = "0x%x"%insn.address
                mnemonic     = "%-8s"%insn.mnemonic
                ops          = "%s"%insn.op_str
                disasm[address] = {"bytes":"%-16s"%bytesTohex(insn.bytes),"mnemonic":mnemonic,"ops":ops}

        else:
            logging.debug("Error in capDisassemble")

        return disasm

    def getAllRegisters(self):
        self.gen_registers =  list(self.getFrame().regs)[0]
        self.registers = {i.name: i.value for i in self.gen_registers.__iter__()}
        return self.registers

    def getRegValue(self, reg):
        self.getAllRegisters()
        if reg in self.registers.keys():
            return self.registers[reg]

        return False

    def getEflags(self):
        eflags = self.getRegValue("rflags") or self.getRegValue("eflags")
        eflags = int(eflags, 16)
        masks = {"CF":0, "PF":2, "AF":4, "ZF":6, "SF":7, "TF":8, "IF":9, "DF":10, "OF":11}
        return {key: bool(eflags & (1 << value)) for key, value in masks.items()}

    def context(self):
        frame = self.getFrame()

        if not frame:
            return None, "process is not in a valid state"

        thread = self.getThread()

        REGISTERS = {
            # 8 : ["al", "ah", "bl", "bh", "cl", "ch", "dl", "dh"],
            # word: ["ax", "bx", "cx", "dx"],
            'dword': ["eax", "ebx", "ecx", "edx", "esi", "edi", "ebp", "esp", "eip"],
            'qword': ["rax", "rbx", "rcx", "rdx", "rsi", "rdi", "rbp", "rsp", "rip",
                 "r8", "r9", "r10", "r11", "r12", "r13", "r14", "r15"]
        }

        allRegisters = self.getAllRegisters()
        registers    = {}
        for i in REGISTERS:
            registers[i] = []
            for j in REGISTERS[i]:
                if j in allRegisters.keys():
                    registers[i].append({'reg':j,"value":allRegisters[j]})

        rip               = hexToAddr_t(allRegisters["rip"])
        disas             = self.capDisassemble(rip, 0x30)

        #instruction at rip
        inst_at_rip     = disas[disas.keys()[0]]
        eflags          = self.getEflags()
        #if jump, check if it is taken to address
        jump, address   = self.testjump(rip, eflags)

        symbol          = self.getFrame().symbol.name

        # collect registers present in current instruction
        for i in registers:
            for j in xrange(len(registers[i])):
                reg = registers[i][j]["reg"]
                if reg in inst_at_rip["ops"]:
                    dicts = {"in_instruction":True}
                    registers[i][j] = dict(registers[i][j].items()+dicts.items())

        return registers, disas, symbol, jump, address

    def testjump(self, pc, flags):
            """
            Test if jump instruction is taken or not
            Returns:
                True if jump is taken or False if not
            """
            inst=None

            if not flags:
                return False, None

            if not inst:
                success, inst = self.runCommands("x/1i $pc")
                if not success:
                    return False, None

            opcode = inst.split('  ')[2]

            if opcode == "jmp":
                return (True,inst.split('  ')[4])
            if opcode == "je" and flags["ZF"]:
                return (True,inst.split('  ')[4])
            if opcode == "jne" and not flags["ZF"]:
                return (True,inst.split('  ')[4])
            if opcode == "jg" and not flags["ZF"] and (flags["SF"] == flags["OF"]):
                return (True,inst.split('  ')[4])
            if opcode == "jge" and (flags["SF"] == flags["OF"]):
                return (True,inst.split('  ')[4])
            if opcode == "ja" and not flags["CF"] and not flags["ZF"]:
                return (True,inst.split('  ')[4])
            if opcode == "jae" and not flags["CF"]:
                return (True,inst.split('  ')[4])
            if opcode == "jl" and (flags["SF"] != flags["OF"]):
                return (True,inst.split('  ')[4])
            if opcode == "jle" and (flags["ZF"] or (flags["SF"] != flags["OF"])):
                return (True,inst.split('  ')[4])
            if opcode == "jb" and flags["CF"]:
                return (True,inst.split('  ')[4])
            if opcode == "jbe" and (flags["CF"] or flags["ZF"]):
                return (True,inst.split('  ')[4])
            if opcode == "jo" and flags["OF"]:
                return (True,inst.split('  ')[4])
            if opcode == "jno" and not flags["OF"]:
                return (True,inst.split('  ')[4])
            if opcode == "jz" and flags["ZF"]:
                return (True,inst.split('  ')[4])
            if opcode == "jnz" and flags["OF"]:
                return (True,inst.split('  ')[4])

            return (False,None)

    def doReturnStrings(self):
        process = self.process
        pid     = process.GetProcessID()
        print pid
        vmmemory  = subprocess.check_output(["vmmap", "%d" % pid], shell=False)

        memory_address_ranges = []
        address_regex = re.compile("([0-9a-fA-F]{16})-([0-9a-fA-F]{16})")

        for line in vmmemory.split("\n"):
            mem = address_regex.search(line)

            if not mem:
                continue;

            mem_start       = long(mem.group(1), 16)
            mem_end         = long(mem.group(2), 16)

            mem_size        = mem_end-mem_start
            success, memory_buff     = self.readMem(mem_start, mem_size);
            strings = {}
            offset = 0
            if success:
                mem_location = memory_buff.find("")
                for i in self.returnPrintableChars(memory_buff):
                    address = "0x%x"%(mem_start+hexToAddr_t(i[1]))
                    strings[address] = i[0]

            return strings

    def returnPrintableChars(self, data, n=6):
        for match in re.finditer(('([\w/]{%s}[\w/]*)' % n).encode(), data):
            yield match.group(0),hex(match.start())

    def IsCodeType(self, symbol):
        """Check whether an SBSymbol represents code."""
        return symbol.GetType() == lldb.eSymbolTypeCode

    def doReturnFunctions(self):
        self.funcnames = {}
        file = self.target.GetExecutable()
        f=str(file).split('\n')[0]
        for i in self.target.modules:
            j=str(i.file)
            if f==j:
                for k in i.symbols:
                    if self.IsCodeType(k) and k.name!="_mh_execute_header" and k.name!="radr://5614542":
                        self.funcnames[k.name] = {"start_addr":hex(k.addr),"end_addr":hex(k.end_addr)}
                    elif k.GetType()!=24:
                        self.funcnames[k.name] = {"start_addr":hex(k.addr),"end_addr":hex(k.end_addr),"external":True}

        return self.funcnames

    def getFunctionDisassembly(self, func_name):
        if func_name in self.funcnames.keys():
            print self.funcnames[func_name]

    def lldbPermToString(self, perm):
        ePermissionsExecutable = 4
        ePermissionsReadable   = 2
        ePermissionsWritable   = 1

        if perm == ePermissionsReadable ^ ePermissionsWritable ^ ePermissionsExecutable:
            return "rwx"
        elif perm == ePermissionsReadable ^ ePermissionsWritable:
            return "rw"
        elif perm == ePermissionsReadable ^ ePermissionsExecutable:
            return "rx"
        elif perm == ePermissionsWritable ^ ePermissionsExecutable:
            return "wx"

    def doReturnSections(self):
        modules  = self.target.modules
        sections = {}
        sizes = {}
        for i in modules:
            file = self.exe
            j=str(i.file)
            if file==j:
                for k in i.sections:
                    for l in xrange(0,k.GetNumSubSections()):
                        perm = self.lldbPermToString(k.GetSubSectionAtIndex(l).GetPermissions())
                        sections[k.GetSubSectionAtIndex(l).name] = {"file_addr": hex(k.GetSubSectionAtIndex(l).file_addr),"file_offset": hex(k.GetSubSectionAtIndex(l).file_offset),"file_size": hex(k.GetSubSectionAtIndex(l).file_size),"perm":perm}

                    sizes[k.name] = k.file_size

                return sections, sizes

        return sections, sizes

    def vtable(self):
        success, vtable = self.runCommands('image loo -r -v -s "vtable for"')
        if success:
            print(vtable)
            return True

        return False

    def searchMem(self, args):

        args=shlex.split(args)

        parser = argparse.ArgumentParser(prog="searchmem");

        parser.add_argument("-s", "--string",  help="string to look for");
        parser.add_argument("-c", "--count", type=int, default=10,  help="number of results to print");

        args = parser.parse_args(args)

        to_search = args.string

        if not to_search:
            parser.print_help()
            return

        count     = args.count

        process = self.process
        pid     = process.GetProcessID()

        vmmemory  = subprocess.check_output(["vmmap", "%d" % pid], shell=False)

        memory_address_ranges = []
        address_regex = re.compile("([0-9a-fA-F]{16})-([0-9a-fA-F]{16})")

        for line in vmmemory.split("\n"):
            mem = address_regex.search(line)

            if not mem:
                continue;

            mem_start       = long(mem.group(1), 16)
            mem_end         = long(mem.group(2), 16)

            mem_size        = mem_end-mem_start
            success, memory_buff     = self.readMem(mem_start, mem_size);

            offset = 0
            if success:
                while True:
                    mem_location = memory_buff.find(to_search)

                    if not mem_location==-1:
                        offset+=mem_location
                        value = memory_buff[mem_location:mem_location+len(to_search)+16]
                        print "%.016lX"%(mem_start+offset)+"\t%s"%(value)
                        memory_buff = memory_buff[mem_location+len(to_search):]
                        offset += len(to_search)
                    else:
                        break

                    if count==1:
                        return
                    count-=1


    def dump(self, start_range, end_range):
        """Dump's Memory of the process in a given address range
           Syntax: dump outfile 0x6080000fe680 0x6080000fe680+1000
                dump will not read over 1024 bytes of data. To overwride this use -f
           Syntax: dump -o outfile -s 0x6080000fe680 -e 0x6080000fe680+1000 -f"""

        output, error=self.runCommands("memory read -b --force %s %s"%(start_range, end_range))

        if not error:
            return output


    def terminate(self):
        """
            Terminate lldb session
        """

        self.process.Kill()
        self.debugger.Terminate()
        self.debugger = None
        self.lldbEventThread.done = True
        self.lldbEventThread.join()

#
# s = LLDBController()
# print s.setTarget("/Applications/Preview.app/Contents/MacOS/Preview")


# entry = s.getEntryPoint()
# s.capstoneinit()
# print s.readMem(long(entry,16),0x1000)
# print s.capDisassemble(long(entry,16),0x1000)
# print s.runCommands("c")
# print s.runCommands("run ~/Downloads/image.png")
# print s.runCommands("process status")
# print s.runCommands("process interrupt")
# print s.runCommands("process status")
# print s.runCommands("breakpoint set -n objc_msgSend")
# print s.getAllRegisters()
# print s.getEflags()
# s.doContinue()
# print s.doStop()
# print s.runCommands("process status")[1]
# s.doStepInto()
# print s.doStop()
# print s.runCommands("process status")[1]
# print s.context()
# s.doStepInto()
# s.searchMem("-s Preview")
# s.getStrings()
# time.sleep(5)

# print s.doStepInto()
# print s.context()
# print s.doStepInto()
# print s.context()
# print s.doContinue()
# print s.setBreakpointFunction("objc_msgSend")
# print s.setBreakpointAddress(0x105a5bd50)
# print s.getBreakpoints()

# # # # # # # static stuff# # # # # #
# print s.doReturnStrings()
# s.doReturnFunctions()
# print s.doReturnSections()
# print s.vtable()
# time.sleep(10)
# s.terminate()
# print s.context()
# s.terminate()