from django.conf import settings
from evennia.utils.ansi import ANSIString, strip_ansi
#from typeclasses.characters import Character


def header(text: str, player, width: int=settings.CLIENT_DEFAULT_WIDTH, suppress_nl:bool = False) -> str:
    o = player.options
    if not o:
        return ''

    if not text:
        out: str = f"|{o.border_color}{o.header_fill * width}|n"
    else:
        flen: int = width - len(strip_ansi(text)) - 6
        out = f"|{o.border_color}--[ |{o.header_text_color}{text} |{o.border_color}]{'-' * flen}|n"
        
    return out if suppress_nl else f"{out}\n"



def subheader(text: str, player, width: int=settings.CLIENT_DEFAULT_WIDTH, suppress_nl: bool = False) -> str:
    o = player.options
    if not o:
        return ''
    
    l: int = 0
    rsp: int = 0
    lsp: int = 0
    out: str = ''

    if not text:
        out = f"|{o.border_color}{o.separator_fill * width}|n"
    else:

        # Determine the width of the text, accounting for padding.
        l = len(text) + 2

        # Calculate the length of each segment.  Note that we use floor
        # division here to ensure that we end up with an integer rather than
        # a float.
        lsp = rsp = (width - l) // 2

        # If the length of the text is not evenly divisible by 2, our
        # header will be off by one character.  Let's fix that.
        rsp += (width - l) % 2

        # Format the output.
        out = f"|{o.border_color}{o.header_fill * lsp} {text} {o.header_fill * rsp}|n"
    
    return out if suppress_nl else f"{out}\n"



def divider(text: str, player, width: int=settings.CLIENT_DEFAULT_WIDTH) -> str:
    o = player.options
    if not o:
        return ''

    l: int = 0
    rsp: int = 0
    lsp: int = 0
    out: str = ''

    if not text:
        out = f"|{o.border_color}{o.separator_fill * width}|n"
    else:

        # Determine the width of the text, accounting for padding.
        l = len(text) + 2

        # Calculate the length of each segment.  Note that we use floor
        # division here to ensure that we end up with an integer rather than
        # a float.
        lsp = rsp = (width - l) // 2

        # If the length of the text is not evenly divisible by 2, our
        # header will be off by one character.  Let's fix that.
        rsp += (width - l) % 2

        # Format the output.
        out = f"|{o.border_color}{o.header_fill * lsp} |{o.header_text_color}{text} |n|{o.border_color}{o.header_fill * rsp}|n\n"
        
    return out


def banner(text: str, player, width: int=settings.CLIENT_DEFAULT_WIDTH) -> str:
    o = player.options
    if not o:
        return ''

    l: int = 0
    rsp: int = 0
    lsp: int = 0

    if not text:
        out: str = f"|{o.border_color}{o.header_fill * width}|n"
    else:

        # Determine the width of the text, accounting for padding.
        l: int = len(ANSIString(text)) + 6

        # Calculate the length of each segment.  Note that we use floor
        # division here to ensure that we end up with an integer rather than
        # a float. Yet another pointless change to Py3.
        lsp = rsp = (width - l) // 2

        # If the length of the string is not evenly divisible by 2, our
        # header will be off by one character.  Let's fix that.
        rsp += (width - l) % 2

        # Format the output.
        out: str = f"|{o.border_color}.-{lsp * o.header_fill} |{o.header_text_color}{text}|{o.border_color} {rsp * o.header_fill}-.|n"

    return out


def ubanner(text, player, width=settings.CLIENT_DEFAULT_WIDTH):
    o = player.options
    if not o:
        return ''

    lsp: int = 0
    rsp: int = 0
    l: int = 0

    if not text:
        out = f"|{o.border_color}{o.header_fill * width}|n"
    else:

        # Determine the width of the text, accounting for padding.
        l = len(ANSIString(text)) + 6

        # Calculate the length of each segment.  Note that we use floor
        # division here to ensure that we end up with an integer rather than
        # a float. Yet another pointless change to Py3.
        lsp = rsp = (width - l) // 2

        # If the length of the string is not evenly divisible by 2, our
        # header will be off by one character.  Let's fix that.
        rsp += (width - l) % 2

        # Format the output.
        out = f"|{o.border_color}`-{lsp * o.header_fill} |{o.header_text_color}{text}|{o.border_color} |{o.border_color}{rsp * o.header_fill}-'|n"

    return out


def footer(text, player, width=settings.CLIENT_DEFAULT_WIDTH) -> str:
    o = player.options
    if not o:
        return ''

    if not text:
        out = f"|{o.border_color}{o.footer_fill * width}|n"
    else:
        flen: int = width - len(strip_ansi(text)) - 6
        out = f"|{o.border_color}{o.footer_fill * flen}|{o.border_color}[ |{o.header_text_color}{text} |{o.border_color}]--|n"

    return out


def multiheader(lhs: str, rhs: str, player, width: int=settings.CLIENT_DEFAULT_WIDTH) -> str:
    o = player.options
    if not o:
        return ''

    actual: int = 0

    actual = width - (len(strip_ansi(lhs)) + len(strip_ansi(rhs)) + 12)
    if actual < 0:
        actual = 0

    return f"|{o.border_color}{o.header_fill * 2}[ |{o.header_text_color}{lhs} |{o.border_color}]{o.header_fill * actual}[ |w{rhs} |{o.border_color}]--|n\n"


def red_scale(a=0.0, maxx=0):
    b = int(a * max + 0.5)

    if maxx < 5:
        maxx = 5
    if maxx > 75:
       maxx = 75
    if b < 0:
       b = 0
    if b > maxx:
       b = maxx

    return f"|024[|R{'=' * b}|024{'-' * (maxx - b)}|024]|n"

