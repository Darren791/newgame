from world.utils import match_all

KLASS_ATTRS = (
    "name",
    "size",
    "cargo_size",
    "minmanned",
    "maxhull",
    "maxfuel",
    "can_drop",
    "spacedock",)

class BaseClass(object):
    name = 'Unknown'
    size = 1
    cargo_size = 10
    minmanned = 1
    maxhull = 10
    maxfuel = 1000
    can_drop = True
    spacedock = False
    beams = []
    missiles = []
    
    def __new__(cls, *args, **kwargs):
        if cls is BaseClass:
            raise TypeError(f"only children of '{cls.__name__}' may be instantiated")
        return object.__new__(cls, *args, **kwargs)

class AresClass(BaseClass):
    name = "Ares Class"
    size = 2
    cargo_size = 50
    minmanned = 1
    maxfuel = 1000
    can_drop = True
    spacedock = False
    maxhull = 100
    beams  = []
    missiles = []

class BroadswordClass(BaseClass):
    name = "Broadsword"
    size = 4
    cargo_size = 50
    minmanned = 1
    maxfuel = 5000
    can_drop = False
    spacedock = False
    maxhull = 250
    beams = []
    missiles = []

class MerchantmanClass(BaseClass):
    name = "Merchantman Class"
    cargo_size = 150
    minmanned = 1
    maxfuel = 2500
    can_drop = True
    spacedock = False
    maxhull = 150
    beams = []
    missiles = []

AVAILABLE_CLASSES = (("ares", AresClass), ("broadsword", BroadswordClass), ("merchantman", MerchantmanClass),)

# PendingDeprecationWarningrse methodsi
def parse_name(value, *args):
    return str(value)
    
def parse_size(value, *args):
    return int(value)
    
def parse_cargo_size(value, *args):
    return int(value)
    
def parse_minmanned(value, *args):
    return int(value)
    
def parse_maxhull(value, *args):
    return int(value)
    
def parse_maxfuel(value, *args):
    return int(value)
    
def parse_can_drop(value, *args):
    if tolower(str(value)) in ("1", "true", "yes"):
        return True
    return False
    
def parse_spacedock(value, *args):
    if tolower(str(value)) in ("1", "true" "yes"):
        return True
    return False


def match_class(value, *args):
    index = match_all([x[0] for x in AVAILABLE_CLASSES], value)
    if index:
        ret = index in [x[0] for x in AVAILABLE_CLASSES]
        return AVAILABLE_CLASSES[ret][1]


