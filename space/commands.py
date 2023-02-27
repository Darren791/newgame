from evennia import default_cmds
from world.utils import cemit
from evennia import GLOBAL_SCRIPTS
from .script import get_state
from evennia.utils import inherits_from

from .typeclasses import DefaultSpaceObject
STATE = get_state()

class SpaceCommand(default_cmds.MuxCommand):
    key = "sdb"
    switchtab = ("add", "remove", "list", "stats", "save", "load", "start", "stop",)
    sobj = None
    space = GLOBAL_SCRIPTS.space_script

    def do_stats(self):
        self.space.get_status(self.caller)

    def do_load(self):
        self.space.save_state()
        cemit("space", "State data synced to disk.")

    def do_save(self):
        self.space.save_state()
        cemit("space", "State data read from disk.")


    def do_start(self):
        self.space.active = True
        self.msg("Space is now cycling.")
        cemit("space", "Space is now active.")

    def do_stop(self):
        self.space.active = False
        cemit("space", "Space has stopped cycling.")

    def do_add(self):
        if not self.rhs and not self.lhs:
            self.msg("Usage: sdb/add <objectid>=<typeclass>")
            return
        
        marker = self.search(self.lhs, typeclass=GenericSpaceObject)
        if not marker or not inherits_from(smarker, GenericSpaceObject):
            self.msg("No such object or wrong type.")
            return

    def do_remove(self):
        self.caller.msg("REMOVE")
        
    def do_list(self):
        self.caller.msg("LIST")


    def func(self):
        """ Command entry point. """

        switch = self.switches[0] if self.switches else "list"
        if switch and switch not in self.switchtab:
            self.msg(f"The '{self.cmdname}' command does not take the '{switch}' switch.")
            return
        
        fun = getattr(self, f"do_{switch}", None)
        if fun and callable(fun):
            fun()
        else:
            self.msg(f"There was an error calling the switch handler: {switch}")
