
from world.genders import _GENDER_PRONOUN_MAP
from datetime import datetime
from evennia.server.sessionhandler import SESSIONS
import time
import world.headers as headers
import evennia.utils as utils
from evennia.utils.ansi import ANSIString, strip_ansi
from evennia.comms.models import Msg
from django.conf import settings
import world.utils as myutils
import world.pmatch as pmatch
import re
from evennia import ObjectDB, AccountDB, DefaultCharacter
from typeclasses.objects import Object
from typeclasses.characters import Character
import sys
from world.utils import cemit_debug
from evennia import default_cmds, CmdSet

_AT_SEARCH_RESULT = utils.variable_from_module(
    *settings.SEARCH_AT_RESULT.rsplit(".", 1)
)


class CmdSex(default_cmds.MuxCommand):
    """
    Usage:
      sex male||female||neuter

    The @sex command is used to set your character's sex and pronouns.
    """

    key = "sex"
    help_category = "General"
    locks = "cmd:notguest();"

    def func(self):
        caller = self.caller
        arg = self.args.lower()
        try:
            gender = _GENDER_PRONOUN_MAP[arg]
        except KeyError:
            caller.msg(
                f"Usage: {self.cmdstring} {'||'.join(_GENDER_PRONOUN_MAP.keys())}."
            )
            return
        caller.db.gender = arg
        caller.db.pronouns = gender
        caller.msg(f"You are now |C{arg}|n.")
        caller.msg(f"Your pronouns: |C{', '.join(gender.values())}.|n")



# make sure you import datetime for this!
class CmdLast(default_cmds.MuxCommand):
    """
    Usage:
      last
      lastlog

      Displays a list of your last few logins, including the timestamp, IP
      address and the character connected to.  The system is currently
      configured to store a maximum of 24 logins.

    Options:
      @prefs lastlog_elapsed_time=True|False:
          If set to True then last login times will be formatted as elapsed
          relative time (ie, You last connected 2 days ago), Otherwise
          absolute times will be used.  This effects both the lastlog
          command and the message you see just after logging in.
    """

    key = "lastlog"
    aliases = "last"
    help_category = "General"
    account_caller = True

    def func(self):
        if self.caller.is_guest:
            self.caller.msg("Only Admins may view guest login history.")
            return

        if self.args:
            if self.caller.is_superuser:
                target = pmatch.pmatch(
                    self.args, player=self.caller, match_account=True
                )
                if not target:
                    self.caller.msg("No such account.")
                    return
            else:
                self.caller.msg("Permission denied.")
                return
        else:
            target = self.caller

        last = target.db.lastsite or None
        if not last:
            self.caller.msg("This is your first login!")
            return

        elapsed_time = self.caller.options.get("lastlog_elapsed_time", False)
        table = self.styled_table(
            "ADDRESS", "DATE" if not elapsed_time else "LAST LOGIN", "CHARACTER"
        )
        for x in last:
            try:
                if elapsed_time:
                    now = time.time() - x[1]
                    table.add_row(x[0], f"{utils.time_format(now, 4)} ago", x[2])
                else:
                    now = datetime.fromtimestamp(x[1])
                    table.add_row(x[0], now.strftime("%a, %d %b, %Y %H:%M"), x[2])
            except IndexError:
                self.caller.msg("Something's messed up with your login db. Contact a staffer.")
                return

        self.caller.msg(str(table))

import random
def rainbow_word(source):
    out = ''
    for x in source:
        out += f"|{random.choice(('r', 'g', 'y', 'b', 'm', 'c', 'w', 'n'))}{x}|n"
    
    return out

# TIME=1:50
USERINFO = (

    ("Knight Austin Thomas", "M", "2h", "1s", "|rBOS|n", "The Prydwen"),
    ("|cDarren|n*", "M",     "1h", "1s", "ADM", "Darren's Office"),
    ("Terry Malloy", "F",   "1h", "6s", "DC", "Diamond City"),
    ("Scribe Nancy Wright", "F",   "1h", "|g3m|n", "|rBOS|n", "The Prydwen"),
    ("Parker",              "F",    "4h", "|y17m|n", "DC", "Diamond City"),
    ("Kevin Johnson", "M",    "23m", "|y21m|n", "DC", "Diamond City"),
    ("|cGeneva|n*", "F",     "2d", "|r24m|n", "ADM", "Geneva's Office"),
    ("John Proctor", "M",   "7h", "|r1h|n", "|MDC|n", "Diamond City"),
)

class CmdResGen(default_cmds.MuxCommand):
    key = "@res"
    
    
    def func(self):
        pass
        
        
class CmdWho(default_cmds.MuxCommand):
    key = 'who'
    aliases = 'doing'

    def func(self):
        caller = self.caller
        
        caller.msg(headers.banner('Fallout MUSH Connected Players', player=caller, width=80))
        color = caller.options.border_color
        caller.msg(f"|{color}|||n{' ' * 78}|{color}|||n".center(78))
        caller.msg(f"|{color}|||n|w{'** Please remember that this game is still in pre-alpha! **'.center(78)}|{color}|||n")
        caller.msg(f"|{color}|||n{' ' * 78}|{color}|||n".center(78))
        table = self.styled_table("NAME", "S", "CONN", "IDLE", "ORG", "REGION", width=80)
        for x in USERINFO:
            table.add_row(*x)
        
        table.reformat_column(0, width=32, align="l")
        table.reformat_column(1, width=4, align="c")
        table.reformat_column(2, width=7, align="r")
        table.reformat_column(3, width=7, align="l")
        table.reformat_column(4, width=7, align="c")
        caller.msg(str(table))

        output = ANSIString(f"** |c{len(USERINFO)}|n connected, |c{len(USERINFO)-2}|n unique, |c{12}|n record **").center(78)
        caller.msg(f"|b|||n{output}|b|||n")
        
        caller.msg(headers.ubanner("", player=caller, width=80))
        caller.msg("")

class CmdWho2(default_cmds.MuxCommand):
    """
    Usage:
      who [prefix]
      who/hide
      doing [prefix]
      doing/set [message]

    This command displays a list of all of the accounts presently connected
    to the game. If a prefix is given, it will only show the accounts whose
    names start with that prefix. For example, if you wanted to see only
    those characters whose names started with "a", you would do `who a`.

    You can use `who/hide` to remove your name from the connected players
    list. Note that you will still be visible to Admins and Directors but
    not to regular players. Hiding applies only to the connected players
    list, it will not prevent other players from seeing you in a room, etc.
    The setting is persistent so if you disconnect while hidden, you'll
    still be hidden the next time that you connect. To turn it off, type
    `who/hide` again.

    To set a @doing message, type `doing/set <message>`. To clear the
    mesage, simply omit the message, e.g. `doing/set`. Note that the message
    will be truncated at 37 characters.

    Credits:
      Based on example code by Packetdancer.
    """

    key = "who"
    aliases = "doing"
    locks = "cmd:all()"
    account_caller = False
    switch_options = ("set", "hide")

    def func(self):
        def parse_flags(who):
            if who.check_permstring("Admin"):
                return "A--"

            flags = "I" if who.tags.get("ic", category="flags", default=None) else "-"
            flags += "b" if not flags and who.check_permstring("Builder") else "-"
            flags += "D" if who.check_permstring("Developer") else "-"
            return flags

        def get_sessions(prefix=None):
            # Get the raw list of sessions from Evennia
            sessions = SESSIONS.get_sessions()

            # Filter out any with a key that does not start with the prefix.
            if prefix:
                sessions = filter(
                    lambda sess: sess.get_account().key.startswith(prefix)
                    if sess.get_account() is not None
                    else False,
                    sessions,
                )

            return sessions

        caller = self.caller

        # Check to see if they're only setting/clearing their doing msg.
        if self.cmdstring == "doing" and "set" in self.switches:
            if self.args == "":
                self.msg("Doing field cleared.")
                del self.caller.db.who_doing
            else:
                self.msg("Doing field set: {}".format(self.args))
                self.caller.db.who_doing = self.args

            return

        # Check to see if they're only hiding.
        if "hide" in self.switches:
            hide = not (self.caller.db.hidden or False)
            self.caller.db.hidden = hide
            self.msg(
                "You are %s on the WHO list."
                % ("|rnow hidden|n" if hide else "|gno longer hidden|n")
            )
            return

        # Get all of the sessions that match our args.
        session_list = get_sessions(self.args)
        # Sort the sessions in order of ascending connect time.  This will
        # put the players who have been connected the longest at the bottom
        # of the list.  We need to do a reverse sort for this.
        session_list = sorted(
            session_list, key=lambda sess: sess.conn_time, reverse=True
        )

        out = []
        line = ""
        show_admin_data = True
        caller.msg(headers.header("Connected Players", self.caller, 79))

        line = f"|{self.caller.options.column_names_color}Name(alias)          Flg G Conn  Idle  Org Doing|n"
        caller.msg(line)
        line = f"|{self.caller.options.border_color}-------------------- --- - ----- ----- --- ------------------------------------|n"
        caller.msg(line)
        hide = 0
        # Initialize some vars to hold IP addresses and account namess.
        addresses = set()
        logged = 1
        org = ""
        # Iterate the sessions list.
        for session in session_list:

            # Check to see if the session is logged in.
            if not session.logged_in:
                logged += 1
                continue

            # Add Account to the accounts list (a set).
            account = session.get_account()
            character = session.get_puppet()

            if character:
                hidden = character.db.hidden or False
            else:
                hidden = False

            # Add Address to the address list (a set).
            addresses.add(session.address)

            # Now
            if hidden:
                hide += 1

            # Skip over this character if they are hidden
            # and the caller is not an admin.
            if hidden and not show_admin_data:
                continue

            # Calculate idle and connected times.
            delta_cmd = time.time() - session.cmd_last_visible
            delta_conn = time.time() - session.conn_time

            gender = ANSIString(character.gender if character else "N")
            # name = ANSIString(character.cname() if character else account.key)
            name = ANSIString(character.key)
            doing_string = ANSIString(
                (character.db.who_doing or "") if character else ""
            )
            org = ANSIString("")

            # If the character is hidden, display their name in a different color to
            # make them stand out. The default is to bold the name.
            color = ANSIString(
                "| 000|[w"
                if hidden and (show_admin_data or self.caller is character)
                else "|n"
            )

            caller.msg(
                f"{color}{name:<20.20} {parse_flags(account).ljust(3)} {gender[0].upper()} {utils.time_format(delta_conn,1).rjust(5)} {myutils.idle_ctime(delta_cmd)}{utils.time_format(delta_cmd,1).ljust(4)}|n {doing_string.ljust(36)}"
            )
        line = f"|{self.caller.options.border_color}-------------------- --- - ----- ----- --- ------------------------------------|n"
        caller.msg(line)

        line = ANSIString(
            f"|y{len(session_list)}|n connected, |y{len(addresses)}|n unique IP, |y{hide}|n hidden."
        )
        self.caller.msg(line.center(79))

        caller.msg(headers.footer("", self.caller, 79))


