"""
Room

Rooms are simple containers that have no location of their own.

"""
import inflect
from collections import defaultdict

from evennia import DefaultRoom, default_cmds
from typeclasses.characters import Character
from .mixins.types import TypeMixins
from .mixins.names import NameMixins
import world.utils as myutils
import evennia.utils as utils
import world.headers as headers
from world.utils import cemit_debug
from evennia.utils.optionhandler import OptionHandler
from evennia.utils import lazy_property
from django.conf import settings
from evennia.utils.ansi import ANSIString
from evennia.utils import list_to_string
from .exits import Exit
from .mixins.ownership import OwnerMixins
from .mixins.messages import MessageMixins
from evennia.utils import evtable

def class_color(who):
    """ return a color code representing permissions """
    perms = who.permissions.all()
    if who.is_superuser:
        return '|g'
    elif "admin" in perms:
        return '|Y'
    elif "programmer" in perms:
        return 'C'
    elif who.is_guest_account:
        return '|M'
    elif "builders" in perms:
        return '|B'
    elif "helpers" in perms:
        return '|M'
    return '|n'


def sort_exits(elist: list) -> list:
    """
    Sort exits, allowing for a user-defined tag
    to over-ride the default sort order (which is
    alphabetically by name).

    All tagged exits will appear at the front of the
    exits list, sorted by the value of the sort_code
    tag.

    Untagged exits will be sorted alphabetically
    and will appear after any tagged exits.

    """
    tagged: list = []
    untagged: list = []
    out: list = []

    for x in elist:
        if sc := x.tags.get(category="sort_code"):
            tagged.append([x, sc])
        else:
            untagged.append([x, x.key])

    if agged:
        out += sorted(tagged, key=lambda i: i[1])

    if untagged:
        out += sorted(untagged, key=lambda i: i[1])

    return [x[0] for x in out]


def format_exits(looker, width, exits):
    return myutils.twocol([e.format_exit(user=looker) for e in sort_exits(exits)], width)
    

# Display the players list for the room.
def format_players(looker, width=80, users=None):
    if not users:
        return ''

    line = ''
    for x in utils.make_iter(users):
        shortdesc = ANSIString(x.db.sdesc or '')
        #if looker is x and not shortdesc:
        #    shortdesc = "(Use sdesc <description>' to set this)".center(width - 30)
        if shortdesc and looker.options.crop_shortdescs:
            shortdesc = utils.crop(shortdesc, width - 30)

        if x.attributes.has('sitting_at_table'):
            p_name = f"{x.key} ({x.db.sitting_at_table})"
            if len(p_name) > 18:
                p_name = x.key
        else:
            p_name = x.key
        fmt_player = f"{' '}{class_color(x)}{p_name:<18.18}|n ({x.gender[0].upper()}) {myutils.idle_ctime(x.idle_time or 0.0)}{utils.time_format(x.idle_time or 0.0, 1):5.5}|n "

        if shortdesc:
            line += f"{fmt_player}{myutils.wrap(shortdesc, width=width, indent=30, label=' ' * 30).lstrip()}\n"
        else:
            line += f"{fmt_player}\n"

    return line

def format_contents(looker: Character = None, width: int = 80, contents: list = None):
    return f"{myutils.twocol([x.name_format() for x in contents], width)}"

def format_places(looker, width, places):
    return f"{myutils.twocol([x.name_format() for x in places], width)}"


