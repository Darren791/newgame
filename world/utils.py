from evennia.utils import evtable, inherits_from, make_iter
import re
from evennia.comms.models import ChannelDB, Msg
from evennia.utils.ansi import strip_ansi, ANSIParser, ANSIString
from evennia import ObjectDB, AccountDB
import inflect
from django.conf import settings
from django.db.models.signals import post_save, pre_delete
from evennia.utils import make_iter
DEBUG_CHAN = None
import textwrap

def twocol(items, width=80):
    out = ANSIString('')
    colwidth = width // 2
    
    #array = sublist(items, 2)
    """
    for x in array:
        out += x[0].ljust(colwidth)
        if len(x) == 2:
            out += f" {x[1].ljust(colwidth-1)}"
        out += "\n"
    """
    index = 0
    for x in items:
        i = index % 2
        if i:
            out += " "
        out += x.ljust(colwidth-1)
        if i:
            out += "\n"
        index += 1   
    return out.rstrip()


def itemize(items, prep='and', sep=', '):
    # type: (list, str, str) -> str
    """
    Format a list of items (Assumed to be strings) as a proper english list, e.g.
    itemize([x, y, z, w]) -> "x, y, z and w".

    Args:
        items: List of items, these should all be strings.
        prep: The preposition to use in front of the last item, defaults to 'and'.
        sep: The seperator to use.  Defaults to ', '.

    Returns: The list of items formatted as a proper english list.
    """

    if not items or not len(items):
        return ''
    elif len(items) == 1:
        return [items[0]]
    else:
        #return "%s %s %s" % (sep.join(items[:-1]), prep, items[-1])
        return f"{sep.join(items[:-1])} {prep} {items[-1]}"

# This really doesn't need to be a method but it's easier for me to remember this way.
def sublist(arg, size=2) -> list:
    i: int = 0

    # List comprehensions ftw!
    return [arg[i:i + size] for i in range(0, len(arg), size)]


# TODO: debug performance issues when using with @help.
def columnize(items: list, width: int=80, cols: int=3) -> str:

    if not items:
        return ''

    # Initialize a new table. No fancy border or headers, we just want a grid
    # of plain text (with any markup intact, of course).
    table = evtable.EvTable(border='none', width=width)

    out = sublist(items, cols)
    if not out:
        return ""

    colwidth = width // cols
    index = 0
    
    # Add each row.
    for x in out:
        table.add_row(*x)
        table.reformat_column(index)
        index += 1

    return str(table)


# Implementation suggested by Neil "Polk" Stevens.
def match_begin(source, target, unique=True):
    """
      Searches a list of strings for ones that start with the target string.
      If unique==True then the search must produce a unique match.

    """

    searchstr = re.compile("^%s" % re.escape(target), re.IGNORECASE | re.UNICODE)
    matches = tuple(filter(lambda x:searchstr.search(x), source))

    # Ideally this would return FailedMatch or AmbigiousMatch but...
    if not matches:
        return None
    elif unique and len(matches) != 1:
        return False
    else:
        return matches[0]

def match_all(source, target):
    """
      Searches a list of strings for ones that start with the target string.
      If unique==True then the search must produce a unique match.

    """

    searchstr = re.compile("^%s" % re.escape(target), re.IGNORECASE | re.UNICODE)
    matches = [x for x in source if searchstr.search(x)]
    #matches = tuple(filter(lambda x:searchstr.search(x), source))

    # Ideally this would return FailedMatch or AmbigiousMatch but...
    return matches[0] if len(matches) == 1 else None


def cemit_debug(type, message):
    global DEBUG_CHAN

    if not DEBUG_CHAN:
        DEBUG_CHAN = ChannelDB.objects.channel_search("debug").first() or None

    if DEBUG_CHAN:
        DEBUG_CHAN.msg("[|R%s|n]: %s" % (type, message))

ChannelCache = {}