class CmdGlance(default_cmds.MuxCommand):
    """
    Syntax: glance

    Displays the short description for all players in the looker's current location.

    """

    key = "glance"
    aliases = "peer"
    lock = "cmd:all()"
    help_category = "General"

    def func(self):
        caller = self.caller
        visible = (con for con in caller.location.players if con.access(caller, "view"))
        table = self.styled_table("Name", "Short Description", width=caller.screenwidth)
        for x in visible:
            if x == caller and not x.db.sdesc:
                default = "|YUse @desc <text> to set this.|n"
                newf = True
            else:
                default = ""
            table.add_row(x.key, x.db.sdesc or default)
        table.reformat_column(0, width=26)
        caller.msg(
            headers.banner(
                f"Glance::{caller.location.key}",
                player=caller,
                width=caller.screenwidth,
            )
        )
        self.caller.msg(str(table))


class CmdSdesc(default_cmds.MuxCommand):
    """
    manages your character's shortdesc.

    Syntax: sdesc[/clear] [<text>]

    Sets, displays or clears your character's shortdesc.
    """

    key = "sdesc"
    aliases = "sd"
    help_category = "General"
    locks = "notguest()"
    allowed_switches = "clear"

    def func(self):
        if not self.args:
            if "clear" in self.switches:
                del self.caller.db.sdesc
                self.caller.msg("Shortdesc cleared.")
            else:
                if self.caller.db.shortdesc:
                    self.caller.msg(
                        f"Your current shortdesc is:\n{self.caller.db.sdesc or 'None'}.\n---"
                    )
                else:
                    self.caller.msg("You do not have a short desc set.")
        else:
            self.caller.db.sdesc = self.args
            self.caller.msg(f"Shortdesc set to: {self.args}.")


class CmdInventory(default_cmds.CmdInventory):
    """
    view inventory

    Syntax:
      inventory
      inv
      i

    Shows your inventory.
    """

    key = "inventory"
    aliases = ("inv", "i")
    locks = "cmd:all()"
    arg_regex = r"$"

    def func(self):
        """check inventory"""
        items = self.caller.contents
        if not items:
            self.caller.msg("You aren't carrying anything.")
            return

        self.caller.msg("You are carrying:")
        for item in items:
            owner = item.manager()
            if owner != self.caller:
                self.caller.msg(f"  {item.key}(#{item.id}) [#{owner.id}]")
            else:
                self.caller.msg(f"  {item.key}(#{item.id})")

        self.caller.msg("---")


class CmdPage(default_cmds.MuxCommand):
    """
        send a private message to another account

        Usage:
          page[/switches] [<account>,<account>,...][ = <message>]
          tell        ''
          page <number>

        Switch:
            last - shows who you last messaged
            list - show your last <number> of tells/pages (default)
           clear - deletes all pages sent to you.

        Send a message to target user.  If you do not specify any target(s)
        then the code will attempt to re-page the last account(s) that you
        successfully paged.  Player names may be account names, aliases or
        ids.
        
        Note that this system uses actual objects for pages and those
        objects will persist until you delete them by using the /clear
        switch.  At the moment there is no automatic deletion but that may
        change if bloat becomes an issue later.

        Examples:
          page darren=Hey man what's going on?
          page Hi how are you?
          page/clear

    """

    key = "page"
    aliases = ("tell",)
    switch_options = ("last", "list", "clear")
    locks = "cmd:not pperm(page_banned)"
    help_category = "Comms"

    # this is used by the COMMAND_DEFAULT_CLASS parent
    account_caller = True

    def func(self):
        """Implement function using the Msg methods"""

        # Since account_caller is set above, this will be an Account.
        caller = self.caller

        # TODO: This is not very efficient and needs to be refactored.

        # get the messages we've sent (not to channels)
        pages_we_sent = Msg.objects.get_messages_by_sender(
            caller, exclude_channel_messages=True
        )
        # get last messages we've got
        pages_we_got = Msg.objects.get_messages_by_receiver(caller)

        if "last" in self.switches:
            if pages_we_sent:
                recv = ",".join(obj.key for obj in pages_we_sent[-1].receivers)
                self.msg("You last paged |c%s|n:%s" % (recv, pages_we_sent[-1].message))
                return
            else:
                self.msg("You haven't paged anyone yet.")
                return

        if "clear" in self.switches:
            if not pages_we_got:
                self.msg("You don't have any pages to clear.")
            else:
                i = 0
                for x in pages_we_got:
                    i += 1
                    try:
                        x.delete()
                    except:
                        continue
                self.msg(f"{i} message{'' if (i == 1) else 's'} cleared.")
            return

        if not self.args:
            pages = pages_we_sent + pages_we_got
            pages = sorted(pages, key=lambda page: page.date_created)

            number = 5
            if self.args:
                try:
                    number = int(self.args)
                except ValueError:
                    self.msg("Usage: tell [<account> = msg]")
                    return

            if len(pages) > number:
                lastpages = pages[-number:]
            else:
                lastpages = pages
            template = "%s|w%s|n |c%s|n to |c%s|n: %s"
            lastpages = "\n ".join(
                template
                % (
                    "|r*|n " if "u" in page.tags.get(category="page") else "  ",
                    utils.datetime_format(page.date_created),
                    ",".join(obj.key for obj in page.senders),
                    "|n,|c ".join([obj.name for obj in page.receivers]),
                    page.message,
                )
                for page in lastpages
            )

            if lastpages:
                string = "Your latest pages:\n %s" % lastpages
            else:
                string = "You haven't paged anyone yet."
            self.msg(string)

            return

        # We are sending. Build a list of targets

        if not self.rhs:
            # If there are no targets, then set the targets
            # to the last person we paged.
            if pages_we_sent:
                receivers = pages_we_sent[-1].receivers
            else:
                self.msg("Who do you want to page?")
                return
        else:
            receivers = self.lhslist

        recobjs = []
        for receiver in set(receivers):
            if isinstance(receiver, str):
                # Use pmatch() here instead of search since it handles
                # lookup by alias and filters out multiple matches.
                # obj = pmatch.pmatch(
                #   receiver, **{"player": caller, "match_account": True}
                #
                pobj = pmatch.pmatch(receiver, player=caller, match_account=True)
            elif hasattr(receiver, "character"):
                pobj = receiver
            else:
                self.msg("Who do you want to page?")
                return
            if pobj and not pobj.is_blocking(caller):
                recobjs.append(pobj)
        if not recobjs:
            self.msg("No one found to page.")
            return

        header = f"|wAccount|n |c{caller.key}|n |wpages:|n"

        # If no targets were specified then self.rhs will be None so we need
        # to check for that and use self.args instead.
        message = self.rhs if self.rhs else self.args

        # Check for MUSH-style : and ; prefixes.
        if message.startswith(":"):
            message = f"{caller.key} {message.strip(':').strip()}"
        elif message.startswith(";"):
            message = f"{caller.key}{message.strip(';').strip()}"

        # create the persistent message object
        page = utils.create.create_message(caller, message, receivers=recobjs)
        page.tags.add("U", category="page")

        # tell the accounts they got a message.
        received = []
        rstrings = []
        for pobj in recobjs:
            if not pobj.access(caller, "msg"):
                rstrings.append("You are not allowed to page %s." % pobj)
                continue
            pobj.msg("%s %s" % (header, message))
            if hasattr(pobj, "sessions") and not pobj.sessions.count():
                pobj.db.unread_pages = True
                received.append("|C%s|n" % pobj.name)
                rstrings.append(
                    "%s is offline. They will see your message if they list their pages later."
                    % received[-1]
                )
            else:
                received.append("|c%s|n" % pobj.name)
        if rstrings:
            self.msg("\n".join(rstrings))
        if received:
            self.msg("You paged %s with: '%s'." % (", ".join(received), message))
        else:
            self.msg("No one found to page.")


