from evennia import default_cmds, CmdSet
from .attributes import (SKILLS, 
    ATTRIBUTES,
    match_attribute,
    match_skill,
    match_perk,
)


class CmdRaise(default_cmds.MuxCommand):
    key = "raise"
    aliases = "lower"
    locks = "cmd:notguest();"

    def _raise_attribute(self, attr, caller):
        self.msg(f"raise attribute: {attr}")

    def _raise_skill(self, skill, caller):
        self.msg(f"raise skill: {skill}")

    def _lower_attribute(self, attr, caller):
        self.msg(f"lower_attribute: {attr}")

    def _lower_skill(self, skill, caller):
        self.msg(f"lower skill: {skill}")

    def _raise_perk(self, perk, caller):
        self.msg(f"raise perk: {perk}")

    def _lower_perk(self, perk, caller):
        self.msg(f"lower perk: {perk}")


    def func(self):
        caller = self.caller
        what = None

        if not caller.tags.get(category='chargen'):
            caller.msg('You haven\'t started Chargen yet.')
            return
            
        if not self.args:
            caller.msg('You must specify the trait to modify.')
            return
        
        # how = 'raise' if self.cmdstring == 'raise' else 'lower'
        how = self.cmdstring

        if what := match_attribute(self.args):
            ver = 'attribute'
        elif what := match_skill(self.args):
            ver = 'skill'
        elif what := match_perk(self.args):
            ver = 'perk'
        else:
            self.caller.msg('No such attribute, skill or perk.')
            return

        attr = getattr(self, f"_{how}_{ver}")
        if attr and callable(attr):
            attr(what, self.caller)
        else:
            self.caller.msg(f"No handler: |C_{how}_{ver}()|n.")

# CGEN CMDSET
class ChargenBaseCmdSet(CmdSet):
    def at_cmdset_creation(self):
        self.add(CmdRaise())


# OTHER CMDSETS
class CmdSkill(default_cmds.MuxCommand):
    key = "skill"
    switch_options = "list"
    locks = "cmd:all()"
    help_category = "Chargen"

    def func(self):
        out = self.styled_table("NAME", "ATTR", "EXTRA", width=40)
        for x in SKILLS:
            out.add_row(x[0], ATTRIBUTES[x[1]].title(), "Yes" if x[2] else 'No')
        out.reformat_column(1, width=10)
        out.reformat_column(2, width=10)

        self.caller.msg(str(out))


        
    
