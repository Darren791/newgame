from objects import HSObject
from universe import HSUniverse
from evennia.scripts.scripts import DefaultScript


class SpaceScript(DefaultScript):
    def at_script_creation(self):
        self.key = "space"
        self.desc = "Space storage and timer script."
        self.interval = 1
        self.universes = []
        
    def at_repeat(self) -> None:
        pass

    def add_universe(self, obj: HSUniverse) -> bool:
        l = self.universes or []
        l.append(obj)

    def remove_universe(self, obj: HSUniverse) -> bool:
        self.universes.remove(obj)

    def find_universe(self, obj: any) -> HSUniverse:
        pass

    def find_object(self, uid: int = 0) -> HSObject:
        pass

    def all_universes(self):
        return self.universes or []
        