class CmdShout(default_cmds.MuxCommand):
    """
    shout

    Usage:
      shout <message>
      shout/loudly <MESSAGE>

    Sends a message to adjacent rooms. Shout sends a message
    to the rooms connected to your current one, while
    shout/loudly sends farther than that. Use with care!
    """

    key = "shout"
    help_category = "Social"

    def func(self):
        """Handles the toggle"""
        caller = self.caller
        args = self.args
        switches = self.switches
        loudly = False
        if not args:
            caller.msg("Shout what?")
            return
        if switches and "loudly" in switches:
            loudly = True
        loudstr = "loudly " if loudly else ""
        from_dir = "from nearby"
        caller.msg('You shout, "%s"' % args)
        txt = '{c%s{n shouts %s%s, "%s"' % (caller.name, loudstr, from_dir, args)
        caller.location.msg_contents(
            txt,
            exclude=caller,
            options={"shout": True, "from_dir": from_dir},
            from_obj=self.caller,
        )


class CmdFollow(default_cmds.MuxCommand):
    """
    follow

    Usage:
        follow

    Starts following the chosen object. Use follow without
    any arguments to stop following. While following a player,
    you can follow them through locked doors they can open.

    To stop someone from following you, use 'ditch'.
    """

    key = "follow"
    locks = "cmd:all()"
    help_category = "Travel"

    def func(self):
        """Handles followin'"""
        caller = self.caller
        args = self.args
        f_targ = caller.ndb.following
        if not args and f_targ:
            caller.stop_follow()
            return
        if not args:
            caller.msg("You are not following anyone.")
            return
        f_targ = caller.search(args)
        if not f_targ:
            caller.msg("No one to follow.")
            return

        if f_targ.is_blocking(self.caller):
            self.caller.msg("You cannot follow that character.")
            return

        caller.follow(f_targ)


class CmdStyle(default_cmds.MuxCommand):
    """
    configure various in-game options

    Usage:
      prefs
      prefs <option> = <value>
      prefs/clear [option]

    Configure various character level options including the colors used by
    the various UI elements.  Use without arguments to see all available
    options.

    The clear switch sets an option back to it's default value.  To clear
    all options, omit the option arg.


    Examples:
      prefs                       : Displays all options and their current
                                    values.
      prefs border_color=r        : Sets the 'border_color' option to 'r'.
      prefs/clear                 : Sets all options back to their defaults.
      prefs/clear border_color    : Sets the 'border_color' option to it's
                                    default value.
      prefs header_text_color=140 : Sets the 'header_text_color' option to
                                    140.

    |cCredits|n: Originally based on Volund's @style command.
    """

    key = "pref"
    aliases = ("prefs", "preferences", "style", "styles")
    switch_options = ["clear"]
    account_caller = True

    def func(self):
        if "clear" in self.switches:
            key = self.lhs.lower() if self.args else None

            if key and not key in settings.OPTIONS_ACCOUNT_DEFAULT.keys():
                self.msg("No such option.")
                return
            if key:
                self.caller.options.set(key, settings.OPTIONS_ACCOUNT_DEFAULT[key][2])
                self.caller.msg(f'Style for "{key}" was reset.')
            else:
                for x in settings.OPTIONS_ACCOUNT_DEFAULT.keys():
                    data = settings.OPTIONS_ACCOUNT_DEFAULT[x][2]
                    self.caller.options.set(x, data)
                self.msg("All style options reset to default values.")
            return

        if not self.args:
            self.list_styles()
        else:
            self.set()

    def list_styles(self):
        self.msg(headers.banner("Configurable Styles", self.caller, width=78))
        table = self.styled_table("Option", "Description", "Type", "Value", width=78)
        for op_key in self.caller.options.options_dict.keys():
            op_found = self.caller.options.get(op_key, return_obj=True)
            table.add_row(
                op_key,
                op_found.description,
                op_found.__class__.__name__,
                op_found.display(),
            )
        self.msg(str(table))

    def set(self):
        try:
            result = self.caller.options.set(self.lhs, self.rhs)
        except ValueError as e:
            self.msg(str(e))
            return
        self.msg("Style %s set to %s" % (self.lhs, result))


class CmdName(default_cmds.CmdName):
    """
    Change the name and/or aliases of an object.

    Usage:
      name <obj> = <newname>;alias1;alias2
      name *darren=Darren;dar

    Rename an object to something new.  Use *obj to rename an account.
    Requires rename or Builder perms.

    ANSI is stripped from the name.

    """

    key = "name"
    aliases = ["rename"]
    locks = "cmd:perm(rename) or perm(Builder)"
    help_category = "Building"

    def func(self):
        """change the name"""

        caller = self.caller
        if not self.args:
            caller.msg("Usage: name <obj> = <newname>[;alias;alias;...]")
            return

        obj = None
        if self.lhs_objs:
            objname = self.lhs_objs[0]["name"]
            aliases = self.lhs_objs[0]["aliases"]
            if objname.startswith("*"):
                # account mode
                obj = caller.account.search(objname.lstrip("*"))
                if obj:
                    newname = strip_ansi(self.rhs_objs[0]["name"])
                    aliases = self.rhs_objs[0]["aliases"]
                    if not newname:
                        caller.msg("No name defined!")
                        return
                    if not (
                        obj.access(caller, "control") or obj.access(caller, "edit")
                    ):
                        caller.msg(f"You don't have right to edit this account {obj}.")
                        return
                    obj.username = newname
                    astring = ""
                    if aliases:
                        [obj.aliases.add(alias) for alias in aliases]
                        astring = f" ({', '.join(aliases)})"
                    obj.save()
                    caller.msg(f"Account's name changed to '{newname}'{astring}.")
                    return
            # object search, also with *
            obj = caller.search(objname)
            if not obj:
                return
        if self.rhs_objs:
            newname = strip_ansi(self.rhs_objs[0]["name"])
            aliases = self.rhs_objs[0]["aliases"]
        else:
            newname = strip_ansi(self.rhs)
            aliases = None
        if not newname and not aliases:
            caller.msg("No names or aliases defined!")
            return
        if not (obj.access(caller, "control") or obj.access(caller, "edit")):
            caller.msg(f"You don't have the right to edit {obj}.")
            return
        # change the name and set aliases:
        if newname:
            obj.name = strip_ansi(newname)
            if obj.attributes.has("cname"):
                obj.attributes.remove("cname")
        astring = ""
        if aliases:
            [obj.aliases.add(alias) for alias in aliases]
            astring = f" ({', '.join(aliases)})"
        # fix for exits - we need their exit-command to change name too
        if obj.destination:
            obj.flush_from_cache(force=True)
        caller.msg(f"Object's name changed to '{newname}'{astring}.")


class CmdAudit(default_cmds.MuxCommand):
    key = "audit"
    aliases = "owned"
    help_category = "Building"
    locks = "notguest();"



    def func(self):
        found = utils.search.search_tag(self.caller.owner_tag, category="owner")
        if not found:
            self.caller.msg("Nothing found.")
            return

        # filters in use.
        filters = ""

        # Filter by name.
        if self.lhs:
            filters = f"name={self.lhs}*"
            found = found.filter(db_key__startswith=self.lhs)

        # Filter by type: room, exit, character, place, etc
        if self.rhs:
            if filters:
                filters += ", "
            filters += f"type={self.rhs}"
            found = found.filter(db_typeclass_path__contains=self.rhs)

        if not found:
            self.caller.msg(
                f"Nothing found using filter: {filters if filters else '(None)'}"
            )
            return

        self.caller.msg(
            headers.banner(
                f"{self.caller.name_and_dbref} Owned Objects",
                player=self.caller,
                width=self.caller.client_width(),
            )
        )
        table = self.styled_table("Name", "Type", "Location")
        for x in list(found):
            table.add_row(
                x.name_and_dbref,
                x.typename,
                x.location.name_and_dbref if x.location else ''

            )

            table.reformat(width=self.client_width())
        self.caller.msg(str(table))
        if filters:
            tmp = ANSIString(f"|wACTIVE FILTERS|n: {filters}.")
            self.caller.msg(tmp.center(self.caller.client_width()))
            self.caller.msg(
                headers.subheader(
                    "", player=self.caller, width=self.caller.client_width()
                )
            )


class CmdChown(default_cmds.MuxCommand):
    key = "chown"
    help_category = "Building"
    locks = "notguest();"

    def func(self):
        if not self.lhs or not self.rhs:
            self.caller.msg("Usage: chown <object>=<player>")
            return

        obj = self.caller.search(self.lhs)
        if not obj:
            return

        player = pmatch.pmatch(self.rhs, player=self.caller, match_account=False)
        if not player:
            self.caller.msg("No such player.")
            return

        obj.tags.add(f"#{player.id}", "owner")
        obj.db.owner = player
        self.caller.msg(f"{obj.key}(#{obj.id}) chowned to {player.key}(#{player.id}).")


