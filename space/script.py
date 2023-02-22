from evennia import DefaultScript
from .objects import SPACE
from world.utils import cemit
from os.path import exists
from .objects import HSObject
import pickle

class SpaceScript(DefaultScript):
    """ Timer and data store """

    def at_script_creation(self) -> None:
        """Called once, when script is first created"""
        self.key = "space"
        self.desc = "Space script"
        self.interval = 2  # 2 sec tick
        self.universes = []

    
    def at_server_start(self):
        cemit("space", "START")
        global SPACE

        if not SPACE:
            if exists("space/space.bin"):
                with open("space/space.bin", "rb") as f:
                    SPACE = pickle.load(f)
                    cemit("space", "State file read")
            else:
                SPACE = SPACE.new()
                cemit("space", "State file not found. Initializing default.")

   
    def at_repeat(self):
        """ Called once every tick """
        #cemit("space", "TICK")
        for x in SPACE.ship_list:
            """ Cycle through each universe, updating all objects """
            try:
                x.cycle()
            except Exception as e:
                # add logging here to channel
                continue

    def on_add(self, sobj: HSObject) -> None:
        sobj.activate()
        self.sync()


    def on_del(self, sobj: HSObject) -> None:
        sobj.deactivate()
        self.sync()

