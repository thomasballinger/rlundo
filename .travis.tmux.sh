#!/bin/bash
set -e
set -x

wget https://s3.amazonaws.com/tmux/tmux
chmod +x tmux
sudo mv tmux /usr/local/bin