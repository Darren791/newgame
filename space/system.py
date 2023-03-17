
'''
An array of systems that can exist for a ship.
In fact, the systems are stored in a linked list.
'''
from .types import HSOT, HSST, HSD
from world.utils import match_all

HSSystemTypes = (                                                                                                                                                                                                                           
    ("Reactor",        HSST.REACTOR),
    ("Life Support",     HSST.LIFE_SUPPORT),
    ("Internal Computer",  HSST.COMPUTER),
    ("Engines",        HSST.ENGINES),
    ("Sensor Array",     HSST.SENSORS),
    ("Maneuv. Thrusters",  HSST.THRUSTERS),
    ("Fore Shield",      HSST.FORE_SHIELD),
    ("Aft Shield",     HSST.AFT_SHIELD),
    ("Starboard Shield",   HSST.STARBOARD_SHIELD),
    ("Port Shield",      HSST.PORT_SHIELD),
    ("Fuel System",      HSST.FUEL_SYSTEM),
    ("Jump Drive",     HSST.JUMP_DRIVE),
    ("Comm. Array",      HSST.COMM),
    ("Cloaking Device",    HSST.CLOAK),
    ("Tachyon Sensor Array", HSST.TACHYON),
    ("Fictional System",   HSST.FICTIONAL),
    ("Damage Control",   HSST.DAMCON),
    ("Comm. Jammer",     HSST.JAMMER),
    ("Tractor Beam",     HSST.TRACTOR)
    )                                                                                                                                                                                              
    
class SystemsHandler(object):
    num_systems = 0
    power_use = 0
        
    def match_system_by_name(self, target):
        ret = match_all((x[0] for x in HSSystemTypes), target)
        return ret

    def match_system_by_type(self, val):
        return [x for x in self.systems if x.type == val]

    def has(self, res):
        ret = [x for x in self.systems if x.type == val
                ]
    def __init__(self, obj):
        self.obj = obj
        self.num_systems = 0
        self.power_use = 0
        self.systems = []
        
    
    def __eq__(self, what):
        pass
    
    def get_name(self):
        return self.name

    def add_system(self, system):
        self.systems.append(system)
    
    def del_system(self, system):
        self.systems.remove(system)
    
    def cycle(self):
        for x in self.systems:
            try:
               x.cycle()
            except Exception as e:
                cemit("space", f"Error {e} in SystemsHandler.do_cycle()")

    def update_power_use(self):
        pass
    
    def save_to_file(self):
        pass
    
    def bump_system(self, system, index):
        pass
    
    def get_power_use(self):
        pass
    
    def num_systems(self):
        pass
    
    def new_system(self, what):
        pass
    
    def get_system(self, what):
        pass
    
    def get_system_by_name(self, name):
        pass
    
    def get_head(self):
        pass

    def get_random_system(self):
        pass
        
        
    def get_eng_system_name(self, sys):
        for x in self.systems:
            if x.name == sys:
                return x.name
        
        return None
    
    def get_eng_system_type(self, sys):
        for x in self.systems:
            if x.type == sys:
                return x.type

        return HSST.NONE
        
