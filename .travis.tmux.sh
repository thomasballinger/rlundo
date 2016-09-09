#!/bin/bash
set -e
set -x

curl https://github.com/tmux/tmux/releases/download/2.2/tmux-2.2.tar.gz > tmux.tar.gz
tar -czvf tmux.tar.gz tmuxbuild
cd tmuxbuild
./configure
./make
chmod +x tmux
sudo mv tmux /usr/local/bin
