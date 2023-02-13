from evennia import default_cmds

class CmdDesc(default_cmds.CmdDesc):
    """
    describe an object or the current room.

    Usage:
      desc <obj>        : Display the current description.
      desc <obj>=       : Clears the description of <obj>.
      desc <obj>=<text> : Sets the object description.

    Switches:
      edit - Open up a line editor for more advanced editing.
      clear - Clears the description of <obj>.

    Sets the "desc" attribute on an object. You must control the
    object or have edit perms in order to do this. Unlike the stock
    Evennia @describe command, this does not require builder perms
    and does not default to the current room being the target.

    """
    switch_options = ("clear")
    
    def func(self):
        """Define command"""

        caller = self.caller

        if not self.args and "edit" not in self.switches:
            caller.msg("Usage: desc[/<switch>] [[<obj> =] <description>]")
            return

        obj = caller.search(self.lhs)
        if not obj:
            caller.msg("I don't see that here.")
            return
        
        if not obj.access(self.caller, "control") or not obj.access(self.caller, "edit"):
            caller.msg("You don't have permission to change the description of that object.")
            return

        if "edit" in self.switches:
            self.edit_handler()
            return

        if self.rhs == "" or "clear" in self.switches:
            del obj.db.desc
            self.msg("Description cleared.")
        elif self.rhs is None:
            # No '=' in args
            self.msg(obj.db.desc or "(No description set.)")
        else:
            obj.db.desc = self.rhs
            self.msg("Description set.")

