from evennia import default_cmds
from evennia.utils import logger, inherits_from
from .models import KeyDB
from evennia import ObjectDB, DefaultExit
from world.pmatch import pmatch
import world.headers as headers
from .api import match_key
from django.db.models.signals import post_save, pre_delete, post_init, post_delete
from world.utils import cemit_debug
from evennia.utils import logger
from typeclasses.accounts import Guest


class CmdKey(default_cmds.MuxCommand):
    """
        Manage your keyring.

        Your keyring contains virtual keys which allow you to pass through
        specific exits, effectively bypassing any locks in effect on the
        exit.  This was primarily intended for private rooms, but it may be
        useful in other situations as well.


    Usage: key||keys||keyring[[/switch] [<args>]]

       key/give <exit>=<player: Gives a key to the indicated player.

       key/list : Displays all of the keys in your keyring.

       key/desc <key>=<text> : Adds an optional, short description to a key
                               which you will be able to use to manage keys
                               later.

       key/retract <player>[=<door>] : Removes key(s) given to a specific
                                       player.  If called with the optional
                                       <door> arg, removes only the target
                                       player's key for that specific exit.

       key/mine : Displays a list of all keys that you have issued to
                  other players.

       key/discard <key> : Discards (destroys) a key, removing it from your
                           keyring.  <key> may be the key number or unique
                           text contained in the key desc.

       key/auth <on||off||never> : If set to 'off', you will automatically accept
                                 any offered keys.  If set to 'on', you must
                                 authorize each key to be added to your
                                 keyring.  If set to 'never' then all
                                 offered keys will be automatically rejected
                                 without prompting.

    Typing 'key' with no args is the same as typing 'key/list'.

    Note the following caveats:

    * Room owners may use a privacy lock to temporarily disable access via room keys.

    * If the room owner has you on ignore, they must first authorize your key to be used

    """

    key = "keys"
    aliases = ("key", "keyring")
    switch_options = (
        "list",
        "give",
        "retract",
        "desc",
        "discard",
        "mine",
        "verify",
        "auth",
    )
    help_catgory = "General"

    def do_key_list(self):
        keys = KeyDB.objects.filter(holder=self.caller)
        if not keys:
            self.caller.msg("Your keyring is empty.")
            return

        table = self.styled_table(
            "ID", "Desc", "Door", "Location", "Issuer", width=self.caller.screenwidth
        )
        for x in keys:
            table.add_row(
                x.id,
                x.key or "(None)",
                x.target.name_and_dbref,
                x.target.location.name_and_dbref,
                x.owner.key,
            )
        table.reformat_column(0, width=8, justify="right")
        self.caller.msg(
            headers.banner(
                "Your Keyring", player=self.caller, width=self.caller.screenwidth
            )
        )
        self.caller.msg(str(table))

    def do_key_give(self):
        """Creates a new key for a specific exit that you own or
        control and gives it to another player."""

        # Command syntax: key/give <exit>=<player>
        if not self.lhs or not self.rhs:
            self.caller.msg("Usage: key/give <door>=<character>")
            return

        # First, find the exit.
        door = self.caller.search(self.lhs, location=self.caller.location, typeclass=DefaultExit)
        if not door:
            return

        # Make sure it's actually an exit. You could use
        # inherits_from() for this as well, but this is faster.
        if not door.is_exit:
            self.caller.msg("Target must be a door.")
            return

        # Now find the player.
        player = pmatch(self.rhs, player=self.caller, use_account=False)
        if not player:
            self.caller.msg("No such player.")
            return

        # if player is self.caller:
        #    self.caller.msg("You don't need a key since you own or control the door.")
        #    return

        if inherits_from(player.account, Guest):
            self.caller.msg("Guests do not have keyrings.")
            return

        # Ownership/control check.
        if not door.access(self.caller, "owner") or not door.access(
            self.caller, "control"
        ):
            self.caller.msg("No way Josea.")
            return

        # Make sure this player doesn't already have a key.
        found = KeyDB.objects.filter(target=door, holder=player)
        if found.count():
            self.caller.msg("That player already has a key to that door.")
            return

        try:
            key = KeyDB(key="", target=door, owner=self.caller, holder=player)
            key.save()
        except Exception:
            logger.log_trace()
            self.caller.msg("Error creating key.")
            cemit_debug("KEY ERROR", "ERROR CREATING KEY PLEASE CHECK THE LOGS.")
            return

        # Add the key to the player's keyring. Technically we're adding
        # the door it goes to and not the key itself.
        player.keys.add(key.target)
        cemit_debug(
            "keys",
            f"CREATE: {key}, door={door.name_and_dbref}, creator={self.caller.name_and_dbref}, holder={player.name_and_dbref}.",
        )
        player.msg(
            f"{self.caller.key} has issued you a key (|Cid={key.id}|n) for {door.name_and_dbref} leading to {door.destination.key}."
        )
        self.caller.msg(f"You gave {player.key} a key to {door.name_and_dbref}.")

    def do_key_retract(self):
        if not self.lhs:
            self.caller.msg("Usage: key/remove <key>")
            return

        key = match_key(self.lhs, self.caller)
        if not key:
            self.caller.msg("No such key.")
            return
        key.delete()
        self.caller.msg("Key deleted.")

    def do_key_verify(self):
        pass

    def do_key_desc(self):
        if not self.lhs or not self.rhs:
            self.caller.msg("Usage: key/desc #=description")
            return

        key = match_key(self.lhs, self.caller)

        if not key:
            self.caller.msg("Couldn't find a key that matches.")
            return

        if key.holder is not self.caller:
            self.caller.msg("That's not your key. You can't describe it.")
            return

        key.key = self.rhs if self.rhs else ""
        key.save()
        self.caller.msg("Key description saved.")

    def do_key_discard(self):
        pass

    def do_key_mine(self):
        try:
            keys = KeyDB.objects.get(owner=self.caller)
        except:
            self.caller.msg("You have not issued any keys to anyone.")
            return

        table = self.styled_table(
            "ID", "Desc", "Door", "Location", width=self.caller.screenwidth
        )
        for x in keys:
            table.add_row(
                x.id,
                x.key or "(None)",
                x.target.name_and_dbref,
                x.target.location.name_and_dbref,
            )
        table.reformat_column(0, width=8, justify="right")
        self.caller.msg(
            headers.banner(
                "Your Issued Keys", player=self.caller, width=self.caller.screenwidth
            )
        )
        self.caller.msg(str(table))

    def do_key_auth(self):
        pass

    def func(self):
        if self.switches:
            switch = self.switches[0]
        else:
            switch = "list"
        if switch == "list":
            self.do_key_list()
        elif switch == "give":
            self.do_key_give()
        elif switch == "retract":
            self.do_key_retract()
        elif switch == "verify":
            self.do_key_veriy()
        elif switch == "desc":
            self.do_key_desc()
        elif switch == "discard":
            self.do_key_discard()
        elif switch == "auth":
            self.do_key_auth()
        elif switch in ("me", "mine", "self"):
            self.do_key_mine()
        else:
            self.caller.msg("Invalid switch.")


# Called when a save or delete operation occurs.
def update_key_cache(sender, **kwargs):
    # cemit_debug("signal.at_post_save", f"sender={sender}, kwargs={kwargs}")
    model = kwargs.get("instance", None)
    player = model.holder if model else None

    if model and player:
        player.keys.init_cache()
        cemit_debug("SIGNAL:KEY CACHE", f"Cache updated: user={player}")


def del_key_from_cache(sender, **kwargs):
    model = kwargs.get("instance", None)
    if not model:
        return
    player = model.holder or None
    if player:
        try:
            player.keys.remove(model.target)
        except Exception:
            logger.log_trace()
    cemit_debug("SIGNAL:KEY DELETE", f"Cache delete: user={player}")


# def at_init(sender, **kwargs):
#    cemit_debug("signal.at_post_init", f"sender={sender}, kwargs={kwargs}")


# post_save.connect(update_key_cache, sender=KeyDB)
post_delete.connect(del_key_from_cache, sender=KeyDB)
# post_init.connect(at_init, sender=KeyDB)
