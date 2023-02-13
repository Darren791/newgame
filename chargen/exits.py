"""
Exits

Exits are connectors between Rooms. An exit always has a destination property
set and has a single command defined on itself with the same name as its key,
for allowing Characters to traverse the exit to its destination.

"""
from typeclasses.exits import Exit

class CgenExit(Exit):
    """
    """
    

    def can_traverse(self, character):
        if self.destination.check_banned(character):
            character.msg("You have been banned from entering that room.")
            ret = False
        elif self.access(character, 'traverse'):
            self.generate_message("no_go", character)
            # we may traverse the exit.
            ret = False
        elif character.has_key_for(self):
            character.msg(f"You unlock {self.key} with your key.")
            ret = True
        if ret:
            self.generate_message("leave", character)
        
        return ret
        
    def at_traverse(self, traversing_object, target_location, **kwargs):
        """
        This implements the actual traversal. The traverse lock has
        already been checked (in the Exit command) at this point.

        Args:
            traversing_object (Object): Object traversing us.
            target_location (Object): Where target is going.
            **kwargs (dict): Arbitrary, optional arguments for users
                overriding the call (unused by default).

        """
        source_location = traversing_object.location
        if traversing_object.move_to(target_location):
            if quiet := kwargs.get("quiet", False):
                self.generate_message("leave", traversing_object, location=self.location, iobj=target_location)
            self.at_after_traverse(traversing_object, source_location, **kwargs)
        else:
            # No shorthand error message. Call hook.
            self.at_failed_traverse(traversing_object, **kwargs)
        #super().at_traverse(traversing_object, target_location, **kwargs)

    def at_failed_traverse(self, traversing_object, **kwargs):
        """
        Overloads the default hook to implement a simple default error message.

        Args:
            traversing_object (Object): The object that failed traversing us.
            **kwargs (dict): Arbitrary, optional arguments for users
                overriding the call (unused by default).

        """
        if not kwargs.get("quiet", False):
            self.generate_message("nogo", traversing_object)
        super().at_failed_traverse(traversing_object)

    def at_after_traverse(self, traversing_object, source_location, **kwargs):
        if kwargs.get("quiet", False):
            return True

        location = traversing_object.location
        location and location.generate_message("arrive", traversing_object, location=location, iobj=source_location)
        super().at_after_traverse(traversing_object, source_location, **kwargs)

    def at_object_creation(self, **kwargs):
        self.init_owner()
        super().at_object_creation(**kwargs)
        
