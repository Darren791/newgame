"""
Characters

Characters are (by default) Objects setup to be puppeted by Accounts.
They are what you "see" in game. The Character class in this module
is setup to be the "default" character type created by the default
creation commands.

"""
from evennia import DefaultCharacter
from .mixins.types import TypeMixins
from .mixins.names import NameMixins
from .mixins.player import PlayerMixins
from .mixins.decorator import DecoratorMixins
from .mixins.messages import MessageMixins

from .ilocks import iLockManager


from evennia.utils import lazy_property
from django.conf import settings
from keys.managers import KeyHandler
from chargen.attributes import match_attribute


class Character(
    MessageMixins,
    NameMixins,
    PlayerMixins,
    TypeMixins,
    DecoratorMixins,
    DefaultCharacter
):
    """
    The Character defaults to reimplementing some of base Object's hook methods with the
    following functionality:

    at_basetype_setup - always assigns the DefaultCmdSet to this object type
                    (important!)sets locks so character cannot be picked up
                    and its commands only be called by itself, not anyone else.
                    (to change things, use at_object_creation() instead).
    at_after_move(source_location) - Launches the "look" command after every move.
    at_post_unpuppet(account) -  when Account disconnects from the Character, we
                    store the current location in the pre_logout_location Attribute and
                    move it to a None-location so the "unpuppeted" character
                    object does not need to stay on grid. Echoes "Account has disconnected"
                    to the room.
    at_pre_puppet - Just before Account re-connects, retrieves the character's
                    pre_logout_location Attribute and move it back on the grid.
    at_post_puppet - Echoes "AccountName has entered the game" to the room.

    """

    @property
    def typestr(self):
        return 'C'

    @lazy_property
    def ilocks(self):
        return iLockManager(self)

    @property
    def is_character(self):
        return True

    @property
    def is_guest(self):
        return False

    @property
    def owner_tag(self):
        return f"#{self.id}"

    @property
    def gender(self):
        return self.db.gender or 'neuter'

    @property
    def options(self):
        if hasattr(self.account, 'options'):
            return self.account.options
        return None

    @property
    def session(self):
        if a := self.sessions.all():
            return a[0]
        return None

    @property
    def screenwidth(self):
        if session := self.session:
            return session.protocol_flags.get(
                'SCREENWIDTH', {0: settings.CLIENT_DEFAULT_WIDTH}
            )[0]
        return settings.CLIENT_DEFAULT_WIDTH

    def at_before_puppet(self, account, session=None, **kwargs):
        try:
            tmp = self.options
            tmp = self.account.options
        except:
            pass

    def at_post_unpuppet(self, account, session=None, **kwargs):
        # Clear places.
        if table := self.db.sitting_at_table or None:
            table.leave(self)
        if console := self.db.console or None:
            self.attributes.remove('console')
            console.attributes.remove('user')
            console.announce_unman(self)
            
    @lazy_property
    def keys(self):
        return KeyHandler(self)

    def at_before_move(self, destination):
        if destination.check_banned(self):
            self.msg('You have been banned from entering that room.')
            return False

        return super().at_before_move(destination)

    def at_after_move(self, source_location, **kwargs):
        table = self.db.sitting_at_table or None
        if table and source_location != self.location:
            table.leave(self)

        if self.ndb.following and self.ndb.following.location != self.location:
            self.stop_follow()

        console = self.db.console or None
        if console:
            self.attributes.remove('console')
            console.attributes.remove('user')
            console.announce_unman(self)


        super().at_after_move(source_location, **kwargs)

    def get_cg_attr(self, key, value):
        return ""