class Room(MessageMixins, NameMixins, OwnerMixins, TypeMixins, DefaultRoom):
    """
    Rooms are like any Object, except their location is None
    (which is default). They also use basetype_setup() to
    add locks so they cannot be puppeted or picked up.
    (to change that, use at_object_creation instead)

    See examples/object.py for a list of
    properties and methods available on all Objects.
    """

    @lazy_property
    def options(self):
        return OptionHandler(
            self,
            options_dict=settings.DEFAULT_ROOM_OPTIONS,
            savefunc=self.attributes.add,
            loadfunc=self.attributes.get,
            save_kwargs={"category": "option"},
            load_kwargs={"category": "option"},
        )

    def format_options(self, player: Character = None, width: int = 80, cmd=None) -> str:
        """
        """
        table = player.styled_table(border=None, width=width)
        for op_key in self.options.options_dict.keys():
            op_found = self.options.get(op_key, return_obj=True)
            if op_found.display() not in ("None", "Unlimited", "0", ""):
                table.add_row(
                    f"|C{myutils.capstr(op_key.replace('_', ' '))}|n:",
                    op_found.display(),
                )
                table.reformat_column(0, align="r", width=20)
        return f"{str(table)}\n{headers.divider('', player=player, width=width)}\n"

    def visible_contents(self, player: Character) -> list:
        return self.contents

    @property
    def is_room(self):
        return True

    @property
    def players(self):
        return [x for x in self.contents if x.is_character and x.sessions]

    @property
    def entrances(self):
        return Exit.objects.filter(db_destination=self)

    @property
    def zone(self):
        tmp = self.tags.get(category="zone", return_list=True)
        return (myutils.capstr(tmp[0].replace("_", " "))) if tmp else ""

    @property
    def area(self):
        tmp = self.tags.get(category="area", return_list=True)
        return (myutils.capstr(tmp[0].replace("_", " "))) if tmp else ""

    def ban_character(self, character):
        if character not in self.banlist:
            self.banlist.append(character)

    def unban_character(self, character):
        if character in self.banlist:
            self.banlist.remove(character)

    @property
    def banlist(self):
        return self.db.banlist or []

    def check_banned(self, character):
        return character in self.banlist

    def match_place(self, what):
        places = self.db.places or []
        if not places:
            return None

        found = self.search(what, candidates=places, typeclass="typeclasses.places.places.Place")
        if not found or len(found) != 1 or not found.is_place:
            return None

        return found

    def at_object_creation(self):
        super().at_object_creation()
        self.init_owner()
        self.db.banlist = []

    def format_name(self, looker: Character = None, width: int = 80) -> str:
        # Get the base name.
        out = self.get_display_name(looker)
        zstr = ''

        # Get the area name.
        if tmp := self.area:
            zstr = tmp

        # Get the zone name.
        if tmp := self.zone:
            zstr += f"{', ' if zstr else ''}{tmp}"
           
        if zstr:
            return headers.multiheader(out, zstr, looker, width)
        else:
            return headers.header(out, looker, width)

    
    def return_appearance2(self, looker, **kwargs):
        """
        This formats a description. It is the hook a 'look' command
        should call.

        Args:
            looker (Object): Object doing the looking.
            **kwargs (dict): Arbitrary, optional arguments for users
                overriding the call (unused by default).
        """
        if not looker:
            return ""

        # get and identify all objects
        visible = (con for con in self.contents if con != looker and con.access(looker, "view"))
        exits, users, things = [], [], defaultdict(list)
        for con in visible:
            key = con.get_display_name(looker)
            if con.destination:
                exits.append(con)
            elif con.has_account:
                users.append("|c%s|n" % key)
            else:
                # things can be pluralized
                things[key].append(con)
        # get description, build string
        string = "|w%s" % self.key;

        sZone = self.db.zone;
        if sZone and len(sZone) > 0:
            string += " |b<|w%s|b>|n" % sZone.capitalize();
        string += "\n";
 
        desc = self.db.desc;
        if desc:
            string += "%s\n" % desc;
            
        iConLen = len(self.contents);
        iExitLen = len(self.exits);
        
        
        if exits:
            iCount = 0;
            aExits = [];
            sExitAlias = "";
            sExit = "";
            iExitLen = len(exits);

            while iCount < iExitLen:
                sExit = exits[iCount].key;
                sExitAlias = exits[iCount].aliases.all();
                if sExitAlias and len(sExitAlias) > 0:
                    if len(sExit) > 0:
                        sExit += " ";
                    sExit += "|b(|w%s|b)|n" % sExitAlias[0];
                aExits.append(sExit);
                iCount += 1
            string += "\n|bObvious Exits:|n\n|b[|n%s|b]|n" % list_to_string(aExits)

        if users or things:
                # handle pluralization of things (never pluralize users)
                thing_strings = []
                for key, itemlist in sorted(things.items()):
                    nitem = len(itemlist);
                    if nitem == 1:
                        key, _ = itemlist[0].get_numbered_name(nitem, looker, key=key)
                    else:
                        key = [item.get_numbered_name(nitem, looker, key=key)[1] for item in itemlist][
                            0
                        ]
                    thing_strings.append(key)

                string += "\n|bYou see:|n " + list_to_string(users + thing_strings)

        return string

    # Format the room description.
    def return_appearance(self, looker, **kwargs):
        """
        This formats a description. It is the hook a 'look' command
        should call.

        Args:
            looker (Object): Object doing the looking.
            **kwargs (dict): Arbitrary, optional arguments for users
                overriding the call (unused by default).
        """
        # Cache the looker's screenwidth.
        screenwidth = looker.screenwidth

        # Get and identify all objects. This needs to be replaced with
        # the new visible_contents method that knows about dark and
        # visibility.
        visible = (
            con for con in self.contents if con != looker and con.access(looker, "view")
        )
        # Initialize the lists of the various types of objects we're looking for.
        exits, users, things, places = [], [], [], []

        # Add the looker to the front of the users list.
        if looker.location is self:
            users = [looker]

        # Filter the visible objects into lists based on their type.
        for con in visible:
            if con.is_exit:
                exits.append(con)
            elif con.has_account and con.sessions:
                users.append(con)
            elif con.is_place:
                places.append(con)
            elif con.is_thing:
                things.append(con)

        string = self.format_name(looker, screenwidth)
        # string += self.format_options(looker, screenwidth)
        string += f"{self.db.desc or ''}\n"

        if users:
            string += headers.divider("Players", looker, screenwidth)
            string += format_players(looker, screenwidth, users)
        if things:
            string += headers.divider("Contents", looker, screenwidth)
            string += format_contents(looker, screenwidth, things)
        if places:
            string += headers.divider("Places", looker, screenwidth)
            string += self.format_places(looker, screenwidth, places)
        if exits:
            string += headers.divider("Exits", looker, screenwidth)
            string += format_exits(looker, screenwidth, exits)

        t = []
        self.db.details and t.append('details')
        places and t.append('places')
        self.tags.get('logging') and t.append('logging')
        self.tags.get('scene') and t.append('scene')
        if t:
            string += headers.footer(myutils.itemize(t), looker, width=screenwidth)
        else:
            string += headers.footer('', looker, width=screenwidth)

        return string
