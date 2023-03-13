from enum import Enum

class HSSystemType(Enum):
    ENGINES     = 0
    COMPUTER = 1
    SENSORS = 2
    LIFE_SUPPORT = 3
    REACTOR = 4
    THRUSTERS = 5
    FORE_SHIELD = 6
    AFT_SHIELD = 7
    STARBOARD_SHIELD = 8
    PORT_SHIELD = 9
    FUEL_SYSTEM = 10
    JUMP_DRIVE = 11
    COMM = 12
    NOTYPE = 13
    CLOAK = 14
    TACHYON = 15
    FICTIONAL = 16
    DAMCON = 17
    JAMMER = 18
    TRACTOR = 19
HSST = HSSystemType

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

class HSDamage(Enum):
    NONE = 0
    LIGHT = 1
    MEDIUM = 2
    HEAVY = 3
    INOPERABLE = 4
HSD = HSDamage

class HSObjectType(Enum):
    GENERIC = 0
    PLANET = 1
    SHIP = 2
    JUMPGATE = 3
    RESOURCE = 4
    CARGOPOD = 5
    NEBULA = 6
    ASTEROIDS = 7
HSOT = HSObjectType

