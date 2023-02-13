from evennia import default_cmds
from typeclasses.characters import Character
from .attributes import ATTRIBUTES, SKILLS
from world.utils import columnize
from world.headers import header, footer, subheader

from django.conf import settings

COLOR = "|G"

def match_attribute(attr):
    return None
    
class CmdSheet(default_cmds.MuxCommand):
    key = "sheet"
    locks = "cmd:all()"
    help_category = "Chargen"

    def format_pair(self, d1="", d2="", color=COLOR):
        return f"{color}{d1:<20.20}|n: |R{d2:<17.17}|n".strip()

    def func(self):
        out = []
        caller = self.caller
        
        if self.args:
            target = caller.search(self.args, typeclass=Character)
            if not target:
                return
            if not target.access(caller, "view"):
                caller.msg("You do not have permission to view that character's sheet.")
                return
        else:
            target = caller
                
        caller.msg(header(f"Character Sheet", player=caller, width=80, suppress_nl=True))        

        out = []
        for x in ATTRIBUTES:
            y = target.get_cg_attr(x)
            out.append(f"{COLOR}{x.title():>19.19}|n ({y[0]:>2}/{y[1]:<2})")
        
        caller.msg(subheader("Attributes",player=caller, width=80, suppress_nl=True))
        caller.msg(columnize(out, width=80, cols=2))
        caller.msg(subheader("Skills",player=caller, width=80, suppress_nl=True))
        caller.msg(subheader("Perks",player=caller, width=80, suppress_nl=True))
        caller.msg(footer("", player=caller, width=80))

class CmdSheet2(default_cmds.MuxCommand):
    key = "sheet"
    locks = "cmd:all()"
    help_category = "Chargen"

    def format_pair(self, d1, d2, color=COLOR):
        return f"{color}{d1:14.14}|n {d2:<14.14}"

    def func(self):
        caller = self.caller
        target = caller

        if self.args:
            target = caller.search(self.args, typeclass=Character)
            if not target:
                return
            if not target.access(caller, "view"):
                caller.msg("You do not have permission to view that character's sheet.")
                return

        caller.msg(header(f"What makes {target.name} S.P.E.C.I.A.L.", player=caller, width=80, suppress_nl=True))        
        out = []

        
        out.append(self.format_pair("Origin", "Survivor", color=COLOR))
        out.append(self.format_pair("Concept", "Gunner", color=COLOR))
        out.append(self.format_pair("Age", "44", color=COLOR))
        out.append(self.format_pair("Allegiance", "Commonwealth", color=COLOR))
        out.append(self.format_pair("Level", "2", color=COLOR))
        out.append(self.format_pair("Approved", "Yes", color=COLOR))
        out.append(self.format_pair("XP Earned", "102", color=COLOR))
        out.append(self.format_pair("XP Total", "102", color=COLOR))

        caller.msg(columnize(out, width=80, cols=2))

        out = []

        for x in ATTRIBUTES:
            out.append(f"{COLOR}{x.title():14.14}|n ({target.get_cg_attr(x, True):>2}/{target.get_cg_attr(x, False):<2})")

        caller.msg(subheader("Attributes",player=caller, width=80, suppress_nl=True))
        caller.msg(columnize(out, cols=3))

        caller.msg(subheader("Skills", player=caller, width=80, suppress_nl=True))
        
        out = []
        for x in SKILLS:
            out.append(f"{COLOR}{x[0].title():14}|n ({0:>2}/{4:<2})")

        caller.msg(columnize(out, width=80, cols=3))

        caller.msg(subheader("Perks", player=caller, width=80, suppress_nl=True))
        out = []
        out.append(self.format_pair('Big Leagues', '*' ))
        out.append(self.format_pair('Bloody Mess', '**' ))
        out.append(self.format_pair('Can Do!', '***'))
        
        caller.msg(columnize(out, width=80, cols=3))

        caller.msg(footer("", player=caller, width=80))