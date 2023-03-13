
'''
An array of systems that can exist for a ship.
In fact, the systems are stored in a linked list.
'''
from .types import HSSystemTypes
    
class SystemsHandler(object):
    num_systems = 0
    power_use = 0
        
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
        pass
    
    def del_system(self, system):
        pass
    
    def do_cycle(self):
        pass

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
        