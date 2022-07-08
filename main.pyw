from tkinter import Tk, Text, Frame, filedialog, Listbox
import idlelib.colorizer as ic
import idlelib.percolator as ip
import os, sys, json, re, subprocess

with open('config/theme.json', 'r') as f:
    json = json.loads(f.read())

font = (json['font-family'], json['font-size'], json['font-weight'])
curr = None
file_ = '.'
file = None

def entering(file):
    global file_
    file_ = file.replace('\\', '/')
    while file_[-1]!='/':file_=file_[:-1]
    side.delete(0, 'end')
    side.insert('end',f'\uD83D\uDCC2 ..')
    for i in os.listdir(file_)[::-1]:
        try:
            os.listdir(i)
            side.insert('end',f'\uD83D\uDCC2 {i}')
        except:
            side.insert('end',f'{i}')

def saveas():
    global curr
    file = filedialog.asksaveasfilename(initialdir=os.curdir, title="Select a File")
    with open(file, 'w') as f:
        f.write(text.get(1.0, 'end')[:-1])
    curr = file
def save(b):
    global curr
    if curr == None:
        saveas()
    else:
        with open(curr, 'w') as f:
            f.write(text.get(1.0, 'end')[:-1])
def read(b,argc=None):
    global curr,side,file_,file
    if argc == None:
        file = filedialog.askopenfilename(initialdir=os.curdir, title="Select a File")
    else:
        file = argc
    #########
    entering(file)
    #########
    with open(file, 'r') as f:
        text.delete(1.0,'end')
        code = f.read()
        if code[-1] == '\n':
            text.insert('end', code[:-1])
            return
        text.insert('end', code)
    curr = file

root = Tk()
root.geometry(f'{int(json["WINDOW-SIZE"][0])}x{int(json["WINDOW-SIZE"][1])}')
root.title(json['TITLE'])
root.resizable(json['RESIZABLE'][0], json['RESIZABLE'][1])
root.iconbitmap(json['ICON'])
if json['SCALED']:
    root.state('zoomed')
root.attributes("-fullscreen", json['FULLSCREEN'])

frame = Frame(root, bg='#000000')
frame.pack(fill='both')

side = Listbox(frame, width=50, height=root.winfo_screenheight(), bg=json['SIDEBAR'], fg=json['STANDARD'], highlightthickness=0, bd=0, selectbackground='#2f2f2f')
side.pack(side='left')

output = Text(frame, height=12, highlightthickness=0, width=root.winfo_screenwidth(), bg=json['SIDEBAR'], fg=json['STANDARD'], bd=0, insertunfocussed='hollow',
            insertbackground='#868686', blockcursor=True, font=font, selectbackground='#2f2f2f')
output.pack(side='bottom')

# text field
text = Text(frame, highlightthickness=0, bg=json['BACKGROUND'], fg=json['STANDARD'], bd=0, insertunfocussed='hollow', insertbackground='#868686',
            width=root.winfo_screenwidth(), height=root.winfo_screenheight(), blockcursor=True, font=font, selectbackground='#2f2f2f', tabs=int(int(json['indentation'])*10))
text.pack(side='right')

