from evennia import DefaultScript

# HSUniverse: A container for ships. A unique instance of space e.g. Simspace, Realspace.
# HSObject: Base HSpace object class.

class SpaceScript(DefaultScript):
    """ Timer and data store """
    universes: list =  None
    
    def at_script_creation(self) -> None:
        """Called once, when script is first created"""
        self.key = "space"
        self.desc = "Space script"
        self.interval = 2  # 2 sec tick
        self.universes = []
        
    def at_repeat(self):
        """ Called once every tick """
        for x in self.universes:
            """ Cycle through each universe, updating all objects """
            try:
                x.cycle()
            except Exception as e:
                # add logging here to channel
                log_to_channel("space", {self.name}({self.id}): {e})
                continue
    
    def on_add(self, sobj: HSObject) -> None:
        sobj.activate()
        self.sync()
          
    def on_del(self, sobj: HSObject) -> None:
        sobj.deactivate()
        self.sync()
    
    def add_universe(self, sobj: HSUniverse=None) -> bool:
        if sobj and sobj not in self.universes:
            self.universes.append(sobj)
            self.on_add(sobj)
            return True

        return False

    def del_universe(self, sobj: HSUniverse=None) -> bool:
        if index := self.universes.index(sobj):
            self.universes.remove(index)
            self.on_del(sobj)
            return True
        
        return False