def format_pair(d1, d2, color="|n", nochop=False):
    if not nochop:
        return ANSIString(f"|y{d1:>19.19}|n: {color}{d2:<19.19}|n")
    else:
        return ANSIString(f"|y{d1:>19.19}|n: {color}{d2:<40.40}|n")


def format_bar(caption, value, width, cap2=""):
    out = f"|C{caption:>19.19}|n: {headers.red_scale(value, width-36)} ({(value * 100.0):6.2f}%) {cap2}"
    return out


import world.messages as MESS


class CmdMessage(default_cmds.MuxCommand):
    """
    sets, clears or displays object messages.

    Syntax: @msg[/clear] <obj>[[/<message>]=<text>]
            @msg <obj>


    Messages are text that gets displayed when certain events occur in-game.
    They serve the same purpose as MUSH's @FAIL, @SUCCESS and similar
    attributes.  Most are movement related, for example, when you pass
    through an exit, teleport, enter a room, etc.  Messages are dynamically
    parsed and may contain embedded substitutions that are replaced with
    their associated values when the message is generated.

    Note that all substitutions are relative to the direct object with the
    exception of %N and the pronoun subs, which always refer to the
    Character (aka the enactor, or the thing that triggered the action that
    generated the message).


    The following substitutions are supported:


    %N: The name of the object that triggered the action, aka the enactor.
        This will always be a player (ie, a Character object).

    %L: The name of the location of the direct object.  If the direct object
        has no location property then it is assumed to be a Room and
        location will be self.  See also: %C.

    %I: The name of the indirect object of the action.  Some actions may
        involve an object in addition to the direct object.  An example of
        this is when a player moves through an exit, the destination room
        (or source room, if it's after the move) will be passed as the
        indirect object.  Not all messages define the indirect object.

    %A: The name of the area (aka zone) of the direct object.  Only
        meaningful for Rooms. See also: %Z.

    %Z: Like %A but returns only the topmost area in the areas's parent
        hierarchy.  For example, consider the case of an area named
        "Chargen" which has a parent area "OOC".  If the room's area is set
        to "OOC" then %A returns "OOC" and so does %Z.  If the room's area
        is set to "Chargen" then %A returns "Chargen" but %Z returns "OOC".

    %S: Subjective pronoun of the enactor.
    %O: Objective pronoun of the enactor.
    %R: Reflexive pronoun of the enactor.
    %P: Personal pronoun of the enactor.
    %Q: Posessive pronoun of the enactor.

    %C: Returns the name of the direct object's outermost container by
        recursing its location hierarchy until it finds an object with a
        location property of None (or another false value) then returns the
        last object with a valid location.  This will usually be a room
        since only rooms should ever have a location property of None, but
        the code does not enforce this.

    %T: This. The direct object, or, the object being acted upon.

    %(<var>): Returns the value of a property.  For example, "%(location)"
              would return the value of the location property of the direct
              object.  Not a useful example since we have %L but hopefully
              it gets the concept across.

    %(db.<var>): Returns the value of a db attribute.  For example,
                 "%(db.title)" would return the value of the direct object's
                 "title" db attr.

    %f(<fun>): The return value of the method <fun>, converted into a
               string.

    Each sub has an upper-case version which runs the return result through
    utils.title() to capitalize it, and a lower-case version, which returns
    the result as-is.

    If you wish to block a message, simply set it to '@'.  This will also
    block any defaults on the parent.

    """

    key = "msg"
    aliases = ("message", "messages", "msgs")
    switch_options = "clear"

    def do_show_msg(self, targ, player):

        atr = f"{targ.typename.upper()}_MESSAGES"
        messages = getattr(MESS, atr, None)
        if not messages:
            player.msg("No messages have been configured for that type of object.")
            return

        player.msg(f"Messages on {targ.name_and_dbref} <{targ.typename}>:")
        for x in messages:
            atr = targ.attributes.get(x, None)
            default = False if atr else True
            if not atr:
                atr = getattr(MESS, x.upper(), None)
            player.msg(
                f"|{player.options.column_names_color}{x:>10.10}|n: {atr if atr else ''} {'[|cdefault|n]' if default and atr else ''}"
            )
        player.msg("---")

    def func(self):
        if not self.args:
            self.caller.msg(f"Usage: {self.cmdstring} <object>")
            return

        try:
            targ, msg = self.lhs.split("/")
        except:
            targ = self.args
            msg = None

        if not targ and not msg:
            self.caller.msg("Usage: msg obj/message=text")
            return

        targ = targ.strip()
        msg = msg.strip() if msg else None

        target = self.caller.search(targ)
        if not target:
            return

        if not (
            target.access(self.caller, "edit") or target.access(self.caller, "control")
        ):
            self.caller.msg("Permission denied.")
            return

        if not msg:
            target.list_messages(self.caller)
            return

        if self.switches and "clear" in self.switches:
            target.messages.remove(message)
            self.caller.msg("Message cleared.")
            return

        value = self.rhs.strip()

        if msg not in MESS.ALL_MESSAGES:
            self.caller.msg("There's no message with that name.")
            return

        atr = f"{target.typename.upper()}_MESSAGES"
        message = getattr(MESS, atr, None)
        if not message:
            player.msg("That object does not respond to that message.")
        else:
            target.attributes.add(msg, value)
            self.caller.msg(f'You set the {msg} message of {target} to "{value}".')


class CmdGive(default_cmds.MuxCommand):
    """
    give away something to someone

    Usage:
      give <inventory obj> <to||=> <target>

    Gives an items from your inventory to another character,
    placing it in their inventory.
    """

    key = "give"
    rhs_split = ("=", " to ")  # Prefer = delimiter, but allow " to " usage.
    locks = "cmd:all()"
    arg_regex = r"\s|$"

    def func(self):
        """Implement give"""

        caller = self.caller
        if not self.args or not self.rhs:
            caller.msg("Usage: give <inventory object> = <target>")
            return
        to_give = caller.search(
            self.lhs,
            location=caller,
            nofound_string="You aren't carrying %s." % self.lhs,
            multimatch_string="You carry more than one %s:" % self.lhs,
        )
        target = caller.search(self.rhs)
        if not (to_give and target):
            return
        if target == caller:
            caller.msg("You keep %s to yourself." % to_give.key)
            return
        if not to_give.location == caller:
            caller.msg("You are not holding %s." % to_give.key)
            return

        if target.is_blocking(self.caller):
            self.caller.msg(f"You cannot give {to_give.key} to that character.")
            return

        # calling at_before_give hook method
        if not to_give.at_before_give(caller, target):
            return

        # give object
        to_give.move_to(target, quiet=True)
        # Call the object script's at_give() method.
        to_give.at_give(caller, target)


class CmdDrop(default_cmds.CmdDrop):
    """
    drop something

    Usage:
      drop <obj>

    Lets you drop an object from your inventory into the
    location you are currently in.
    """

    key = "drop"
    locks = "cmd:all()"
    arg_regex = r"\s|$"

    def func(self):
        """Implement command"""

        caller = self.caller
        if not self.args:
            caller.msg("Drop what?")
            return

        # Because the DROP command by definition looks for items
        # in inventory, call the search function using location = caller
        obj = caller.search(
            self.args,
            location=caller,
            nofound_string="You aren't carrying %s." % self.args,
            multimatch_string="You carry more than one %s:" % self.args,
        )
        if not obj:
            return

        # Call the object script's at_before_drop() method.
        if not obj.at_before_drop(caller):
            obj.generate_message("nodrop", 'onodrop', caller=caller)
            return

        obj.move_to(caller.location, quiet=True)
        obj.at_drop(caller)


