#!/usr/bin/env python
import sys

from rlundoable import modify_env_with_modified_rl
from rewrite import run_with_listeners

if __name__ == "__main__":
    modify_env_with_modified_rl()
    run_with_listeners(sys.argv[1:])
