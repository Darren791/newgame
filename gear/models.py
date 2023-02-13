
"""
Basic gear module.
"""
from django.db import models

SLOT_HEAD = 0x01
SLOT_NECK = 0x02
SLOT_SHOULDERS = 0x04
SLOT_ARMS = 0x08
SLOT_WAIST = 0x10
SLOT_LEGS = 0x20
SLOT_FEET = 0x40
SLOT_CHEST = 0x80
SLOT_HANDS = 0x100

def gear_type(ob: any) -> int:
    pass

class GenericGear(models.Model):
    """
    Basic gear model.
    """

class GenericAmmo(models.Model):
    """
    """


class Armor(GenericGear):
    """
    Basic armor.
    
    Layer: Top, Bottom, External
    SDP: int
    WORN: boolean
    SLOTS: int (bitmask of slots)
    DURABILITY: int
    WEAR: int (when wear == 0, weapon is no longer functional)

    """


class Weapon(GenericGear):
    """
    Extends basic gear to allow wearing.
    """

class MeleeWeapon(Weapon):
    pass

class RangedWeapon(Weapon):
    pass
