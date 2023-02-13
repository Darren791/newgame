from typeclasses.rooms import Room
from .commands import ChargenBaseCmdSet
from .attributes import initialize_character
from world.utils import cemit_debug

class CGenRoom(Room):
    def at_init(self):
        self.cmdset.add(ChargenBaseCmdSet)
    
    def at_object_receive(self, obj, source):
        if not obj.is_character:
            return

        if not obj.tags.get(category="chargen"):
            obj.msg("Initializing...")
            try:
                initialize_character(obj)
                cemit_debug("CG", f"{obj.name} was initialized.")
            except:
                cemit_debug("CG", f"{obj.name} failed to initialize!")
                obj.msg("Oops.")
                return
        else:
            cemit_debug("CG", f"{obj.name} has already been initialized.")

        super().at_object_receive(obj, source)