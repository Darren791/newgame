from evennia import default_cmds

class SpaceCommand(default_cmds.MuxCommand):
    key = "sdb"
    switchtab = ("add", "remove", "list",)
    sobj = None


    def do_add(self):
        self.caller.msg("ADD")
        
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
        
        sobj =  
        fun = getattr(self, f"do_{switch}", None)
        if fun and callable(fun):
            fun()
        else:
            self.msg(f"There was an error nonlocalling the switch handler: {switch}")
