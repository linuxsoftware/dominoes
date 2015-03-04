#---------------------------------------------------------------------------
# Process functions
#---------------------------------------------------------------------------
import sys
import time
import os
import signal
from pathlib import Path
from contextlib import suppress

#---------------------------------------------------------------------------
# Daemon functions
#---------------------------------------------------------------------------
def daemonSpawn(cmd, *args, cwd="/", log="/dev/null", delayStart=None):
    # Parent
    if not isinstance(cmd, str) and not callable(cmd):
        raise TypeError("Bad type for cmd")
    pidPipe = os.pipe() # a pipe for passing back the grandchild's pid
    childPid = os.fork()
    if childPid > 0:
        os.close(pidPipe[1])
        try:
            with os.fdopen(pidPipe[0], 'r') as pipeIn:
                grandchildPid = int(pipeIn.read())
        except (ValueError, TypeError):
            grandchildPid = 0
        pid, status = os.waitpid(childPid, 0)
        return grandchildPid

    # Child
    with suppress(PermissionError):
        os.setsid()
    os.close(pidPipe[0])
    grandchildPid = os.fork()
    if grandchildPid > 0:
        with os.fdopen(pidPipe[1], 'w') as pipeOut:
            pipeOut.write(str(grandchildPid))
        os._exit(0)

    # Grandchild
    os.chdir(cwd)
    os.umask(0)
    sys.stdout.flush()
    sys.stderr.flush()
    for fdPath in Path("/proc/self/fd").iterdir():
        with suppress(ValueError, OSError):
            os.close(int(fdPath.name))
    os.open("/dev/null", os.O_RDONLY)                      # reopen STDIN
    os.open(log, os.O_RDWR|os.O_CREAT|os.O_APPEND, 0o660)  # reopen STDOUT
    os.dup2(1, 2)                                          # reopen STDERR
    if delayStart is not None:
        time.sleep(delayStart) # favour parent process
    if isinstance(cmd, str):
        os.execlp(cmd, Path(cmd).name, *args)
    elif callable(cmd):
        cmd(*args)
    else:
        sys.stderr.write("Bad type for cmd. Should never happen!")
    sys.exit(0)

#---------------------------------------------------------------------------
# DaemonHandle
#---------------------------------------------------------------------------
class DaemonHandle:
    """Wraps together daemon starting/stopping with a PID file"""

    def __init__(self, filename, cmd=None):
        self.filename = filename
        self.cmd      = cmd
        self.pid      = self._load()

    def _load(self):
        try:
            with open(self.filename, 'r') as pidFile:
                pid = int(pidFile.read())
            if not pid:
                return None
        except (ValueError, TypeError):
            # file exists but has no pid
            print("No PID found in file {}".format(self.filename))
            self._removePidFile()
            print("Removed PID file {}".format(self.filename))
            return None
        except FileNotFoundError:
            return None

        statPath = Path("/proc") / str(pid) / "stat"
        # NB: don't use cmdline because if the process is swapped out 
        # then cmdline may not be there
        # TODO consider using pythonhosted.org/psutil
        if not statPath.exists():
            print("Stale PID {} left in file {}".format(pid, self.filename))
            self._removePidFile()
            print("Removed stale PID file {}".format(self.filename))
            return None
        try:
            with statPath.open() as procFile:
                procStatus = procFile.read()
                procPid, _, procStatus = procStatus.partition('(')
                procCmd, _, procStatus = procStatus.partition(')')
                procState = procStatus.partition(' ')[0]
        except OSError:
            print("Cannot access stat of PID {} from file {}"
                  .format(pid, self.filename))
            self._removePidFile()
            print("Removed PID file {}".format(self.filename))
            return None
        try:
            procPid = int(procPid)
        except (ValueError, TypeError):
            procPid = None
        if procPid != pid:
            print("Proc status invalid! {} {}".format(procPid, pid))
            return None
        if self.cmd:
            # check if this is the *right* process
            if procCmd[:15] != self.cmd[:15]:
                print("Wrong process. PID {}'s comm {} does not match {}"
                      .format(pid, procCmd[:15], self.cmd[:15]))
                self._removePidFile()
                print("Removed stale PID file {}".format(self.filename))
                return None
        if procState == 'Z':
            print("Process {} has turned into a zombie!".format(pid))
            return None
        return pid

    def _removePidFile(self):
        try:
            os.unlink(self.filename)
        except OSError:
            try:
                with open(self.filename, 'w') as pidFile:
                    pidFile.write("")
                print("Wiped stale PID from file {}".format(self.filename))
            except OSError:
                print("Stale PID left in file {}".format(self.filename))

    def start(self, cmd, *args, cwd="/", log="/dev/null", delayStart=None):
        if self.pid:
            print("Daemon is already running (PID: {} from file {})"
                  .format(self.pid, self.filename))
            return self.pid

        logPath = str(Path(log).absolute())
        self.pid = daemonSpawn(cmd, *args, cwd=cwd,
                               log=logPath, delayStart=delayStart)
        if self.pid:
            with open(self.filename, 'w') as pidFile:
                pidFile.write(str(self.pid))
        else:
            print("Failed to start daemon")
            return 1
        return 0

    def stop(self):
        if not self.pid:
            print("No PID in file {} to stop".format(self.filename))
            return 2
        procPath = Path("/proc") / str(self.pid)
        retry = 0
        os.kill(self.pid, signal.SIGTERM)
        time.sleep(.1)
        while procPath.exists():
            os.kill(self.pid, signal.SIGTERM)
            retry += 1
            if retry > 10:
                break
            time.sleep(2)
        if procPath.exists():
            print("Failed to kill process {}".format(self.pid))
            return 3
        self._removePidFile()
        return 0

#---------------------------------------------------------------------------
#---------------------------------------------------------------------------
#---------------------------------------------------------------------------
