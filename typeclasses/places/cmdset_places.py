"""
This defines the cmdset for the red_button. Here we have defined
the commands and the cmdset in the same module, but if you
have many different commands to merge it is often better
to define the cmdset separately, picking and choosing from
among the available commands as to what should be included in the
cmdset - this way you can often re-use the commands too.
"""
from evennia import default_cmds, CmdSet
from evennia.utils.utils import list_to_string


def get_movement_message(verb, place):
    """Returns the movement message for joining/leaving a place"""
    if not place or not place.key:
        return "You %s the place." % verb
    prefix = place.key.split()[0]
    article = ""
    if prefix.lower() not in ("the", "a", "an"):
        article = "the "
    return "You %s %s%s." % (verb, article, place.key)

# ------------------------------------------------------------
# Commands defined for places
# ------------------------------------------------------------


class CmdJoin(default_cmds.MuxCommand):
    """
    Sits down at a place inside a room

    Usage:
        join <place #>
        join <place name>

    Sits down at one of the places in the room for private chat if it
    has room remaining. Once sitting at a place, the 'tt' or
    'tabletalk' command will be available. Logging out or disconnecting
    will require you to rejoin a place upon reconnecting.

    To leave, use 'depart'.
    
    |cCredit|n:
    From Arx, with minor changes.
    """
    key = "join"
    locks = "cmd:all()"
    help_category = "Social"

    def func(self):
        """Implements command"""
        caller = self.caller
        places = caller.location.db.places or []
        table = caller.db.sitting_at_table or None
        args = self.args

        if not args:
            caller.msg("Usage: join <place name or number>")
            caller.msg("To see a list of places: places")
            return

        if table:
            table.leave(caller)

        # The player probably only has this command if it's in their inventory
        if not places:
            caller.msg("This room contains no places.")
            return
            
        args = args.strip("#").strip()
        if args.isnumeric():
            args = abs(int(args) - 1)
            if not (0 <= args < len(places)):
                caller.msg("Number specified does not match any of the places here.")
                return
            table = places[args]
        else:
            table = caller.location.match_place(args)
        
        if not table:
            self.caller.msg("No such place.")
            return
                   
        occupants = table.db.occupants or []
        if occupants and len(occupants) >= (table.db.max_spots or 0):
            caller.msg(f"There is no more room at {table.key}.")
            return
    
        table.join(caller)

        table.generate_message("join", caller=caller)

        
class CmdListPlaces(default_cmds.MuxCommand):
    """
    Lists places in current room for private chat
    Usage:
        places

    Lists all the places in the current room that you can chat at and how
    many empty spaces each has. If there any places within the room, the
    'join' command will be available. Once sitting at a place, the 'tt' or
    'tabletalk' command will be available. Logging out or disconnecting
    will require you to join a place once more. To leave a place, use
    'depart'.

    |cCredits|n:
    From Arx, with minor changes.
    """
    key = "places"
    locks = "cmd:all()"
    help_category = "Social"

    def func(self):
        """Implements command"""
        caller = self.caller
        places = caller.location.db.places or []
        caller.msg("Places here:")
        caller.msg("------------")
        if not places:
            caller.msg("No places found.")
            return
        table = self.styled_table("NAME", "##", "OCCUPANTS", width=40)
        for num in range(len(places)):
            table.add_row(places[num].key,
                    places[num].db.max_spots or 0,
                    ", ".join([x.name for x in places[num].db.occupants]))

        #for num in range(len(places)):
        #    p_name = places[num].key
        #    max_spots = places[num].db.max_spots or 0
        #    occupants = places[num].db.occupants or []
        #    spots = max_spots - len(occupants)
        #    caller.msg("%s (#%s) : %s empty spaces" % (p_name, num + 1, spots))
        #    if occupants:
        #        # get names rather than keys so real names don't show up for masked characters
        #        names = [ob.name for ob in occupants if ob.access(caller, "view#")]
        #        caller.msg("-Occupants: %s" % list_to_string(names))
        self.caller.msg(str(table))