class CmdTeleport(default_cmds.MuxCommand):
    """
    teleport object to another location

    Usage:
      tel/switch [<object> to||=] <target location>

    Examples:
      tel Limbo
      tel/quiet box = Limbo
      tel/tonone box

    Switches:
      quiet  - don't echo leave/arrive messages to the source/target
               locations for the move.
      intoexit - if target is an exit, teleport INTO
                 the exit object instead of to its destination
      tonone - if set, teleport the object to a None-location. If this
               switch is set, <target location> is ignored.
               Note that the only way to retrieve
               an object from a None location is by direct #dbref
               reference. A puppeted object cannot be moved to None.
      loc - teleport object to the target's location instead of its contents

    Teleports an object somewhere.  If no object is given, you yourself are
    teleported to the target location.
    """

    key = "tel"
    aliases = "teleport"
    switch_options = ("quiet", "intoexit", "tonone", "loc")
    rhs_split = ("=", " to ")  # Prefer = delimiter, but allow " to " usage.
    locks = "cmd:perm(teleport) or perm(Builder)"
    help_category = "Building"

    def func(self):
        """Performs the teleport"""

        caller = self.caller
        args = self.args
        lhs, rhs = self.lhs, self.rhs
        switches = self.switches

        # setting switches
        tel_quietly = "quiet" in switches
        to_none = "tonone" in switches
        to_loc = "loc" in switches

        if to_none:
            # teleporting to None
            if not args:
                obj_to_teleport = caller
            else:
                obj_to_teleport = caller.search(lhs, global_search=True)
                if not obj_to_teleport:
                    caller.msg("Did not find object to teleport.")
                    return
            if obj_to_teleport.has_account:
                caller.msg(
                    "Cannot teleport a puppeted object "
                    "(%s, puppeted by %s) to a None-location."
                    % (obj_to_teleport.key, obj_to_teleport.account)
                )
                return
            caller.msg("Teleported %s -> None-location." % obj_to_teleport)
            if obj_to_teleport.location and not tel_quietly:
                obj_to_teleport.location.msg_contents(
                    "%s teleported %s into nothingness." % (caller, obj_to_teleport),
                    exclude=caller,
                )
            obj_to_teleport.location = None
            return

        # not teleporting to None location
        if not args and not to_none:
            caller.msg("Usage: teleport[/switches] [<obj> =] <target_loc>||home")
            return
        args = {}
        if rhs:
            obj_to_teleport = caller.search(lhs, global_search=True)
            destination = caller.search(rhs, global_search=True)
        else:
            obj_to_teleport = caller
            destination = caller.search(lhs, global_search=True)
            args = {"type": "teleport", "origin": obj_to_teleport.location}
        if not obj_to_teleport:
            caller.msg("Did not find object to teleport.")
            return

        if not destination:
            caller.msg("Destination not found.")
            return
        if to_loc:
            destination = destination.location
            if not destination:
                caller.msg("Destination has no location.")
                return
        if obj_to_teleport == destination:
            caller.msg("You can't teleport an object inside of itself!")
            return
        if obj_to_teleport == destination.location:
            caller.msg("You can't teleport an object inside something it holds!")
            return
        if obj_to_teleport.location and obj_to_teleport.location == destination:
            caller.msg("%s is already at %s." % (obj_to_teleport, destination))
            return
        use_destination = True
        if "intoexit" in self.switches:
            use_destination = False

        # try the teleport
        if obj_to_teleport.move_to(
            destination,
            quiet=tel_quietly,
            emit_to_obj=caller,
            use_destination=use_destination,
            **args,
        ):
            if obj_to_teleport == caller:
                caller.msg("Teleported to %s." % destination)
            else:
                caller.msg("Teleported %s -> %s." % (obj_to_teleport, destination))


class CmdPose(default_cmds.MuxCommand):
    """
    strike a pose

    Usage:
      pose <pose text>
      pose's <pose text>
      :<pose text>
      :'s <pose text>

    Example:
      pose is standing by the wall, smiling.
       -> others will see:
      Tom is standing by the wall, smiling.
      
      :'s head hurts.
       -> others will see:
      Tom's head hurts.

    Describe an action being taken.  The pose text will automatically begin
    with your name, followed by a space, and then the pose text.  You can
    suppress the space by starting your pose text with a special character
    such as "'", ";" or ":".
    
    
    """

    key = "pose"
    aliases = [":", ";", "emote"]
    locks = "cmd:all()"
    arg_regex = r"[\w\'\"].+|\s.+|$"
    #arg_regex = r"\w.+|\s.+|$"

    def parse(self):
        """
        Custom parse the cases where the emote
        starts with some special letter, such
        as 's, at which we don't want to separate
        the caller's name and the emote with a
        space.
        """
        args = self.args
        if args and not args[0] in ["'", ",", ":", ";"]:
            args = " %s" % args.strip()
        self.args = args

    def func(self):
        """Hook function"""
        if not self.args:
            msg = "What do you want to do?"
            self.caller.msg(msg)
        else:
            #sep = "" if self.cmdname in ("semipose", "semi", ";") else " "

            out = f"{self.caller.name}{self.args}"
            # regexp = re.compile(r"`([\w]+)")
            # out = regexp.sub(utils.replace_name, out)

            self.caller.location.msg_contents(
                text=(out, {"type": "pose"}), from_obj=self.caller
            )


class CmdSay(default_cmds.MuxCommand):
    """
    speak as your character

    Usage:
      say <message>

    Talk to those in your current location.
    """

    key = "say"
    aliases = ['"', "'"]
    locks = "cmd:all()"
    arg_regex = r"\w.+|\s.+|$"

    def func(self):
        """Run the say command"""

        caller = self.caller
        speech = self.args

        if not speech:
            caller.msg("Say what?")
            return

        # Calling the at_before_say hook on the character
        speech = caller.at_before_say(speech, from_obj=caller)

        # If speech is empty, stop here
        if not speech:
            return

        # Call the at_after_say hook on the character
        caller.at_say(speech, msg_self=True, from_obj=caller)


class CmdAccess(default_cmds.MuxCommand):
    """
    show your current game access

    Usage:
      access

    This command shows you the permission hierarchy and
    which permission groups you are a member of.
    """

    key = "access"
    aliases = "hierarchy"
    locks = "cmd:all()"
    arg_regex = r"$"

    def func(self):
        """Load the permission groups"""

        caller = self.caller
        hierarchy_full = settings.PERMISSION_HIERARCHY
        string = "\n|wPermission Hierarchy|n (climbing):\n %s" % ", ".join(
            hierarchy_full
        )

        if self.caller.account.is_superuser:
            cperms = "<Superuser>"
            pperms = "<Superuser>"
        else:
            cperms = ", ".join(caller.permissions.all())
            pperms = ", ".join(caller.account.permissions.all())

        string += "\n|wYour access|n:"
        string += "\nCharacter |c%s|n: %s" % (caller.key, cperms)
        if hasattr(caller, "account"):
            string += "\nAccount |c%s|n: %s" % (caller.account.key, pperms)
        caller.msg(string)


class CmdWhisper(default_cmds.MuxCommand):
    """
    Speak privately as your character to another

    Usage:
      whisper <character> = <message>
      whisper <char1>, <char2> = <message>

    Talk privately to one or more characters in your current location, without
    others in the room being informed.
    """

    key = "whisper"
    locks = "cmd:all()"

    def func(self):
        """Run the whisper command"""

        caller = self.caller
        from_obj = self.caller

        if not self.lhs or not self.rhs:
            caller.msg("Usage: whisper <character> = <message>")
            return

        receivers = [recv.strip() for recv in self.lhs.split(",")]

        receivers = [caller.search(receiver) for receiver in set(receivers)]
        receivers = [
            recv for recv in receivers if recv and not recv.is_blocking(caller)
        ]

        speech = self.rhs
        # If the speech is empty, abort the command
        if not speech or not receivers:
            return

        # Call a hook to change the speech before whispering
        speech = caller.at_before_say(
            speech, whisper=True, receivers=receivers, **{"from_obj": caller}
        )

        # no need for self-message if we are whispering to ourselves (for some reason)
        msg_self = None if caller in receivers else True
        caller.at_say(
            speech,
            msg_self=msg_self,
            receivers=receivers,
            whisper=True,
            **{"from_obj": caller},
        )


class CmdGet(default_cmds.CmdGet):
    """
    pick up something

    Usage:
      get <obj>
      get <obj> from <source>

    Get something from your current location or other object.
    """

    key = "get"
    aliases = ("grab", "take")
    locks = "cmd:all()"
    arg_regex = r"\s|$"
    rhs_split = ("=", " from ")

    def func(self):
        """implements the command."""

        caller = self.caller

        # Make sure they passed some args.
        if not self.args:
            caller.msg(f"{self.cmdstring.title()} what?")
            return

        # First match the location.
        if self.rhs:
            from_loc = caller.search(self.rhs)
            if not from_loc:
                return
        else:
            from_loc = caller.location

        # Then the target object.
        obj = caller.search(self.lhs, location=from_loc)
        if not obj:
            return

        # The player and the container object of the target should be
        # in the same room.
        if myutils.room(from_loc) is not myutils.room(caller):
            caller.msg("You may only get nearby things.")
            return

        # Players should not be able to get/take exits, rooms, players, etc.
        if not utils.inherits_from(obj, Object):
            caller.msg(f"You can't {self.cmdstring} {obj.typename.lower()}s!")
            return

        # Check that the object isn't already in the player's inventory.
        if obj.location is caller:
            caller.msg("You already have that object.")
            return

        # Check the get lock on the object.
        if not obj.access(caller, "get"):
            obj.generate_message("get_failed", 'oget_failed', caller=caller)
            return

        # calling at_before_get hook method
        if not obj.at_before_get(caller):
            return

        obj.location.msg_contents(f"{caller.name} gets {obj.name}.", exclude=caller)

        # Perform the move.
        obj.move_to(caller, quiet=True)

        # Display messages.
        obj.generate_message("get", 'oget', caller=caller)

        # calling at_get hook method
        obj.at_get(caller)
        caller.msg(f"You got {obj.name}.")


