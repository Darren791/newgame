from evennia import DefaultScript
from .objects import DBVERSION, SPACEDB, SpaceInstance, NAME, VERSION, HSOT
from world.utils import cemit
from .objects import HSObject
import pickle
import os.path

# Statee data
STATE = None

class SpaceScript(DefaultScript):

    def add_object(self, sobj):
        if sobj in self.deletions:
            return

        if sobj.type == HSOT.SHIP:
            if sobj not in self.ship_list:
                self.ship_list.append(sobj)
                self.on_add(sobj)
                sobj.on_add()
        else:
            if sobj not in self.object_list:
                self.object_list.append(sobj)
                self.on_add(sobj)
                sobj.on_add()



    def del_object(self, sobj):
        if sobj.type == HSOT.SHIP:
            if sobj in self.ship_list:
                self.ship_list.remove(sobj)
                self.on_del(sobj)
                sobj.on_del()
            else:
                if sobj in self.object_list:
                    self.object_list.remove(sobj)
                    self.on_del(sobj)
                    sobj.on_del()

    """ Timer and data store """
    def at_script_creation(self) -> None:
        """Called once, when script is first created"""
        self.key = "space"
        self.desc = "Space script"
        self.interval = 2  # 2 sec tick
        self.has_state = False

    def load_state(self):
        global STATE

        with open(SPACEDB, "rb") as f:
            STATE = pickle.load(f)
        self.has_state = True if STATE else False

    def save_state(self):
        with open(SPACEDB, "wb") as f:
            pickle.dump(STATE, f)

    def get_status(self, player):
        player.msg("STATS:")
        player.msg(f"STATE={STATE}")
        player.msg(f"Ships={STATE.ship_list}")

    def at_server_start(self):
        global STATE
       
        cemit("space", f"Initializing {NAME} {VERSION}...")
        self.has_state = False
        if os.path.isfile(SPACEDB):
            self.load_state()
            if not self.has_state:
                cemit("space", "Failed to initialize state handler.")
                self.active = False
                return
        else:
            STATE = SpaceInstance();
            self.has_state = True
            self.save_state()

        self.active = False
        if self.has_state:
            cemit("space", "Initialization successful. Not cycling.")
        else:
            cemit("space", "Initialization was not successful.")

    def at_repeat(self):
        if self.active:
            cemit("space", "PING")
            for x in STATE.ship_list or []:
                try:
                    x.cycle()
                except Exception as e:
                    cemit("space", f"Exception in at_repeat(): {e}.")
                    continue

    def on_add(self, sobj: HSObject) -> None:
        sobj.activate()


    def on_del(self, sobj: HSObject) -> None:
        sobj.deactivate()



def get_state():
    return STATE

