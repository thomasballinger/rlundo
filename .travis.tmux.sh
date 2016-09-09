#!/bin/bash
set -e
set -x

wget https://github.com/tmux/tmux/releases/download/2.2/tmux-2.2.tar.gz
tar xzvf tmux-2.2.tar.gz
cd tmux-2.2
./configure
make
chmod +x tmux
sudo mv tmux /usr/local/bin