class CmdGive(default_cmds.CmdGive):
    """
    give away something to someone

    Usage:
      give <inventory obj> <to||=> <target>

    Gives an items from your inventory to another character,
    placing it in their inventory.
    """

    key = "give"
    rhs_split = ("=", " to ")  # Prefer = delimiter, but allow " to " usage.
    locks = "cmd:all()"
    arg_regex = r"\s|$"

    def func(self):
        """Implement give"""

        caller = self.caller
        if self.db.mobile:
            print('YES")')
        else:
            print("NO")
        if not self.args or not self.rhs:
            caller.msg("Usage: give <inventory object> = <target>")
            return
        to_give = caller.search(
            self.lhs,
            location=caller,
            nofound_string=f"You aren't carrying {self.lhs}.",
            multimatch_string=f"You carry more than one {self.lhs}:",
        )
        target = caller.search(self.rhs)
        if not (to_give and target):
            return
        if target == caller:
            caller.msg(f"You keep {to_give.key} to yourself.")
            return

        if not to_give.location == caller:
            caller.msg(f"You are not holding {to_give.key}.")
            return

        # calling at_before_give hook method
        if not to_give.at_before_give(caller, target):
            return

        # give object
        caller.msg(f"You give {to_give.key} to {target.key}.")
        to_give.move_to(target, quiet=True)
        target.msg(f"{caller.key} gives you {to_give.key}.")
        # Call the object script's at_give() method.
        to_give.at_give(caller, target)


class CmdBlock(default_cmds.MuxCommand):
    """
    manage your blocklist.

    Syntax: block <player>     : Adds a player to your blocklist.
            unblock <player>   : Removes a player from your blocklist.
            block/clear        : Clears (wipes out!) your blocklist.
            block              : Display your current blocklist.


        When called with no args, displays the current blocklist.  When
        called with the 'clear' switch, removes all entries in your
        blocklist.  When called as 'block' with a player name, adds the
        player to the blocklist.  When called as 'unblock' with a player
        name, removes the player from the blocklist.

        Blocking another player prevents you from seeing their speech,
        whispers, poses, pages, mails, places messages, channel messages or
        emits.  Basically, any text sent via .msg() when the sender is
        passed via the 'from_obj' argument may be filtered.  Note that this
        does not work with room or channel history as those systems do not
        preserve the sender context.
        
        Blocking a player will immediately revoke any keys you have issued
        to them, as well as any keys you may have that were issued by the
        player being blocked.
    """

    key = "block"
    aliases = "unblock"
    help_category = "Comms"
    allowed_switches = "clear"
    
    
    def retract_keys(self, key_holder, key_owner):
        keys = KeyDB.filter(db_owner=key_owner, db_holder=key_holder)
        if keys:
            for x in keys:
                x.delete()
        

    # Main entry point.
    def func(self):
        # Non-account-caller, so caller is assumed to be a Character.
        caller = self.caller

        # First handle the reset switch.
        if self.switches:
            if "clear" in self.switches:
                caller.ilocks.reset_cache()
                caller.msg("Your blocklist has been cleared.")
            else:
                self.caller.msg(f"Usage: {self.cmdstring}[/reset] [<user>]")
            return

        # If called with no args, just display the blocklist.
        if not self.args:
            if len(caller.ilocks) == 0:
                caller.msg("You're not blocking anyone.")
            else:
                caller.msg(
                    f"You are currently blocking:\n{myutils.itemize([x.name_and_dbref for x in self.caller.ilocks.all()])}."
                )
            # Exit, we're finished.
            return

        # This will return either a Character instance or None
        target = pmatch.match_player_by_name(self.args)
        if not target:
            # If target is invalid (None) then the player
            # lookup was not successful.
            caller.msg("No character found with that name or alias.")
            return

        # Don't let players block themselves!
        if target is caller:
            caller.msg("You can't block yourself!")
            return

        # Seriously folks, if you feel the need to block staff
        # then you're probably playing on the wrong game.
        if target.is_superuser or "admin" in target.permissions.all():
            caller.msg("You may not block superusers.")
            return

        # Let's do it! First check for unblock.
        if self.cmdstring == "unblock":
            if not caller.is_blocking(target):
                caller.msg("You are not blocking that player.")
            else:
                caller.ilocks.remove(target)
                caller.msg(f"You are no longer blocking {target.name_and_dbref}.")
            return
        else:
            # Now let's handle blocking.
            if caller.is_blocking(target):
                # Merely a warning. Duplicates aren't possible with blocklist being a set.
                caller.msg("You are already blocking that player.")
            else:
                caller.ilocks.add(target)
                self.retract_keys(target, self)
                caller.msg(f"You are now blocking {target.name_and_dbref}.")


class CmdFEdit(default_cmds.MuxCommand):
    """
    Syntax: @fedit <object>

    Loads an object description into your MUSH-compatible client's command
    line for fast, easy editing. This works with all clients, but some may
    require that you define a trigger for it (MUSHclient, TinyFugue and BeipMU,
    for example), or enable support by clicking a box in settings (Atlantis).
    """

    key = "fedit"
    help_category = "General"

    def func(self):
        if not self.lhs:
            self.caller.msg("Syntax: %s <object>" % self.cmdname)
            return
        what = self.caller.search(self.lhs, location=self.caller.location)

        # Just quit if we didn't find anything. The search will handle the error message.
        if not what:
            return

        # Make sure that the caller has permission to modify the object.
        if not what.access(self.caller, "control") or not what.access(
            self.caller, "edit"
        ):
            self.caller.msg(
                "You don't have permission to modify the description of that object."
            )
            return

        # If the attr isn't present on the object, obj.db.desc will be None and this will cause
        # problems for us when we go to edit, so we default to an empty string.
        desc = what.db.desc or ""

        self.caller.msg(f"FugueEdit > @desc #{what.id}={desc}", options={"raw": True})


class CmdFriend(default_cmds.MuxCommand):
    key = "friend"
    aliases = "friends"
    help_category = "General"
    account_caller = True

    def func(self):
        if not self.args or "list" in self.switches:
            self.caller.msg("You has frands!")
            return

        self.caller.msg("You has no frands.")


class CmdManagers(default_cmds.MuxCommand):
    key = "managers"

    def func(self):
        self.caller.msg("HEYA")


class CmdFinger(default_cmds.MuxCommand):
    key = "finger"
    aliases = "det"
    help_category = "General"

    def func(self):
        if self.args:
            target = pmatch.pmatch(self.args, player=self.caller)
            if not target:
                self.caller.msg("There is no player with that name or alias.")
                return
        else:
            target = self.caller

        self.caller.msg(
            headers.header(
                f"Finger Info for {target.key}",
                player=self.caller,
                width=self.caller.client_width(),
            )
        )
        self.caller.msg(
            headers.subheader("", player=self.caller, width=self.caller.client_width())
        )


class CmdExtendedRoomLook(default_cmds.CmdLook):
    """
    look

    Usage:
      look
      look <obj>
      look <room detail>
      look *<account>

    Observes your location, details at your location or objects in your vicinity.
    """

    def func(self):
        """
        Handle the looking - add fallback to details.
        """
        caller = self.caller
        args = self.args
        if args:
            looking_at_obj = caller.search(
                args,
                candidates=caller.location.contents + caller.contents,
                use_nicks=True,
                quiet=True,
            )
            if not looking_at_obj:
                # no object found. Check if there is a matching
                # detail at location.
                location = caller.location
                if (
                    location
                    and hasattr(location, "return_detail")
                    and callable(location.return_detail)
                ):
                    detail = location.return_detail(args)
                    if detail:
                        # we found a detail instead. Show that.
                        caller.msg(detail)
                        return
                # no detail found. Trigger delayed error messages
                _AT_SEARCH_RESULT(looking_at_obj, caller, args, quiet=False)
                return
            else:
                # we need to extract the match manually.
                looking_at_obj = utils.make_iter(looking_at_obj)[0]
        else:
            looking_at_obj = caller.location
            if not looking_at_obj:
                caller.msg("You have no location to look at!")
                return

        if not hasattr(looking_at_obj, "return_appearance"):
            # this is likely due to us having an account instead
            looking_at_obj = looking_at_obj.character
        if not looking_at_obj.access(caller, "view"):
            caller.msg("Could not find '%s'." % args)
            return
        # get object's appearance
        caller.msg(looking_at_obj.return_appearance(caller))
        # the object's at_desc() method.
        looking_at_obj.at_desc(looker=caller)


# Custom build commands for setting seasonal descriptions
# and detailing extended rooms.


