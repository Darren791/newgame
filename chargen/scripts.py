from evennia import DefaultScript
from world.utils import match_begin


class ChargenScript(DefaultScript):

    def at_start(self, **kwargs):
        pass

    def at_repeat(self, **kwargs):
        pass

    def at_script_creation(self):
        self.attributes = ("intelligence", "wisdom", "strength", "charisma", "dexterity", "stamina")

    def match_attribute(self, which):
        if found := match_begin(self.attributes, which, True):
            return found
        return None

    




