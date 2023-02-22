from enum import Enum
import pickle
from world.utils import cemit

class HSObjectType(Enum):
    GENERIC = 0
    PLANET = 1
    SHIP = 2
    JUMPGATE = 3
    RESOURCE = 4
    CARGOPOD = 5
    NEBULA = 6
    ASTEROIDS = 7
    END = 8

HSOT = HSObjectType


class SpaceInstance(object):
    ship_list = []
    object_list = []
    insertions = []
    deletions = []
    active = False
    clean = True
    interval = 2

    def __init__(self, *args):
        self.ship_list = []
        self.object_list = []
        self.insertions = []
        self.deletions = []
        self.active = False
        self.clean = False
        self.interval = 2
        self.save()
        self.load()
        self.save()


    def add_object_to_space(self, sobj):
        pass


    def remove_object_from_space(self, sobj):
        pass


    def load(self):
        with open("space/space.bin", "rb") as f:
            SpaceInstance = pickle.load(f)
        cemit("space", "LOAD")
        
    
    def save(self):
        with open("space/space.bin", "wb") as f:
            pickle.dump(SpaceInstance, f)
            cemit("space", "DUMP")
            
    
    def cycle(self):

        if self.insertions:
            pass            # add ship to space

        
        for sl in self.ship_list:
            try:
                sl.cycle()
            except Exception as e:
                    contiue
        if self.deletions:
            remove_object_from_space(sl)        


    
class HSObject:
    def __init__(self, **args):
        self.type = args.get('name', 'Unknown')
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

SPACE = None
