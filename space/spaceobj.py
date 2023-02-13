import constants as cons
import systems as systems
import script as script
import vector
import systems

class HSObject(object):
    name = 'Unknown'
    pos = [0.0, 0.0, 0.0]
    size = 1.0
    flags = 0x0
    toggles = 0x0
    systems = []
    
    

    @property
    def is_dropped(self):
        return (self.flags & cons.DROPPED) != 0
    
    @property
    def is_docked(self):
        return (self.flags & cons.DOCKED) != 0
    
    @property
    def is_gating(self):
        return (self.flags & cons.GATEING) != 0
    
    @property
    def is_destroyed(self):
        return (self.flags & cons.DESTROYED) != 0
    
    @property
    def is_ship(self):
        return (self.flags & cons.HS_SHIP) != 0    

    @property
    def is_celestial(self):
        return (self.flags & cons.HS_CELESTIAL) != 0

    @property   
    def is_missile(self):
        return (self.flags & cons.HS_MISSILE) != 0
    
    @property
    def is_debris(self):
        return (self.flags & cons.HS_DEBRIS) != 0
    
    @property
    def is_gate(self):
        return (self.flags & cons.HS.MISSILE) != 0
    
class HSShip(HSObject):
    ident = None
    target = None
    current_xyheading: int = 0
    desired_xyheading: int = 0
    current_zheading: int = 0
    desired_zheading: int = 0
    current_roll: int = 0
    dock_status:int = 0
    drop_status:int = 0
    motion_vector = None
    systems = HSSystemArray()
    
def initialize(self):
    self.current_xyheading = 0.0
    self.desired_xyheading = 0.0
    self.current_zheading = 0.0
    self.desired_zheading = 0.0
    self.current_roll = 0.0
    self.desired_roll = 0.0
    self.flags = cons.HS_SHIP
    self.systems = HSSystemArray()
    self.set_heading_vector(0, 0, 0)    

def set_heading_vector(self, i=0, j=0, k=0):
    vec = HSVector(i, j, k)
    self.motion_vector = vec

class HSCelestial(HSObject):
    pass
    
class HSDebris(HSObject):
    pass
    
class HSMissile(HSObject):
    pass    

class HSGate(HSObject):
    pass

