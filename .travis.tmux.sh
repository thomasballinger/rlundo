#!/bin/bash
set -e
set -x

wget https://github.com/tmux/tmux/releases/download/1.9a/tmux-1.9a.tar.gz
tar -xzvf tmux-1.9a.tar.gz
cd tmux-1.9a.tar.gz && ./authgen.sh && make && ./configure && sudo make install
