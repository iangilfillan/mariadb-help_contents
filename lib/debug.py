"""Contains ANSI escape codes"""
# Colors
CL_YELLOW = '\u001b[33m'
CL_RED = '\u001b[31m'
CL_GREEN = '\u001b[32m'
CL_BLUE = '\u001b[34m'
CL_CYAN = '\u001b[36m'

CL_END = '\33[0m'

# Debug Funcs
def error(text: str):
    print(CL_RED, "[ERROR] ", text, CL_END, sep="")
    exit(1)

def warn(text: str):
    print(CL_YELLOW, "[WARNING] ", text, CL_END, sep="")

def info(text: str):
    print(CL_BLUE, "[INFO] ", text, CL_END, sep="")

def time_info(text: str):
    print(CL_CYAN, "[INFO] ", text, CL_END, sep="")

def success(text: str):
    print(CL_GREEN, "[SUCCESS] ", text, CL_END, sep="")
    