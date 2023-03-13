"""
Object

The Object is the "naked" base class for things in the game world.

Note that the default Character, Room and Exit does not inherit from
this Object, but from their respective default implementations in the
evennia library. If you want to use this class as a parent to change
the other types, you can do so by adding this as a multiple
inheritance.

"""
from .objects import Object

class Console(Object):
    user = None

    def announce_unman(self, who):
        who.msg(f"You unman {self.name}.")
        self.msg_contents(f"{self.name} powers down.", exclude=who)

    def name_format(self, fmt=0):
        user = self.db.user or None
        if user:
            if not user.sessions.count():
                try:
                    user.db.console.attributes.remove('user')
                    user.attributes.remove('console')
                except:
                    pass

                return self.name
            else:
                return f"{self.name} ({user.name})"

        return self.name
