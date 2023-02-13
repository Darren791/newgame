"""
Account

The Account represents the game "account" and each login has only one
Account object. An Account is what chats on default channels but has no
other in-game-world existence. Rather the Account puppets Objects (such
as Characters) in order to actually participate in the game world.


Guest

Guest accounts are simple low-level accounts that are created/deleted
on the fly and allows users to test the game without the commitment
of a full registration. Guest accounts are deactivated by default; to
activate them, add the following line to your settings file:

    GUEST_ENABLED = True

You will also need to modify the connection screen to reflect the
possibility to connect with a guest account. The setting file accepts
several more options for customizing the Guest account system.

"""

from evennia import DefaultAccount, DefaultGuest
from evennia.comms.models import Msg
from evennia.utils import time_format
from .mixins.types import TypeMixins
from .mixins.names import NameMixins
from .mixins.decorator import DecoratorMixins
from .mixins.player import PlayerMixins
from world.utils import cemit_debug
from django.conf import settings

import time
import datetime

class Account(DecoratorMixins, NameMixins, PlayerMixins, TypeMixins, DefaultAccount):
    """
    This class describes the actual OOC account (i.e. the user connecting
    to the MUD). It does NOT have visual appearance in the game world (that
    is handled by the character which is connected to this). Comm channels
    are attended/joined using this object.

    It can be useful e.g. for storing configuration options for your game, but
    should generally not hold any character-related info (that's best handled
    on the character level).

    Can be set using BASE_ACCOUNT_TYPECLASS.


    * available properties

     key (string) - name of account
     name (string)- wrapper for user.username
     aliases (list of strings) - aliases to the object. Will be saved to database as AliasDB entries but returned as strings.
     dbref (int, read-only) - unique #id-number. Also "id" can be used.
     date_created (string) - time stamp of object creation
     permissions (list of strings) - list of permission strings

     user (User, read-only) - django User authorization object
     obj (Object) - game object controlled by account. 'character' can also be used.
     sessions (list of Sessions) - sessions connected to this account
     is_superuser (bool, read-only) - if the connected user is a superuser

    * Handlers

     locks - lock-handler: use locks.add() to add new lock strings
     db - attribute-handler: store/retrieve database attributes on this self.db.myattr=val, val=self.db.myattr
     ndb - non-persistent attribute handler: same as db but does not create a database entry when storing data
     scripts - script-handler. Add new scripts to object with scripts.add()
     cmdset - cmdset-handler. Use cmdset.add() to add new cmdsets to object
     nicks - nick-handler. New nicks with nicks.add().

    * Helper methods

     msg(text=None, **kwargs)
     execute_cmd(raw_string, session=None)
     search(ostring, global_search=False, attribute_name=None, use_nicks=False, location=None, ignore_errors=False, account=False)
     is_typeclass(typeclass, exact=False)
     swap_typeclass(new_typeclass, clean_attributes=False, no_default=True)
     access(accessing_obj, access_type='read', default=False)
     check_permstring(permstring)

    * Hook methods (when re-implementation, remember methods need to have self as first arg)

     basetype_setup()
     at_account_creation()

     - note that the following hooks are also found on Objects and are
       usually handled on the character level:

     at_init()
     at_cmdset_get(**kwargs)
     at_first_login()
     at_post_login(session=None)
     at_disconnect()
     at_message_receive()
     at_message_send()
     at_server_reload()
     at_server_shutdown()

    """

    @property
    def is_account(self):
        return True

    @property
    def is_guest_account(self):
        return False

    def at_account_creation(self):
        """
        This is called once, the very first time
        the player is created (i.e. first time they
        register with the game). It's a good place
        to store attributes all players should have,
        like configuration values etc.
        """
        # set an (empty) attribute holding the characters this player has
        lockstring = "attrread:perm(Wizards);attredit:perm(Wizards);attrcreate:perm(Wizards)"
        self.attributes.add("_playable_characters", [], lockstring=lockstring)
        self.attributes.add("_jnotes", [], lockstring=lockstring)
        self.attributes.add("lastsite", [])
        self.attributes.add("friends_list", None)
        self.tags.add("new", category="flags")
        self.options_dict = dict(settings.OPTIONS_ACCOUNT_DEFAULT)
        

    def do_lastlog(self, session):
        if session is None:
            return
            
        # LastSite data is stored in a DB attribute as a list
        # of tuples (ip, datetime, character). If this attribute
        # isn't set on the account, default to an empty list.
        lastsite = self.db.lastsite or []

        # Insert the current record at the head of the list.
        lastsite.insert(0, (session.address, int(time.time()), self.puppet.key if self.puppet else 'None'))

        # If the list has grown longer than the max length we defined
        # in settings, then pop the oldest record.
        if len(lastsite) > settings.MAX_LOGIN_RECORDS:
            lastsite.pop()

        # Save it. This is only needed if the DB attribute
        # wasn't set and we had to default to an empty list.
        self.db.lastsite = lastsite

        # Could use `inherits_from(self, Guest)` here instead
        # but this way is much faster.
        if self.is_guest_account:
            return

        # Retrieve the previous connection data, which should
        # be the 1st record in the list. If there was no
        # previous connection than we use the current one instead,
        # which will be the 0th record.
        former = self.db.lastsite[1 if len(lastsite) > 1 else 0]

        if hasattr(self, 'options') and self.options.get("lastlog_elapsed_time", False):
            now = time.time() - former[1]
            self.msg(f"You last connected {time_format(now, 4)} ago from {former[0]}.")
        else:
            now = datetime.date.fromtimestamp(former[1])
            self.msg(f"You last connected on {now.strftime('%a, %d %b %y %H:%M')} from {former[0]}.")

    def get_all_mail(self):
        msgs = Msg.objects.get_by_tag(category="mail").filter(db_receivers_accounts=self)
        if msgs.count() == 0:
            self.msg("You have no unread mail.")
            return

        count = 0
        for x in msgs:
            if x.tags.get("U"):
                count += 1
        self.msg(f"You have {msgs.count()} mail message(s), {count} unread.")

    def at_post_login(self, session=None):
        super().at_post_login(session)

        self.do_lastlog(session)
        self.get_all_mail()
        #self.get_boards()
        #self.get_messages()
        #self.get_jobs()

    
class Guest(NameMixins, TypeMixins, DefaultGuest):
    """
    This class is used for guest logins. Unlike Accounts, Guests and their
    characters are deleted after disconnection.
    """

    @property
    def is_guest_account(self):
        return True

    def is_blocking(self, who):
        return False
