# Intro

Hackish script to convert chm files to markdown.

# Use

Use ``archmage`` to convert chm files to html.

Use ``./hacking.py`` to convert html files to markdown.

# Current State

Right now ``hacking.py`` match the different types of lines, but does not 
output markdown. This will require an additional state machine, building 
tables, merging lines, etc.

## TODOs

- There are a few unidentified line types still
- The matching is only good on the aay1541.HTM
- There needs some word wrapping magic for asm and jump lines (ending with many data words)
- The tables need work - should the old width and line-breaks be kept? Most probably!

# Hacking

Hack away. Hosted on github. Use pull requests and enjoy.
