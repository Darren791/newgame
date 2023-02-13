from world.genders import _GENDER_PRONOUN_MAP as PRO
from evennia.utils.ansi import ANSIString

class NameMixins(object):

    def get_display_name(self, looker):
        """
        Displays the name of the object in a viewer-aware manner.

        Args:
            looker (TypedObject): The object or account that is looking
                at/getting inforamtion for this object.

        Returns:
            name (str): A string containing the name of the object,
                including the DBREF if this user is privileged to control
                said object.

        Notes:
            This function could be extended to change how object names
            appear to users in character, but be wary. This function
            does not change an object's keys or aliases when
            searching, and is expected to produce something useful for
            builders.

        """
        if self.locks.check_lockstring(looker, "perm(Builder)"):
            return f"{self.name}(#{self.id})"
        return self.name

    # Like get_display_name but doesn't check permissions.  Sometimes you
    # just want the name and dbref.

    @property
    def name_and_dbref(self):
        return f"{self.key}(#{self.id})"

    # Returns the object name and shortest alias
    @property
    def name_and_alias(self):
        if a := self.aliases.all():
            return f"{self.key} ({a[0]})"
        return self.key

    def shortest_alias(self):
        if a := self.aliases.all():
            return sorted(a, key=len)[0]
        return None
    
    def format_name(self, width=80):
        return ANSIString(self.title()).ljust(width)

    def name_format(self, fmt=0):
        return self.title()

    def pronoun(self, pro="ps"):
        if gender := self.db.pronouns:
            return gender[pro] if pro in gender.keys() else ""
        return PRO["neuter"][pro] if pro in PRO["neuter"].keys() else ""

    def title(self):
        return self.key
