import constants as cons
# A universe

class HSUniverse(object):
    def __len__(self):
        return len(self.ship_list) 

    def __init__(self, name="Simspace"):
        self.name: str = name
        self.ship_list: list = []
        self.celestial_list: list = []
        self.debris_list: list = []
        self.gate_list: list = []
        self.missile_list: list = []

        self.id: int = len(self.object_list) + 1
        self.name: str = f"{name} {self.id}"
        self.active: bool = False

    def add_object(self, sobj):
        if not sobj or not hasattr(sobj, 'sdb'):
            return False
        attr = sobj.sdb or None
        if not attr:
            return False
        if attr == cons.HS_SHIP:
            self.add_ship(sobj)
        elif attr == cons.HS_CELESTIAL:
            self.add_celestial(sobj)
        elif attr == cons.HS_DEBRIS:
            self.add_debris(sobj)
        elif attr == cons.HS_GATE:
            self.add_gate(sobj)


    def add_ship(self, sobj=None) -> bool:
        if sobj and sobj not in self.ship_list:
            self.ship_list.append(sobj)
            self.on_add(sobj)
            return True

        return False

    def del_ship(self, sobj=None) -> bool:
        if index := self.ship_list.index(sobj):
            self.ship_list.remove(index)
            self.on_del(self, sobj)
            return True
        
        return False

    def add_object(self, sobj=None) -> bool:
        if sobj and sobj not in self.ship_list:
            self.ship_list.append(sobj)
            self.on_add(sobj)
            return True

        return False

    def del_ship(self, sobj=None) -> bool:
        if index := self.ship_list.index(sobj):
            self.ship_list.remove(index)
            self.on_del(self, sobj)
            return True
        
        return False



    def cycle(self):
        # Called each tick of the update task.
        for x in self.ship_list:
            try:
                x.cycle()
            except:
               continue 

    def on_init(self):
        pass


    def on_add(self, sobj):
        pass


    def on_del(self, sobj):
        pass
        
