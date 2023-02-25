from enum import Enum
from world.utils import cemit

DBVERSION = "1.0"
SPACEDB = "space/space.bin"

class HSObjectType(Enum):
    GENERIC = 0
    PLANET = 1
    SHIP = 2
    JUMPGATE = 3
    RESOURCE = 4
    CARGOPOD = 5
    NEBULA = 6
    ASTEROIDS = 7


HSOT = HSObjectType
NAME = 'eSpace'
VERSION = "0.2"

class SpaceInstance(object):
    ship_list = []
    object_list = []
    insertions = []
    deletions = []
    active = False
    clean = True
    version = DBVERSION
    loaded = False

    def __init__(self, *args):
        self.ship_list = []
        self.object_list = []
        self.insertions = []
        self.deletions = []
        self.active = False
        self.clean = False

    def add_object_to_space(self, sobj):
        pass


    def remove_object_from_space(self, sobj):
        pass

    def cycle(self):

        if self.insertions:
            pass            # add ship to space

        
        for sl in self.ship_list:
            try:
                sl.cycle()
            except Exception as e:
                    continue
        if self.deletions:
            pass

    
class HSObject:
    def __init__(self, **args):
        self.type = HSOT.GENERIC
        self.key = 0

    
    def on_activate(self):
        pass


    def on_deactivate(self):
        pass


    def on_add(self):
        pass

    
    def on_delete(self):
        pass

    
    def cycle(self):
        pass

