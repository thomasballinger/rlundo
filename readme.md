
##Prototype

- [x] run a program in a subprocess, and know what the current state of the terminal screen is.
- [x] keep track of original cursor starting location
- [x] take snapshots of terminal state.
- [x] restore previous snapshots
  - [x] keep track of number of times scrolled down.
    - [x] modify doy's vt100 to keep track of scroll_offset
- [x] start vt100 cursor position where it was when started
- [x] send signal from rlundo program to snapshot and restore states

##The real thing

- [ ] set up testing harness: use a GUI terminal emulator 
  - [ ] programmatically set up tmux
    - [ ] programmatically set up tmux
  - [ ] request state of scrollback buffer and screen
  - [ ] write a simple test
  - [ ] implement cursor query to discover how cursor moved
  - [ ] terminal detection via env TERM and database for wrap strategies

- Test cases:
  - [ ] same screen, no line wrapping
    - [ ] write test
    - [ ] test passing
  - [ ] test case: scroll down, no line wrapping
    - [ ] write test
    - [ ] test passing
  - [ ] test case: same screen, line wrapping
    - [ ] write test
    - [ ] test passing
  - [ ] test case: scroll down, line wrapping
    - [ ] write test
    - [ ] test passing
  - [ ] test case: scroll off of the screen, no line wrapping
    - [ ] write test
    - [ ] test passing
  - [ ] test case: scroll off the screen, line wrapping
    - [ ] write test
    - [ ] test passing
  - [ ] test case: screen resize
    - [ ] write test
    - [ ] test passing