def run_code(event):
    global curr
    output.delete(1.0, 'end')
    if curr is None:
        output.insert(1.0, 'no file found')
        return
    p = subprocess.Popen(json['command'].replace('__file__', curr), stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    result, error = p.communicate()
    output.insert(1.0, result)
    output.insert(1.0, error)

def auto_indent(event):
    text = event.widget
    line = text.get("insert linestart", "insert")
    match = re.match(r'^(\s+)', line)
    whitespace = match.group(0) if match else ""
    text.insert("insert", f"\n{whitespace}")
    return "break"

def select_file(b):
    i = side.get(side.curselection())
    try:
        os.listdir(i[1:][1:])
    except:
        read(None, f'{file_}{i}')

# key bindings
text.bind(json['save'], save)
text.bind(json['open'], read)
text.bind(json['run'], run_code)
text.bind("<Return>", auto_indent)
side.bind("<Double-1>", select_file)
#text.bind(json['run' ], run )

#syntax highlighter patterns
KEYWORD   = r"\b(?P<KEYWORD>False|None|True|and|as|assert|async|await|break|class|continue|def|del|elif|else|except|finally|for|from|global|if|import|in|is|lambda|nonlocal|not|or|pass|raise|return|try|while|with|yield)\b"
EXCEPTION = r"([^.'\"\\#]\b|^)(?P<EXCEPTION>ArithmeticError|AssertionError|AttributeError|BaseException|BlockingIOError|BrokenPipeError|BufferError|BytesWarning|ChildProcessError|ConnectionAbortedError|ConnectionError|ConnectionRefusedError|ConnectionResetError|DeprecationWarning|EOFError|Ellipsis|EnvironmentError|Exception|FileExistsError|FileNotFoundError|FloatingPointError|FutureWarning|GeneratorExit|IOError|ImportError|ImportWarning|IndentationError|IndexError|InterruptedError|IsADirectoryError|KeyError|KeyboardInterrupt|LookupError|MemoryError|ModuleNotFoundError|NameError|NotADirectoryError|NotImplemented|NotImplementedError|OSError|OverflowError|PendingDeprecationWarning|PermissionError|ProcessLookupError|RecursionError|ReferenceError|ResourceWarning|RuntimeError|RuntimeWarning|StopAsyncIteration|StopIteration|SyntaxError|SyntaxWarning|SystemError|SystemExit|TabError|TimeoutError|TypeError|UnboundLocalError|UnicodeDecodeError|UnicodeEncodeError|UnicodeError|UnicodeTranslateError|UnicodeWarning|UserWarning|ValueError|Warning|WindowsError|ZeroDivisionError)\b"
BUILTIN   = r"([^.'\"\\#]\b|^)(?P<BUILTIN>abs|all|any|ascii|bin|breakpoint|callable|chr|classmethod|compile|complex|copyright|credits|delattr|dir|divmod|enumerate|eval|exec|exit|filter|format|frozenset|getattr|globals|hasattr|hash|help|hex|id|input|isinstance|issubclass|iter|len|license|locals|map|max|memoryview|min|next|oct|open|ord|pow|print|quit|range|repr|reversed|round|set|setattr|slice|sorted|staticmethod|sum|type|vars|zip)\b"
DOCSTRING = r"(?P<DOCSTRING>(?i:r|u|f|fr|rf|b|br|rb)?'''[^'\\]*((\\.|'(?!''))[^'\\]*)*(''')?|(?i:r|u|f|fr|rf|b|br|rb)?\"\"\"[^\"\\]*((\\.|\"(?!\"\"))[^\"\\]*)*(\"\"\")?)"
STRING    = r"(?P<STRING>(?i:r|u|f|fr|rf|b|br|rb)?'[^'\\\n]*(\\.[^'\\\n]*)*'?|(?i:r|u|f|fr|rf|b|br|rb)?\"[^\"\\\n]*(\\.[^\"\\\n]*)*\"?)"
TYPES     = r"\b(?P<TYPES>bool|bytearray|bytes|dict|float|int|list|str|tuple|object)\b"
NUMBER    = r"\b(?P<NUMBER>((0x|0b|0o|#)[\da-fA-F]+)|((\d*\.)?\d+))\b"
CLASSDEF  = r"(?<=\bclass)[ \t]+(?P<CLASSDEF>\w+)[ \t]*[:\(]" #recolor of DEFINITION for class definitions
DECORATOR = r"(^[ \t]*(?P<DECORATOR>@[\w\d\.]+))"
INSTANCE  = r"\b(?P<INSTANCE>super|self|cls)\b"
COMMENT   = r"(?P<COMMENT>#[^\n]*)"
SYNC      = r"(?P<SYNC>\n)"

#colors
COMMENT     = json['COMMENT']
TYPES       = json['TYPES']
NUMBERS     = json['STANDARD']
BUILTIN     = json['BUILTIN']
STRING      = json['STRING']
DOCSTRING   = json['STANDARD']
EXCEPTIONS  = json['STANDARD']
DEFINITION  = json['DEFINITION']
DECORATION  = json['STANDARD']
INSTANCE    = json['STANDARD']
KEYWORD     = json['KEYWORD']
CLASSDEF    = json['CLASSDEF']

# syntax highlights
TAGDEFS   = {
                'COMMENT'    : {'foreground': COMMENT     , 'background': None},
                'TYPES'      : {'foreground': TYPES       , 'background': None},
                'NUMBER'     : {'foreground': NUMBER      , 'background': None},
                'BUILTIN'    : {'foreground': BUILTIN     , 'background': None},
                'STRING'     : {'foreground': STRING      , 'background': None},
                'DOCSTRING'  : {'foreground': DOCSTRING   , 'background': None},
                'EXCEPTION'  : {'foreground': EXCEPTION   , 'background': None},
                'DEFINITION' : {'foreground': DEFINITION  , 'background': None},
                'DECORATOR'  : {'foreground': DECORATOR   , 'background': None},
                'INSTANCE'   : {'foreground': INSTANCE    , 'background': None},
                'KEYWORD'    : {'foreground': KEYWORD     , 'background': None},
                'CLASSDEF'   : {'foreground': CLASSDEF    , 'background': None},
            }
IDPROG = r"(?<!class)\s+(\w+)"
PROG   = rf"{KEYWORD}|{BUILTIN}|{EXCEPTION}|{TYPES}|{COMMENT}|{DOCSTRING}|{STRING}|{SYNC}|{INSTANCE}|{DECORATOR}|{NUMBER}|{CLASSDEF}"

cd = ic.ColorDelegator()

cd.tagdefs = {**cd.tagdefs, **TAGDEFS}
ip.Percolator(text).insertfilter(cd)

try:
    read(b=None, argc=sys.argv[1])
except:
    pass

root.mainloop()
