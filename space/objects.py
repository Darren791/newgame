from enum import Enum

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

sObjectTypeCount: int = HSOT.END

class HSObject:
  
    def __init__(self, **args):
        self.id = len(ObjectList) + 1
        self.type = args.get('name', 'Unknown')
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