class DefaultCmdSet(CmdSet):
    """
    The default cmdset always sits
    on the button object and whereas other
    command sets may be added/merge onto it
    and hide it, removing them will always
    bring it back. It's added to the object
    using obj.cmdset.add_default().
    """
    key = "PlacesDefault"
    # if we have multiple wearable objects, just keep
    # one cmdset, ditch others
    key_mergetype = {"PlacesDefault": "Replace"}
    priority = 0
    duplicates = False

    def at_cmdset_creation(self):
        """Init the cmdset"""
        self.add(CmdJoin())
        self.add(CmdListPlaces())
        

class SittingCmdSet(CmdSet):
    """
    The default cmdset always sits
    on the button object and whereas other
    command sets may be added/merge onto it
    and hide it, removing them will always
    bring it back. It's added to the object
    using obj.cmdset.add_default().
    """
    key = "SittingCmdSet"
    # if we have multiple wearable objects, just keep
    # one cmdset, ditch others
    key_mergetype = {"SittingCmdSet": "Replace"}
    priority = 0
    duplicates = False

    def at_cmdset_creation(self):
        """Init the cmdset"""
        self.add(CmdDepart())
        self.add(CmdTableTalk())


class CmdDepart(default_cmds.MuxCommand):
    """
    Stands up from the table you are at.

    Usage:
        depart

    Leaves your current table. Logging out or disconnecting will
    cause you to leave automatically. To see available places,
    use 'places'. To join a place, use 'join'.
    
    |cCredits|n:
    From Arx, with minor changes.
    """
    key = "depart"
    locks = "cmd:all()"
    help_category = "Social"

    def func(self):
        """Implements command"""
        caller = self.caller
        table = caller.db.sitting_at_table
        if not table:
            caller.msg("You are not sitting at a place.")
            return
        table.leave(caller)
        #table.generate_message("depart", caller)
        #caller.msg(get_movement_message("leave", table))
        del caller.db.sitting_at_table


class CmdTableTalk(default_cmds.MuxCommand):
    """
    Speaks at your current table.

    Usage:
        tt <message>
        tt/ooc <message>

    Sends a message to your current table. You may pose at the table by
    starting a message with ':' or ';'. ':' has a space after your name,
    while ';' does not. So ':waves' is 'Bob waves', while ';s waves' is
    'Bobs waves'. A table emit '|' does not add your name, so be sure to 
    identify yourself somehow in your text.

    To leave a place, use 'depart'.
    
    |cCredits|n:
    From Arx, with minor changes.
    """
    key = "tt"
    locks = "cmd:all()"
    help_category = "Social"
    # characters used for poses/emits
    char_symbols = (";", ":", "|")

    def func(self):
        """Implements command"""
        caller = self.caller
        args = self.args
        if not args:
            caller.msg("Usage: |wtt <message>|n")
            return
        table = caller.db.sitting_at_table
        if not table:
            caller.msg("You are not sitting at a private table currently.")
            return
        options = {'is_pose': True}
        ooc_string = ""
        if "ooc" in self.switches:
            options = {}
            ooc_string = "|w(OOC)|n "
        prefix = "%sAt the %s," % (ooc_string, table.key)
        # get the first character to see if it's special
        start_char = args[0]
        if start_char in self.char_symbols:
            whitespace = " " if args.startswith(":") else ""
            msg = args.lstrip(":").lstrip(";").lstrip("|")
            msg = "%s%s" % (whitespace, msg)
            if start_char == "|":
                # send message as an emit
                msg = "%s %s" % (prefix, msg)
                emit = True
            else:  # send message as a pose
                msg = "%s |c%s|n%s" % (prefix, caller.name, msg)
                emit = False
            # gives the message, its sender, and whether it's an emit
            table.tt_msg(msg, from_obj=caller, emit=emit, options=options)
            return
        caller.msg('%s you say, "%s"' % (prefix, args), options=options, from_obj=caller)
        table.tt_msg('%s |c%s|n says, "%s"' % (prefix, caller.name, args), from_obj=caller,
                     exclude=caller, options=options)
