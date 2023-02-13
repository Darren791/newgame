"""
Exits

Exits are connectors between Rooms. An exit always has a destination property
set and has a single command defined on itself with the same name as its key,
for allowing Characters to traverse the exit to its destination.

"""
from evennia import DefaultExit, default_cmds
from .mixins.types import TypeMixins
from .mixins.names import NameMixins
from .mixins.ownership import OwnerMixins
from .mixins.messages import MessageMixins

from evennia.utils.ansi import ANSIString
from django.conf import settings


class MyExitCommand(default_cmds.MuxCommand):
    """
    
    This is the default command which initiates the movement of an object
    through an exit.  This has been over-ridden to check for room bans and
    keyrings.
    

    """

    obj = None

    def func(self):
        """
        Default exit traverse if no syscommand is defined.
        """
        ret = self.obj.can_traverse(self.caller)
        
        if ret:
            self.obj.at_traverse(self.caller, self.obj.destination)
        else:
            # exit is locked
            if self.obj.db.err_traverse:
                # if exit has a better error message, let's use it.
                self.caller.msg(self.obj.db.err_traverse)
            else:
                # No shorthand error message. Call hook.
                self.obj.at_failed_traverse(self.caller)


class Exit(MessageMixins, NameMixins, OwnerMixins, TypeMixins, DefaultExit):
    """
    Exits are connectors between rooms. Exits are normal Objects except
    they define the `destination` property. It also does work in the
    following methods:

     basetype_setup() - sets default exit locks (to change, use `at_object_creation` instead).
     at_cmdset_get(**kwargs) - this is called when the cmdset is accessed and should
                              rebuild the Exit cmdset along with a command matching the name
                              of the Exit object. Conventionally, a kwarg `force_init`
                              should force a rebuild of the cmdset, this is triggered
                              by the `@alias` command when aliases are changed.
     at_failed_traverse() - gives a default error message ("You cannot
                            go there") if exit traversal fails and an
                            attribute `err_traverse` is not defined.

    Relevant hooks to overload (compared to other types of Objects):
        at_traverse(traveller, target_loc) - called to do the actual traversal and calling of the other hooks.
                                            If overloading this, consider using super() to use the default
                                            movement implementation (and hook-calling).
        at_after_traverse(traveller, source_loc) - called by at_traverse just after traversing.
        at_failed_traverse(traveller) - called by at_traverse if traversal failed for some reason. Will
                                        not be called if the attribute `err_traverse` is
                                        defined, in which case that will simply be echoed.
    """
    
    exit_command = MyExitCommand
    
    @property
    def is_exit(self):
        return True
    
    def can_traverse(self, traversing_obj) -> bool:
        """
        Checks whether a player is able to pass through the exit, either by
        passing the lock, or posessing a key. Also displays the appropriate
        movement message.

        """

        ret = False

        # First, check the traverse lock.
        if self.access(traversing_obj, 'traverse'):
            # The exit is either unlocked or the player passes the lock.
            ret = True
        elif traversing_obj.has_key_for(self):
            # The exit is locked but the player has a key.
            traversing_obj.msg(f"You unlock #{self.key} with your key.")
            ret = True

        if ret:
            # TODO: should this be done from the perspective of the room instead?
            self.generate_message('leave', 'oleave', caller=traversing_obj, iobj=self.destination)
        else:
            self.generate_message('nogo', 'onogo', caller=traversing_obj,  iobj=self.destination)

        return ret
        
    def at_after_traverse(self, traveller, source_loc):
        self.generate_message('arrive', 'oarrive', caller=traveller, iobj=self.destination)
        
        # super().at_after_traverse(traveller, source_loc)
        
    def at_object_creation(self, **kwargs):
        self.init_owner()
        super().at_object_creation(**kwargs)
        
    def announce_move_to(self, source_location, msg=None, mapping=None, **kwargs):
        pass

    def format_exit(self, user=None):
        if user:
            eb = user.options.exit_bracket_color
            en = user.options.exit_name_color
            ea = user.options.exit_alias_color
        else:
            eb = settings.OPTIONS_ACCOUNT_DEFAULT.get('exit_bracket_color', 'b')
            en = settings.OPTIONS_ACCOUNT_DEFAULT.get('exit_name_color', 'w')
            ea = settings.OPTIONS_ACCOUNT_DEFAULT.get('exit_alias_color', 'w')

        out = ANSIString(self.key)
        if alias := self.shortest_alias():
            out += f" |{eb}<|{en}{alias}|{eb}>|n"

        return out

