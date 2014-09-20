import subprocess
import os
from threading import Thread
import time
import shlex
from Queue import Queue, Empty

from churnhash import ChurnHash
from diffparser import DiffParser

class ChurnDriverError(Exception):
    def __init__(self, msg):
        self.value = msg
    def __str__(self):
        return repr(self.value)

class StreamReader:
    def __init__(self, stream):
        self._s = stream
        self._q = Queue()
        def _populateQueue(stream, queue):
            while True:             
                line = stream.readline()
                if line:
                    queue.put(line)
                else:
                    # The stream is ended
                    break
        self._t = Thread(target=_populateQueue, args=(self._s, self._q))
        self._t.daemon = True
        self._t.start()
    def readline(self, timeout = None):
        try:
            return self._q.get(block = timeout is not None, timeout = timeout)
        except Empty:
            return None
    def is_empty(self):
        return self._q.empty()


class ChurnDriver(object):
    def __init__(self, repo_location, repo_command, repo_type='hg'):
        if not os.path.exists(repo_location):
            raise ChurnDriverError("Repo Location does not exist: %s" % repo_location)
        if not repo_command:
            raise ChurnDriverError("Repo Command cannot be empty")
        self._repo_location = os.path.abspath(repo_location)
        self._repo_type = repo_type
        self._cmd = repo_command
        self._dp = DiffParser(self._repo_type)
        self._ch = ChurnHash()

    def run(self):
        args = shlex.split(self._cmd)
        p = subprocess.Popen(args, cwd=self._repo_location, stdout=subprocess.PIPE)
       
        sr = StreamReader(p.stdout)
        
        now = time.time()
        # Wait for 5 seconds with no output
        while (time.time() - now < 5):
            if sr.is_empty():
                print '.',
                time.sleep(1)
                continue

            lines = sr.readline(0.5)
            # Got a line of output, reset timer
            now = time.time()
            
            if lines:                
                diffs = self._dp.parse(lines.split('\n'))
                if diffs:
                    while len(diffs):
                        d = diffs.popitem()
            
                        # These are now key, value tuples, the second half is the embedded dict
                        for k in d[1].keys():
                            if k == 'user':
                                # We don't use this right now
                                continue
                            # Otherwise, it's a file name with a churn value
                            self._ch.add_file_path(k, d[1][k])
        p.wait()

        # Now we save to some backend - or perhaps just wire this into churnhash directly
        # For now, we pull this back and return it
        return self._ch
    
