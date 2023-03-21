"""
"""
from evennia.utils import lazy_property
from world.utils import cemit
from .vector import HSVector
from .types import HSOT
from .system import SystemsHandler

DBVERSION = "1.0"
SPACEDB = "space/space.bin"
NAME = "eSpace"
VERSION = "0.2"
SCRIPT = "space_script"

class SpaceInstance():
    """
    """

    ship_list = set()
    object_list = set()
    insertions = set()
    deletions = set()
    active = False
    clean = True
    version = DBVERSION
    loaded = False

    def __init__(self, *args):
        self.ship_list = set()
        self.object_list = set()
        self.insertions = set()
        self.deletions = set()
        self.active = False
        self.clean = False

    def cycle(self):
        if self.insertions:
            pass  # add ship to space

        for sl in self.ship_list:
            try:
                sl.cycle()
            except Exception as e:
                cemit("space", f"Exception: {e}.")
                continue
        
        if self.deletions:
            pass


class HSObject:

    @lazy_property
    def systems(self):
        return SystemsHandler(self)

    def __init__(self, **args):
        self.type = HSOT.GENERIC
        self.key = 0
        self.set_motion_vector()

    def set_motion_vector(self, i=0, j=0, k=0):
        self.motion_vector = HSVector(i, j, k)


    def on_activate(self):
        pass

    def on_deactivate(self):
        pass

    def on_add(self):
        cemit("space", f"{self} was added to the active list.")

    def on_delete(self):
        pass

    def cycle(self):
        pass


class HSShip(HSObject):
    type = HSOT.SHIP
    ident = None
    target = None
    current_xyheading = 0
    desired_xyheading = 0
    current_zheading = 0
    desired_zheading = 0
    current_roll = 0
    desired_roll = 0
    hull_points = 1
    map_range = 1000
    drop_status = 0
    dock_status = 0
    age = 0
    heat_pool = 10
    heat_points = 0
    reactor_online = False
    ghosted = False
    in_space = True
    docked = False
    dropped = False
    destroyed = False

    @lazy_property
    def systems(self):
        return SystemsHandler(self)

    def is_active(self):
        if (not self.docked and not self.dropped and
                self.in_space and not self.destroyed):
            return True

        return False

    def cycle(self):
        self.systems.cycle()