class CmdExtendedRoomDetail(default_cmds.MuxCommand):

    """
    sets a detail on a room

    Usage:
        @detail[/del] <key> [= <description>]
        @detail <key>;<alias>;... = description

    Example:
        @detail
        @detail walls = The walls are covered in ...
        @detail castle;ruin;tower = The distant ruin ...
        @detail/del wall
        @detail/del castle;ruin;tower

    This command allows to show the current room details if you enter it
    without any argument.  Otherwise, sets or deletes a detail on the current
    room, if this room supports details like an extended room. To add new
    detail, just use the @detail command, specifying the key, an equal sign
    and the description.  You can assign the same description to several
    details using the alias syntax (replace key by alias1;alias2;alias3;...).
    To remove one or several details, use the @detail/del switch.

    """

    key = "detail"
    aliases = "details"
    # locks = "cmd:perm(Builder)"
    help_category = "Building"

    def func(self):
        if not self.lhs:
            self.caller.msg("You must specify an object.")
            return

        location = self.caller.search(self.lhs)
        if not location:
            self.caller.msg("I don't see that here.")
            return

        if not self.rhs:
            details = location.db.details
            if not details:
                self.msg(
                    f'That {location.typename.lower()} "{location}" doesn\'t have any details set.'
                )
            else:
                details = sorted([f"{key}: {desc}" for key, desc in details.items()])
                self.msg(
                    f"Details on {location.typename.lower()}:\n" + "\n".join(details)
                )
            return

        if not self.rhs and "del" not in self.switches:
            detail = location.return_detail(self.lhs)
            if detail:
                self.msg(
                    f"Detail '|y{self.lhs}|n' on {location.typename.lower()}:\n{detail}"
                )
            else:
                self.msg(f"Detail '{self.lhs}' not found.")
            return

        method = "set_detail" if "del" not in self.switches else "del_detail"
        if not hasattr(location, method):
            self.caller.msg("Details cannot be set on %s." % location)
            return
        for key in self.lhs.split(";"):
            # loop over all aliases, if any (if not, this will just be
            # the one key to loop over)
            getattr(location, method)(key, self.rhs)
        if "del" in self.switches:
            self.caller.msg("Detail %s deleted, if it existed." % self.lhs)
        else:
            self.caller.msg("Detail set '%s': '%s'" % (self.lhs, self.rhs))


# Simple command to view the current time and season


class CmdExtendedRoomGameTime(default_cmds.MuxCommand):
    """
    Check the game time

    Usage:
        time

    Shows the current in-game time and season.
    """

    key = "time"
    locks = "cmd:all()"
    help_category = "General"

    def func(self):
        """Reads time info from current room"""
        location = self.caller.location
        if not location or not hasattr(location, "get_time_and_season"):
            self.caller.msg("No location available - you are outside time.")
        else:
            season, timeslot = location.get_time_and_season()
            prep = "a"
            if season == "autumn":
                prep = "an"
            self.caller.msg("It's %s %s day, in the %s." % (prep, season, timeslot))


# CmdSet for easily install all commands


class ExtendedRoomCmdSet(CmdSet):
    """
    Groups the extended-room commands.

    """

    def at_cmdset_creation(self):
        self.add(CmdExtendedRoomLook)
        # self.add(CmdExtendedRoomDesc)
        self.add(CmdExtendedRoomDetail)
        # self.add(CmdExtendedRoomGameTime)


from evennia.utils.ansi import strip_ansi


class CmdCname(default_cmds.MuxCommand):
    """
    sets or clears your character's color name, which is a copy of your
    regular name that may contain ANSI.

    Syntax:
      cname <color_name> : Sets your colorized name.
      cname/clear        : Clears your colorized name.
      cname              : Displays your colorized name (including the raw
                           ANSI codes).

    Example:
      > cname ||105D||205ar||305r||405e||505n

      Would set my cname to |105D|205ar|305r|405e|505n|n.

    Your colorized name must be the same as your regular name (case counts!)
    minus the ANSI codes.

    If you do not include a terminating ||n, it will be automatically added.

    If you change your name, your color name will be deleted automatically.

    """

    key = "cname"
    help_category = "General"
    allowed_switches = "clear"

    def func(self):
        if self.switches and "clear" in self.switches:
            self.caller.attributes.remove("cname")
            self.caller.msg("Color name has been cleared.")
            return

        if not self.args:
            if cname := self.caller.attributes.get("cname", None):
                self.caller.msg(f"Your current CName: {cname}.", options={"raw": True})
            else:
                self.caller.msg("You do not have a color name set.")
            return

        current_name = self.caller.name
        new_name = self.args

        if not new_name.endswith("|n"):
            new_name += "|n"

        if current_name == strip_ansi(new_name):
            self.caller.db.cname = new_name
            self.caller.msg(f"Color name changed to: {new_name}.")
        else:
            self.caller.msg("Color name does not match your normal name.")


class CmdRoom(default_cmds.MuxCommand):
    key = "+room"
    help_category = "Building"
    locks = "cmd:all()"

    def show_room_options(self, opts):
        self.caller.msg(headers.header("Room Options", player=self.caller, width=79))
        self.caller.msg(f"|gOptions|n:")
        for x in settings.DEFAULT_ROOM_OPTIONS:
            self.caller.msg(f"{x:<14}: {opts.get(x, None)}")
        OTHER_OPTIONS = {
            "Owner": "Darren(#12)",
            "Player Housing": "True",
            "Open Linking": "True",
            "Area": self.caller.location.db.area or "None",
        }

        self.caller.msg("\n|rOther Settings|n:")
        for x in OTHER_OPTIONS:
            self.caller.msg(f"{x:<14}: {OTHER_OPTIONS.get(x, None)}")

        self.caller.msg(headers.header("", player=self.caller, width=79))
        return

    def func(self):
        if not self.args:
            self.show_room_options(
                self.caller.location.db.room_options or settings.DEFAULT_ROOM_OPTIONS
            )
            return

        if not self.lhs or not self.rhs:
            self.caller.msg("Usage: @room <key>=<value>")
            return
        loc = self.caller.location
        if not loc:
            self.caller.msg("You must be inside a room to do that.")
            return

        if not loc.access(self.caller, "control") and not loc.access(
            self.caller, "edit"
        ):
            self.caller.msg("You do not have permission to modify that room.")
            return

        key = self.lhs.lower()
        opts = loc.db.room_options or settings.DEFAULT_ROOM_OPTIONS

        opts[key] = self.rhs
        loc.db.room_options = opts
        self.caller.msg("TEST")
        self.caller.msg(f"The room's {key} option changed to {self.rhs}.")

        self.caller.msg(headers.header("THIS", player=self.caller, width=79))


class CmdRoom(default_cmds.MuxCommand):
    key = "room"
    switch_options = ("clear",)

    def func(self):

        target = self.caller.location
        if not target or not target.is_room:
            self.caller.msg("You must use this command from within a room.")
            return

        if not target.access(self.caller, "control") and not target.access(
            self.caller, "edit"
        ):
            self.caller.msg(
                "You don't have permission to access the options for this room."
            )
            return

        if "clear" in self.switches:
            key = self.lhs.lower() if self.args else None

            if key and not key in settings.DEFAULT_ROOM_OPTIONS.keys():
                self.msg("No such option.")
                return
            if key:
                target.options.set(key, settings.DEFAULT_ROOM_OPTIONS[key][2])
                self.caller.msg(f'Style for "{key}" was reset.')
            else:
                for x in settings.DEFAULT_ROOM_OPTIONS.keys():
                    # self.caller.options.set(x, settings.OPTIONS_ACCOUNT_DEFAULT[x][2])
                    target.attributes.remove(x)
                self.msg("All style options reset to default values.")
            return

        if not self.args:
            self.list_options(target)
        else:
            self.set(target)

    def list_options(self, target):
        self.msg(headers.banner("Room Options", self.caller, width=78))
        table = self.styled_table("Option", "Description", "Type", "Value", width=78)
        for op_key in target.options.options_dict.keys():
            try:
                op_found = target.options.get(op_key, return_obj=True)
                table.add_row(
                    op_key,
                    op_found.description,
                    op_found.__class__.__name__,
                    op_found.display(),
                )
            except Exception as id:
                self.caller.msg(id)

            # if op_found:
            #    table.add_row(op_key, op_found.description, op_found.__class__.__name__, op_found.display())
        self.msg(str(table))

    def set(self, target):
        try:
            result = target.options.set(self.lhs, self.rhs)
        except ValueError as e:
            self.msg(str(e))
            return
        self.msg(f"Room option |c{self.lhs}|n set to |c{result}|n.")


class CmdUnique(default_cmds.MuxCommand):
    key = "unique"
    aliases = ("proper",)
    help_category = "Building"
    locks = "pperm(Builder)"

    def func(self):
        if not self.args:
            self.caller.msg("Usage: unique <object>")
            return

        target = self.caller.search(self.args)
        if not target:
            return

        already_set = target.tags.get("unique", category="flags")
        if already_set:
            target.tags.remove("unique", category="flags")
            self.caller.msg(f"Unique tag removed from {target.key}.")
        else:
            target.tags.add("unique", category="flags")
            self.caller.msg(f"Unique tag added to {target.key}.")


