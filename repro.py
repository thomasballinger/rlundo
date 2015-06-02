import sys

import pexpect

class LogFile(object):
    def __init__(self):
        self.output = ''
    def write(self, data):
        self.output += data
    def flush(self):
        pass

log = LogFile()

def run(argv):
    child = pexpect.spawn(argv[0], argv[1:], logfile=log)
                       #master_read=master_read,
                       #handle_window_size=True)
    child.interact()


run([sys.executable])
print repr(log.output)
