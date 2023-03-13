from evennia import default_cmds
from world.utils import cemit
from evennia import GLOBAL_SCRIPTS
from .script import get_state
from evennia.utils import inherits_from
from .templates import match_class
from .typeclasses import DefaultSpaceObject
from .objects import HSShip
STATE = get_state()
from .script import SpaceScript as SPACE
from .systems import SystemsHandler

class SpaceCommand(default_cmds.MuxCommand):
    key = "sdb"
    switchtab = ("addship", "delship", "list", "stats", "save", "load", "start", "stop",)
    sobj = None
    space = GLOBAL_SCRIPTS.space_script

    def parse(self):
        self.state = get_state()
        super().parse()
        
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
        self.msg(f"SystemHandler: {self.state.ship_list[0].systems}")
        self.msg(self.state)

    def do_stop(self):
        self.space.active = False
        cemit("space", "Space has stopped cycling.")

    def do_addship(self):
        if not self.rhs and not self.lhs:
            self.msg("Usage: sdb/addship <class>=<name>")
            return

        klass = match_class(self.lhs)
        if not klass:
            self.msg("No such class.")
            return
            
        if not self.state:
            self.msg("System state cannot be determined.")
            return
        
        sname = self.rhs.lower()
        for x in self.state.ship_list:
            if x.name.lower() == sname:
                self.msg("A ship with that name already exists.")
                return
                
        ship = HSShip()
        klass.name = sname

        for x in (klass.__dict__.keys()):
            if  not x.startswith("_"):
                cemit("space", f"Setting {x} to {getattr(klass, x)}.")
                setattr(ship, x, getattr(klass, x))


        self.msg(f"Ship \"{sname}\" created.")
        self.space.add_object(sobj=ship)

    def do_delship(self):
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