class CmdDestroy(default_cmds.CmdDestroy):
    """
    permanently delete objects

    Usage:
       destroy[/switches] [obj, obj2, obj3, [dbref-dbref], ...]

    Switches:
       override - The destroy command will usually avoid accidentally
                  destroying account objects. This switch overrides this safety.
       force - destroy without confirmation.
    Examples:
       destroy house, roof, door, 44-78
       destroy 5-10, flower, 45
       destroy/force north

    Destroys one or many objects. If dbrefs are used, a range to delete can be
    given, e.g. 4-10. Also the end points will be deleted. This command
    displays a confirmation before destroying, to make sure of your choice.
    You can specify the /force switch to bypass this confirmation.
    """

    key = "destroy"
    aliases = ["delete", "del", "nuke"]
    switch_options = ("override", "force", "purge")
    locks = "cmd:perm(destroy) or perm(Builder)"
    help_category = "Building"

    confirm = True  # set to False to always bypass confirmation
    default_confirm = "yes"  # what to assume if just pressing enter (yes/no)

    def func(self):
        """Implements the command."""

        caller = self.caller
        delete = True

        if not self.args or not self.lhslist:
            caller.msg("Usage: destroy[/switches] [obj, obj2, obj3, [dbref-dbref],...]")
            delete = False

        def delobj(obj):
            # helper function for deleting a single object
            string = ""
            if not obj.pk:
                string = "\nObject %s was already deleted." % obj.db_key
            else:
                objname = obj.name
                if not (obj.access(caller, "control") or obj.access(caller, "delete")):
                    return "\nYou don't have permission to delete %s." % objname
                if obj.account and "override" not in self.switches:
                    return (
                        "\nObject %s is controlled by an active account. Use /override to delete anyway."
                        % objname
                    )
                if obj.dbid == int(settings.DEFAULT_HOME.lstrip("#")):
                    return (
                        "\nYou are trying to delete |c%s|n, which is set as DEFAULT_HOME. "
                        "Re-point settings.DEFAULT_HOME to another "
                        "object before continuing." % objname
                    )

                had_exits = hasattr(obj, "exits") and obj.exits
                had_objs = hasattr(obj, "contents") and any(
                    obj
                    for obj in obj.contents
                    if not (hasattr(obj, "exits") and obj not in obj.exits)
                )
                # do the deletion
                okay = obj.delete()
                if not okay:
                    string += (
                        "\nERROR: %s not deleted, probably because delete() returned False."
                        % objname
                    )
                else:
                    string += "\n%s was destroyed." % objname
                    if had_exits:
                        string += (
                            " Exits to and from %s were destroyed as well." % objname
                        )
                    if had_objs:
                        string += (
                            " Objects inside %s were moved to their homes." % objname
                        )
            return string

        objs = []
        for objname in self.lhslist:
            if not delete:
                continue

            if "-" in objname:
                # might be a range of dbrefs
                dmin, dmax = [
                    utils.dbref(part, reqhash=False) for part in objname.split("-", 1)
                ]
                if dmin and dmax:
                    for dbref in range(int(dmin), int(dmax + 1)):
                        obj = caller.search("#" + str(dbref))
                        if obj:
                            objs.append(obj)
                    continue
                else:
                    obj = caller.search(objname)
            else:
                obj = caller.search(objname)

            if obj is None:
                self.caller.msg(
                    " (Objects to destroy must either be local or specified with a unique #dbref.)"
                )
            elif obj not in objs:
                objs.append(obj)

        if objs and ("force" not in self.switches and type(self).confirm):
            confirm = "Are you sure you want to destroy "
            if len(objs) == 1:
                confirm += objs[0].get_display_name(caller)
            elif len(objs) < 5:
                confirm += ", ".join([obj.get_display_name(caller) for obj in objs])
            else:
                confirm += ", ".join(["#{}".format(obj.id) for obj in objs])
            confirm += " [yes]/no?" if self.default_confirm == "yes" else " yes/[no]"
            answer = ""
            answer = yield (confirm)
            answer = self.default_confirm if answer == "" else answer

            if answer and answer not in ("yes", "y", "no", "n"):
                caller.msg(
                    "Canceled: Either accept the default by pressing return or specify yes/no."
                )
                delete = False
            elif answer.strip().lower() in ("n", "no"):
                caller.msg("Canceled: No object was destroyed.")
                delete = False

        if delete:
            results = []
            for obj in objs:
                results.append(delobj(obj))

            if results:
                caller.msg("".join(results).strip())

from typeclasses.rooms import Room 
from evennia.utils.search import search_tag

class CmdHangout(default_cmds.MuxCommand):
    """
      Syntax: hangouts
      
      Displays a list of hangouts.  Hangouts are simply public rooms that
      you can fast travel to via the 'go' command.
    """
      
    key = "hangouts"
    help_category = "General"
    
    def func(self):
        all_hangouts = Room.objects.filter(db_tags__db_key='hangouts')
        if not all_hangouts:
            self.caller.msg('No hangouts exist.')
            return

class CmdTravel(default_cmds.MuxCommand):
    key = "go"
    aliases = ("travel", "port", "tport")
    help_category = "General"
    
    def func(self):
        self.caller.msg("There are no hangouts to travel to!")
        

class CmdMOTD(default_cmds.MuxCommand):
    key = "motd"
    switch_options = ("clear",
        "set", "read")

    def func(self):
        caller = self.caller
        try:
            motd = ObjectDB.objects.get(pk=settings.MOTD_OBJ or 41) 
        except:
            self.caller.msg("Oops. No MOTD.")
            return
        mdesc = motd.db.desc or None
        if not mdesc:
            self.caller.msg("No MOTD has been set.")
            return

        self.caller.msg(headers.header("MOTD", player=self.caller, width=caller.screenwidth))
        self.caller.msg(f"{mdesc}\n")
        self.caller.msg(headers.footer("EOF", player=caller, width=caller.screenwidth))

import random 
from evennia import EvMenu

def _select_random_node(caller, raw_string, **kwargs):
    kwargs["visit_nr"] = kwargs.get("visit_nr", 1) + 1
    next_node_name = random.choice(["first", "second"])
    # the kwargs returned here will become **kwargs input to next node
    return next_node_name, kwargs

def node_first(caller, raw_string, **kwargs):
    visit_nr = kwargs.get("visit_nr", 1)
    text = f"The first node (visit #{visit_nr})." 
    options = (
        {"key": ("Continue", "C"),
         "desc": "Move on to the next random node!",
         "goto": (_select_random_node, kwargs)
        }
    )
    return text, options

def node_second(caller, raw_string, **kwargs):
    visit_nr = kwargs.get("visit_nr", 1)
    text = f"The second node (visit #{visit_nr})."
    options = (
        {"key": ("Continue", "C"),
         "desc": "Randomize another node!",
         "goto": (_select_random_node, kwargs)
        }
    )
    
class CmdTest(default_cmds.MuxCommand):
    key = "test"

    def func(self):
        menu_nodes = {"first": node_first, "second": node_second}
        EvMenu(self.caller, menu_nodes, startnode="first")
        

LOOTTABLES = (
    ("Rad Scrubber",  4,  "Science:2", "Science", "Uncommon"),
    ("Sensor Array", 5, "Science:3",  "Science", "Uncommon"),
    ("Targeting HUD", 5, "Science:3",  "Science", "Uncommon"),
    ("Internal Database", 4, "Science:2", "Science", "Uncommon"),
    ("Welded Rebar (Raider only)", 2, "Armorer:1", "Repair", "Uncommon"),
    ("Core Assembly", 5, "Science:3", "Science", "Uncommon"),
    ("Blood Cleanser", 4, "Science:1", "Science", "Uncommon"),
    ("Emergency Protocols", 6, "Science:4", "Science", "Uncommon"),
    ("Motion-Assist Servos", 5, "Science:3", "Science", "Uncommon"),
    ("Kinetic Dynamo", 6, "Science:4", "Science",  "Uncommon"),
    ("Medic Pump", 6, "Science:4", "Science", "Uncommon"),
    ("Reactive Plates", 5, "Armorer:4", "Repair", "Uncommon"),
    ("Tesla Coils", 5, "Science:3", "Science", "Uncommon"),
    ("Stealth Boy", 6, "Science:4", "Science", "Uncommon"),
    ("Jetpack", 7, "Armorer:4\nScience:4", "Repair", "Uncommon"),
    ("Rusty Knuckles", 2, "Blacksmith:1",  "Repair", "Uncommon"),
    ("Hydraulic Bracers", 4, "Blacksmith:3",  "Repair",  "Uncommon"),
    ("Optimized Bracers", 2,  "Blacksmith:1", "Repair", "Uncommon"),
    ("Tesla Bracers", 6,  "Blacksmith:3\nScience:1", "Repair",  "Uncommon"),
    ("Calibrated Shocks", 4, "Science:2", "Science", "Uncommon"),
    ("Explosive Vent", 5, "Science:3",  "Science", "Uncommon"),
    ("Overdrive Servos", 5, "Science:3", "Science", "Uncommon"),
)


class CmdResList(default_cmds.MuxCommand):
    key = "listres"

    def colorize(self, i, what):
        return f"|{'C' if i % 2 else 'n'}{what}|n"

    def func(self):
        table = self.styled_table("POWER ARMOR ITEM", "CMP", "PERKS", "SKILL", "RARITY", width=80)
        index = 0
        for x in LOOTTABLES:
            table.add_row(self.colorize(index, str(x[0])),
            self.colorize(index, str(x[1])),
            self.colorize(index, str(x[2])),
            self.colorize(index, str(x[3])),
            self.colorize(index, str(x[4])))
            index = (index+1) % 2

        table.reformat_column(0, width=32)
        table.reformat_column(1, width=7, justify="r")

        self.caller.msg(headers.banner("Power Armor Systems", self.caller, width=80))
        self.caller.msg(str(table))
