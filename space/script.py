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

        if sobj not in self.insertions:
           self.insertions.append(sobj)
        cemit("space", f"{sobj.name} scheduled for insertion.")

    def del_object(self, sobj):
        if sobj in self.insertions:
            return

        if sobj not in self.deletions:
            sobj.deletions.append(sobj) 
        cemit("space", f"{sobj.name} scheduled for deletion.")

    """ Timer and data store """
    def at_script_creation(self) -> None:
        """Called once, when script is first created"""
        self.key = "space"
        self.desc = "Space script"
        self.interval = 2  # 2 sec tick
        self.has_state = False
        self.deletions = []
        self.insertions = []

    def load_state(self):
        global STATE

        with open(SPACEDB, "rb") as f:
            STATE = pickle.load(f)
        self.has_state = True if STATE else False

    def save_state(self):
        with open(SPACEDB, "wb") as f:
            pickle.dump(STATE, f)

    def get_status(self, player):
        tmp = f'{NAME} version {VERSION} Stats:'
        player.msg(tmp)
        player.msg("-" * len(tmp))
        player.msg(f'Is Loaded: {"True" if STATE else "False"}')
        player.msg(f'  # Ships: {len(STATE.ship_list)}')
        player.msg(f'# Objects: {len(STATE.object_list)}')

    def at_server_reload(self):
        cemit("space", "State saved.")
        self.save_state()


    def at_server_start(self):
        global STATE
       
        self.deletions = []
        self.insertions = []
        cemit("space", f"Initializing {NAME} {VERSION}...")
        self.has_state = False
        if os.path.isfile(SPACEDB):
            self.load_state()
            if not self.has_state:
                cemit("space", "|RFailed to initialize state handler.|n")
                self.active = False
                return
        else:
            STATE = SpaceInstance()
            self.has_state = True
            self.save_state()

        self.active = False
        if self.has_state:
            cemit("space", "Initialization was |GSUCCESSFUL|n.")
            cemit("space", f"Cycling is {'|GENABLED|n' if STATE.active else '|RDISABLED|n'}.")
        else:
            cemit("space", "Initialization was not successful.")
            return

        cemit("space", "Loading objects...")
        count = 12
        cemit("space", f"Done loading {count} object(s).")
        if not STATE.active:
            cemit("space", "Use \'|Csdb/start|n\' to enable cycling.")

    def at_repeat(self):
        for x in self.insertions:
            try:
                if x not in STATE.ship_list:
                    STATE.ship_list.append(x)
                self.insertions.remove(x)
                x.on_add()
            except Exception  as e:
                cemit("space", f"Error in at_repeat(): {e}.")

        #cemit("space", "PING")
        if STATE.active or True:
            for x in STATE.ship_list or []:
                try:
                    x.cycle()
                    cemit("space", f"Ship: {x.name}")
                except Exception as e:
                    cemit("space", f"Error in at_repeat(): {e}.")
                    continue

    def on_add(self, sobj: HSObject) -> None:
        cemit("space", f"{sobj} was added to the active list.")
        sobj.activate()


    def on_del(self, sobj: HSObject) -> None:
        cemit("space", f"{sobj} was removed from the active list.")
        sobj.deactivate()



def get_state():
    return STATE

