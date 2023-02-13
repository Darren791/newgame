from evennia.utils import inherits_from
from evennia import DefaultRoom

from world.utils import match_all

CHARGEN_ID = 11
SKILLS = ()
STARTING_ATTRIBUTE_DICE = 12
STARTING_SKILL_DICE = 7


def chargen_room() -> any:
    ret = None

    try:
        return DefaultRoom.objects.get(pk=CHARGEN_ID)
    finally:
        return None


CHARGEN_ROOM = chargen_room()


# Attributes table.
ATTRIBUTES = (
  'strength',
  'perception',
  'endurance',
  'charisma',
  'intelligence',
  'agility',
  'luck',
)

# Skills table.
SKILLS = (
  ('athletics', 'strength'),
  ('barter', 'charisma'),
  ('big guns', 'endurance'),
  ('energy weapons', 'perception'),
  ('explosives', 'perception'),
  ('lockpick', 'perception'),
  ('medicine', 'intelligence'),
  ('melee weapons', 'strength'), 
)

# Perks table.
PERKS = ()


# Lookup an attribute by name.
def match_attribute(attr):
    return match_all(ATTRIBUTES)


# Lookup # a skill by name.
def match_skill(attr):
    return match_all([x[0] for x in SKILLS], attr)


# Lookup a perk by name.
def match_perk(attr):
    return match_all(PERKS, attr)


def initialize_character(char, **kwargs):
    if not char.is_character:
        return

    attrs = {}
    for x in ATTRIBUTES:
      attrs[x] = 0
    char.db.attrs = attrs


    attribute_dice = kwargs.get("attribute_dice", STARTING_ATTRIBUTE_DICE)
    char.db.attribute_dice = [attribute_dice, attribute_dice]

    skill_dice = kwargs.get("skill_dice", STARTING_SKILL_DICE)

    char.db.skill_dice = [skill_dice, skill_dice]


    char.db.skills = {}
    char.db.perks = {}
    char.tags.add("initialized", category="chargen")

