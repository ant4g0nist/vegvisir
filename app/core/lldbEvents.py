import json
import logging
from ..config import config
from threading import Thread

verbose = config.verbose
logging.basicConfig(name="lldb",level=logging.DEBUG)

def logEvent(eventType, event):
    if verbose:
        logging.debug("[:EVENT:] Type %d (%s)\n" %(eventType, str(event)))

def msgProcess(msg):
    if verbose:
        logging.debug("[:MSG:] %s"%(json.dumps(msg)))

def stateTypeToString(state, lldb):
    """
        Returns the state type string for the given an state.
    """
    if state == lldb.eStateInvalid:
        return "invalid"
    elif state == lldb.eStateUnloaded:
        return "unloaded"
    elif state == lldb.eStateConnected:
        return "connected"
    elif state == lldb.eStateAttaching:
        return "attaching"
    elif state == lldb.eStateLaunching:
        return "launching"
    elif state == lldb.eStateStopped:
        return "stopped"
    elif state == lldb.eStateRunning:
        return "running"
    elif state == lldb.eStateStepping:
        return "stepping"
    elif state == lldb.eStateCrashed:
        return "crashed"
    elif state == lldb.eStateDetached:
        return "detached"
    elif state == lldb.eStateExited:
        return "exited"
    elif state == lldb.eStateSuspended:
        return "suspended"
    else:
        raise Exception("Unknown StateType enum")

class LLDBEvents(Thread):
    """
        Listens for Events from lldb process
        -- modified from do_listen_for_and_print_event lldb examples

    """
    def __init__(self, handler, lldb):
        Thread.__init__(self)
        self.lldb  = lldb
        self.handler = handler

    def run(self):
        target  = self.handler.target
        process = target.GetProcess()
        listener = self.lldb.SBListener("LLDB events listener")

        # create process broadcaster to listen for state changes,
        processBroadcaster = process.GetBroadcaster()
        processBroadcaster.AddListener(listener, self.lldb.SBProcess.eBroadcastBitStateChanged | self.lldb.SBProcess.eBroadcastBitSTDOUT | self.lldb.SBProcess.eBroadcastBitSTDERR)

        self.done = False
        event = self.lldb.SBEvent()

        while not self.done:
            if listener.WaitForEvent(1, event):

                # get the broadcaster for this event
                eBroadcaster = event.GetBroadcaster()
                eventType = event.GetType()

                logEvent(eventType, event)
                
                # get details give by process broadcaster
                if eBroadcaster == processBroadcaster:
                    # eBroadcastBitStateChanged
                    if eventType == self.lldb.SBProcess.eBroadcastBitStateChanged:
                        state = self.lldb.SBProcess.GetStateFromEvent(event)

                        message = {"status":"event", "type":"state", "inferior_state":state, "state_desc": stateTypeToString(state,self.lldb)}

                        if state == self.lldb.eStateExited:
                            message["exit_status"] = process.GetExitStatus()

                    # eBroadcastBitSTDOUT
                    elif eventType == self.lldb.SBProcess.eBroadcastBitSTDOUT:
                        stdout = process.GetSTDOUT(256)
                        if stdout is not None and len(stdout) > 0:
                            message = {"status":"event", "type":"stdout", "output": "".join(["%02x" % ord(i) for i in stdout])}

                    # eBroadcastBitSTDERR
                    elif eventType == self.lldb.SBProcess.eBroadcastBitSTDERR:
                        stderr = process.GetSTDERR(256)
                        if stderr is not None and len(stderr) > 0:
                            message = {"status":"event", "type":"stderr", "output": "".join(["%02x" % ord(i) for i in stderr])}

                    msgProcess(message)

        return 
