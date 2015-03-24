import sys
import os
from subprocess import Popen, PIPE

modified_readline_path = os.path.join(os.path.dirname(os.path.realpath('__file__')),
                                      'modified-readline-6.3/shlib')

if sys.platform == 'darwin':
    os.environ["DYLD_LIBRARY_PATH"] = modified_readline_path
else:
    os.environ["LD_LIBRARY_PATH"] = modified_readline_path

p = Popen(sys.argv[1:])
p.communicate()
