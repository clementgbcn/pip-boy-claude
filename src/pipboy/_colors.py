"""ANSI escape codes – phosphor-green-on-black palette."""

G   = '\033[32m'       # dim green
BG  = '\033[92m'       # bright green
DG  = '\033[2;32m'     # very dim green
AM  = '\033[33m'       # amber (warnings)
R   = '\033[0m'        # reset
B   = '\033[1m'        # bold
CLS = '\033[2J\033[H'  # clear + home
HC  = '\033[?25l'      # hide cursor
SC  = '\033[?25h'      # show cursor
INV = '\033[7m'        # inverse video
