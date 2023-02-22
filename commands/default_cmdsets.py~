"""
Command sets

All commands in the game must be grouped in a cmdset.  A given command
can be part of any number of cmdsets and cmdsets can be added/removed
and merged onto entities at runtime.

To create new commands to populate the cmdset, see
`commands/command.py`.

This module wraps the default command sets of Evennia; overloads them
to add/remove commands from the default lineup. You can create your
own cmdsets by inheriting from them or directly from `evennia.CmdSet`.

"""

from evennia import default_cmds

from .zone import CmdZone
from .mail import CmdMailCharacter
from .news import CmdNews
from .local import *
from .scenesys import CmdScene
from keys.commands import CmdKey
from boards.commands import BoardCmdSet
from orgs.commands import CmdOrg
from jobs.commands import CmdJobs
from .desc import CmdDesc
from typeclasses.places.cmdset_places import DefaultCmdSet
from chargen.sheet import CmdSheet
from chargen.commands import CmdSkill
from .help import CmdHelp

class CharacterCmdSet(default_cmds.CharacterCmdSet):
    """alias gall="git add * && git commit -m "." && git push"
    The `CharacterCmdSet` contains general in-game commands like `look`,
    `get`, etc available on in-game Character objects. It is merged with
    the `AccountCmdSet` when an Account puppets a Character.
    """

    key = "DefaultCharacter"

    def at_cmdset_creation(self):
        super().at_cmdset_creation()
        self.add(CmdZone)
        self.add(CmdMailCharacter)
        self.add(CmdKey)
        self.add(CmdWho)
        self.add(CmdSay)
        self.add(CmdGive)
        self.add(CmdDrop)
        self.add(CmdAudit)
        self.add(CmdSex)
        self.add(CmdFEdit)
        self.add(CmdAudit)
        self.add(CmdChown)
        self.add(CmdInventory)
        self.add(CmdGlance)
        self.add(CmdShout)
        self.add(CmdPage)
        self.add(CmdFollow)
        self.add(CmdBlock)
        self.add(CmdMessage)
        self.add(CmdNews())
        self.add(CmdOrg())
        self.add(CmdPose())
        self.add(DefaultCmdSet())
        self.add(CmdScene())
        #self.add(CmdHangout())
        #self.add(CmdTravel())
        self.add(CmdSdesc())
        self.add(CmdDesc())
        self.add(CmdMOTD())
        self.add(CmdSheet())
        self.add(CmdSkill())
        self.add(CmdRoom())
        self.add(CmdResGen())
        self.add(CmdTest())
        self.add(CmdResList())
        
class AccountCmdSet(default_cmds.AccountCmdSet):
    """
    This is the cmdset available to the Account at all times. It is
    combined with the `CharacterCmdSet` when the Account puppets a
    Character. It holds game-account-specific commands, channel
    commands, etc.
    """

    key = "DefaultAccount"

    def at_cmdset_creation(self):
        """
        Populates the cmdset
        """
        super().at_cmdset_creation()
        #
        # any commands you add below will overload the default ones.
        #
        self.add(CmdLast)
        self.add(CmdStyle)
        self.add(BoardCmdSet())
        self.add(CmdJobs())
        self.add(CmdHelp())


class UnloggedinCmdSet(default_cmds.UnloggedinCmdSet):
    """
    Command set available to the Session before being logged in.  This
    holds commands like creating a new account, logging in, etc.
    """

    key = "DefaultUnloggedin"

    def at_cmdset_creation(self):
        """
        Populates the cmdset
        """
        super().at_cmdset_creation()
        #
        # any commands you add below will overload the default ones.
        #


class SessionCmdSet(default_cmds.SessionCmdSet):
    """
    This cmdset is made available on Session level once logged in. It
    is empty by default.
    """

    key = "DefaultSession"

    def at_cmdset_creation(self):
        """
        This is the only method defined in a cmdset, called during
        its creation. It should populate the set with command instances.

        As and example we just add the empty base `Command` object.
        It prints some info.
        """
        super().at_cmdset_creation()
        #
        # any commands you add below will overload the default ones.
        #