def cemit(channelname:str="", message:str=""):
    """
    Send a message to a channel.
    """

    global ChannelCache

    if not channelname or not message:
        return

    try:
        channel = ChannelCache[channelname]
    except KeyError:
        channel = ChannelDB.objects.channel_search(channelname).first()
        if channel:
            ChannelCache[channelname] = channel

    if channel:
        channel.msg(message)

_UPPERCASE = ['ooc', 'i', 'ic', 'rp', 'ikv', 'chr', 'uss']

def capstr(word):
    words = word.split(" ")
    out = []

    for x in words:
        if not x in _UPPERCASE:
            out.append(x.title())
        else:
            out.append(x.upper())

    return " ".join(out)


def pluralize(word, number):
    p = inflect.engine()
    return p.plural(word, number)

# How many levels should we allow?
ROOM_NEST_LIMIT = 10

def room(obj):
    """ Returns the topmost location. """
    last = None
    i = 0
    loc = obj.location or None
    if not loc:
        # If the object has no location, and of it's a room, then return self, otherwise
        # return None.
        return obj if inherits_from(obj, settings.BASE_ROOM_TYPECLASS) else None

    # Avoid potential infinite loops.
    while loc and i < 10:
        i += 1
        last = loc
        if inherits_from(last, settings.BASE_ROOM_TYPECLASS):
            return last
        loc = loc.location

    return last

def columnize2(lst, cols=3, linelength=79, return_list=True):
    separator = "  "
    width = linelength // cols - len(separator)
    lines = ""

    while(lst):
        line = f"{lst[0]:{width}.{width}}"
        out = []
        lst = lst[1:]
        for _ in range(1, cols):
            if lst:
                line = f"{line}{separator}{lst[0]:{width}.{width}}"
                lst = lst[1:]
        lines += line + "\n"

    return lines


def columnize3(args, cols=3, linelength=79, pre="R"):
    separator = "  "
    width = linelength // cols - len(separator)
    lines = []
    i = 1

    lst = make_list(args, pre)

    while(lst):
        line = f"{lst[0]:{width}.{width}}"
        lst = lst[1:]
        for _ in range(1, cols):
            if lst:
                line = f"{line}{separator}{lst[0]:{width}.{width}}"
                lst = lst[1:]
        lines += [line]
        i += 1

    return lines


def replace_character(template):
    def replace(match):
        player = pmatch(match.group(0), match_account=False)
        if player:
            return player.name
        else:
            return match.group(0)

    regexp = re.compile(r"`([\w]+)")
    return regexp.sub(replace, template)


def safe_list_item(arg, index=0):
    if arg:
        args = make_iter(arg)
        return args[index if (index <= len(args) and index >= 0) else 0]
    return None
    

def idle_ctime(idle = 0):
    if idle <= 300:
        return "|g"
    elif idle <= 1800:
        return "|y"
    else:
        return "|r"


def format_pair(d1="(None)", d2="(None)", color="|n",  width=80):
    l1 = (width - 3) // 4
    return ANSIString(f"|y{d1:>{l1}.{l1}}|n: {color}{d2:<{l1}.{l1}}|n")

    
def wrap(text, width=80, indent=0, label=""):
    """
    Safely wrap text to a certain number of characters.
    Args:
        text (str): The text to wrap.
        width (int, optional): The number of characters to wrap to.
        indent (int): How much to indent each line (with whitespace).
    Returns:
        text (str): Properly wrapped text.
    """
    width = width if width else settings.CLIENT_DEFAULT_WIDTH

    if indent:
        indent_s = " " * indent
    else:
        indent_s = ""

    if label:
        initial_indent = label
    else:
        initial_indent = ""
                        
    if not text:
        return ""
    s_indent = (" " * 30)
    return str(textwrap.fill(text, width, initial_indent=initial_indent, subsequent_indent=indent_s))    

def parse_int_or_dbref(value: str):
    value = value.strip(' #')
    return int(value) if value and value.isnumeric() else None



