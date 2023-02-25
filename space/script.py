from evennia import DefaultScript
from .objects import DBVERSION, SPACEDB, SpaceInstance
from world.utils import cemit
from .objects import HSObject
import pickle
import os.path

STATE = None

class SpaceScript(DefaultScript):
    """ Timer and data store """
    def at_script_creation(self) -> None:
        """Called once, when script is first created"""
        self.key = "space"
        self.desc = "Space script"
        self.interval = 2  # 2 sec tick

    def load_state(self):
        global STATE

        with open(SPACEDB, "rb") as f:
            STATE = pickle.load(f)

    def save_state(self):
        with open(SPACEDB, "wb") as f:
            pickle.dump(STATE, f)

    def get_status(self, player):
        player.msg("STATS:")
        player.msg(f"STATE={STATE}")
        player.msg(f"Ships={STATE.ship_list}")

    def at_server_start(self):
        global STATE

        if os.path.isfile(SPACEDB):
            self.load_state()
        else:
            STATE = SpaceInstance();
            self.save_state()

        self.active = False
        cemit("space", f"STATE={STATE}")

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

