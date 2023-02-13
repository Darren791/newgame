"""
Places for tabletalk
"""

from evennia import DefaultObject
from .cmdset_places import DefaultCmdSet, SittingCmdSet
from evennia.utils.utils import make_iter
from evennia.utils import inherits_from
import world.utils as utils

from typeclasses.rooms import Room
from typeclasses.mixins.messages import MessageMixins
from typeclasses.mixins.ownership import OwnerMixins
from typeclasses.mixins.types import TypeMixins
from typeclasses.mixins.names import NameMixins


class Place(MessageMixins, NameMixins, OwnerMixins, TypeMixins, DefaultObject):
    """
    Class for placed objects that allow the 'tabletalk' command.
    """
    PLACE_LOCKS = "call:true();control:perm(Wizards);delete:perm(Wizards);examine:perm(Builders);" \
                  "get:perm(Builders);puppet:perm(Immortals);tell:all();view:all()"

    @property
    def is_place(self):
        return True

    def at_object_creation(self, **kwargs):
        """
        Run at Place creation.
        """
        self.init_owner(**kwargs)
        super().at_object_creation()
        self.db.occupants = []
        self.db.max_spots = 6
        self.db.desc = 'A place for a group of people to chat privately. Dropping it in a room will make it part of the room.'
        # locks so characters cannot 'get' it
        self.locks.add(self.PLACE_LOCKS)
        self.at_init()      
        
    def leave(self, character):
        """
        Character leaving the table.
        """
        occupants = self.db.occupants or []
        if character in occupants:
            occupants.remove(character)
            self.db.occupants = occupants
            character.cmdset.delete(SittingCmdSet)
            del character.db.sitting_at_table
            self.generate_message("depart", character)
            return

    def join(self, character):
        """
        Character joins the table
        """
        occupants = self.db.occupants or []
        character.cmdset.add(SittingCmdSet, permanent=True)
        character.db.sitting_at_table = self
        occupants.append(character)
        self.db.occupants = occupants
        self.generate_message("join", character)

    def tt_msg(self, message, from_obj, exclude=None, emit=False, options=None):
        """
        Send msg to characters at table. Note that if this method was simply named
        'msg' rather than tt_msg, it would be called by msg_contents in rooms, causing
        characters at the places to receive redundant messages, since they are still
        objects in the room as well.
        """
        # utils.make_iter checks to see if an object is a list, set, etc, and encloses it in a list if not
        # needed so that 'ob not in exclude' can function if we're just passed a character
        exclude = make_iter(exclude)
        for ob in self.db.occupants:
            if ob.is_blocking(from_obj):
                continue

            if ob not in exclude:
                if emit and ob.tags.get("emit_label"):
                    formatted_message = "|w[|c%s|w]|n %s" % (from_obj, message)
                else:
                    formatted_message = message
                ob.msg(formatted_message, from_obj=from_obj, options=options)

    def at_after_move(self, source_location, **kwargs):
        """If new location is not our wearer, remove."""
        
        location = self.location
            
        # first, remove ourself from the source location's places, if it exists
        #if source_location and inherits_from(source_location, "typeclasses.rooms.Room"):
        if source_location and inherits_from(source_location, Room):
            if source_location.db.places and self in source_location.db.places:
                source_location.db.places.remove(self)
        # if location is a room, add cmdset
        # if location and inherits_from(location, "typeclasses.rooms.Room"):
        if location and inherits_from(location, Room):
            places = location.db.places or []
            self.cmdset.add_default(DefaultCmdSet, permanent=True)
            places.append(self)
            location.db.places = places
        else:
            self.cmdset.delete_default()

    @property
    def max_spots(self):
        return self.db.max_spots or 0
        
    @property
    def occupants(self):
        return self.db.occupants or []

    @property
    def remaining_spots(self):
        return self.max_spots - len(self.occupants)
                
    def return_appearance(self, looker, **kwargs):
        output = "%s\n" % self.name_format(looker)
        output += "%s\n---\n" % self.db.desc or ''
        
        o = self.db.occupants or []
        if o:
            output += "Players seated here:\n%s." % utils.itemize([x.key for x in o])

        return output
